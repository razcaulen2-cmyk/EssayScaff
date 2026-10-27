(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.createWritingActivityTracker = api.createWritingActivityTracker;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const IDLE_MS = 60_000;
  const TICK_MS = 5_000;
  const FLUSH_MS = 30_000;
  const BUCKET_MS = 5_000;
  const LOCK_TTL_MS = 20_000;
  const MAX_EVENTS_PER_REQUEST = 24;
  const MAX_BUFFER_EVENTS = 60;
  const MAX_RETRY_EVENTS = 240;
  const WRITING_STAGES = new Set(["INTRODUCTION", "BODY", "CONCLUSION"]);

  function makeTabId() {
    const cryptoObject = typeof globalThis !== "undefined" ? globalThis.crypto : null;
    if (cryptoObject && typeof cryptoObject.randomUUID === "function") {
      return cryptoObject.randomUUID();
    }
    return `tab-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  function mergeEvents(events) {
    const merged = new Map();
    for (const event of events) {
      const key = `${event.stage}:${event.bucket_start}`;
      const existing = merged.get(key);
      if (!existing || event.seconds > existing.seconds) {
        merged.set(key, { ...event });
      }
    }
    return [...merged.values()].sort(
      (first, second) => first.bucket_start - second.bucket_start
    );
  }

  function createWritingActivityTracker(options = {}) {
    const canTrack =
      typeof options.canTrack === "function" ? options.canTrack : () => true;
    const isHidden =
      typeof options.isHidden === "function" ? options.isHidden : () => false;
    const now = typeof options.now === "function" ? options.now : () => Date.now();
    const fetchImpl =
      typeof options.fetchImpl === "function" ? options.fetchImpl : null;
    const storage = options.storage || null;
    const setIntervalImpl =
      typeof options.setIntervalImpl === "function"
        ? options.setIntervalImpl
        : null;
    const clearIntervalImpl =
      typeof options.clearIntervalImpl === "function"
        ? options.clearIntervalImpl
        : null;
    const onDisabled =
      typeof options.onDisabled === "function" ? options.onDisabled : () => {};
    const tabId = options.tabId || makeTabId();

    let enabled = false;
    let disabledByServer = false;
    let assignmentId = null;
    let sessionId = null;
    let activeStage = null;
    let lastEditAt = null;
    let lastTickAt = null;
    let lastFlushAt = null;
    let buffer = [];
    let retryBuffer = [];
    let timer = null;
    let flushPromise = null;

    function lockKey() {
      return `essayScaffActivityWriter:${assignmentId}`;
    }

    function claimLock(currentTime) {
      if (!storage) return;
      try {
        storage.setItem(
          lockKey(),
          JSON.stringify({ tabId, expiresAt: currentTime + LOCK_TTL_MS })
        );
      } catch (_error) {
        // Browser storage can be unavailable; tracking still works without the lease.
      }
    }

    function ownsLock(currentTime) {
      if (!storage) return true;
      try {
        const raw = storage.getItem(lockKey());
        if (!raw) return false;
        const lease = JSON.parse(raw);
        return Boolean(lease) && lease.tabId === tabId && lease.expiresAt >= currentTime;
      } catch (_error) {
        return true;
      }
    }

    function releaseLock() {
      if (!storage) return;
      try {
        const raw = storage.getItem(lockKey());
        if (!raw) return;
        const lease = JSON.parse(raw);
        if (lease && lease.tabId === tabId) storage.removeItem(lockKey());
      } catch (_error) {
        // Ignore unavailable or malformed leases.
      }
    }

    function stopTimer() {
      if (timer !== null && clearIntervalImpl) clearIntervalImpl(timer);
      timer = null;
    }

    function ensureTimer() {
      if (timer !== null || !setIntervalImpl) return;
      timer = setIntervalImpl(() => tick(), TICK_MS);
    }

    function endActivityPeriod(release = true) {
      activeStage = null;
      lastEditAt = null;
      lastTickAt = null;
      if (release) releaseLock();
    }

    function addEvent(stage, timestamp, seconds) {
      const bucketStart = Math.floor(timestamp / BUCKET_MS) * (BUCKET_MS / 1000);
      const existing = buffer.find(
        (event) => event.stage === stage && event.bucket_start === bucketStart
      );
      if (existing) {
        existing.seconds = Math.max(existing.seconds, seconds);
        return;
      }
      buffer.push({ stage, bucket_start: bucketStart, seconds });
    }

    function requeue(events) {
      retryBuffer = mergeEvents(events.concat(retryBuffer)).slice(
        -MAX_RETRY_EVENTS
      );
    }

    async function postEvents(events) {
      if (!fetchImpl) return "discard";
      try {
        const response = await fetchImpl("/api/writing-activity", {
          method: "POST",
          keepalive: true,
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": options.csrfToken || "",
          },
          body: JSON.stringify({
            assignment_id: assignmentId,
            session_id: sessionId,
            events,
          }),
        });
        if (response && response.ok) return "ok";
        if (response && response.status === 503) return "disabled";
        if (
          response &&
          [400, 403, 404, 409].includes(response.status)
        ) {
          return "discard";
        }
        return "retry";
      } catch (_error) {
        return "retry";
      }
    }

    function flush() {
      if (flushPromise) {
        return flushPromise.then(() => {
          if (
            !enabled ||
            assignmentId === null ||
            !sessionId ||
            (!buffer.length && !retryBuffer.length)
          ) {
            return undefined;
          }
          return flush();
        });
      }
      if (
        !enabled ||
        assignmentId === null ||
        !sessionId ||
        (!buffer.length && !retryBuffer.length)
      ) {
        return Promise.resolve();
      }
      const pending = mergeEvents(retryBuffer.concat(buffer));
      buffer = [];
      retryBuffer = [];
      flushPromise = (async () => {
        try {
          for (let index = 0; index < pending.length; index += MAX_EVENTS_PER_REQUEST) {
            const chunk = pending.slice(index, index + MAX_EVENTS_PER_REQUEST);
            const outcome = await postEvents(chunk);
            if (outcome === "ok") continue;
            if (outcome === "disabled") {
              disabledByServer = true;
              enabled = false;
              stopTimer();
              onDisabled();
              return;
            }
            if (outcome === "retry") {
              requeue(pending.slice(index));
              return;
            }
            return;
          }
        } finally {
          flushPromise = null;
        }
      })();
      return flushPromise;
    }

    function configure(context = {}) {
      const nextAssignmentId = Number.isInteger(context.assignmentId)
        ? context.assignmentId
        : null;
      const nextSessionId =
        typeof context.sessionId === "string" && context.sessionId
          ? context.sessionId
          : null;
      const contextChanged =
        nextAssignmentId !== assignmentId || nextSessionId !== sessionId;
      if (contextChanged) {
        if (buffer.length || retryBuffer.length) void flush();
        buffer = [];
        retryBuffer = [];
        endActivityPeriod();
        stopTimer();
        lastFlushAt = null;
      }
      assignmentId = nextAssignmentId;
      sessionId = nextSessionId;
      enabled =
        Boolean(context.enabled) &&
        !disabledByServer &&
        assignmentId !== null &&
        sessionId !== null;
      if (!enabled) {
        endActivityPeriod();
        stopTimer();
      }
    }

    function noteEdit(stage) {
      if (
        !enabled ||
        disabledByServer ||
        !WRITING_STAGES.has(stage) ||
        !canTrack() ||
        isHidden()
      ) {
        return;
      }
      const currentTime = now();
      if (activeStage !== stage) {
        activeStage = stage;
        lastTickAt = currentTime;
        lastFlushAt = currentTime;
      } else if (lastTickAt === null) {
        lastTickAt = currentTime;
      }
      if (lastEditAt === null) lastTickAt = currentTime;
      if (lastFlushAt === null) lastFlushAt = currentTime;
      lastEditAt = currentTime;
      claimLock(currentTime);
      ensureTimer();
    }

    function tick() {
      if (!enabled || disabledByServer || !canTrack()) return;
      if (isHidden()) {
        leaveWorkspace();
        return;
      }
      if (activeStage === null || lastEditAt === null) return;
      const currentTime = now();
      if (currentTime - lastEditAt > IDLE_MS) {
        endActivityPeriod();
        stopTimer();
        void flush();
        return;
      }
      if (!ownsLock(currentTime)) {
        endActivityPeriod();
        stopTimer();
        void flush();
        return;
      }
      if (lastTickAt === null || lastTickAt > currentTime) {
        lastTickAt = currentTime;
      }
      const elapsedMs = Math.min(TICK_MS, currentTime - lastTickAt);
      lastTickAt = currentTime;
      const seconds = Math.round(elapsedMs / 1000);
      if (seconds >= 1) addEvent(activeStage, currentTime, seconds);
      claimLock(currentTime);
      if (lastFlushAt === null) {
        lastFlushAt = currentTime;
      } else if (currentTime - lastFlushAt >= FLUSH_MS) {
        lastFlushAt = currentTime;
        void flush();
      }
      if (buffer.length >= MAX_BUFFER_EVENTS) void flush();
    }

    function stageChanged() {
      endActivityPeriod();
      stopTimer();
      lastFlushAt = null;
      if (buffer.length) void flush();
    }

    function leaveWorkspace() {
      endActivityPeriod();
      stopTimer();
      lastFlushAt = null;
      void flush();
    }

    return {
      configure,
      noteEdit,
      tick,
      flush,
      stageChanged,
      leaveWorkspace,
      getState() {
        return {
          enabled,
          assignmentId,
          sessionId,
          activeStage,
          bufferEvents: buffer.length,
          retryEvents: retryBuffer.length,
        };
      },
    };
  }

  return {
    createWritingActivityTracker,
    IDLE_MS,
    TICK_MS,
    FLUSH_MS,
    BUCKET_MS,
    MAX_EVENTS_PER_REQUEST,
  };
});
