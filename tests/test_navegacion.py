import time
from selenium.webdriver.common.by import By
from .conftest import slow_type, slow_click

class TestNavegacionSPA:
    def _login(self, driver):
        """Helper para hacer login y acceder al menú."""
        slow_type(driver, By.ID, "login-email", "ivan@vetcare.co")
        slow_type(driver, By.ID, "login-password", "Admin1234!")
        slow_click(driver, By.XPATH, "//button[contains(text(),'Iniciar sesión')]")
        time.sleep(0.8)

    def test_ir_a_pacientes_y_ver_tabla(self, browser):
        driver = browser
        self._login(driver)

        # Hacer clic en el ítem "Pacientes" (usamos su clase .nav-item y el texto)
        pacientes_btn = driver.find_element(By.XPATH, "//div[contains(@class,'nav-item') and contains(.,'Pacientes')]")
        slow_click(driver, By.XPATH, pacientes_btn)
        time.sleep(0.5)

        # Verificar que la página de pacientes esté activa
        page = driver.find_element(By.ID, "page-pacientes")
        assert "active" in page.get_attribute("class"), "La página de pacientes debería estar activa"

        # La tabla debe tener al menos una fila (los datos demo)
        tabla = driver.find_element(By.ID, "tabla-mascotas")
        filas = tabla.find_elements(By.TAG_NAME, "tr")
        # la primera fila es el encabezado
        assert len(filas) > 1, "La tabla de mascotas debería tener registros"

    def test_crear_mascota_desde_modal(self, browser):
        driver = browser
        self._login(driver)

        # Ir a pacientes
        pacientes_btn = driver.find_element(By.XPATH, "//div[contains(@class,'nav-item') and contains(.,'Pacientes')]")
        slow_click(driver, By.XPATH, pacientes_btn)
        time.sleep(0.4)

        # Abrir el modal de nueva mascota
        add_btn = driver.find_element(By.XPATH, "//button[contains(text(),'+ Nueva mascota')]")
        slow_click(driver, By.XPATH, add_btn)
        time.sleep(0.5)

        # Rellenar datos del dueño y mascota
        slow_type(driver, By.ID, "f-dueno-nombre", "Nuevo Dueño", delay_ms=60)
        slow_type(driver, By.ID, "f-m-nombre", "Rex", delay_ms=100)

        # Hacer clic en el botón Registrar del modal
        registrar_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Registrar')]")
        slow_click(driver, By.XPATH, registrar_btn, delay_before=0.3)
        time.sleep(0.6)

        # Verificar que apareció un toast de éxito
        toast = driver.find_element(By.ID, "toast")
        assert "Mascota registrada" in toast.text
        # Verificar que la mascota aparece en la tabla
        tabla = driver.find_element(By.ID, "tabla-mascotas")
        assert "Rex" in tabla.text
