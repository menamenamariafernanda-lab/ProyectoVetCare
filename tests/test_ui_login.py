import pytest, time
from selenium.webdriver.common.by import By
from .conftest import slow_type, slow_click, wait_for_login_to_disappear

@pytest.mark.functional
class TestReportes:
    def _login(self, driver):
        slow_type(driver, By.ID, "login-email", "ivan@vetcare.co", delay_ms=80)
        slow_type(driver, By.ID, "login-password", "Admin1234!", delay_ms=80)
        slow_click(driver, By.XPATH, "//button[contains(text(),'Iniciar sesión')]")
        wait_for_login_to_disappear(driver)

    def test_carga_de_reportes(self, browser):
        driver = browser
        self._login(driver)
        slow_click(driver, By.XPATH, "//div[contains(@class,'nav-item') and contains(.,'Reportes')]")
        time.sleep(0.8)
        rep_especies = driver.find_element(By.ID, "rep-especies")
        assert len(rep_especies.text.strip()) > 0, "El panel de especies está vacío"
        rep_citas = driver.find_element(By.ID, "rep-citas-estado")
        assert len(rep_citas.text.strip()) > 0, "El panel de citas por estado está vacío"
