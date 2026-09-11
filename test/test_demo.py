import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("options", [[], ["--theme", "light"]])
def test_demo_runs_from_another_directory_without_package_install(tmp_path, options):
    root = Path(__file__).resolve().parents[1]
    script = """
import runpy
import sys
from pathlib import Path
from qtpy import QtWidgets
from qtpy.QtCore import QTimer

demo, package, *options = sys.argv[1:]

class DemoApplication(QtWidgets.QApplication):
    def exec_(self):
        import settings_dialog
        assert Path(settings_dialog.__file__).resolve() == Path(package).resolve()
        assert any(window.isVisible() for window in self.topLevelWidgets())
        QTimer.singleShot(20, self.quit)
        return super().exec_()

QtWidgets.QApplication = DemoApplication
sys.argv = [demo, *options]
runpy.run_path(demo, run_name="__main__")
"""
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["QT_QPA_PLATFORM"] = "offscreen"
    result = subprocess.run(
        [sys.executable, "-c", script, str(root / "examples/demo.py"),
         str(root / "src/settings_dialog/__init__.py"), *options],
        cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
