import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """앱 테스트 환경 설정"""

    # Appium 서버
    APPIUM_HOST = os.getenv("APPIUM_HOST", "http://127.0.0.1:4723")

    # 플랫폼 설정
    PLATFORM = os.getenv("PLATFORM", "android")  # android | ios

    # Android 설정
    ANDROID_CAPS = {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:appPackage": os.getenv("APP_PACKAGE", "com.knockknock.voca"),
        "appium:appActivity": os.getenv("APP_ACTIVITY", ".inapp.MainActivity"),
        "appium:noReset": os.getenv("NO_RESET", "true").lower() == "true",
        "appium:newCommandTimeout": 300,
        "appium:autoGrantPermissions": True,
    }

    # iOS 설정
    IOS_CAPS = {
        "platformName": "iOS",
        "appium:automationName": "XCUITest",
        "appium:bundleId": os.getenv("BUNDLE_ID", "com.knockknock.voca"),
        "appium:noReset": os.getenv("NO_RESET", "true").lower() == "true",
        "appium:newCommandTimeout": 300,
        "appium:autoAcceptAlerts": True,
    }

    # 테스트 계정
    TEST_EMAIL = os.getenv("TEST_EMAIL", "")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "")

    # 타임아웃
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "10"))
    EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "15"))

    @classmethod
    def get_caps(cls):
        if cls.PLATFORM.lower() == "ios":
            return cls.IOS_CAPS
        return cls.ANDROID_CAPS


settings = Settings()
