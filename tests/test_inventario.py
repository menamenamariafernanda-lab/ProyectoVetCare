import pytest, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .conftest import slow_type, slow_click, wait_for_login_to_disappear

@pytest.mark.functional
class TestInventario:
    def _login(self, driver):
        slow_type(driver, By.ID, "login-email", "ivan@vetcare.co", delay_ms=80)
        slow_type(driver, By.ID, "login-password", "Admin1234!", delay_ms=80)
        slow_click(driver, By.XPATH, "//button[contains(text(),'Iniciar sesión')]")
        wait_for_login_to_disappear(driver)

    def test_agregar_producto(self, browser):
        driver = browser
        self._login(driver)
        slow_click(driver, By.XPATH, "//div[contains(@class,'nav-item') and contains(.,'Inventario')]")
        time.sleep(0.4)

        slow_click(driver, By.XPATH, "//button[contains(text(),'+ Agregar producto')]")
        time.sleep(0.5)

        # Campos obligatorios
        slow_type(driver, By.ID, "f-p-codigo", "MED-999", 50)
        slow_type(driver, By.ID, "f-p-nombre", "Producto Test", 50)

        # ── Campos opcionales ──
        # Categoría: cambiar a "insumo"
        Select(driver.find_element(By.ID, "f-p-cat")).select_by_visible_text("insumo")
        time.sleep(0.15)
        slow_type(driver, By.ID, "f-p-pc", "1000", 50)
        slow_type(driver, By.ID, "f-p-pv", "2000", 50)
        slow_type(driver, By.ID, "f-p-stock", "100", 50)
        slow_type(driver, By.ID, "f-p-stmin", "10", 50)
        slow_type(driver, By.ID, "f-p-unidad", "caja", 50)
        slow_type(driver, By.ID, "f-p-venc", "2027-12-31", 50)

        slow_click(driver, By.XPATH, "//div[contains(@class,'modal-footer')]//button[contains(text(),'Agregar')]")
        time.sleep(0.6)

        assert "Producto agregado" in driver.find_element(By.ID, "toast").text
        tabla = driver.find_element(By.ID, "tabla-inventario")
        assert "MED-999" in tabla.text
