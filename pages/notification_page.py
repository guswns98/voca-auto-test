import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class NotificationPage(BasePage):
    """알림 화면"""

    # ── 로케이터 ──
    _TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("알림")')
    _UNREAD_COUNT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("안 읽은 알림")')
    _MARK_ALL_READ = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("모두 읽음")')
    _BACK_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.view.View").clickable(true).instance(0)')

    # ── 검증 ──

    def is_notification_visible(self) -> bool:
        return self.is_visible(self._TITLE, timeout=5)

    @allure.step("알림 화면 타이틀 확인")
    def get_title(self) -> str:
        return self.get_text(self._TITLE)

    @allure.step("안 읽은 알림 수 확인")
    def get_unread_text(self) -> str:
        return self.get_text(self._UNREAD_COUNT)

    def has_mark_all_read(self) -> bool:
        return self.is_visible(self._MARK_ALL_READ, timeout=3)

    # ── 액션 ──

    @allure.step("모두 읽음 탭")
    def tap_mark_all_read(self):
        self.tap(self._MARK_ALL_READ)

    @allure.step("뒤로가기")
    def tap_back(self):
        self.tap(self._BACK_BTN)
