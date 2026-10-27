"""Small, reusable linguistic analyzer backed by spaCy."""

from typing import Any

from spacy.tokens import Doc

import spacy
from spacy.language import Language


class NLPService:
    """Analyze text once and derive linguistic observations from that Doc."""

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        try:
            self.nlp: Language = spacy.load(model_name)
        except OSError as error:
            raise RuntimeError(
                f"spaCy model '{model_name}' is not installed. "
                f"Install it with: python -m spacy download {model_name}"
            ) from error

    def analyze(self, text: str) -> dict[str, Any]:
        """Return counts, sentences, tokens, dependencies, and noun phrases.

        Character offsets are zero-based, end-exclusive offsets into the original
        input string. Token count includes punctuation; alphabetic word count
        counts tokens made up only of alphabetic characters.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        return self.analyze_doc(self.parse(text))

    def parse(self, text: str) -> Doc:
        """Parse text once and return its reusable spaCy Doc."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return self.nlp(text)

    def analyze_doc(self, doc: Doc) -> dict[str, Any]:
        """Build the Phase 1 result from an already parsed Doc."""
        text = doc.text

        # spaCy can expose whitespace-only input as a space token/sentence.
        # Those are not linguistic tokens or sentences for this service.
        if not text.strip():
            return {
                "text": text,
                "counts": {
                    "alphabetic_word_count": 0,
                    "sentence_count": 0,
                    "token_count": 0,
                },
                "sentences": [],
                "tokens": [],
                "noun_phrases": [],
            }

        tokens = [self._token_data(token) for token in doc if not token.is_space]
        sentences = []
        for sentence in doc.sents:
            sentence_tokens = [token for token in sentence if not token.is_space]
            if not sentence_tokens:
                continue
            sentence_start = sentence_tokens[0].idx
            sentence_end = sentence_tokens[-1].idx + len(sentence_tokens[-1])
            sentence_token_data = [self._token_data(token) for token in sentence_tokens]
            sentence_dependencies = [
                {
                    "text": token.text,
                    "start": token.idx,
                    "end": token.idx + len(token),
                    "dependency": token.dep_,
                    "head": token.head.text,
                    "head_start": token.head.idx,
                }
                for token in sentence
                if not token.is_space
            ]
            sentences.append(
                {
                    "text": text[sentence_start:sentence_end],
                    "start": sentence_start,
                    "end": sentence_end,
                    "tokens": sentence_token_data,
                    "dependencies": sentence_dependencies,
                    "subjects": self._related_tokens(sentence, {"nsubj", "nsubjpass", "csubj", "csubjpass"}),
                    "objects_or_complements": self._related_tokens(
                        sentence,
                        {"dobj", "obj", "iobj", "pobj", "attr", "oprd", "acomp", "ccomp", "xcomp"},
                    ),
                }
            )

        noun_phrases = [
            {"text": phrase.text, "start": phrase.start_char, "end": phrase.end_char}
            for phrase in doc.noun_chunks
        ]

        return {
            "text": text,
            "counts": {
                "alphabetic_word_count": sum(1 for token in doc if token.is_alpha),
                "sentence_count": len(sentences),
                "token_count": len(tokens),
            },
            "sentences": sentences,
            "tokens": tokens,
            "noun_phrases": noun_phrases,
        }

    @staticmethod
    def _token_data(token: Any) -> dict[str, Any]:
        return {
            "index": token.i,
            "text": token.text,
            "start": token.idx,
            "end": token.idx + len(token),
            "lemma": token.lemma_,
            "pos": token.pos_,
            "tag": token.tag_,
            "dependency": token.dep_,
            "head": token.head.text,
            "is_alpha": token.is_alpha,
        }

    @staticmethod
    def _related_tokens(sentence: Any, dependencies: set[str]) -> list[dict[str, Any]]:
        """Return only relationships actually tagged by the parser."""
        return [
            {
                "text": token.text,
                "start": token.idx,
                "end": token.idx + len(token),
                "dependency": token.dep_,
                "head": token.head.text,
            }
            for token in sentence
            if not token.is_space and token.dep_ in dependencies
        ]
