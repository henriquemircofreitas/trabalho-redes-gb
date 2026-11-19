"""The video notebook must stay in sync with its generator and execute without errors."""

import importlib.util
from pathlib import Path

import pytest

nbformat = pytest.importorskip("nbformat")
nbclient = pytest.importorskip("nbclient")

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "notebooks" / "demo_video.ipynb"


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "make_notebook", ROOT / "scripts" / "make_notebook.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_notebook_matches_generator():
    expected = [cell.source for cell in _load_generator().build().cells]
    committed = [cell.source for cell in nbformat.read(NOTEBOOK, 4).cells]
    assert committed == expected, "run: uv run --group notebook python scripts/make_notebook.py"


def test_notebook_executes_and_reproduces_all_trials():
    notebook = _load_generator().build()
    nbclient.NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    ).execute()
    printed = "".join(
        output.get("text", "")
        for cell in notebook.cells
        if cell.cell_type == "code"
        for output in cell.outputs
    )
    assert "990/990 ensaios" in printed
