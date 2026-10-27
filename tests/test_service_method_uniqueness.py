"""Guard against shadowed duplicate methods in production service classes."""

import ast
from collections import Counter
from pathlib import Path


SERVICES_DIR = Path(__file__).resolve().parents[1] / "services"


def test_service_classes_have_no_duplicate_method_definitions() -> None:
    duplicates = []
    for source_path in sorted(SERVICES_DIR.rglob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            methods = [
                member.name
                for member in node.body
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            duplicates.extend(
                f"{source_path.relative_to(SERVICES_DIR)}:{node.name}.{name}"
                for name, count in Counter(methods).items()
                if count > 1
            )

    assert duplicates == [], "Duplicate service methods shadow definitions: " + ", ".join(duplicates)
