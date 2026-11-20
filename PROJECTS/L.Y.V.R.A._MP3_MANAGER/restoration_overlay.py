"""Load the optional Restoration Lab interface in its own Python namespace."""
import importlib
import importlib.util
from pathlib import Path
import sys

PACKAGE = "lyvra_restoration_lab"
SOURCES = (
    "__init__.py", "app.py", "audio_input.py", "legacy_app.py", "manual.py",
    "mastering_tools.py", "metal_ui.py", "realtime.py", "reference_engine.py",
    "studio_tools.py", "studio_ui.py",
)


def source_directory():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "restoration_lab"
    return Path(__file__).resolve().parent.parent / "Restoration-Lab-main"


def load_app():
    if PACKAGE not in sys.modules:
        directory = source_directory()
        initializer = directory / "__init__.py"
        if not initializer.is_file():
            raise FileNotFoundError(f"Restoration Lab not found: {initializer}")
        spec = importlib.util.spec_from_file_location(
            PACKAGE, initializer, submodule_search_locations=[str(directory)]
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load Restoration Lab from {directory}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[PACKAGE] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            del sys.modules[PACKAGE]
            raise
    return importlib.import_module(f"{PACKAGE}.app").App
