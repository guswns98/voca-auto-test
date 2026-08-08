import time
import subprocess

import pytest
import allure
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from config.settings import settings

APP_PACKAGE = "com.knockknock.voca"


def _is_text_visible(drv, text, timeout=3):
    """텍스트 요소가 화면에 보이는지 확인"""
    try:
        locator = (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")')
        WebDriverWait(drv, timeout).until(EC.visibility_of_element_located(locator))
        return True
    except (TimeoutException, WebDriverException):
        return False


def _tap_text(drv, text, timeout=5):
    """텍스트로 요소를 찾아 탭"""
    locator = (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")')
    el = WebDriverWait(drv, timeout).until(EC.element_to_be_clickable(locator))
    el.click()
    time.sleep(1.5)


def _is_on_home(drv, timeout=3):
    """홈 화면인지 확인 (홈 고유 텍스트로 판별)"""
    return (_is_text_visible(drv, "캐시 더 모으기", timeout=timeout)
            or _is_text_visible(drv, "퀴즈 풀러 가기", timeout=1))


def _dismiss_lock_screen(drv):
    """잠금 화면 퀴즈가 뜬 경우 홈 버튼(우측 하단)으로 앱 홈 이동"""
    if _is_text_visible(drv, "밀어서 해제", timeout=3):
        # 우측 하단 홈 버튼 좌표 탭
        drv.tap([(959, 2029)])
        time.sleep(3)


def _ensure_home_screen(drv):
    """앱이 홈 화면에 도달하도록 보장. 이미 홈이면 즉시 리턴."""
    # 앱 로딩 대기 (Compose 렌더링 + 네트워크 로딩)
    time.sleep(5)

    # 잠금 화면 퀴즈가 뜬 경우 홈 버튼으로 이동
    _dismiss_lock_screen(drv)

    # 홈 화면을 최대 15초까지 폴링
    for _ in range(5):
        if _is_on_home(drv, timeout=3):
            return
        time.sleep(2)

    # 홈이 아니면 온보딩 플로우 시도
    # "가입 없이 시작하기"가 보일 때만 온보딩 진행
    if _is_text_visible(drv, "가입 없이 시작하기", timeout=3):
        _tap_text(drv, "가입 없이 시작하기")

        if _is_text_visible(drv, "이어서 이용하기", timeout=5):
            _tap_text(drv, "이어서 이용하기")

        if _is_text_visible(drv, "전체 동의합니다", timeout=5):
            _tap_text(drv, "전체 동의합니다")
            _tap_text(drv, "확인")

        if _is_text_visible(drv, "무엇을 공부하시겠어요?", timeout=5):
            _tap_text(drv, "영어")
            _tap_text(drv, "시작하기")

        if _is_text_visible(drv, "공부 코스 선택", timeout=5):
            _tap_text(drv, "생활영어 기본")
            _tap_text(drv, "확인")

        if _is_text_visible(drv, "코스 선택 완료", timeout=5):
            _tap_text(drv, "시작하기")

    # 최종: 홈이 아니면 뒤로가기로 복귀 시도
    for _ in range(5):
        if _is_on_home(drv, timeout=3):
            return
        drv.back()
        time.sleep(2)


@pytest.fixture(scope="session")
def driver():
    """Appium 드라이버 세션 (전체 테스트 세션 동안 유지)"""
    caps = settings.get_caps()
    options = AppiumOptions()
    for key, value in caps.items():
        options.set_capability(key, value)

    # 기존 앱 프로세스 강제 종료 후 깨끗한 상태에서 시작
    subprocess.run(["adb", "shell", "am", "force-stop", APP_PACKAGE], capture_output=True)
    time.sleep(2)

    drv = webdriver.Remote(settings.APPIUM_HOST, options=options)
    drv.implicitly_wait(settings.IMPLICIT_WAIT)

    # 홈 화면 도달 보장 (앱은 caps의 appPackage/appActivity로 자동 실행됨)
    _ensure_home_screen(drv)

    yield drv

    drv.quit()


def _close_sheet(drv):
    """시트(코스 선택 등) 닫기 버튼 탭"""
    try:
        locator = (AppiumBy.ACCESSIBILITY_ID, "시트 닫기")
        el = WebDriverWait(drv, 2).until(EC.element_to_be_clickable(locator))
        el.click()
        time.sleep(1)
        return True
    except (TimeoutException, WebDriverException):
        return False


@pytest.fixture(scope="function", autouse=True)
def ensure_home(driver, request):
    """각 테스트 시작 전 홈 화면으로 복귀 보장 (no_home_reset 마커 시 스킵)"""
    if request.node.get_closest_marker("no_home_reset"):
        yield
        return
    try:
        for _ in range(5):
            if _is_on_home(driver, timeout=3):
                break
            if not _close_sheet(driver):
                driver.back()
            time.sleep(1)
        else:
            driver.terminate_app(APP_PACKAGE)
            time.sleep(1)
            driver.activate_app(APP_PACKAGE)
            time.sleep(5)
    except WebDriverException:
        try:
            driver.terminate_app(APP_PACKAGE)
            time.sleep(1)
            driver.activate_app(APP_PACKAGE)
            time.sleep(5)
        except Exception:
            pass
    yield


@pytest.fixture(scope="function", autouse=True)
def test_context(driver, request):
    """각 테스트 시작/종료 시 컨텍스트 관리"""
    yield

    # 테스트 실패 시 자동 스크린샷 첨부
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        try:
            png = driver.get_screenshot_as_png()
            allure.attach(
                png,
                name=f"FAIL_{request.node.name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 결과를 fixture에서 접근할 수 있도록 저장"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
