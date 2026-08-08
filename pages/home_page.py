import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class HomePage(BasePage):
    """홈 화면 (단일 스크롤 페이지)"""

    # ── 상단 영역 ──
    _COURSE_SELECTOR = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("영어").className("android.widget.TextView")')
    _NOTIFICATION_ICON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.view.View").clickable(true).instance(1)')

    # ── 캐시 더 모으기 섹션 ──
    _SECTION_EARN_CASH = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("캐시 더 모으기")')
    _MENU_DAILY_MISSION = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("학습미션")')
    _MENU_EXTRA_BENEFITS = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("추가 혜택")')
    _MENU_INVITE_FRIEND = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("친구초대")')
    _MENU_INVITE_CASH = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("1,500캐시")')

    # ── 캐시 교환하기 섹션 ──
    _SECTION_EXCHANGE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("캐시 교환하기")')
    _MENU_GIFTICON = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("기프티콘")')
    _MENU_WITHDRAW = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("현금 출금")')

    # ── 학습하기 섹션 ──
    _SECTION_LEARN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("학습하기")')
    _MENU_BONUS_QUIZ = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("보너스 퀴즈")')
    _MENU_BONUS_QUIZ_SUB = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("2분이면")')

    # ── 하단 광고 배너 ──
    _AD_BANNER = (AppiumBy.ID, "com.knockknock.voca:id/applovin_strip_banner_title_text_view")

    # ── 검증 ──

    def is_home_visible(self) -> bool:
        return self.is_visible(self._SECTION_EARN_CASH, timeout=5)

    @allure.step("홈 화면 진입 확인")
    def verify_home_screen(self) -> dict:
        """홈 화면의 주요 섹션이 모두 표시되는지 확인하고 결과를 반환"""
        result = {
            "캐시_더_모으기": self.is_visible(self._SECTION_EARN_CASH, timeout=5),
            "캐시_교환하기": self.is_visible(self._SECTION_EXCHANGE, timeout=3),
            "학습하기": self.is_visible(self._SECTION_LEARN, timeout=3),
        }
        self.attach_screenshot("홈_화면_검증")
        return result

    @allure.step("홈 화면 메뉴 항목 존재 확인")
    def verify_menu_items(self) -> dict:
        """모든 메뉴 항목이 표시되는지 확인"""
        return {
            "학습미션": self.is_visible(self._MENU_DAILY_MISSION, timeout=3),
            "추가_혜택": self.is_visible(self._MENU_EXTRA_BENEFITS, timeout=3),
            "친구초대": self.is_visible(self._MENU_INVITE_FRIEND, timeout=3),
            "기프티콘": self.is_visible(self._MENU_GIFTICON, timeout=3),
            "현금_출금": self.is_visible(self._MENU_WITHDRAW, timeout=3),
            "보너스_퀴즈": self.is_visible(self._MENU_BONUS_QUIZ, timeout=3),
        }

    def get_current_course(self) -> str:
        return self.get_text(self._COURSE_SELECTOR)

    # ── 탐색 ──

    @allure.step("코스 선택 화면 진입")
    def tap_course_selector(self):
        self.tap(self._COURSE_SELECTOR)

    @allure.step("알림 화면 진입")
    def tap_notification(self):
        self.find_clickable(self._NOTIFICATION_ICON).click()

    @allure.step("학습미션 탭")
    def tap_daily_mission(self):
        self.tap(self._MENU_DAILY_MISSION)

    @allure.step("추가 혜택 탭")
    def tap_extra_benefits(self):
        self.tap(self._MENU_EXTRA_BENEFITS)

    @allure.step("친구초대 탭")
    def tap_invite_friend(self):
        self.tap(self._MENU_INVITE_FRIEND)

    @allure.step("기프티콘 구매 탭")
    def tap_gifticon(self):
        self.tap(self._MENU_GIFTICON)

    @allure.step("현금 출금 탭")
    def tap_withdraw(self):
        self.tap(self._MENU_WITHDRAW)

    @allure.step("보너스 퀴즈 탭")
    def tap_bonus_quiz(self):
        self.tap(self._MENU_BONUS_QUIZ)

    def has_ad_banner(self) -> bool:
        return self.is_visible(self._AD_BANNER, timeout=3)
