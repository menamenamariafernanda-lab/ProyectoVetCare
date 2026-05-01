import pytest, time
from selenium.webdriver.common.by import By
from .conftest import slow_type, slow_click, wait_for_login_to_disappear, wait_for_kpi_text

@pytest.mark.functional
class TestDashboard:
    def _login(self, driver):
        slow_type(driver, By.ID, "login-email", "ivan@vetcare.co", delay_ms=80)
        slow_type(driver, By.ID, "login-password", "Admin1234!", delay_ms=80)
        slow_click(driver, By.XPATH, "//button[contains(text(),'Iniciar sesión')]")
        wait_for_login_to_disappear(driver)

    def test_kpis_despues_de_login(self, browser):
        driver = browser
        self._login(driver)
        wait_for_kpi_text(driver, "kpi-pacientes")
        wait_for_kpi_text(driver, "kpi-citas")
        wait_for_kpi_text(driver, "kpi-ingresos")
        assert driver.find_element(By.ID, "kpi-pacientes").text != "—"
        assert driver.find_element(By.ID, "kpi-citas").text != "—"
        assert driver.find_element(By.ID, "kpi-ingresos").text != "—"
        filas = driver.find_elements(By.CSS_SELECTOR, "#dash-citas-body tr")
        assert len(filas) > 0
