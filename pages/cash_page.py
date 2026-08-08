import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class CashPage(BasePage):
    """캐시(보상) 화면"""

    # ── 로케이터 (실제 앱 분석 후 업데이트 필요) ──
    _CASH_BALANCE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*balance.*|.*cash.*total.*")')
    _CASH_HISTORY = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("내역")')
    _EXCHANGE_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("교환")')
    _GIFTICON_LIST = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*gift.*item.*")')
    _LOTTERY_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("복권")')
    _BOOSTER_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("부스터")')
    _EXCHANGE_CONFIRM = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("교환하기")')
    _INSUFFICIENT_MSG = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("부족")')
    _HISTORY_ITEM = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*history.*item.*")')

    # ── 액션 ──

    @allure.step("캐시 교환 페이지 이동")
    def tap_exchange(self):
        self.tap(self._EXCHANGE_BTN)

    @allure.step("캐시 내역 조회")
    def tap_history(self):
        self.tap(self._CASH_HISTORY)

    @allure.step("복권 참여")
    def tap_lottery(self):
        self.tap(self._LOTTERY_BTN)

    @allure.step("부스터 활성화")
    def tap_booster(self):
        self.tap(self._BOOSTER_BTN)

    @allure.step("기프티콘 교환 확인")
    def confirm_exchange(self):
        self.tap(self._EXCHANGE_CONFIRM)

    # ── 검증 ──

    def get_balance(self) -> str:
        return self.get_text(self._CASH_BALANCE)

    def get_balance_as_int(self) -> int:
        text = self.get_balance()
        digits = "".join(c for c in text if c.isdigit())
        return int(digits) if digits else 0

    def is_exchange_page_visible(self) -> bool:
        return self.is_visible(self._EXCHANGE_BTN)

    def is_insufficient_balance(self) -> bool:
        return self.is_visible(self._INSUFFICIENT_MSG, timeout=5)

    def has_history_items(self) -> bool:
        return self.is_visible(self._HISTORY_ITEM, timeout=5)
