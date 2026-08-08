"""
똑똑보카 앱 화면 별 UI 덤프 스크립트

실행: python dump_screens.py
결과: dumps/ 디렉토리에 화면별 XML + 스크린샷 + summary.json
"""

import sys
import time

from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.settings import settings
from utils.screen_dumper import ScreenDumper


def create_driver():
    caps = settings.get_caps()
    # 이미 앱이 열려있으므로 noReset
    caps["appium:noReset"] = True
    options = AppiumOptions()
    for k, v in caps.items():
        options.set_capability(k, v)
    drv = webdriver.Remote(settings.APPIUM_HOST, options=options)
    drv.implicitly_wait(3)
    return drv


def wait(sec: float = 2.0):
    time.sleep(sec)


def try_tap(driver, text: str, timeout: float = 3.0) -> bool:
    """텍스트로 요소를 찾아 탭. 못 찾으면 False."""
    try:
        locator = (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")')
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
        el.click()
        return True
    except (TimeoutException, NoSuchElementException, Exception):
        return False


def try_tap_view(driver, index: int) -> bool:
    """clickable View를 인덱스로 탭"""
    try:
        locator = (AppiumBy.ANDROID_UIAUTOMATOR,
                   f'new UiSelector().className("android.view.View").clickable(true).instance({index})')
        el = driver.find_element(*locator)
        el.click()
        return True
    except Exception:
        return False


def dump_all_screens(driver, dumper: ScreenDumper):
    print("\n" + "=" * 50)
    print("똑똑보카 화면 덤프 시작")
    print("=" * 50 + "\n")

    # ── 1) 홈 화면 (현재 상태) ──
    wait(2)
    dumper.dump("홈_화면")

    # ── 2) 홈 화면 상단 영역 ──
    # "영어" 코스 셀렉터 (좌상단)
    if try_tap(driver, "영어", timeout=2):
        wait(2)
        dumper.dump("코스_선택_화면")
        driver.back()
        wait(1)

    # ── 3) 돈 버는 오늘의 학습미션 ──
    if try_tap(driver, "학습미션", timeout=2):
        wait(2)
        dumper.dump("학습미션_화면")
        driver.back()
        wait(1)

    # ── 4) 추가 혜택 리스트 ──
    if try_tap(driver, "추가 혜택", timeout=2):
        wait(2)
        dumper.dump("추가_혜택_화면")
        driver.back()
        wait(1)

    # ── 5) 친구초대 ──
    if try_tap(driver, "친구초대", timeout=2):
        wait(2)
        dumper.dump("친구초대_화면")
        driver.back()
        wait(1)

    # ── 6) 기프티콘 구매 · 쿠폰함 ──
    if try_tap(driver, "기프티콘", timeout=2):
        wait(2)
        dumper.dump("기프티콘_구매_화면")
        driver.back()
        wait(1)

    # ── 7) 현금 출금하기 ──
    if try_tap(driver, "현금 출금", timeout=2):
        wait(2)
        dumper.dump("현금_출금_화면")
        driver.back()
        wait(1)

    # ── 8) 보너스 퀴즈 ──
    if try_tap(driver, "보너스 퀴즈", timeout=2):
        wait(2)
        dumper.dump("보너스_퀴즈_화면")
        driver.back()
        wait(1)

    # ── 9) 우상단 아이콘 (설정/알림 등) ──
    # bounds [933,132][1059,258] 위치의 View
    try:
        locator = (AppiumBy.ANDROID_UIAUTOMATOR,
                   'new UiSelector().className("android.view.View").clickable(true).instance(1)')
        el = driver.find_element(*locator)
        el.click()
        wait(2)
        dumper.dump("우상단_메뉴_화면")
        driver.back()
        wait(1)
    except Exception:
        print("[SKIP] 우상단 메뉴 접근 실패")

    # ── 10) 스크롤 다운 후 추가 요소 확인 ──
    size = driver.get_window_size()
    driver.swipe(size['width']//2, int(size['height']*0.7), size['width']//2, int(size['height']*0.3), 800)
    wait(2)
    dumper.dump("홈_스크롤_하단")

    # 원위치 복귀
    driver.swipe(size['width']//2, int(size['height']*0.3), size['width']//2, int(size['height']*0.7), 800)
    wait(1)

    # ── 완료 ──
    dumper.save_summary()


def main():
    print("Appium 서버 연결 중...")
    try:
        driver = create_driver()
    except Exception as e:
        print(f"[ERROR] Appium 연결 실패: {e}")
        sys.exit(1)

    dumper = ScreenDumper(driver)

    try:
        dump_all_screens(driver, dumper)
    except Exception as e:
        print(f"\n[ERROR] 덤프 중 오류: {e}")
        import traceback
        traceback.print_exc()
        dumper.save_summary()
    finally:
        driver.quit()

    print(f"\n총 {dumper.dumped_count}개 고유 화면 덤프 완료")


if __name__ == "__main__":
    main()
