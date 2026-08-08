import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class SettingsPage(BasePage):
    """설정 화면"""

    # ── 로케이터 (실제 앱 분석 후 업데이트 필요) ──
    _SETTINGS_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("설정")')
    _LOCK_SCREEN_TOGGLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("잠금화면")')
    _PUSH_TOGGLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("알림")')
    _ALARM_SETTING = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("학습 알람")')
    _INQUIRY_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("문의")')
    _LOGOUT_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("로그아웃")')
    _DELETE_ACCOUNT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("탈퇴")')
    _CONFIRM_DIALOG = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("확인")')
    _CANCEL_DIALOG = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("취소")')
    _VERSION_INFO = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("버전")')

    # ── 액션 ──

    @allure.step("잠금화면 설정 토글")
    def toggle_lock_screen(self):
        self.tap(self._LOCK_SCREEN_TOGGLE)

    @allure.step("푸시 알림 토글")
    def toggle_push_notification(self):
        self.tap(self._PUSH_TOGGLE)

    @allure.step("학습 알람 설정 진입")
    def tap_alarm_setting(self):
        self.tap(self._ALARM_SETTING)

    @allure.step("문의하기 탭")
    def tap_inquiry(self):
        self.tap(self._INQUIRY_BTN)

    @allure.step("로그아웃")
    def tap_logout(self):
        self.tap(self._LOGOUT_BTN)

    @allure.step("로그아웃 확인")
    def confirm_logout(self):
        self.tap_logout()
        self.tap(self._CONFIRM_DIALOG)
        self.attach_screenshot("로그아웃_완료")

    @allure.step("회원 탈퇴 탭")
    def tap_delete_account(self):
        self.tap(self._DELETE_ACCOUNT)

    @allure.step("다이얼로그 확인 탭")
    def confirm_dialog(self):
        self.tap(self._CONFIRM_DIALOG)

    @allure.step("다이얼로그 취소 탭")
    def cancel_dialog(self):
        self.tap(self._CANCEL_DIALOG)

    # ── 검증 ──

    def is_settings_visible(self) -> bool:
        return self.is_visible(self._SETTINGS_TITLE)

    def get_version(self) -> str:
        return self.get_text(self._VERSION_INFO)
