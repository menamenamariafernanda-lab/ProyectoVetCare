import pytest, time
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .conftest import slow_type, slow_click, wait_for_login_to_disappear

@pytest.mark.functional
class TestCitas:
    def _login(self, driver):
        slow_type(driver, By.ID, "login-email", "ivan@vetcare.co", delay_ms=80)
        slow_type(driver, By.ID, "login-password", "Admin1234!", delay_ms=80)
        slow_click(driver, By.XPATH, "//button[contains(text(),'Iniciar sesión')]")
        wait_for_login_to_disappear(driver)

    def test_agendar_cita(self, browser):
        driver = browser
        self._login(driver)

        # Ir a Citas
        slow_click(driver, By.XPATH, "//div[contains(@class,'nav-item') and contains(.,'Citas')]")
        time.sleep(0.4)

        # Abrir modal "+ Agendar cita"
        slow_click(driver, By.XPATH, "//button[contains(text(),'+ Agendar cita')]")
        time.sleep(0.5)

        hoy = date.today().isoformat()

        # Rellenar campos obligatorios
        slow_type(driver, By.ID, "f-cita-mascota", "1", 50)
        slow_type(driver, By.ID, "f-cita-vet", "1", 50)

        # --- El campo date no funciona con slow_type, usar JS ---
        driver.execute_script(f"document.getElementById('f-cita-fecha').value = '{hoy}'")
        # Hora también la dejamos fija (ya que el input type="time" puede tener problemas similares)
        driver.execute_script("document.getElementById('f-cita-hora').value = '09:00'")

        # Clic en "Agendar" dentro del modal
        slow_click(driver, By.XPATH, "//div[contains(@class,'modal-footer')]//button[contains(text(),'Agendar')]")
        time.sleep(0.3)

        # Verificar toast de éxito
        assert "Cita agendada correctamente" in driver.find_element(By.ID, "toast").text

        # Esperar a que el modal desaparezca
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "modal-cita"))
        )

        # Limpiar el filtro de fecha para ver todas las citas
        driver.execute_script("document.getElementById('filtro-fecha-cita').value = ''")
        # Disparar el evento onchange para que se recargue la tabla
        driver.execute_script("loadCitas();")
        time.sleep(0.5)

        # Verificar que aparezca "Pendiente" en la tabla (la cita recién creada)
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "tabla-citas"), "Pendiente")
        )
        assert "Pendiente" in driver.find_element(By.ID, "tabla-citas").text
