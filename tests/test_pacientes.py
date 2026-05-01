import pytest, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .conftest import slow_type, slow_click, wait_for_login_to_disappear

@pytest.mark.functional
class TestPacientes:
    def _login(self, driver):
        slow_type(driver, By.ID, "login-email", "ivan@vetcare.co", delay_ms=80)
        slow_type(driver, By.ID, "login-password", "Admin1234!", delay_ms=80)
        slow_click(driver, By.XPATH, "//button[contains(text(),'Iniciar sesión')]")
        wait_for_login_to_disappear(driver)

    def test_crear_mascota(self, browser):
        driver = browser
        self._login(driver)
        slow_click(driver, By.XPATH, "//div[contains(@class,'nav-item') and contains(.,'Pacientes')]")
        time.sleep(0.4)

        # Abrir modal "+ Nueva mascota"
        slow_click(driver, By.XPATH, "//button[contains(text(),'+ Nueva mascota')]")
        time.sleep(0.5)

        # ── Dueño ──
        slow_type(driver, By.ID, "f-dueno-nombre", "Dueño Completo", 50)
        slow_type(driver, By.ID, "f-dueno-tel", "3001234567", 50)
        slow_type(driver, By.ID, "f-dueno-email", "dueno@test.com", 50)
        slow_type(driver, By.ID, "f-dueno-dir", "Calle Falsa 123", 50)

        # ── Mascota ──
        slow_type(driver, By.ID, "f-m-nombre", "Firulais", 50)
        # Seleccionar especie "Gato"
        Select(driver.find_element(By.ID, "f-m-especie")).select_by_visible_text("Gato")
        time.sleep(0.15)
        slow_type(driver, By.ID, "f-m-raza", "Siamés", 50)
        slow_type(driver, By.ID, "f-m-edad", "2", 50)
        slow_type(driver, By.ID, "f-m-peso", "4.5", 50)

        # Registrar
        slow_click(driver, By.XPATH, "//div[contains(@class,'modal-footer')]//button[contains(text(),'Registrar')]")
        time.sleep(0.6)

        assert "Mascota registrada" in driver.find_element(By.ID, "toast").text
        assert "Firulais" in driver.find_element(By.ID, "tabla-mascotas").text
