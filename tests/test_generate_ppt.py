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
