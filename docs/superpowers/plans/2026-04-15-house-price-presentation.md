# House Price Presentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 5-slide PowerPoint presentation about the house price prediction project and save it as a `.pptx` file.

**Architecture:** Use a small Python script based only on the standard library to generate a valid PowerPoint package. Keep the presentation content fixed and matched to the approved slide outline. Validate the output with a small test that confirms the expected slide files are present in the generated archive.

**Tech Stack:** Python standard library, ZIP-based Open XML PowerPoint structure

---

### Task 1: Add a failing test for the presentation generator

**Files:**
- Create: `tests/test_generate_ppt.py`
- Test: `tests/test_generate_ppt.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
import subprocess
import sys
import zipfile


def test_generator_creates_five_slide_pptx(tmp_path):
    output_path = tmp_path / "deck.pptx"
    result = subprocess.run(
        [sys.executable, "tools/generate_ppt.py", str(output_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.exists()

    with zipfile.ZipFile(output_path) as archive:
        slide_files = sorted(
            name for name in archive.namelist() if name.startswith("ppt/slides/slide")
        )

    assert len(slide_files) == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_generate_ppt.py -v`
Expected: FAIL because `tools/generate_ppt.py` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
# Add a script at tools/generate_ppt.py that writes a valid pptx archive with 5 slides.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_generate_ppt.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_generate_ppt.py tools/generate_ppt.py
git commit -m "feat: add ppt generator"
```

### Task 2: Generate the real presentation file

**Files:**
- Create: `house_price_prediction_presentation.pptx`
- Modify: `tools/generate_ppt.py`

- [ ] **Step 1: Generate the deck**

Run: `python3 tools/generate_ppt.py house_price_prediction_presentation.pptx`
Expected: file `house_price_prediction_presentation.pptx` is created

- [ ] **Step 2: Verify the archive structure**

Run: `python3 - <<'PY'
from zipfile import ZipFile
with ZipFile('house_price_prediction_presentation.pptx') as zf:
    slides = [n for n in zf.namelist() if n.startswith('ppt/slides/slide')]
    print(len(slides))
PY`
Expected: `5`

- [ ] **Step 3: Commit**

```bash
git add house_price_prediction_presentation.pptx
git commit -m "feat: add house price presentation"
```
