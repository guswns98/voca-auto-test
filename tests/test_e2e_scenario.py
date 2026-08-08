"""
똑똑보카 E2E 시나리오 테스트
- 앱 실행 → 핵심 기능 순회
- 회원 로그인 상태 전제
- 시나리오를 하나씩 추가하며 운영
"""
import time

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

    # ── E2E-01: 앱 실행 → 홈 화면 요소 확인 → 퀴즈 풀러가기 → 팝업 X → 홈 버튼 ──

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
    @allure.title("E2E-04: 홈 버튼 선택")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.no_home_reset
    def test_e2e_04_go_home(self, driver):
        """홈 버튼을 선택하여 앱 홈 화면으로 이동한다."""
        self._screenshot("E2E_04_홈버튼전")
        self.driver.tap([(959, 2029)])
        time.sleep(3)
        self._screenshot("E2E_04_홈버튼후")
        assert self._is_text("캐시 더 모으기", timeout=10), "앱 홈 화면이 표시되어야 한다"
