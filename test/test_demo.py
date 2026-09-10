import os
from pathlib import Path
import subprocess
import sys


def test_demo_runs_from_another_directory_without_package_install(tmp_path):
    root = Path(__file__).resolve().parents[1]
    script = """
import runpy
import sys
from pathlib import Path
from qtpy import QtWidgets
from qtpy.QtCore import QTimer

class DemoApplication(QtWidgets.QApplication):
    def exec_(self):
        import settings_dialog
        assert Path(settings_dialog.__file__).resolve() == Path(sys.argv[2]).resolve()
        assert any(window.isVisible() for window in self.topLevelWidgets())
        QTimer.singleShot(20, self.quit)
        return super().exec_()

QtWidgets.QApplication = DemoApplication
runpy.run_path(sys.argv[1], run_name="__main__")
"""
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["QT_QPA_PLATFORM"] = "offscreen"
    result = subprocess.run(
        [sys.executable, "-c", script, str(root / "examples/demo.py"),
         str(root / "src/settings_dialog/__init__.py")],
        cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
