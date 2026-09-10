import pytest
from qtpy.QtCore import QPoint, Qt
from qtpy.QtGui import QColor, QPalette
from qtpy.QtTest import QTest
from qtpy.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QLabel, QLineEdit,
    QListWidget, QSpinBox, QToolButton, QVBoxLayout, QWidget,
)

from settings_dialog import SettingsWidget


def test_embedded_widget_paints_background(app, schema):
    parent = QWidget()
    palette = parent.palette()
    palette.setColor(QPalette.Window, QColor("white"))
    parent.setPalette(palette)
    parent.setAutoFillBackground(True)
    widget = SettingsWidget(schema)
    QVBoxLayout(parent).addWidget(widget)
    parent.resize(1000, 760)
    parent.show()
    app.processEvents()
    try:
        # 부모 화면을 캡처해야 자식의 실제 배경 페인팅 여부를 확인할 수 있다.
        snapshot = parent.grab()
        point = widget.mapTo(parent, QPoint(5, 5))
        scale = snapshot.devicePixelRatio()
        color = snapshot.toImage().pixelColor(int(point.x() * scale), int(point.y() * scale))
        assert color == QColor("#1f1f1f")
    finally:
        parent.close()
        parent.deleteLater()
        app.processEvents()


@pytest.mark.parametrize("definition,initial,prefix,suffix,expected", [
    ({"type": "integer", "default": 1000, "minimum": 100, "maximum": 60000},
     2000, "1000", "0", 10000),
    ({"type": "number", "default": 1.0}, 2.0, "1", ".5", 1.5),
    ({"type": "string", "default": "file"}, "old", "file", "name", "filename"),
    ({"type": "string", "default": ""}, "old", "", "new", "new"),
])
def test_modified_filter_keeps_focus_while_typing_through_default(
    app, definition, initial, prefix, suffix, expected,
):
    widget = SettingsWidget(
        {"groups": [{"title": "General", "properties": {"test.value": definition}}]},
        {"test.value": initial},
    )
    widget.resize(1000, 760)
    widget.show()
    app.processEvents()
    try:
        widget.findChild(QCheckBox, "modifiedOnly").setChecked(True)
        editor = widget.findChild(QWidget, "test.value")
        editor.setFocus()
        editor.selectAll()
        QTest.keyClick(app.focusWidget(), Qt.Key_Backspace)
        QTest.keyClicks(app.focusWidget(), prefix)
        assert widget.value("test.value") == definition["default"]
        assert editor.isVisible()
        assert editor.hasFocus()
        assert widget.findChild(QLabel, "resultCount").text() == "0 settings"
        assert not widget.findChild(QLabel, "emptyState").isVisible()
        QTest.keyClicks(app.focusWidget(), suffix)
        assert widget.value("test.value") == expected
        assert editor.hasFocus()
        assert widget.findChild(QLineEdit, "settingsSearch").text() == ""
        assert widget.findChild(QLabel, "resultCount").text() == "1 setting"
    finally:
        widget.close()
        widget.deleteLater()
        app.processEvents()


def test_json_creates_typed_controls_and_defaults(widget):
    assert isinstance(widget.findChild(QWidget, "editor.fontFamily"), QLineEdit)
    assert isinstance(widget.findChild(QWidget, "editor.fontSize"), QSpinBox)
    assert isinstance(widget.findChild(QWidget, "editor.formatOnSave"), QCheckBox)
    assert isinstance(widget.findChild(QWidget, "editor.zoom"), QDoubleSpinBox)
    assert isinstance(widget.findChild(QWidget, "files.autoSave"), QComboBox)
    assert widget.values() == {
        "editor.fontFamily": "Monospace", "editor.fontSize": 14,
        "editor.formatOnSave": False, "editor.zoom": 0.0, "files.autoSave": "off",
    }


def test_control_edits_emit_typed_values_once(widget):
    changes = []
    widget.valueChanged.connect(lambda key, value: changes.append((key, value)))
    editor = widget.findChild(QLineEdit, "editor.fontFamily")
    editor.selectAll()
    QTest.keyClicks(editor, "A")
    QTest.keyClick(widget.findChild(QCheckBox, "editor.formatOnSave"), Qt.Key_Space)
    spin = widget.findChild(QSpinBox, "editor.fontSize")
    spin.setFocus()
    QTest.keyClick(spin, Qt.Key_Up)
    widget.findChild(QDoubleSpinBox, "editor.zoom").setValue(0.25)
    combo = widget.findChild(QComboBox, "files.autoSave")
    combo.setCurrentIndex(1)
    assert changes == [
        ("editor.fontFamily", "A"), ("editor.formatOnSave", True),
        ("editor.fontSize", 15), ("editor.zoom", 0.25), ("files.autoSave", "afterDelay"),
    ]
    assert widget.values() == dict(changes)
    widget.setValue("editor.zoom", 0.25)
    assert len(changes) == 5


def test_values_are_copied_and_input_schema_is_detached(app, schema):
    initial = {"editor.fontFamily": "", "editor.zoom": -0.5}
    widget = SettingsWidget(schema, initial)
    schema["groups"][0]["properties"]["editor.fontSize"]["default"] = 20
    snapshot = widget.values()
    snapshot["editor.zoom"] = 2
    assert initial == {"editor.fontFamily": "", "editor.zoom": -0.5}
    assert widget.value("editor.zoom") == -0.5
    widget.setValue("editor.fontSize", 18)
    widget.resetValue("editor.fontSize")
    assert widget.value("editor.fontSize") == 14
    assert widget.value("editor.fontFamily") == ""
    widget.deleteLater()


@pytest.mark.parametrize("key,value", [
    ("editor.fontSize", True), ("editor.fontSize", 14.5), ("editor.fontSize", 73),
    ("editor.formatOnSave", 1), ("editor.fontFamily", None),
    ("editor.zoom", float("nan")), ("editor.zoom", float("inf")),
    ("editor.zoom", -4), ("editor.zoom", 0.001), ("files.autoSave", "invalid"),
])
def test_invalid_values_do_not_change_state(widget, key, value):
    original = widget.values()
    with pytest.raises(ValueError):
        widget.setValue(key, value)
    assert widget.values() == original


def test_batch_validation_prevents_partial_updates(widget):
    original = widget.values()
    with pytest.raises(ValueError):
        widget.setValues({"editor.fontSize": 16, "files.autoSave": "invalid"})
    assert widget.values() == original
    with pytest.raises(KeyError):
        widget.setValues({"editor.fontSize": 16, "missing": True})
    assert widget.values() == original


def test_search_matches_all_words_in_key_title_description_and_category(widget):
    search = widget.findChild(QLineEdit, "settingsSearch")
    search.setText("EDITOR disk")
    assert widget.findChild(QWidget, "editor.formatOnSave").isVisible()
    assert not widget.findChild(QWidget, "editor.fontSize").isVisible()
    assert widget.findChild(QLabel, "resultCount").text() == "1 setting"
    search.setText("files.autosave")
    assert widget.findChild(QWidget, "files.autoSave").isVisible()
    assert not widget.findChild(QWidget, "editor.formatOnSave").isVisible()
    search.setText("no matching setting")
    assert widget.findChild(QLabel, "emptyState").isVisible()
    search.clear()
    assert not widget.findChild(QLabel, "emptyState").isVisible()
    assert widget.findChild(QLabel, "resultCount").text() == "5 settings"


def test_category_and_search_filters_combine(widget):
    navigation = widget.findChild(QListWidget, "settingsNavigation")
    navigation.setCurrentRow(2)
    assert widget.findChild(QWidget, "files.autoSave").isVisible()
    assert not widget.findChild(QWidget, "editor.fontFamily").isVisible()
    widget.findChild(QLineEdit, "settingsSearch").setText("font")
    assert widget.findChild(QLabel, "emptyState").isVisible()
    navigation.setCurrentRow(0)
    assert widget.findChild(QLabel, "resultCount").text() == "2 settings"


def test_modified_filter_and_reset_controls(widget):
    widget.setValues({"editor.fontSize": 16, "files.autoSave": "afterDelay"})
    QTest.mouseClick(widget.findChild(QCheckBox, "modifiedOnly"), Qt.LeftButton)
    assert widget.findChild(QLabel, "resultCount").text() == "2 settings"
    assert not widget.findChild(QWidget, "editor.fontFamily").isVisible()
    row = widget.findChild(QWidget, "editor.fontSize").parentWidget()
    QTest.mouseClick(row.findChild(QToolButton), Qt.LeftButton)
    assert widget.value("editor.fontSize") == 14
    assert row.isVisible()
    assert widget.findChild(QLabel, "resultCount").text() == "1 setting"
    navigation = widget.findChild(QListWidget, "settingsNavigation")
    navigation.setCurrentRow(1)
    assert not row.isVisible()
    assert widget.findChild(QLabel, "emptyState").isVisible()
    navigation.setCurrentRow(0)
    assert not widget.findChild(QLabel, "emptyState").isVisible()
    widget.resetToDefaults()
    assert widget.value("files.autoSave") == "off"
    assert widget.findChild(QWidget, "files.autoSave").isVisible()
    assert widget.findChild(QLabel, "resultCount").text() == "0 settings"
    widget.findChild(QLineEdit, "settingsSearch").setText("autoSave")
    assert not widget.findChild(QWidget, "files.autoSave").isVisible()
    assert widget.findChild(QLabel, "emptyState").isVisible()


def test_duplicate_keys_are_rejected(app, schema):
    schema["groups"][1]["properties"]["editor.fontSize"] = {
        "type": "integer", "default": 10,
    }
    with pytest.raises(ValueError, match="Duplicate setting key"):
        SettingsWidget(schema)


@pytest.mark.parametrize("definition", [
    {"type": "array", "default": []},
    {"type": "integer", "default": 12, "minimum": 20, "maximum": 10},
    {"type": "string", "default": "", "enum": []},
    {"type": "string", "default": "a", "enum": [1, 2]},
    {"type": "integer", "default": 100, "maximum": 10},
])
def test_invalid_definitions_are_rejected(app, definition):
    with pytest.raises(ValueError):
        SettingsWidget({"groups": [{"title": "General", "properties": {"test": definition}}]})


def test_empty_schema_has_empty_state(app):
    widget = SettingsWidget({"groups": []})
    assert widget.values() == {}
    assert not widget.findChild(QLabel, "emptyState").isHidden()
    widget.deleteLater()
