import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class LoginPage(BasePage):
    """로그인/회원가입 화면"""

    # ── 로케이터 (실제 앱 분석 후 업데이트 필요) ──
    _EMAIL_INPUT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText").instance(0)')
    _PASSWORD_INPUT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText").instance(1)')
    _LOGIN_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("로그인")')
    _SIGNUP_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("회원가입")')
    _KAKAO_LOGIN_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("카카오")')
    _GOOGLE_LOGIN_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Google")')
    _APPLE_LOGIN_BTN = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Apple")')
    _FORGOT_PASSWORD = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("비밀번호 찾기")')
    _REFERRAL_INPUT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("추천인")')
    _LOGIN_ERROR_MSG = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("일치하지")')

    # ── 액션 ──

    @allure.step("이메일 입력: {email}")
    def enter_email(self, email: str):
        self.type_text(self._EMAIL_INPUT, email)

    @allure.step("비밀번호 입력")
    def enter_password(self, password: str):
        self.type_text(self._PASSWORD_INPUT, password)

    @allure.step("로그인 버튼 탭")
    def tap_login(self):
        self.tap(self._LOGIN_BTN)

    @allure.step("회원가입 버튼 탭")
    def tap_signup(self):
        self.tap(self._SIGNUP_BTN)

    @allure.step("카카오 로그인 탭")
    def tap_kakao_login(self):
        self.tap(self._KAKAO_LOGIN_BTN)

    @allure.step("Google 로그인 탭")
    def tap_google_login(self):
        self.tap(self._GOOGLE_LOGIN_BTN)

    @allure.step("비밀번호 찾기 탭")
    def tap_forgot_password(self):
        self.tap(self._FORGOT_PASSWORD)

    @allure.step("추천인 코드 입력: {code}")
    def enter_referral_code(self, code: str):
        self.type_text(self._REFERRAL_INPUT, code)

    # ── 복합 액션 ──

    @allure.step("이메일로 로그인: {email}")
    def login_with_email(self, email: str, password: str):
        self.enter_email(email)
        self.enter_password(password)
        self.tap_login()
        self.attach_screenshot("로그인_시도")

    # ── 검증 ──

    def is_login_page_visible(self) -> bool:
        return self.is_visible(self._LOGIN_BTN)

    def is_login_error_visible(self) -> bool:
        return self.is_visible(self._LOGIN_ERROR_MSG, timeout=5)
