import allure
import pytest

from pages import HomePage


@allure.epic("똑똑보카")
@allure.feature("홈 화면")
class TestHome:
    """홈 화면 (비회원) 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.home = HomePage(driver)

    @allure.story("화면 구성")
    @allure.title("HOME-001: 홈 화면 3개 섹션 표시")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_home_sections_visible(self, driver):
        """홈 화면에 캐시 더 모으기, 캐시 교환하기, 학습하기 섹션이 모두 표시된다."""
        result = self.home.verify_home_screen()
        assert result["캐시_더_모으기"], "'캐시 더 모으기' 섹션이 표시되어야 한다"
        assert result["캐시_교환하기"], "'캐시 교환하기' 섹션이 표시되어야 한다"
        assert result["학습하기"], "'학습하기' 섹션이 표시되어야 한다"

    @allure.story("화면 구성")
    @allure.title("HOME-002: 홈 화면 6개 메뉴 항목 표시")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_home_menu_items(self, driver):
        """홈 화면에 모든 메뉴 항목이 표시된다."""
        result = self.home.verify_menu_items()
        for name, visible in result.items():
            assert visible, f"'{name}' 메뉴가 표시되어야 한다"

    @allure.story("화면 구성")
    @allure.title("HOME-003: 현재 코스명 표시")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_current_course_displayed(self, driver):
        """좌상단에 현재 선택된 코스명(영어)이 표시된다."""
        course = self.home.get_current_course()
        assert len(course) > 0, "코스명이 표시되어야 한다"
        self.home.attach_screenshot("현재_코스명")

    @allure.story("화면 구성")
    @allure.title("HOME-004: 광고 배너 표시")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_ad_banner_visible(self, driver):
        """하단에 광고 배너가 표시된다."""
        assert self.home.has_ad_banner(), "광고 배너가 표시되어야 한다"

    @allure.story("네비게이션")
    @allure.title("HOME-005: 코스 선택 화면 진입")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_navigate_to_course_selection(self, driver):
        """좌상단 코스명 탭 시 코스 선택 화면으로 이동한다."""
        from pages import CoursePage
        self.home.tap_course_selector()
        course_page = CoursePage(driver)
        assert course_page.is_course_page_visible(), "코스 선택 화면이 표시되어야 한다"
        course_page.attach_screenshot("코스_선택_진입")
        driver.back()

    @allure.story("네비게이션")
    @allure.title("HOME-006: 알림 화면 진입")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_navigate_to_notification(self, driver):
        """우상단 알림 아이콘 탭 시 알림 화면으로 이동한다."""
        from pages import NotificationPage
        self.home.tap_notification()
        noti_page = NotificationPage(driver)
        assert noti_page.is_notification_visible(), "알림 화면이 표시되어야 한다"
        noti_page.attach_screenshot("알림_화면_진입")
        driver.back()

    @allure.story("비회원 제한")
    @allure.title("HOME-007: 비회원 학습미션 탭 시 코스 선택 리다이렉트")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_guest_mission_redirects_to_course(self, driver):
        """비회원이 학습미션을 탭하면 코스 선택 화면으로 이동한다."""
        from pages import CoursePage
        self.home.tap_daily_mission()
        course_page = CoursePage(driver)
        assert course_page.is_course_page_visible(), "비회원은 코스 선택 화면으로 리다이렉트되어야 한다"
        course_page.attach_screenshot("비회원_학습미션_리다이렉트")
        driver.back()

    @allure.story("비회원 제한")
    @allure.title("HOME-008: 비회원 기프티콘 탭 시 코스 선택 리다이렉트")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_guest_gifticon_redirects_to_course(self, driver):
        """비회원이 기프티콘을 탭하면 코스 선택 화면으로 이동한다."""
        from pages import CoursePage
        self.home.tap_gifticon()
        course_page = CoursePage(driver)
        assert course_page.is_course_page_visible(), "비회원은 코스 선택 화면으로 리다이렉트되어야 한다"
        driver.back()
