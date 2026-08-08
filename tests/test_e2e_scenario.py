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
        """퀴즈 화면에서 문제 유형, 질문, 보기 추출"""
        quiz = {"type": None, "question": None, "hint": None, "options": []}

        # 문제 유형 판별
        if self._is_text("다음 단어의 뜻은", timeout=3):
            quiz["type"] = "word_meaning"
            # 영단어 추출 (InLineIcon 패턴 또는 일반 텍스트)
            try:
                locator = (AppiumBy.ANDROID_UIAUTOMATOR,
                           'new UiSelector().className("android.view.View").clickable(true).textContains("InLineIcon")')
                el = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(locator))
                raw = el.text
                quiz["question"] = raw.split("InLineIcon")[-1].strip() if "InLineIcon" in raw else raw.strip()
            except (TimeoutException, WebDriverException):
                pass
        elif self._is_text("빈칸에 알맞은 단어는", timeout=3):
            quiz["type"] = "fill_blank"
            # 영어 문장 추출
            try:
                locator = (AppiumBy.ANDROID_UIAUTOMATOR,
                           'new UiSelector().className("android.widget.TextView").textContains("(")')
                el = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(locator))
                quiz["question"] = el.text.strip()
            except (TimeoutException, WebDriverException):
                pass
            # 한국어 해석 추출
            try:
                locator = (AppiumBy.ANDROID_UIAUTOMATOR,
                           'new UiSelector().className("android.widget.TextView").textMatches(".*[가-힣].*[가-힣].*")')
                elements = self.driver.find_elements(*locator)
                for el in elements:
                    text = el.text.strip()
                    if text and text not in ("빈칸에 알맞은 단어는?", "밀어서 해제", "복권 긁기", "게임 설치만 해도 즉시 지급"):
                        quiz["hint"] = text
                        break
            except WebDriverException:
                pass

        # 보기 추출 (영어 또는 한국어)
        try:
            xml = self.driver.page_source
            from xml.etree import ElementTree as ET
            root = ET.fromstring(xml)
            skip_texts = {"레슨 1", "밀어서 해제", "복권 긁기", "300캐시 받기",
                          "게임 설치만 해도 즉시 지급", "다음 단어의 뜻은?",
                          "빈칸에 알맞은 단어는?", "날씨"}
            for el in root.iter():
                if el.get("class") == "android.widget.TextView":
                    bounds = el.get("bounds", "")
                    parts = bounds.replace("][", ",").replace("[", "").replace("]", "").split(",")
                    if len(parts) == 4:
                        x1, y1 = int(parts[0]), int(parts[1])
                        # 보기 영역: x 121~959, y 800~1300 범위
                        if 100 <= x1 <= 600 and 800 <= y1 <= 1300:
                            text = el.get("text", "").strip()
                            if text and text not in skip_texts:
                                quiz["options"].append(text)
        except Exception:
            pass

        return quiz

    def _ask_llm(self, quiz):
        """Ollama gemma3로 정답 판별"""
        if quiz["type"] == "word_meaning":
            prompt = (f"영어 단어 '{quiz['question']}'의 한국어 뜻을 보기에서 골라. "
                      f"보기: {', '.join(quiz['options'])}. 정답만 한 단어로 답해.")
        elif quiz["type"] == "fill_blank":
            prompt = (f"다음 영어 문장의 빈칸에 알맞은 단어를 보기에서 골라.\n"
                      f"문장: {quiz['question']}\n")
            if quiz["hint"]:
                prompt += f"해석: {quiz['hint']}\n"
            prompt += f"보기: {', '.join(quiz['options'])}. 정답만 한 단어로 답해."
        else:
            prompt = (f"다음 퀴즈의 정답을 보기에서 골라. "
                      f"보기: {', '.join(quiz['options'])}. 정답만 한 단어로 답해.")

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
        """퀴즈 풀러가기를 선택한다."""
        self._screenshot("E2E_02_퀴즈선택전")
        if self._is_text("퀴즈 풀러 가기", timeout=3):
            self._tap("퀴즈 풀러 가기")
        elif self._is_text("퀴즈 풀러가기", timeout=3):
            self._tap("퀴즈 풀러가기")
        elif self._is_text("퀴즈", timeout=3):
            self._tap("퀴즈")
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
        self._screenshot("E2E_04_퀴즈화면")

        # 퀴즈 정보 추출
        quiz = self._get_quiz_info()
        assert quiz["type"], "퀴즈 유형을 판별할 수 없음"
        assert quiz["question"], "퀴즈 문제를 찾을 수 없음"
        assert len(quiz["options"]) >= 2, f"보기가 부족: {quiz['options']}"

        allure.attach(quiz["type"], name="퀴즈 유형", attachment_type=allure.attachment_type.TEXT)
        allure.attach(quiz["question"], name="퀴즈 문제", attachment_type=allure.attachment_type.TEXT)
        allure.attach(", ".join(quiz["options"]), name="보기 목록", attachment_type=allure.attachment_type.TEXT)

        # LLM 정답 판별
        answer = self._ask_llm(quiz)
        allure.attach(answer, name="LLM 정답", attachment_type=allure.attachment_type.TEXT)

        # 정답 탭
        self._tap(answer)
        self._screenshot("E2E_04_정답선택후")

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
