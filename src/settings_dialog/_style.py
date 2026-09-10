"""설정 화면 내부에만 적용되는 VS Code 스타일."""

from pathlib import Path

STYLE = """
QWidget { color: #cccccc; font-size: 13px; }
QWidget#settingsWidget, QDialog#settingsDialog { background: #1f1f1f; }
QLabel { background: transparent; }
QLabel#pageTitle { color: #f0f0f0; font-size: 25px; font-weight: 600; }
QLabel#pageDescription, QLabel#resultCount, QLabel#dialogStatus { color: #999999; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #313131; border: 1px solid #565656; border-radius: 2px;
    padding: 5px 8px; min-height: 22px; selection-background-color: #264f78;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border-color: #007acc;
}
QLineEdit#settingsSearch { min-height: 28px; }
QSpinBox, QDoubleSpinBox { padding-right: 24px; }
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border; subcontrol-position: top right;
    width: 20px; background: #383838; border-left: 1px solid #565656;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border; subcontrol-position: bottom right;
    width: 20px; background: #383838; border-left: 1px solid #565656;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover { background: #505050; }
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url("@icons@/up.svg"); width: 8px; height: 5px;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow, QComboBox::down-arrow {
    image: url("@icons@/down.svg"); width: 8px; height: 5px;
}
QComboBox { padding-right: 28px; }
QComboBox::drop-down {
    subcontrol-origin: padding; subcontrol-position: top right;
    width: 24px; border: none;
}
QComboBox QAbstractItemView {
    background: #252526; border: 1px solid #565656; color: #cccccc;
    selection-background-color: #04395e; selection-color: #ffffff;
}
QListWidget#settingsNavigation {
    background: #181818; border: none; outline: none; padding: 10px 0;
}
QListWidget#settingsNavigation::item { padding: 10px 16px; border-left: 2px solid transparent; }
QListWidget#settingsNavigation::item:hover { background: #2a2d2e; }
QListWidget#settingsNavigation::item:selected {
    background: #04395e; color: #ffffff; border-left-color: #007acc;
}
QScrollArea#settingsScroll { background: #1f1f1f; border: none; }
QWidget#settingsContent, QFrame#settingsGroup { background: #1f1f1f; }
QLabel#groupTitle { color: #f0f0f0; font-size: 19px; font-weight: 600; padding: 14px 18px 8px; }
QFrame#settingRow { background: transparent; border: none; border-left: 2px solid transparent; }
QFrame#settingRow:hover { background: #242424; }
QFrame#settingRow[modified="true"] { border-left-color: #007acc; }
QLabel#settingTitle { color: #eeeeee; font-size: 14px; font-weight: 600; }
QLabel#settingKey { color: #858585; font-size: 11px; }
QLabel#settingDescription { color: #b0b0b0; }
QLabel#modifiedLabel { color: #75beff; font-size: 11px; }
QLabel#emptyState { color: #aaaaaa; padding: 36px 18px; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px; border: 1px solid #777777;
    border-radius: 2px; background: #313131;
}
QCheckBox::indicator:checked {
    background: #007acc; border-color: #007acc; image: url("@icons@/check.svg");
}
QCheckBox::indicator:hover, QCheckBox::indicator:focus { border-color: #75beff; }
QToolButton { color: #aaaaaa; background: transparent; border: none; padding: 4px 8px; }
QToolButton:hover { color: #ffffff; background: #383838; border-radius: 3px; }
QToolButton:disabled { color: #555555; }
QPushButton {
    background: #333333; color: #eeeeee; border: 1px solid #565656;
    border-radius: 2px; padding: 6px 18px;
}
QPushButton:hover { background: #444444; }
QPushButton:default { background: #007acc; border-color: #007acc; color: #ffffff; }
QPushButton:default:hover { background: #008ae6; }
QPushButton:disabled { color: #777777; background: #292929; border-color: #383838; }
QSplitter::handle { background: #303030; }
QScrollBar:vertical { background: #1f1f1f; width: 12px; margin: 0; }
QScrollBar::handle:vertical { background: #494949; min-height: 28px; }
QScrollBar::handle:vertical:hover { background: #606060; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
""".replace("@icons@", Path(__file__).with_name("icons").as_posix())
