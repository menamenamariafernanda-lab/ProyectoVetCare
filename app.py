import webview
import os

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_vetcare.html")

webview.create_window(
    title="VetCare — Clínica Veterinaria",
    url=f"file:///{html_path}",
    width=1100,
    height=700,
    min_size=(900, 580),
    resizable=True
)

webview.start()
