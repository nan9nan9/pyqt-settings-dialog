# PyQt Settings Dialog

VS Code 설정 화면처럼 검색과 카테고리 탐색을 제공하는 Qt 설정 UI.
JSON으로 항목을 정의하면 타입에 맞는 입력 컨트롤을 생성한다.
`qtpy`를 통해 PyQt5, PyQt6, PySide2, PySide6 공통 API를 사용한다.

## 실행

`qtpy`와 Qt 바인딩이 이미 설치되어 있으면 패키지 설치 없이 실행할 수 있다.

```bash
python examples/demo.py
python examples/demo.py --theme light
```

`--theme`으로 `dark`(기본) 또는 `light` 테마를 선택한다.

데모는 실행 파일 위치를 기준으로 이 저장소의 `src` 패키지와
`examples/settings.json`을 불러온다. 다른 디렉토리에서도 데모의 절대 경로로 실행할 수 있다.

Qt API는 `qtpy`를 통해 사용하며, 요구 버전은 `qtpy>=2.3.1`이다.

Python 3.9 이상과 각 바인딩이 지원하는 Python 환경이 필요하다.
여러 바인딩을 설치했다면 `QT_API`로 지정한다.

```bash
QT_API=pyqt5 python examples/demo.py
QT_API=pyqt6 python examples/demo.py
QT_API=pyside2 python examples/demo.py
QT_API=pyside6 python examples/demo.py
```

데모의 설정들은 UI 구성 예제이며, 실제 편집기·테마·터미널 동작을 변경하지 않는다.
Apply 또는 OK를 누르면 적용된 값 전체를 콘솔에 JSON으로 출력한다.

## 설치

다른 프로젝트에서 패키지로 사용할 때:

```bash
pip install .
```

Qt 바인딩도 함께 설치해야 한다면 원하는 extra를 선택한다.
`pyqt5` 대신 `pyqt6`, `pyside2`, `pyside6`를 사용할 수 있다.

```bash
pip install ".[pyqt5]"
pip install -e ".[pyqt6,dev]"
```

## JSON 정의

UI 정의와 사용자가 선택한 값은 분리한다. 정의의 `groups`가 왼쪽 카테고리를,
각 그룹의 `properties`가 오른쪽 설정 항목을 구성한다. 배열과 객체의 순서대로 표시한다.

```json
{
  "title": "Settings",
  "description": "Application preferences",
  "groups": [
    {
      "title": "Editor",
      "properties": {
        "editor.fontSize": {
          "type": "integer",
          "title": "Font Size",
          "description": "Controls the font size in pixels.",
          "default": 14,
          "minimum": 8,
          "maximum": 72
        },
        "editor.formatOnSave": {
          "type": "boolean",
          "title": "Format On Save",
          "default": false
        },
        "editor.wordWrap": {
          "type": "string",
          "title": "Word Wrap",
          "default": "off",
          "enum": ["off", "on"]
        }
      }
    }
  ]
}
```

그룹의 `title`, `properties`와 각 항목의 `type`, `default`는 필수다.
항목의 `title`을 생략하면 키를 표시하고, `description`은 선택 사항이다.
키는 모든 그룹에서 유일해야 한다. `editor.fontSize` 같은 점이 포함된 키도
중첩 객체로 바꾸지 않고 그대로 사용한다.

| 항목 정의 | 입력 컨트롤 | 선택 속성 |
| --- | --- | --- |
| `type: "string"` | 한 줄 텍스트 | |
| `type: "string"` + `enum` | 선택 목록 | `enum`: 비어 있지 않은 문자열 배열 |
| `type: "boolean"` | 체크박스 | |
| `type: "integer"` | 정수 입력 | `minimum`, `maximum`, `step` |
| `type: "number"` | 실수 입력 | `minimum`, `maximum`, `step`, `decimals` |

정수 범위의 기본값은 signed 32-bit, 실수 범위는 ±1e100이다.
`step`은 기본 1이며 증가/감소 버튼의 간격이다. `decimals`는 기본 2이며 소수점 자릿수다.
기본값과 전달하는 값은 타입·범위·소수점 정밀도에 맞아야 한다.
`number`의 반환값은 기본값을 정수로 정의해도 항상 `float`다(예: `0` → `0.0`).
이 형식은 JSON Schema의 일부 속성명을 사용하지만 전체 JSON Schema나
VS Code 확장 설정 명세를 구현하지는 않는다.

## 사용

```python
import json
import sys
from qtpy.QtWidgets import QApplication
from settings_dialog import SettingsDialog

app = QApplication(sys.argv)
with open("examples/settings.json", encoding="utf-8") as stream:
    schema = json.load(stream)

dialog = SettingsDialog(schema, values={"editor.fontSize": 16}, theme="light")
dialog.settingsApplied.connect(lambda values: print(values))
dialog.show()
sys.exit(app.exec_())
```

`SettingsDialog`는 Apply/OK를 누를 때 `settingsApplied(dict)`를 발생시킨다.
Cancel, Escape 또는 창 닫기는 마지막 적용 이후의 편집을 취소한다.
Restore Defaults는 모든 항목을 기본값으로 편집하며, 적용하려면 Apply/OK를 눌러야 한다.
`dialog.values()`는 마지막으로 적용된 값의 복사본을 반환한다.
`theme`은 `"dark"`(기본) 또는 `"light"`이며, `SettingsWidget`에도 같은 인자를 전달한다.
다른 값은 `ValueError`를 발생시킨다.

기존 화면에 넣어 사용하려면 `SettingsWidget`을 레이아웃에 추가한다.

```python
from settings_dialog import SettingsWidget

widget = SettingsWidget(schema, values={"editor.fontSize": 16})
widget.valueChanged.connect(lambda key, value: print(key, value))
layout.addWidget(widget)

widget.setValue("editor.fontSize", 18)
widget.setValues({"editor.fontSize": 16, "editor.wordWrap": "on"})
current = widget.values()
widget.resetValue("editor.fontSize")
widget.resetToDefaults()
```

`SettingsWidget.valueChanged(str, object)`는 실제 값이 변경될 때 발생한다.
사용자 편집뿐 아니라 `setValue()`, `setValues()`, 기본값 복원,
다이얼로그의 Cancel 복원에 의한 변경도 포함한다. 같은 값을 다시 설정하면 발생하지 않는다.
숫자는 입력 도중에도 유효한 중간값마다 변경 시그널이 발생한다.
`values()`는 현재 값 전체, `value(key)`는 개별 값을 반환한다.
`setValues()`는 전달한 키만 변경하며, 검증 실패 시 어떤 값도 변경하지 않는다.
알 수 없는 키는 `KeyError`, 잘못된 값은 `ValueError`를 발생시킨다.
생략한 초기값에는 JSON의 `default`를 사용한다.

검색은 키·이름·설명·카테고리에서 대소문자 구분 없이 모든 검색어를 찾는다.
카테고리 선택 및 Modified only와 함께 적용된다. Ctrl+F(macOS에서는 기본 Find 단축키)로
검색창에 포커스를 옮긴다. Modified는 JSON의 기본값과 다른 항목을 뜻한다.
값 변경 시에는 필터에 일치하는 항목 수만 갱신하고 현재 목록은 유지한다.
기본값으로 돌아간 행도 입력 중 사라지지 않으며, 검색어·카테고리·Modified only를
변경할 때 목록을 다시 필터링한다. 기본값 복원과 프로그램적 값 변경에도 같은 규칙을 적용한다.
설정값의 파일 저장과 실제 애플리케이션 반영은 호출 측에서 시그널에 연결한다.

## 구조

```text
src/settings_dialog/
├── __init__.py   # SettingsWidget, SettingsDialog 공개
├── controls.py   # JSON 항목별 입력과 값 검증
├── widget.py     # 검색, 카테고리, 값 접근 API
├── dialog.py     # 적용·확인·취소
├── _style.py     # dark/light 테마 팔레트와 스타일시트
└── icons/        # 테마별 체크 표시와 입력 화살표 (dark/, light/)
examples/
├── demo.py
└── settings.json
test/
├── conftest.py
├── test_widget.py
├── test_dialog.py
└── test_demo.py
```

## 테스트

```bash
QT_QPA_PLATFORM=offscreen QT_API=pyqt5 python -m pytest -q
QT_QPA_PLATFORM=offscreen QT_API=pyqt6 python -m pytest -q
QT_QPA_PLATFORM=offscreen QT_API=pyside6 python -m pytest -q
```

PySide2는 해당 바인딩이 지원하는 Python 환경에서 `QT_API=pyside2`로 실행한다.
