import pytest
from qtpy.QtCore import Qt
from qtpy.QtTest import QTest
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QSpinBox

from settings_dialog import SettingsDialog


@pytest.fixture
def dialog(app, schema):
    instance = SettingsDialog(schema, {"editor.fontSize": 16})
    instance.show()
    app.processEvents()
    yield instance
    instance.close()
    instance.deleteLater()
    app.processEvents()


def test_apply_then_cancel_restores_last_applied_values(dialog):
    applied = []
    dialog.settingsApplied.connect(applied.append)
    buttons = dialog.findChild(QDialogButtonBox)
    assert not buttons.button(QDialogButtonBox.Apply).isEnabled()
    dialog.settingsWidget.setValue("editor.fontSize", 18)
    assert dialog.values()["editor.fontSize"] == 16
    assert applied == []
    QTest.mouseClick(buttons.button(QDialogButtonBox.Apply), Qt.LeftButton)
    assert dialog.isVisible()
    assert dialog.values()["editor.fontSize"] == 18
    assert len(applied) == 1
    applied[0]["editor.fontSize"] = 40
    dialog.settingsWidget.setValue("editor.fontSize", 20)
    QTest.mouseClick(buttons.button(QDialogButtonBox.Cancel), Qt.LeftButton)
    assert dialog.result() == QDialog.Rejected
    assert dialog.values()["editor.fontSize"] == 18
    assert dialog.settingsWidget.value("editor.fontSize") == 18
    assert len(applied) == 1


@pytest.mark.parametrize("button", [QDialogButtonBox.Ok, QDialogButtonBox.Apply])
def test_buttons_apply_typed_numeric_input(dialog, button):
    applied = []
    dialog.settingsApplied.connect(applied.append)
    spin = dialog.findChild(QSpinBox, "editor.fontSize")
    spin.setFocus()
    spin.selectAll()
    QTest.keyClicks(spin, "22")
    target = dialog.findChild(QDialogButtonBox).button(button)
    assert target.isEnabled()
    QTest.mouseClick(target, Qt.LeftButton)
    if button == QDialogButtonBox.Ok:
        assert dialog.result() == QDialog.Accepted
    else:
        assert dialog.isVisible()
    assert dialog.values()["editor.fontSize"] == 22
    assert applied[0]["editor.fontSize"] == 22


def test_escape_discards_unapplied_edits(dialog):
    applied = []
    dialog.settingsApplied.connect(applied.append)
    dialog.settingsWidget.setValue("editor.fontSize", 24)
    QTest.keyClick(dialog, Qt.Key_Escape)
    assert dialog.result() == QDialog.Rejected
    assert dialog.values()["editor.fontSize"] == 16
    assert dialog.settingsWidget.value("editor.fontSize") == 16
    assert applied == []


def test_restore_defaults_requires_apply(dialog):
    buttons = dialog.findChild(QDialogButtonBox)
    QTest.mouseClick(buttons.button(QDialogButtonBox.RestoreDefaults), Qt.LeftButton)
    assert dialog.settingsWidget.value("editor.fontSize") == 14
    assert dialog.values()["editor.fontSize"] == 16
    assert buttons.button(QDialogButtonBox.Apply).isEnabled()
    QTest.mouseClick(buttons.button(QDialogButtonBox.Apply), Qt.LeftButton)
    assert dialog.values()["editor.fontSize"] == 14
    assert not buttons.button(QDialogButtonBox.Apply).isEnabled()
