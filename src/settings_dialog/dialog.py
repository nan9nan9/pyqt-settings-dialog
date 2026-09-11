"""설정 위젯에 적용·확인·취소 동작을 추가한다."""

from __future__ import annotations

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout

from ._style import stylesheet
from .widget import SettingsWidget


class SettingsDialog(QDialog):
    """Apply/OK에서만 settingsApplied(dict)를 발생시키는 설정 창."""

    settingsApplied = Signal(dict)

    def __init__(
        self, schema: dict, values: dict | None = None, parent=None, theme: str = "dark"
    ):
        super().__init__(parent)
        self.setObjectName("settingsDialog")
        self.setWindowTitle(schema.get("title", "Settings"))
        self.setStyleSheet(stylesheet(theme))
        self.resize(1000, 760)
        self.setMinimumSize(660, 460)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.settingsWidget = SettingsWidget(schema, values, self, theme)
        layout.addWidget(self.settingsWidget, 1)
        self._applied_values = self.settingsWidget.values()

        footer = QHBoxLayout()
        footer.setContentsMargins(24, 14, 24, 14)
        self._status = QLabel()
        self._status.setObjectName("dialogStatus")
        footer.addWidget(self._status, 1)
        self._buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            | QDialogButtonBox.Apply | QDialogButtonBox.RestoreDefaults
        )
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        self._buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply)
        self._buttons.button(QDialogButtonBox.RestoreDefaults).clicked.connect(
            self.settingsWidget.resetToDefaults
        )
        footer.addWidget(self._buttons)
        layout.addLayout(footer)
        self.settingsWidget.valueChanged.connect(self._update_state)
        self._update_state()

    def values(self) -> dict:
        """마지막으로 적용된 값의 복사본. 미적용 편집값은 포함하지 않는다."""
        return self._applied_values.copy()

    def apply(self) -> None:
        self._applied_values = self.settingsWidget.values()
        self._update_state()
        self.settingsApplied.emit(self.values())

    def accept(self) -> None:
        self.apply()
        super().accept()

    def reject(self) -> None:
        self.settingsWidget.setValues(self._applied_values)
        super().reject()

    def _update_state(self) -> None:
        changed = self.settingsWidget.values() != self._applied_values
        self._buttons.button(QDialogButtonBox.Apply).setEnabled(changed)
        self._status.setText("Unapplied changes" if changed else "All changes applied")
