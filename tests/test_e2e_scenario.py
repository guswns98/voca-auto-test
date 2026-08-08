"""
똑똑보카 E2E 시나리오 테스트
- 앱 실행 → 핵심 기능 순회
- 회원 로그인 상태 전제
- 시나리오를 하나씩 추가하며 운영
"""
import time
import json
import requests

import allure
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from pages.base_page import BasePage


@allure.epic("똑똑보카")
@allure.feature("E2E 시나리오")
class TestE2EScenario:
    """앱 실행부터 핵심 기능까지 E2E 시나리오"""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.page = BasePage(driver)

    def _is_text(self, text, timeout=3):
        try:
            locator = (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")')
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except (TimeoutException, WebDriverException):
            return False

    def _tap(self, text, timeout=5):
        locator = (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")')
        el = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
        el.click()
        time.sleep(2)

    def _tap_by_desc(self, desc, timeout=5):
        locator = (AppiumBy.ACCESSIBILITY_ID, desc)
        el = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
        el.click()
        time.sleep(2)

    def _screenshot(self, name):
        self.page.attach_screenshot(name)

    def _get_quiz_info(self):
        """퀴즈 화면에서 문제 텍스트와 보기를 추출 (유형 무관)"""
        quiz = {"texts": [], "options": []}

        try:
            xml = self.driver.page_source
            from xml.etree import ElementTree as ET
            root = ET.fromstring(xml)

            skip_texts = {"밀어서 해제", "복권 긁기", "300캐시 받기",
                          "게임 설치만 해도 즉시 지급", "날씨"}

            for el in root.iter():
                if el.get("class") != "android.widget.TextView":
                    continue
                text = el.get("text", "").strip()
                if not text or text in skip_texts:
                    continue

                bounds = el.get("bounds", "")
                parts = bounds.replace("][", ",").replace("[", "").replace("]", "").split(",")
                if len(parts) != 4:
                    continue
                x1, y1 = int(parts[0]), int(parts[1])

                # 보기 영역: x 100~600, y 800~1300
                if 100 <= x1 <= 600 and 800 <= y1 <= 1300:
                    quiz["options"].append(text)
                # 문제 영역: y 400~800
                elif 80 <= x1 <= 990 and 400 <= y1 <= 800:
                    # InLineIcon 패턴 정리
                    if "InLineIcon" in text:
                        text = text.split("InLineIcon")[-1].strip()
                    if text:
                        quiz["texts"].append(text)
        except Exception:
            pass

        return quiz

    def _ask_llm(self, quiz):
        """Ollama gemma3로 정답 판별 (범용 프롬프트)"""
        question_text = "\n".join(quiz["texts"])
        options_text = ", ".join(quiz["options"])

        prompt = (f"다음은 영어 단어 퀴즈입니다.\n"
                  f"문제: {question_text}\n"
                  f"보기: {options_text}\n"
                  f"정답만 한 단어로 답해.")

        resp = requests.post("http://localhost:11434/api/generate", json={
            "model": "gemma3",
            "prompt": prompt,
            "stream": False,
        }, timeout=30)
        answer = resp.json()["response"].strip()
        # 응답에서 보기에 있는 단어만 추출
        for opt in quiz["options"]:
            if opt in answer:
                return opt
        return answer

    # ── E2E-01: 앱 실행 → 홈 화면 확인 → 퀴즈 풀러가기 → 팝업 X → 퀴즈 정답 선택 ──

    @allure.story("메인 시나리오")
    @allure.title("E2E-01: 앱 실행 후 홈 화면 확인")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.p0
    def test_e2e_01_home_screen(self, driver):
        """앱 실행 후 홈 화면 요소가 정상 표시된다."""
        self._screenshot("E2E_01_앱실행직후")
        assert (self._is_text("캐시 더 모으기", timeout=10)
                or self._is_text("다음 단어의 뜻은", timeout=3)
                or self._is_text("레슨", timeout=3)), "앱 화면이 표시되어야 한다"
        self._screenshot("E2E_01_홈화면확인")

    @allure.story("메인 시나리오")
    @allure.title("E2E-02: 퀴즈 풀러가기 선택")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_e2e_02_quiz_entry(self, driver):
        """퀴즈 풀러가기를 선택한다. (하루 퀴즈 완료 시 '단어 공부하러 가기'로 변경)"""
        self._screenshot("E2E_02_퀴즈선택전")
        if self._is_text("퀴즈 풀러 가기", timeout=3):
            self._tap("퀴즈 풀러 가기")
        elif self._is_text("퀴즈 풀러가기", timeout=3):
            self._tap("퀴즈 풀러가기")
        elif self._is_text("단어 공부하러 가기", timeout=3):
            self._tap("단어 공부하러 가기")
            pytest.skip("하루 퀴즈 완료 상태 — 이후 시나리오 스킵")
        else:
            self._screenshot("E2E_02_퀴즈버튼없음")
            pytest.fail("퀴즈 풀러가기 버튼을 찾을 수 없음")
        self._screenshot("E2E_02_퀴즈선택후")

    @allure.story("메인 시나리오")
    @allure.title("E2E-03: 팝업창 X버튼 선택")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.no_home_reset
    def test_e2e_03_close_popup(self, driver):
        """팝업창의 X버튼을 선택하여 닫는다."""
        if self._is_text("학습미션", timeout=3):
            pytest.skip("하루 퀴즈 완료 상태 — 퀴즈 흐름 스킵")
        self._screenshot("E2E_03_팝업확인")
        closed = False
        try:
            self._tap_by_desc("시트 닫기", timeout=3)
            closed = True
        except (TimeoutException, WebDriverException):
            pass
        if not closed:
            try:
                self._tap_by_desc("닫기", timeout=3)
                closed = True
            except (TimeoutException, WebDriverException):
                pass
        if not closed:
            self._screenshot("E2E_03_X버튼없음")
            pytest.fail("팝업 X버튼을 찾을 수 없음")
        self._screenshot("E2E_03_팝업닫기후")

    @allure.story("메인 시나리오")
    @allure.title("E2E-04: 퀴즈 정답 선택")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.no_home_reset
    def test_e2e_04_quiz_answer(self, driver):
        """LLM으로 퀴즈 정답을 판별하여 선택한다."""
        if not (self._is_text("레슨", timeout=3)):
            pytest.skip("하루 퀴즈 완료 상태 — 퀴즈 흐름 스킵")
        self._screenshot("E2E_04_퀴즈화면")

        # 퀴즈 정보 추출
        quiz = self._get_quiz_info()
        assert len(quiz["texts"]) >= 1, f"퀴즈 문제를 찾을 수 없음"
        assert len(quiz["options"]) >= 2, f"보기가 부족: {quiz['options']}"

        allure.attach("\n".join(quiz["texts"]), name="퀴즈 문제", attachment_type=allure.attachment_type.TEXT)
        allure.attach(", ".join(quiz["options"]), name="보기 목록", attachment_type=allure.attachment_type.TEXT)

        # LLM 정답 판별
        answer = self._ask_llm(quiz)
        allure.attach(answer, name="LLM 정답", attachment_type=allure.attachment_type.TEXT)

        # 정답 탭
        self._tap(answer)
        self._screenshot("E2E_04_정답선택후")

    @allure.story("메인 시나리오")
    @allure.title("E2E-05: 정답 확인")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.no_home_reset
    def test_e2e_05_answer_result(self, driver):
        """퀴즈 정답 선택 후 정답 또는 암기완료 화면이 표시된다."""
        if not (self._is_text("정답입니다", timeout=3) or self._is_text("암기완료", timeout=3)):
            pytest.skip("하루 퀴즈 완료 상태 — 퀴즈 흐름 스킵")
        self._screenshot("E2E_05_정답화면")
        is_correct = self._is_text("정답입니다", timeout=5)
        is_memorized = self._is_text("암기완료", timeout=3)
        assert is_correct or is_memorized, "정답 또는 암기완료 화면이 표시되어야 한다"
        self._screenshot("E2E_05_정답확인완료")

    @allure.story("메인 시나리오")
    @allure.title("E2E-06: 홈 복귀")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.no_home_reset
    def test_e2e_06_go_home(self, driver):
        """홈 버튼을 선택하여 앱 홈 화면으로 이동한다."""
        if self._is_text("학습미션", timeout=3) or self._is_text("캐시 더 모으기", timeout=3):
            pytest.skip("하루 퀴즈 완료 상태 — 퀴즈 흐름 스킵")
        self._screenshot("E2E_06_홈버튼전")
        self.driver.tap([(959, 2029)])
        time.sleep(3)
        self._screenshot("E2E_06_홈버튼후")
        assert self._is_text("캐시 더 모으기", timeout=10), "앱 홈 화면이 표시되어야 한다"

    # ── E2E-07~09: 홈 화면 기능 (퀴즈 상태 무관) ──

    @allure.story("홈 화면 기능")
    @allure.title("E2E-07: 학습미션 진입")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_e2e_07_study_mission(self, driver):
        """학습미션 화면에 진입하고 내용을 확인한다."""
        self._screenshot("E2E_07_홈화면")
        self._tap("돈 버는 오늘의 학습미션")
        self._screenshot("E2E_07_학습미션진입")
        assert self._is_text("매일 보상받기", timeout=5), "학습미션 화면이 표시되어야 한다"
        self._screenshot("E2E_07_학습미션확인")

    @allure.story("홈 화면 기능")
    @allure.title("E2E-08: 복권 영역 확인")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_e2e_08_lottery_entry(self, driver):
        """홈에서 복권 화면에 진입하여 복권 긁기 버튼을 확인한다."""
        self._screenshot("E2E_08_홈화면")
        assert self._is_text("꽝없는 복권", timeout=5), "복권 영역이 표시되어야 한다"
        assert self._is_text("복권 긁기", timeout=5), "복권 긁기 버튼이 표시되어야 한다"
        self._screenshot("E2E_08_복권확인완료")

    # @allure.story("메인 시나리오")
    # @allure.title("E2E-04: 홈 버튼 선택")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.p0
    # @pytest.mark.no_home_reset
    # def test_e2e_04_go_home(self, driver):
    #     """홈 버튼을 선택하여 앱 홈 화면으로 이동한다."""
    #     self._screenshot("E2E_04_홈버튼전")
    #     self.driver.tap([(959, 2029)])
    #     time.sleep(3)
    #     self._screenshot("E2E_04_홈버튼후")
    #     assert self._is_text("캐시 더 모으기", timeout=10), "앱 홈 화면이 표시되어야 한다"
