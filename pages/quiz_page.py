import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class QuizPage(BasePage):
    """퀴즈 화면 (돈버는 퀴즈, 2분 집중학습)"""

    # ── 로케이터 (실제 앱 분석 후 업데이트 필요) ──
    _QUIZ_QUESTION = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*question.*")')
    _OPTION_1 = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*option.*").instance(0)')
    _OPTION_2 = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*option.*").instance(1)')
    _OPTION_3 = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*option.*").instance(2)')
    _OPTION_4 = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*option.*").instance(3)')
    _TIMER = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*timer.*")')
    _RESULT_CORRECT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("정답")')
    _RESULT_WRONG = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("오답")')
    _CASH_EARNED = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("캐시")')
    _NEXT_QUIZ = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("다음")')
    _CLOSE_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("닫기")')
    _FOCUS_MODE_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("2분")')
    _QUIZ_COMPLETE = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("완료")')

    # ── 액션 ──

    @allure.step("보기 {index}번 선택")
    def select_option(self, index: int):
        options = [self._OPTION_1, self._OPTION_2, self._OPTION_3, self._OPTION_4]
        if 1 <= index <= 4:
            self.tap(options[index - 1])

    @allure.step("다음 퀴즈로 이동")
    def tap_next(self):
        self.tap(self._NEXT_QUIZ)

    @allure.step("퀴즈 닫기")
    def close_quiz(self):
        self.tap(self._CLOSE_BTN)

    @allure.step("2분 집중학습 시작")
    def start_focus_mode(self):
        self.tap(self._FOCUS_MODE_BTN)

    # ── 검증 ──

    def is_quiz_visible(self) -> bool:
        return self.is_visible(self._QUIZ_QUESTION, timeout=10)

    def get_question_text(self) -> str:
        return self.get_text(self._QUIZ_QUESTION)

    def is_correct(self) -> bool:
        return self.is_visible(self._RESULT_CORRECT, timeout=5)

    def is_wrong(self) -> bool:
        return self.is_visible(self._RESULT_WRONG, timeout=5)

    def get_earned_cash_text(self) -> str:
        return self.get_text(self._CASH_EARNED)

    def is_quiz_complete(self) -> bool:
        return self.is_visible(self._QUIZ_COMPLETE, timeout=5)

    def get_timer_text(self) -> str:
        return self.get_text(self._TIMER)

    @allure.step("퀴즈 한 문제 풀기 (보기 {option}번)")
    def answer_one_question(self, option: int = 1):
        self.select_option(option)
        self.attach_screenshot("퀴즈_답변_후")
