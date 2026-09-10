import pytest
from qtpy.QtWidgets import QApplication

from settings_dialog import SettingsWidget


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def schema():
    return {
        "title": "Test Settings",
        "groups": [
            {
                "title": "Editor",
                "properties": {
                    "editor.fontFamily": {
                        "type": "string", "title": "Font Family", "default": "Monospace",
                    },
                    "editor.fontSize": {
                        "type": "integer", "title": "Font Size", "default": 14,
                        "minimum": 8, "maximum": 72,
                    },
                    "editor.formatOnSave": {
                        "type": "boolean", "title": "Format On Save", "default": False,
                        "description": "Automatically format the document before writing to disk.",
                    },
                    "editor.zoom": {
                        "type": "number", "title": "Zoom", "default": 0.0,
                        "minimum": -3, "maximum": 3, "step": 0.25, "decimals": 2,
                    },
                },
            },
            {
                "title": "Files",
                "properties": {
                    "files.autoSave": {
                        "type": "string", "title": "Auto Save", "default": "off",
                        "enum": ["off", "afterDelay", "onFocusChange"],
                    },
                },
            },
        ],
    }


@pytest.fixture
def widget(app, schema):
    instance = SettingsWidget(schema)
    instance.resize(1000, 760)
    instance.show()
    app.processEvents()
    yield instance
    instance.close()
    instance.deleteLater()
    app.processEvents()
