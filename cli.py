"""Command-line demonstration for the EssayScaff V2 NLP baseline."""

import argparse
import json
import sys

from services.nlp_service import NLPService
from services.topic_service import TopicService


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract linguistic observations from student writing."
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="Text to analyze; omit it to enter text interactively.",
    )
    parser.add_argument(
        "--topic",
        help="Teacher's assignment topic; enables lexical topic analysis.",
    )
    parser.add_argument(
        "--focus-term",
        action="append",
        dest="focus_terms",
        help="Teacher-defined focus term or phrase (repeat the option as needed).",
    )
    arguments = parser.parse_args()
    text = " ".join(arguments.text) if arguments.text else input("Enter text: ")

    try:
        nlp_service = NLPService()
        if arguments.topic:
            result = TopicService(nlp_service).analyze(
                text,
                arguments.topic,
                arguments.focus_terms,
            )
        elif arguments.focus_terms:
            parser.error("--focus-term requires --topic")
        else:
            result = nlp_service.analyze(text)
    except (RuntimeError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
