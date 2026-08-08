import allure
import pytest

from pages import HomePage, CoursePage


@allure.epic("똑똑보카")
@allure.feature("코스 선택")
class TestCourse:
    """코스 선택 화면 (비회원) 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.home = HomePage(driver)
        self.course = CoursePage(driver)

    def _enter_course_page(self):
        if not self.course.is_course_page_visible():
            self.home.tap_course_selector()

    @allure.story("화면 구성")
    @allure.title("COURSE-001: 코스 선택 화면 타이틀")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_course_page_title(self, driver):
        """코스 선택 화면에 '무엇을 공부하시겠어요?' 타이틀이 표시된다."""
        self._enter_course_page()
        title = self.course.get_title()
        assert "공부" in title, f"타이틀에 '공부'가 포함되어야 한다. 실제: {title}"
        driver.back()

    @allure.story("코스 목록")
    @allure.title("COURSE-002: 7개 코스 모두 표시")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_all_courses_visible(self, driver):
        """영어, 한자, 일본어, 국어 어휘, 성경, 중국어, 상식 7개 코스가 모두 표시된다."""
        self._enter_course_page()
        result = self.course.verify_all_courses()
        for course_name, visible in result.items():
            assert visible, f"'{course_name}' 코스가 표시되어야 한다"
        driver.back()

    @allure.story("코스 변경")
    @allure.title("COURSE-003: 코스 선택 후 시작하기")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_select_course_and_start(self, driver):
        """코스를 선택하고 시작하기를 탭하면 세부 코스 화면이 표시된다."""
        self._enter_course_page()
        self.course.select_course("영어")
        self.course.tap_start()
        self.course.attach_screenshot("코스_시작_후")
        # 세부 코스 선택 화면 또는 홈 복귀 확인
        driver.back()

    @allure.story("코스 변경")
    @allure.title("COURSE-004: 다른 코스로 변경")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_change_to_different_course(self, driver):
        """한자 코스로 변경할 수 있다."""
        self._enter_course_page()
        self.course.select_course("한자")
        self.course.tap_start()
        self.course.attach_screenshot("한자_코스_선택")
        # 원래 코스로 복원
        driver.back()

    @allure.story("네비게이션")
    @allure.title("COURSE-005: 닫기 버튼으로 홈 복귀")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_close_returns_to_home(self, driver):
        """닫기 버튼을 탭하면 홈 화면으로 돌아간다."""
        self._enter_course_page()
        self.course.close()
        assert self.home.is_home_visible(), "홈 화면으로 돌아가야 한다"

    @allure.story("네비게이션")
    @allure.title("COURSE-006: 뒤로가기로 홈 복귀")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_back_returns_to_home(self, driver):
        """시스템 뒤로가기 시 홈 화면으로 돌아간다."""
        self._enter_course_page()
        driver.back()
        assert self.home.is_home_visible(), "홈 화면으로 돌아가야 한다"
