"""설정 화면 내부에만 적용되는 VS Code 스타일. dark/light 테마를 제공한다."""

from pathlib import Path
from string import Template

THEMES = {
    "dark": {
        "bg": "#1f1f1f",
        "text": "#cccccc",
        "heading": "#f0f0f0",
        "muted": "#999999",
        "description": "#b0b0b0",
        "strong_text": "#ffffff",
        "disabled_text": "#666666",
        "accent": "#007acc",
        "accent_hover": "#008ae6",
        "accent_text": "#75beff",
        "input_bg": "#313131",
        "border": "#565656",
        "check_border": "#777777",
        "selection": "#264f78",
        "button_bg": "#383838",
        "button_hover": "#4a4a4a",
        "disabled_bg": "#292929",
        "disabled_border": "#383838",
        "popup_bg": "#252526",
        "selected_bg": "#04395e",
        "sidebar_bg": "#181818",
        "sidebar_hover": "#2a2d2e",
        "row_hover": "#242424",
        "splitter": "#303030",
        "scrollbar": "#494949",
        "scrollbar_hover": "#606060",
    },
    "light": {
        "bg": "#ffffff",
        "text": "#3b3b3b",
        "heading": "#1f1f1f",
        "muted": "#6f6f6f",
        "description": "#4f4f4f",
        "strong_text": "#000000",
        "disabled_text": "#a0a0a0",
        "accent": "#005fb8",
        "accent_hover": "#0258a8",
        "accent_text": "#005fb8",
        "input_bg": "#ffffff",
        "border": "#cecece",
        "check_border": "#919191",
        "selection": "#add6ff",
        "button_bg": "#e5e5e5",
        "button_hover": "#d6d6d6",
        "disabled_bg": "#f3f3f3",
        "disabled_border": "#dcdcdc",
        "popup_bg": "#ffffff",
        "selected_bg": "#e8e8e8",
        "sidebar_bg": "#f8f8f8",
        "sidebar_hover": "#f0f0f0",
        "row_hover": "#f5f5f5",
        "splitter": "#e5e5e5",
        "scrollbar": "#c1c1c1",
        "scrollbar_hover": "#a8a8a8",
    },
}

_TEMPLATE = Template("""
QWidget { color: $text; font-size: 13px; }
QWidget#settingsWidget, QDialog#settingsDialog { background: $bg; }
QLabel { background: transparent; }
QLabel#pageTitle { color: $heading; font-size: 25px; font-weight: 600; }
QLabel#pageDescription, QLabel#resultCount, QLabel#dialogStatus { color: $muted; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: $input_bg; border: 1px solid $border; border-radius: 2px;
    padding: 5px 8px; min-height: 22px; selection-background-color: $selection;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border-color: $accent;
}
QLineEdit#settingsSearch { min-height: 28px; }
QSpinBox, QDoubleSpinBox { padding-right: 24px; }
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border; subcontrol-position: top right;
    width: 20px; background: $button_bg; border-left: 1px solid $border;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border; subcontrol-position: bottom right;
    width: 20px; background: $button_bg; border-left: 1px solid $border;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover { background: $button_hover; }
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: url("$icons/up.svg"); width: 8px; height: 5px;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow, QComboBox::down-arrow {
    image: url("$icons/down.svg"); width: 8px; height: 5px;
}
QComboBox { padding-right: 28px; }
QComboBox::drop-down {
    subcontrol-origin: padding; subcontrol-position: top right;
    width: 24px; border: none;
}
QComboBox QAbstractItemView {
    background: $popup_bg; border: 1px solid $border; color: $text;
    selection-background-color: $selected_bg; selection-color: $strong_text;
}
QListWidget#settingsNavigation {
    background: $sidebar_bg; border: none; outline: none; padding: 10px 0;
}
QListWidget#settingsNavigation::item { padding: 10px 16px; border-left: 2px solid transparent; }
QListWidget#settingsNavigation::item:hover { background: $sidebar_hover; }
QListWidget#settingsNavigation::item:selected {
    background: $selected_bg; color: $strong_text; border-left-color: $accent;
}
QScrollArea#settingsScroll { background: $bg; border: none; }
QWidget#settingsContent, QFrame#settingsGroup { background: $bg; }
QLabel#groupTitle { color: $heading; font-size: 19px; font-weight: 600; padding: 14px 18px 8px; }
QFrame#settingRow { background: transparent; border: none; border-left: 2px solid transparent; }
QFrame#settingRow:hover { background: $row_hover; }
QFrame#settingRow[modified="true"] { border-left-color: $accent; }
QLabel#settingTitle { color: $heading; font-size: 14px; font-weight: 600; }
QLabel#settingKey { color: $muted; font-size: 11px; }
QLabel#settingDescription { color: $description; }
QLabel#modifiedLabel { color: $accent_text; font-size: 11px; }
QLabel#emptyState { color: $muted; padding: 36px 18px; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px; border: 1px solid $check_border;
    border-radius: 2px; background: $input_bg;
}
QCheckBox::indicator:checked {
    background: $accent; border-color: $accent; image: url("$icons/check.svg");
}
QCheckBox::indicator:hover, QCheckBox::indicator:focus { border-color: $accent_text; }
QToolButton { color: $muted; background: transparent; border: none; padding: 4px 8px; }
QToolButton:hover { color: $strong_text; background: $button_bg; border-radius: 3px; }
QToolButton:disabled { color: $disabled_text; }
QPushButton {
    background: $button_bg; color: $heading; border: 1px solid $border;
    border-radius: 2px; padding: 6px 18px;
}
QPushButton:hover { background: $button_hover; }
QPushButton:default { background: $accent; border-color: $accent; color: #ffffff; }
QPushButton:default:hover { background: $accent_hover; }
QPushButton:disabled { color: $disabled_text; background: $disabled_bg; border-color: $disabled_border; }
QSplitter::handle { background: $splitter; }
QScrollBar:vertical { background: $bg; width: 12px; margin: 0; }
QScrollBar::handle:vertical { background: $scrollbar; min-height: 28px; }
QScrollBar::handle:vertical:hover { background: $scrollbar_hover; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
""")


def stylesheet(theme: str) -> str:
    """테마 이름("dark" 또는 "light")에 해당하는 스타일시트를 반환한다."""
    if theme not in THEMES:
        raise ValueError(f"unknown theme {theme!r}; expected one of {sorted(THEMES)}")
    icons = Path(__file__).with_name("icons").joinpath(theme).as_posix()
    return _TEMPLATE.substitute(THEMES[theme], icons=icons)
