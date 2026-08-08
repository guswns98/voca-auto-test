import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class OnboardingPage(BasePage):
    """앱 최초 실행 시 온보딩 화면"""

    # ── 로케이터 (실제 앱 분석 후 업데이트 필요) ──
    # Android
    _START_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("시작")')
    _CATEGORY_ENGLISH = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("영어")')
    _CATEGORY_JAPANESE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("일본어")')
    _CATEGORY_CHINESE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("중국어")')
    _NEXT_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("다음")')
    _CONFIRM_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("확인")')
    _SKIP_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("건너뛰기")')
    _PERMISSION_ALLOW = (AppiumBy.ID, "com.android.permissioncontroller:id/permission_allow_button")

    # ── 액션 ──

    @allure.step("온보딩 시작 버튼 탭")
    def tap_start(self):
        self.tap(self._START_BTN)

    @allure.step("학습 카테고리 선택: {category}")
    def select_category(self, category: str = "영어"):
        category_map = {
            "영어": self._CATEGORY_ENGLISH,
            "일본어": self._CATEGORY_JAPANESE,
            "중국어": self._CATEGORY_CHINESE,
        }
        locator = category_map.get(category, self._CATEGORY_ENGLISH)
        self.tap(locator)

    @allure.step("다음 버튼 탭")
    def tap_next(self):
        self.tap(self._NEXT_BTN)

    @allure.step("확인 버튼 탭")
    def tap_confirm(self):
        self.tap(self._CONFIRM_BTN)

    @allure.step("건너뛰기 탭")
    def tap_skip(self):
        if self.is_visible(self._SKIP_BTN, timeout=3):
            self.tap(self._SKIP_BTN)

    @allure.step("권한 허용")
    def allow_permission(self):
        if self.is_visible(self._PERMISSION_ALLOW, timeout=3):
            self.tap(self._PERMISSION_ALLOW)

    # ── 검증 ──

    def is_onboarding_visible(self) -> bool:
        return self.is_visible(self._START_BTN)

    @allure.step("온보딩 전체 플로우 완료")
    def complete_onboarding(self, category: str = "영어"):
        self.allow_permission()
        if self.is_onboarding_visible():
            self.tap_start()
            self.select_category(category)
            self.tap_next()
            self.tap_confirm()
        self.attach_screenshot("온보딩_완료")
