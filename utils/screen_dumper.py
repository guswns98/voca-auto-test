"""
화면 별 UI 계층 덤프 유틸리티

- page_source XML에서 구조적 fingerprint를 추출하여 동일 화면 판별
- 이미 덤프한 화면은 건너뛰고, 새 화면만 저장
- 덤프 결과: dumps/ 디렉토리에 XML + 스크린샷 + 요약 JSON
"""

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from xml.etree import ElementTree as ET

from appium.webdriver.webdriver import WebDriver


DUMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dumps")


@dataclass
class ScreenDump:
    name: str
    fingerprint: str
    xml_path: str
    screenshot_path: str
    elements: list = field(default_factory=list)


class ScreenDumper:
    """화면 덤프 & 중복 감지"""

    # fingerprint 계산 시 무시할 속성 (매번 달라지는 값)
    VOLATILE_ATTRS = {"text", "content-desc", "label", "value", "name"}

    def __init__(self, driver: WebDriver, dump_dir: str = DUMP_DIR):
        self.driver = driver
        self.dump_dir = dump_dir
        self._seen: dict[str, ScreenDump] = {}  # fingerprint → ScreenDump
        os.makedirs(self.dump_dir, exist_ok=True)

    # ──────────────────────────────────────────────
    # 핵심: 화면 fingerprint 생성
    # ──────────────────────────────────────────────

    def _fingerprint(self, page_source: str) -> str:
        """
        page_source XML에서 구조적 fingerprint를 생성한다.

        방법: 모든 노드의 (tag, class, resource-id, bounds) 만 추출하여
        정렬된 문자열로 만든 뒤 SHA256 해시.
        text, content-desc 등 런타임 값은 제외 → 같은 화면이면 동일 해시.
        """
        try:
            root = ET.fromstring(page_source)
        except ET.ParseError:
            return hashlib.sha256(page_source.encode()).hexdigest()[:16]

        parts = []
        for elem in root.iter():
            tag = elem.tag
            cls = elem.attrib.get("class", elem.attrib.get("type", ""))
            rid = elem.attrib.get("resource-id", elem.attrib.get("name", ""))
            bounds = elem.attrib.get("bounds", "")
            parts.append(f"{tag}|{cls}|{rid}|{bounds}")

        structure = "\n".join(parts)
        return hashlib.sha256(structure.encode()).hexdigest()[:16]

    # ──────────────────────────────────────────────
    # 중복 체크
    # ──────────────────────────────────────────────

    def is_already_dumped(self, page_source: str | None = None) -> bool:
        """현재 화면이 이미 덤프되었는지 확인"""
        source = page_source or self.driver.page_source
        fp = self._fingerprint(source)
        return fp in self._seen

    # ──────────────────────────────────────────────
    # 덤프 실행
    # ──────────────────────────────────────────────

    def dump(self, screen_name: str) -> ScreenDump | None:
        """
        현재 화면을 덤프한다.
        이미 동일 구조의 화면이 덤프되었으면 None을 반환한다.

        Returns:
            ScreenDump: 새로 덤프한 경우
            None: 이미 동일 화면이 존재
        """
        source = self.driver.page_source
        fp = self._fingerprint(source)

        if fp in self._seen:
            prev = self._seen[fp]
            print(f"[SKIP] '{screen_name}' → 이미 덤프됨 (기존: '{prev.name}', hash: {fp})")
            return None

        # 파일명 생성
        safe_name = re.sub(r"[^\w가-힣]", "_", screen_name)
        ts = int(time.time())
        xml_path = os.path.join(self.dump_dir, f"{safe_name}_{ts}.xml")
        png_path = os.path.join(self.dump_dir, f"{safe_name}_{ts}.png")

        # XML 저장
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(source)

        # 스크린샷 저장
        self.driver.save_screenshot(png_path)

        # 요소 요약 추출
        elements = self._extract_elements(source)

        dump = ScreenDump(
            name=screen_name,
            fingerprint=fp,
            xml_path=xml_path,
            screenshot_path=png_path,
            elements=elements,
        )
        self._seen[fp] = dump

        print(f"[DUMP] '{screen_name}' 저장 완료 (hash: {fp}, 요소: {len(elements)}개)")
        return dump

    # ──────────────────────────────────────────────
    # 요소 파싱
    # ──────────────────────────────────────────────

    def _extract_elements(self, page_source: str) -> list[dict]:
        """page source에서 의미 있는 UI 요소를 추출"""
        try:
            root = ET.fromstring(page_source)
        except ET.ParseError:
            return []

        elements = []
        for elem in root.iter():
            attrs = elem.attrib

            # 클릭/입력 가능하거나 텍스트가 있는 요소만 수집
            clickable = attrs.get("clickable", attrs.get("accessible", "")) == "true"
            has_text = bool(attrs.get("text", attrs.get("label", attrs.get("value", ""))))
            enabled = attrs.get("enabled", "true") == "true"

            if not (clickable or has_text):
                continue

            info = {
                "tag": elem.tag,
                "class": attrs.get("class", attrs.get("type", "")),
                "resource_id": attrs.get("resource-id", attrs.get("name", "")),
                "text": attrs.get("text", attrs.get("label", attrs.get("value", ""))),
                "content_desc": attrs.get("content-desc", attrs.get("accessibility-id", "")),
                "clickable": clickable,
                "enabled": enabled,
                "bounds": attrs.get("bounds", ""),
            }

            # 빈 값 제거
            info = {k: v for k, v in info.items() if v}
            if info.get("class") or info.get("text") or info.get("resource_id"):
                elements.append(info)

        return elements

    # ──────────────────────────────────────────────
    # 리포트
    # ──────────────────────────────────────────────

    def save_summary(self):
        """모든 덤프 결과를 JSON 요약 파일로 저장"""
        summary = {}
        for fp, dump in self._seen.items():
            summary[dump.name] = {
                "fingerprint": fp,
                "xml": os.path.basename(dump.xml_path),
                "screenshot": os.path.basename(dump.screenshot_path),
                "element_count": len(dump.elements),
                "elements": dump.elements,
            }

        summary_path = os.path.join(self.dump_dir, "summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*50}")
        print(f"덤프 요약: {len(self._seen)}개 고유 화면")
        print(f"저장 위치: {summary_path}")
        print(f"{'='*50}")
        for name, info in summary.items():
            print(f"  [{info['fingerprint']}] {name} — {info['element_count']}개 요소")

        return summary_path

    @property
    def dumped_count(self) -> int:
        return len(self._seen)

    @property
    def dumped_screens(self) -> list[str]:
        return [d.name for d in self._seen.values()]
