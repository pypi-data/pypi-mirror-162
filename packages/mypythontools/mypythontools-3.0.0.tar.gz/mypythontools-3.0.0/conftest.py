"""Runs before every pytest test. Used automatically (at least at VS Code)."""
from __future__ import annotations

from mypythontools_cicd import tests

tests.setup_tests(matplotlib_test_backend=True)
