import allure
import pytest

from pages import HomePage, NotificationPage


@allure.epic("똑똑보카")
@allure.feature("알림")
class TestNotification:
    """알림 화면 (비회원) 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.home = HomePage(driver)
        self.noti = NotificationPage(driver)

    def _enter_notification(self):
        if not self.noti.is_notification_visible():
            self.home.tap_notification()

    @allure.story("화면 구성")
    @allure.title("NOTI-001: 알림 화면 타이틀")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_notification_title(self, driver):
        """알림 화면에 '알림' 타이틀이 표시된다."""
        self._enter_notification()
        title = self.noti.get_title()
        assert title == "알림", f"타이틀이 '알림'이어야 한다. 실제: {title}"
        driver.back()

    @allure.story("화면 구성")
    @allure.title("NOTI-002: 안 읽은 알림 카운트 표시")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_unread_count_displayed(self, driver):
        """'안 읽은 알림' 카운트가 표시된다."""
        self._enter_notification()
        text = self.noti.get_unread_text()
        assert "안 읽은 알림" in text, f"안 읽은 알림 텍스트가 표시되어야 한다. 실제: {text}"
        driver.back()

    @allure.story("화면 구성")
    @allure.title("NOTI-003: 모두 읽음 버튼 표시")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_mark_all_read_visible(self, driver):
        """'모두 읽음' 버튼이 표시된다."""
        self._enter_notification()
        assert self.noti.has_mark_all_read(), "'모두 읽음' 버튼이 표시되어야 한다"
        driver.back()

    @allure.story("네비게이션")
    @allure.title("NOTI-004: 뒤로가기로 홈 복귀")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_back_returns_to_home(self, driver):
        """뒤로가기 시 홈 화면으로 돌아간다."""
        self._enter_notification()
        driver.back()
        assert self.home.is_home_visible(), "홈 화면으로 돌아가야 한다"
