import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class CoursePage(BasePage):
    """공부 코스 선택 화면"""

    # ── 로케이터 ──
    _TITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("무엇을 공부")')
    _SUBTITLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("학습 시작할 코스")')
    _CLOSE_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.view.View").clickable(true).instance(0)')
    _START_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("시작하기")')
    _CONFIRM_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("확인")')

    # 코스 항목
    _COURSE_ENGLISH = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("영어")')
    _COURSE_HANJA = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("한자")')
    _COURSE_JAPANESE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("일본어")')
    _COURSE_KOREAN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("국어 어휘")')
    _COURSE_BIBLE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("성경")')
    _COURSE_CHINESE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("중국어")')
    _COURSE_KNOWLEDGE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("상식")')

    COURSES = {
        "영어": _COURSE_ENGLISH,
        "한자": _COURSE_HANJA,
        "일본어": _COURSE_JAPANESE,
        "국어 어휘": _COURSE_KOREAN,
        "성경": _COURSE_BIBLE,
        "중국어": _COURSE_CHINESE,
        "상식": _COURSE_KNOWLEDGE,
    }

    # ── 검증 ──

    def is_course_page_visible(self) -> bool:
        return self.is_visible(self._TITLE, timeout=5)

    @allure.step("코스 선택 화면 타이틀 확인")
    def get_title(self) -> str:
        return self.get_text(self._TITLE)

    @allure.step("코스 목록 존재 확인")
    def verify_all_courses(self) -> dict:
        """모든 코스가 표시되는지 확인"""
        result = {}
        for name, locator in self.COURSES.items():
            result[name] = self.is_visible(locator, timeout=3)
        self.attach_screenshot("코스_목록_확인")
        return result

    # ── 액션 ──

    @allure.step("코스 선택: {course_name}")
    def select_course(self, course_name: str):
        locator = self.COURSES.get(course_name)
        if locator:
            self.tap(locator)

    @allure.step("시작하기 탭")
    def tap_start(self):
        self.tap(self._START_BTN)

    @allure.step("확인 탭")
    def tap_confirm(self):
        self.tap(self._CONFIRM_BTN)

    @allure.step("닫기 탭")
    def close(self):
        self.tap(self._CLOSE_BTN)

    @allure.step("코스 변경: {course_name}")
    def change_course(self, course_name: str):
        """코스를 선택하고 시작하기까지 완료"""
        self.select_course(course_name)
        self.tap_start()
        self.attach_screenshot(f"코스_변경_{course_name}")
