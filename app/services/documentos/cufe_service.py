import keyboard
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("https://siigonube.siigo.com")


from selenium.webdriver.support.ui import Select


def llenar_formulario():
    try:
        time.sleep(3)

        inputs = driver.find_elements(By.CSS_SELECTOR, "input[input-type='text']")

        valores = [
            "",
            "ANDRES FELIPE",
            "CLAROS LOPEZ",
            "1061817785",
            "AUX ADMINISTRATIVO",
            "ADMINISTRACION",
        ]

        for i, valor in enumerate(valores):
            if i < len(inputs):
                inputs[i].clear()
                inputs[i].send_keys(valor)

        # CHECKBOX
        try:
            checkbox = driver.find_element(
                By.XPATH,
                "//label[contains(.,'Usar los datos')]/preceding-sibling::input",
            )
            if not checkbox.is_selected():
                checkbox.click()
        except Exception:
            print("Checkbox no encontrado")

        # DROPDOWN
        try:
            tipo_id = driver.find_element(By.XPATH, "//select")
            Select(tipo_id).select_by_visible_text("Cédula de ciudadanía")
        except Exception:
            print("Dropdown no encontrado")

        print("Formulario llenado")

    except Exception as e:
        print("Error:", e)


# hotkey global
keyboard.add_hotkey("|", llenar_formulario)
print("Presiona | para llenar el formulario. Ctrl+C para salir")
keyboard.wait()
