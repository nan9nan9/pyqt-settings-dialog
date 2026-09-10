"""설정 정의 하나를 입력 컨트롤로 변환한다."""

from __future__ import annotations

import math

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
)


class SettingRow(QFrame):
    valueChanged = Signal(object)

    def __init__(self, key: str, definition: dict, parent=None):
        super().__init__(parent)
        self.key = key
        self.definition = definition
        self.default = definition["default"]
        self.setObjectName("settingRow")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(8)
        header = QHBoxLayout()
        title = QLabel(definition.get("title", key))
        title.setTextFormat(Qt.PlainText)
        title.setWordWrap(True)
        title.setObjectName("settingTitle")
        header.addWidget(title, 1)
        self._modified = QLabel("Modified")
        self._modified.setObjectName("modifiedLabel")
        header.addWidget(self._modified)
        self._reset = QToolButton()
        self._reset.setText("Reset")
        self._reset.setToolTip("Restore the default value")
        self._reset.setAccessibleName(f"Reset {title.text()}")
        self._reset.clicked.connect(lambda: self.setValue(self.default))
        header.addWidget(self._reset)
        layout.addLayout(header)

        key_label = QLabel(key)
        key_label.setTextFormat(Qt.PlainText)
        key_label.setObjectName("settingKey")
        key_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(key_label)
        description = definition.get("description", "")
        if description:
            label = QLabel(description)
            label.setTextFormat(Qt.PlainText)
            label.setWordWrap(True)
            label.setObjectName("settingDescription")
            layout.addWidget(label)

        self.editor = self._create_editor()
        self.editor.setObjectName(key)
        self.editor.setAccessibleName(title.text())
        self.editor.setAccessibleDescription(description)
        title.setBuddy(self.editor)
        layout.addWidget(self.editor)
        self.validateValue(self.default)
        self._write_value(self.default)
        self._refresh_modified()

        if isinstance(self.editor, QComboBox):
            self.editor.currentIndexChanged.connect(self._on_edited)
        elif isinstance(self.editor, QCheckBox):
            self.editor.toggled.connect(self._on_edited)
        elif isinstance(self.editor, QLineEdit):
            self.editor.textChanged.connect(self._on_edited)
        else:
            self.editor.valueChanged.connect(self._on_edited)

    def _create_editor(self):
        kind = self.definition["type"]
        if kind == "string":
            if "enum" in self.definition:
                options = self.definition["enum"]
                if not options or any(not isinstance(option, str) for option in options):
                    raise ValueError(f"{self.key}: enum must contain strings")
                editor = QComboBox()
                for option in options:
                    editor.addItem(option, option)
                editor.setMaximumWidth(420)
                return editor
            editor = QLineEdit()
            # 기본 제한(32767자)으로 JSON의 문자열이 잘리지 않게 한다.
            editor.setMaxLength(2**31 - 1)
            editor.setMaximumWidth(560)
            return editor
        if kind == "boolean":
            return QCheckBox("Enabled")
        if kind in ("integer", "number"):
            if kind == "integer":
                editor = QSpinBox()
                bounds = (-2**31, 2**31 - 1)
            else:
                editor = QDoubleSpinBox()
                editor.setDecimals(self.definition.get("decimals", 2))
                bounds = (-1e100, 1e100)
            minimum = self.definition.get("minimum", bounds[0])
            maximum = self.definition.get("maximum", bounds[1])
            if minimum > maximum:
                raise ValueError(f"{self.key}: minimum must not exceed maximum")
            editor.setRange(minimum, maximum)
            editor.setSingleStep(self.definition.get("step", 1))
            editor.setMaximumWidth(180)
            return editor
        raise ValueError(f"{self.key}: unsupported setting type {kind!r}")

    def value(self):
        if isinstance(self.editor, QComboBox):
            return self.editor.currentData()
        if isinstance(self.editor, QCheckBox):
            return self.editor.isChecked()
        if isinstance(self.editor, QLineEdit):
            return self.editor.text()
        return self.editor.value()

    def validateValue(self, value) -> None:
        kind = self.definition["type"]
        valid_type = {
            "boolean": type(value) is bool,
            "string": isinstance(value, str),
            "integer": type(value) is int,
            "number": type(value) in (int, float),
        }[kind]
        if not valid_type:
            raise ValueError(f"{self.key}: expected {kind}, got {value!r}")
        if isinstance(self.editor, QComboBox) and value not in self.definition["enum"]:
            raise ValueError(f"{self.key}: {value!r} is not an enum option")
        if kind in ("integer", "number"):
            if not math.isfinite(value) or not self.editor.minimum() <= value <= self.editor.maximum():
                raise ValueError(f"{self.key}: value is outside the allowed range")
            if kind == "number" and round(value, self.editor.decimals()) != value:
                raise ValueError(f"{self.key}: value exceeds the configured decimal precision")

    def setValue(self, value) -> None:
        self.validateValue(value)
        self._write_value(value)

    def _write_value(self, value) -> None:
        if isinstance(self.editor, QComboBox):
            self.editor.setCurrentIndex(self.editor.findData(value))
        elif isinstance(self.editor, QCheckBox):
            self.editor.setChecked(value)
        elif isinstance(self.editor, QLineEdit):
            self.editor.setText(value)
        else:
            self.editor.setValue(value)

    def isModified(self) -> bool:
        return self.value() != self.default

    def _refresh_modified(self) -> None:
        modified = self.isModified()
        self._modified.setVisible(modified)
        self._reset.setEnabled(modified)
        self.setProperty("modified", modified)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _on_edited(self) -> None:
        self._refresh_modified()
        self.valueChanged.emit(self.value())
