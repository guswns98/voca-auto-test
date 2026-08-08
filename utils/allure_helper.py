import allure


def attach_device_info(driver):
    """디바이스 정보를 Allure 리포트에 첨부"""
    try:
        caps = driver.capabilities
        info_lines = [
            f"Platform: {caps.get('platformName', 'N/A')}",
            f"Platform Version: {caps.get('platformVersion', 'N/A')}",
            f"Device: {caps.get('deviceName', 'N/A')}",
            f"Automation: {caps.get('automationName', 'N/A')}",
            f"App Package: {caps.get('appPackage', caps.get('bundleId', 'N/A'))}",
        ]
        allure.attach(
            "\n".join(info_lines),
            name="디바이스 정보",
            attachment_type=allure.attachment_type.TEXT,
        )
    except Exception:
        pass


def attach_page_source(driver, name: str = "page_source"):
    """현재 화면의 page source를 Allure에 첨부 (디버깅용)"""
    try:
        source = driver.page_source
        allure.attach(
            source,
            name=name,
            attachment_type=allure.attachment_type.XML,
        )
    except Exception:
        pass
