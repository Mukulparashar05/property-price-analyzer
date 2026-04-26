import importlib


def test_importing_ollama_smoke_script_has_no_side_effects():
    module = importlib.import_module("ollama_test")
    assert hasattr(module, "main")
