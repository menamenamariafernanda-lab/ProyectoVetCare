import pytest, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .conftest import slow_type, slow_click, wait_for_login_to_disappear

@pytest.mark.functional
class TestVacunas:
    def _login(self, driver):
        slow_type(driver, By.ID, "login-email", "ivan@vetcare.co", delay_ms=80)
        slow_type(driver, By.ID, "login-password", "Admin1234!", delay_ms=80)
        slow_click(driver, By.XPATH, "//button[contains(text(),'Iniciar sesión')]")
        wait_for_login_to_disappear(driver)

    def test_registrar_vacuna(self, browser):
        driver = browser
        self._login(driver)

        # Ir a Vacunas
        slow_click(driver, By.XPATH, "//div[contains(@class,'nav-item') and contains(.,'Vacunas')]")
        time.sleep(0.4)

        # Abrir modal "+ Registrar vacuna"
        slow_click(driver, By.XPATH, "//button[contains(text(),'+ Registrar vacuna')]")
        time.sleep(0.5)

        # Rellenar campos
        slow_type(driver, By.ID, "f-vac-mascota", "1", 50)
        slow_type(driver, By.ID, "f-vac-vet", "1", 50)
        slow_type(driver, By.ID, "f-vac-tipo", "Rabia", 50)
        # Próxima dosis (campo opcional) – usar JS porque es un input date
        driver.execute_script("document.getElementById('f-vac-prox').value = '2027-05-01'")

        # Clic en "Registrar" dentro del modal
        slow_click(driver, By.XPATH, "//div[contains(@class,'modal-footer')]//button[contains(text(),'Registrar')]")
        time.sleep(0.3)

        # Verificar toast de éxito
        assert "Vacuna registrada" in driver.find_element(By.ID, "toast").text

        # Recargar tabla
        driver.execute_script("loadVacunas();")
        time.sleep(0.5)

        # Verificar que aparece la vacuna en la tabla
        tabla = driver.find_element(By.ID, "tabla-vacunas")
        assert "Rabia" in tabla.text, "La vacuna registrada no aparece en la tabla"
