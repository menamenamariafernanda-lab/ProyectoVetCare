import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Ruta al archivo HTML principal
HTML_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "main_vetcare.html"
)
FILE_URL = f"file:///{HTML_PATH}"

# ----------------------------------------------------------------------
# Utilidades para interacción lenta (simula comportamiento humano)
# ----------------------------------------------------------------------
def slow_type(driver, by, identifier, text, delay_ms=120):
    """Escribe texto carácter por carácter, limpiando el campo con JS primero."""
    elem = driver.find_element(by, identifier)
    # Limpiar usando JavaScript para eliminar cualquier valor predefinido
    driver.execute_script("arguments[0].value = '';", elem)
    for ch in text:
        elem.send_keys(ch)
        time.sleep(delay_ms / 1000.0)
    time.sleep(0.2)

def slow_click(driver, by, identifier, delay_before=0.4):
    """Hace clic en un elemento después de una pausa."""
    time.sleep(delay_before)
    driver.find_element(by, identifier).click()
    time.sleep(0.2)

# ----------------------------------------------------------------------
# Esperas explícitas para sincronización
# ----------------------------------------------------------------------
def wait_for_login_to_disappear(driver, timeout=10):
    """Espera hasta que la pantalla de login desaparezca por completo."""
    WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((By.ID, "login-page"))
    )

def wait_for_kpi_text(driver, kpi_id, timeout=10):
    """Espera hasta que el KPI deje de mostrar el placeholder '—'."""
    def not_placeholder(d):
        return d.find_element(By.ID, kpi_id).text != "—"
    WebDriverWait(driver, timeout).until(not_placeholder)

# ----------------------------------------------------------------------
# Fixture del navegador (Selenium)
# ----------------------------------------------------------------------
@pytest.fixture
def browser():
    """Inicia una instancia de Chrome, carga la app y la cierra al final."""
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # Descomenta la línea siguiente si no quieres ver la ventana
    # options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(FILE_URL)
    driver.maximize_window()
    yield driver
    driver.quit()
