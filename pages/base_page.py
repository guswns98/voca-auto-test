import allure
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.settings import settings


class BasePage:
    """모든 Page Object의 기본 클래스"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.EXPLICIT_WAIT)
        self.platform = settings.PLATFORM.lower()

    # ── 요소 탐색 ──

    def find(self, locator: tuple):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_clickable(self, locator: tuple):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def find_all(self, locator: tuple):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def is_visible(self, locator: tuple, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def is_present(self, locator: tuple, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ── 액션 ──

    def tap(self, locator: tuple):
        self.find_clickable(locator).click()

    def type_text(self, locator: tuple, text: str):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        return self.find(locator).text

    def swipe_up(self, duration: int = 800):
        size = self.driver.get_window_size()
        x = size["width"] // 2
        start_y = int(size["height"] * 0.8)
        end_y = int(size["height"] * 0.2)
        self.driver.swipe(x, start_y, x, end_y, duration)

    def swipe_down(self, duration: int = 800):
        size = self.driver.get_window_size()
        x = size["width"] // 2
        start_y = int(size["height"] * 0.2)
        end_y = int(size["height"] * 0.8)
        self.driver.swipe(x, start_y, x, end_y, duration)

    def swipe_left(self, duration: int = 800):
        size = self.driver.get_window_size()
        y = size["height"] // 2
        start_x = int(size["width"] * 0.8)
        end_x = int(size["width"] * 0.2)
        self.driver.swipe(start_x, y, end_x, y, duration)

    # ── 유틸리티 ──

    @allure.step("스크린샷 첨부: {name}")
    def attach_screenshot(self, name: str = "screenshot"):
        png = self.driver.get_screenshot_as_png()
        allure.attach(png, name=name, attachment_type=allure.attachment_type.PNG)

    def wait_for_text(self, text: str, timeout: int = 10) -> bool:
        if self.platform == "android":
            locator = (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")')
        else:
            locator = (AppiumBy.IOS_PREDICATE, f'label CONTAINS "{text}"')
        return self.is_visible(locator, timeout)

    def tap_by_text(self, text: str):
        if self.platform == "android":
            locator = (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
        else:
            locator = (AppiumBy.IOS_PREDICATE, f'label == "{text}"')
        self.tap(locator)

    def go_back(self):
        self.driver.back()
