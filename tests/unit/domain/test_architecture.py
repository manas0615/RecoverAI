import ast
from pathlib import Path

import pytest


def test_domain_has_no_infrastructure_imports():
    """
    Ensures that files in recoverai/domain do not import infrastructure code.
    """
    domain_dir = Path("recoverai/domain")

    forbidden_imports = [
        "sqlite3",
        "sqlalchemy",
        "fastapi",
        "requests",
        "razorpay",
        "recoverai.config",
        "recoverai.integrations",
        "recoverai.ai",
        "recoverai.mcp",
        "recoverai.policy.engine",
        "recoverai.database",
    ]

    violations = []

    for py_file in domain_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=str(py_file))
            except SyntaxError as e:
                pytest.fail(f"Could not parse {py_file}: {e}")

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for forbidden in forbidden_imports:
                            if alias.name == forbidden or alias.name.startswith(
                                forbidden + "."
                            ):
                                violations.append(f"{py_file}: import {alias.name}")
                elif isinstance(node, ast.ImportFrom) and node.module:
                    for forbidden in forbidden_imports:
                        if node.module == forbidden or node.module.startswith(
                            forbidden + "."
                        ):
                            violations.append(
                                f"{py_file}: from {node.module} import ..."
                            )

    assert not violations, (
        f"Domain contains forbidden infrastructure imports: {violations}"
    )
