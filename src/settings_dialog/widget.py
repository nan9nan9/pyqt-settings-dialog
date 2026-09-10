"""검색과 카테고리 탐색을 제공하는 재사용 가능한 설정 위젯."""

from __future__ import annotations

from copy import deepcopy

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QScrollArea,
    QShortcut,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ._style import STYLE
from .controls import SettingRow


class SettingsWidget(QWidget):
    """JSON 정의를 표시한다. valueChanged(key, value)는 값이 변경되면 발생한다."""

    valueChanged = Signal(str, object)

    def __init__(self, schema: dict, values: dict | None = None, parent=None):
        super().__init__(parent)
        schema = deepcopy(schema)
        self.setObjectName("settingsWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(STYLE)

        self._rows: dict[str, SettingRow] = {}
        self._groups = []
        self._search_text = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        header = QVBoxLayout()
        header.setContentsMargins(28, 24, 28, 20)
        header.setSpacing(12)
        title = QLabel(schema.get("title", "Settings"))
        title.setTextFormat(Qt.PlainText)
        title.setObjectName("pageTitle")
        header.addWidget(title)
        if schema.get("description"):
            description = QLabel(schema["description"])
            description.setTextFormat(Qt.PlainText)
            description.setWordWrap(True)
            description.setObjectName("pageDescription")
            header.addWidget(description)

        self._search = QLineEdit()
        self._search.setObjectName("settingsSearch")
        self._search.setPlaceholderText("Search settings by name, description, or key")
        self._search.setAccessibleName("Search settings")
        self._search.setClearButtonEnabled(True)
        header.addWidget(self._search)
        search_options = QHBoxLayout()
        self._result_count = QLabel()
        self._result_count.setObjectName("resultCount")
        search_options.addWidget(self._result_count)
        search_options.addStretch()
        self._modified_only = QCheckBox("Modified only")
        self._modified_only.setObjectName("modifiedOnly")
        self._modified_only.setToolTip("Show settings that differ from their defaults")
        search_options.addWidget(self._modified_only)
        header.addLayout(search_options)
        layout.addLayout(header)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)
        self._navigation = QListWidget()
        self._navigation.setObjectName("settingsNavigation")
        self._navigation.setAccessibleName("Settings categories")
        self._navigation.setMinimumWidth(160)
        self._navigation.addItem("All Settings")
        splitter.addWidget(self._navigation)
        self._scroll = QScrollArea()
        self._scroll.setObjectName("settingsScroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        content.setObjectName("settingsContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 8, 24, 24)
        content_layout.setSpacing(10)
        self._empty_state = QLabel("No settings found. Try another search or category.")
        self._empty_state.setWordWrap(True)
        self._empty_state.setObjectName("emptyState")
        content_layout.addWidget(self._empty_state)

        for group in schema["groups"]:
            group_title = group["title"]
            self._navigation.addItem(group_title)
            section = QFrame()
            section.setObjectName("settingsGroup")
            section_layout = QVBoxLayout(section)
            section_layout.setContentsMargins(0, 0, 0, 0)
            section_layout.setSpacing(0)
            group_label = QLabel(group_title)
            group_label.setTextFormat(Qt.PlainText)
            group_label.setWordWrap(True)
            group_label.setObjectName("groupTitle")
            section_layout.addWidget(group_label)
            rows = []
            for key, definition in group["properties"].items():
                if key in self._rows:
                    raise ValueError(f"Duplicate setting key: {key}")
                row = SettingRow(key, definition)
                self._rows[key] = row
                rows.append(row)
                self._search_text[key] = " ".join(
                    [group_title, key, definition.get("title", ""), definition.get("description", "")]
                ).casefold()
                section_layout.addWidget(row)
                row.valueChanged.connect(lambda value, key=key: self._on_value_changed(key, value))
            self._groups.append((group_title, section, rows))
            content_layout.addWidget(section)
        content_layout.addStretch()
        self._scroll.setWidget(content)
        splitter.addWidget(self._scroll)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([210, 730])
        layout.addWidget(splitter, 1)

        self._navigation.setCurrentRow(0)
        self._search.textChanged.connect(self._filter_settings)
        self._modified_only.toggled.connect(self._filter_settings)
        self._navigation.currentRowChanged.connect(self._filter_settings)
        shortcut = QShortcut(QKeySequence.Find, self)
        shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        shortcut.activated.connect(self._focus_search)
        if values is not None:
            self.setValues(values)
        self._filter_settings()

    def values(self) -> dict:
        """현재 설정값 전체를 새로운 평면 딕셔너리로 반환한다."""
        return {key: row.value() for key, row in self._rows.items()}

    def value(self, key: str):
        return self._rows[key].value()

    def setValue(self, key: str, value) -> None:
        """값을 변경한다. 타입·범위 오류는 ValueError, 알 수 없는 키는 KeyError."""
        self._rows[key].setValue(value)

    def setValues(self, values: dict) -> None:
        """지정한 키만 갱신한다. 검증에 실패하면 어떤 값도 변경하지 않는다."""
        for key, value in values.items():
            self._rows[key].validateValue(value)
        for key, value in values.items():
            self._rows[key].setValue(value)

    def resetValue(self, key: str) -> None:
        row = self._rows[key]
        row.setValue(row.default)

    def resetToDefaults(self) -> None:
        for row in self._rows.values():
            row.setValue(row.default)

    def _on_value_changed(self, key: str, value) -> None:
        # 편집 중 기본값을 지나더라도 입력 행과 포커스를 유지한다.
        self._filter_settings(update_visibility=False)
        self.valueChanged.emit(key, value)

    def _focus_search(self) -> None:
        self._search.setFocus()
        self._search.selectAll()

    def _filter_settings(self, *, update_visibility: bool = True) -> None:
        terms = self._search.text().casefold().split()
        modified_only = self._modified_only.isChecked()
        category = self._navigation.currentRow()
        total = visible = 0
        for index, (title, section, rows) in enumerate(self._groups, 1):
            matches = 0
            for row in rows:
                match = all(term in self._search_text[row.key] for term in terms)
                match = match and (not modified_only or row.isModified())
                if update_visibility:
                    row.setVisible(match and category in (0, index))
                matches += int(match)
            if update_visibility:
                section.setVisible(matches > 0 and category in (0, index))
            self._navigation.item(index).setText(f"{title}  ({matches})")
            total += matches
            if category in (0, index):
                visible += matches
        self._navigation.item(0).setText(f"All Settings  ({total})")
        self._result_count.setText(f"{visible} {'setting' if visible == 1 else 'settings'}")
        if update_visibility:
            self._empty_state.setVisible(visible == 0)
