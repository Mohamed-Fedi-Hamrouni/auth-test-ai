#!/usr/bin/env python3
"""Validate documentation traceability, threat rows, API links and Markdown links."""

from __future__ import annotations

import re
import sys
import ast
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FUNCTIONAL = DOCS / "requirements/functional-requirements.md"
MATRIX = DOCS / "testing/traceability-matrix.md"
API = DOCS / "design/api-contract.md"
THREATS = DOCS / "security/threat-model.md"


def extracted_ids(text: str) -> set[str]:
    return set(re.findall(r"FR-(?:AUTH|ADMIN|AUDIT|TEST|AI)-\d{3}", text))


def validate() -> list[str]:
    errors: list[str] = []
    requirement_ids = extracted_ids(FUNCTIONAL.read_text(encoding="utf-8"))
    matrix_ids = extracted_ids(MATRIX.read_text(encoding="utf-8"))
    if missing := sorted(requirement_ids - matrix_ids):
        errors.append(f"Requirements absent from matrix: {', '.join(missing)}")

    matrix_text = MATRIX.read_text(encoding="utf-8")
    matrix_rows: list[list[str]] = []
    for line in matrix_text.splitlines():
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells[0] != "Requirement ID":
            matrix_rows.append(cells)
    test_ids = [row[2] for row in matrix_rows]
    duplicates = sorted(
        identifier for identifier, count in Counter(test_ids).items() if count > 1
    )
    if duplicates:
        errors.append(f"Duplicate matrix Test Case IDs: {', '.join(duplicates)}")
    statuses = Counter(row[7] for row in matrix_rows)
    total_match = re.search(
        r"Total : (\d+) lignes de données — Implemented: (\d+); Designed: (\d+); Planned: (\d+)\.",
        matrix_text,
    )
    expected_totals = (
        len(matrix_rows),
        statuses["Implemented"],
        statuses["Designed"],
        statuses["Planned"],
    )
    if total_match is None or tuple(map(int, total_match.groups())) != expected_totals:
        errors.append(f"Incorrect matrix totals; expected {expected_totals}")
    for row in matrix_rows:
        if row[7] != "Implemented" or "Pytest" not in row[4]:
            continue
        qualified = re.search(r"`([^`]+)::(test_[^`]+)`", row[8])
        if qualified is None:
            errors.append(f"Implemented Pytest row lacks an exact function: {row[2]}")
            continue
        relative_path, function_name = qualified.groups()
        test_path = ROOT / relative_path
        if not test_path.exists():
            errors.append(f"Missing implemented Pytest file: {relative_path}")
            continue
        tree = ast.parse(test_path.read_text(encoding="utf-8"))
        functions = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        if function_name not in functions:
            errors.append(f"Missing implemented Pytest function: {qualified.group(1)}")

    api_text = API.read_text(encoding="utf-8")
    routes = re.findall(r"`(?:GET|POST|PATCH) (/api/[^`]+)`", api_text)
    for route in routes:
        row = next((line for line in api_text.splitlines() if route in line), "")
        if not re.search(r"(?:FR-|NFR-)[A-Z]+-\d{3}", row):
            errors.append(f"API route without requirement: {route}")

    threat_rows = [
        line
        for line in THREATS.read_text(encoding="utf-8").splitlines()
        if line.startswith("| THR-")
    ]
    for row in threat_rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if (
            len(cells) < 10
            or not cells[5]
            or not cells[7]
            or not cells[7].startswith("SEC-")
        ):
            errors.append(
                f"Threat without mitigation/security test: {cells[0] if cells else row}"
            )

    link_pattern = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
    for markdown in [ROOT / "README.md", *DOCS.rglob("*.md")]:
        for target in link_pattern.findall(markdown.read_text(encoding="utf-8")):
            clean = target.split("#", 1)[0]
            if not clean or re.match(r"(?:https?|mailto):", clean):
                continue
            if not (markdown.parent / clean).resolve().exists():
                errors.append(f"Broken link in {markdown.relative_to(ROOT)}: {target}")

    required = {
        FUNCTIONAL: ["# Exigences fonctionnelles", "## Authentification"],
        API: ["# Contrat API proposé", "## Règles transverses"],
        THREATS: ["# Threat model", "## Vulnérabilités npm modérées observées"],
    }
    for path, headings in required.items():
        content = path.read_text(encoding="utf-8")
        for heading in headings:
            if heading not in content:
                errors.append(f"Missing section in {path.relative_to(ROOT)}: {heading}")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        print("Documentation validation failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        sys.exit(1)
    print("Documentation validation passed.")
