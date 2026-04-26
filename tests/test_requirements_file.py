from pathlib import Path


def test_requirements_pin_chat_dependencies():
    requirements_text = Path("requirements.txt").read_text()

    assert "ollama==0.6.1" in requirements_text
    assert "streamlit==1.56.0" in requirements_text
    assert "pytest==9.0.3" in requirements_text
