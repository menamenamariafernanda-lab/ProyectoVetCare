import pytest, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .conftest import slow_type, slow_click, wait_for_login_to_disappear

@pytest.mark.functional
class TestHistorial:
    def _login(self, driver):
        slow_type(driver, By.ID, "login-email", "ivan@vetcare.co", delay_ms=80)
        slow_type(driver, By.ID, "login-password", "Admin1234!", delay_ms=80)
        slow_click(driver, By.XPATH, "//button[contains(text(),'Iniciar sesión')]")
        wait_for_login_to_disappear(driver)

    def test_registrar_consulta(self, browser):
        driver = browser
        self._login(driver)

        # Ir a Historial clínico
        slow_click(driver, By.XPATH, "//div[contains(@class,'nav-item') and contains(.,'Historial')]")
        time.sleep(0.4)

        # Abrir modal "+ Registrar consulta"
        slow_click(driver, By.XPATH, "//button[contains(text(),'+ Registrar consulta')]")
        time.sleep(0.5)

        # Rellenar campos
        slow_type(driver, By.ID, "f-hc-mascota", "1", 50)
        slow_type(driver, By.ID, "f-hc-vet", "1", 50)
        slow_type(driver, By.ID, "f-hc-diag", "Otitis media aguda", 50)
        slow_type(driver, By.ID, "f-hc-trat", "Antibiótico oral 7 días", 50)
        slow_type(driver, By.ID, "f-hc-obs", "Revisar en 2 semanas", 50)

        # Clic en "Registrar" dentro del modal
        slow_click(driver, By.XPATH, "//div[@id='modal-historial']//div[contains(@class,'modal-footer')]//button[contains(text(),'Registrar')]")
        time.sleep(0.3)

        # Verificar toast de éxito
        assert "Consulta registrada" in driver.find_element(By.ID, "toast").text

        # Esperar a que el modal desaparezca
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "modal-historial"))
        )

        # Forzar recarga de la tabla de historial
        driver.execute_script("loadHistorial();")
        time.sleep(0.5)

        # Verificar que aparezca el diagnóstico en la tabla
        tabla = driver.find_element(By.ID, "tabla-historial")
        assert "Otitis media aguda" in tabla.text, "El diagnóstico no aparece en la tabla"
