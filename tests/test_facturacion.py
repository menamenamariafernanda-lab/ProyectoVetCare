import pytest, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .conftest import slow_type, slow_click, wait_for_login_to_disappear

@pytest.mark.functional
class TestFacturacion:
    def _login(self, driver):
        slow_type(driver, By.ID, "login-email", "ivan@vetcare.co", delay_ms=80)
        slow_type(driver, By.ID, "login-password", "Admin1234!", delay_ms=80)
        slow_click(driver, By.XPATH, "//button[contains(text(),'Iniciar sesión')]")
        wait_for_login_to_disappear(driver)

    def test_crear_factura(self, browser):
        driver = browser
        self._login(driver)
        slow_click(driver, By.XPATH, "//div[contains(@class,'nav-item') and contains(.,'Facturación')]")
        time.sleep(0.4)

        slow_click(driver, By.XPATH, "//button[contains(text(),'+ Nueva factura')]")
        time.sleep(0.5)

        # Dueño y mascota
        slow_type(driver, By.ID, "f-fac-dueno", "1", 50)
        slow_type(driver, By.ID, "f-fac-mascota", "1", 50)

        # Método de pago: cambiar a Tarjeta Crédito
        Select(driver.find_element(By.ID, "f-fac-pago")).select_by_visible_text("Tarjeta Crédito")
        time.sleep(0.15)
        slow_type(driver, By.ID, "f-fac-obs", "Prueba automatizada", 50)

        # Ítem por defecto
        slow_type(driver, By.CLASS_NAME, "item-desc", "Consulta general", 50)
        slow_type(driver, By.CLASS_NAME, "item-precio", "50000", 50)

        slow_click(driver, By.XPATH, "//button[contains(text(),'Crear factura')]")
        time.sleep(0.6)

        assert "Factura" in driver.find_element(By.ID, "toast").text
        assert "Pendiente" in driver.find_element(By.ID, "tabla-facturas").text
