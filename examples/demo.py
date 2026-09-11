"""설치 없이 실행: python examples/demo.py [--theme dark|light]"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# 실행한 작업 디렉토리와 관계없이 이 저장소의 소스를 사용한다.
EXAMPLE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXAMPLE_DIR.parent / "src"))

from qtpy.QtWidgets import QApplication

from settings_dialog import SettingsDialog


def main() -> int:
    parser = argparse.ArgumentParser(description="Settings dialog demo")
    parser.add_argument("--theme", choices=("dark", "light"), default="dark",
                        help="color theme (default: dark)")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    with (EXAMPLE_DIR / "settings.json").open(encoding="utf-8") as stream:
        schema = json.load(stream)

    dialog = SettingsDialog(
        schema,
        values={"editor.fontSize": 16, "files.autoSave": "afterDelay"},
        theme=args.theme,
    )
    dialog.settingsApplied.connect(
        lambda values: print(json.dumps(values, indent=2, ensure_ascii=False), flush=True)
    )
    dialog.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
