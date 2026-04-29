"""
╔══════════════════════════════════════════════════════════════════╗
║         CLÍNICA VETERINARIA VETCARE — MAIN GUI                  ║
║  Interfaz gráfica centralizada para todos los módulos           ║
║  Requiere: sprint1..4_vetcare.py en el mismo directorio         ║
╚══════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
import sys
from datetime import date, datetime

# ─── Importar todos los módulos de los sprints ───────────────────
sys.path.insert(0, os.path.dirname(__file__))

from sprint1_vetcare import (
    inicializar_bd, get_connection,
    GestionPacientes, HistorialClinico, GestionCitas
)
from sprint2_vetcare import ampliar_bd_sprint2, GestionDiagnosticos
from sprint3_vetcare import ampliar_bd_sprint3, GestionInventario
from sprint4_vetcare import (
    ampliar_bd_sprint4, GestionUsuarios,
    GestionFacturacion, GestionReportes
)

# ─── Instancias globales ──────────────────────────────────────────
gp  = GestionPacientes()
hc  = HistorialClinico()
gc  = GestionCitas()
gd  = GestionDiagnosticos()
gi  = GestionInventario()
gu  = GestionUsuarios()
gf  = GestionFacturacion()
gr  = GestionReportes()

USUARIO_ACTIVO = {"data": None}

# ─── Colores y fuentes ────────────────────────────────────────────
PALETTE = {
    "bg":       "#F8F7F4",
    "sidebar":  "#1C1C1E",
    "sidebar_h":"#2C2C2E",
    "accent":   "#0F6E56",
    "accent_l": "#1D9E75",
    "danger":   "#D85A30",
    "text":     "#1C1C1E",
    "text_m":   "#5F5E5A",
    "card":     "#FFFFFF",
    "border":   "#D3D1C7",
    "success":  "#3B6D11",
    "warning":  "#BA7517",
}

FONT_H1   = ("Helvetica", 18, "bold")
FONT_H2   = ("Helvetica", 13, "bold")
FONT_BODY = ("Helvetica", 11)
FONT_SM   = ("Helvetica", 10)
FONT_MONO = ("Courier", 10)


# ═══════════════════════════════════════════════════════════════════
#  HELPERS DE UI
# ═══════════════════════════════════════════════════════════════════

def card_frame(parent, **kwargs):
    f = tk.Frame(parent, bg=PALETTE["card"],
                 relief="flat", bd=0, **kwargs)
    f.configure(highlightbackground=PALETTE["border"],
                highlightthickness=1)
    return f

def label(parent, text, font=FONT_BODY, color=None, **kwargs):
    return tk.Label(parent, text=text, font=font,
                    bg=parent["bg"],
                    fg=color or PALETTE["text"], **kwargs)

def entry(parent, width=28, **kwargs):
    e = tk.Entry(parent, font=FONT_BODY, width=width,
                 relief="flat", bd=1,
                 bg="#F1EFE8", fg=PALETTE["text"],
                 insertbackground=PALETTE["text"], **kwargs)
    e.configure(highlightbackground=PALETTE["border"],
                highlightthickness=1)
    return e

def btn(parent, text, cmd, color=None, **kwargs):
    bg = color or PALETTE["accent"]
    b = tk.Button(parent, text=text, command=cmd,
                  font=FONT_SM, bg=bg, fg="#FFFFFF",
                  relief="flat", bd=0,
                  activebackground=PALETTE["accent_l"],
                  activeforeground="#FFFFFF",
                  padx=12, pady=6, cursor="hand2", **kwargs)
    return b

def btn_ghost(parent, text, cmd, **kwargs):
    b = tk.Button(parent, text=text, command=cmd,
                  font=FONT_SM, bg=PALETTE["bg"],
                  fg=PALETTE["text_m"],
                  relief="flat", bd=0,
                  activebackground=PALETTE["border"],
                  padx=12, pady=6, cursor="hand2", **kwargs)
    return b

def tabla(parent, cols, height=12):
    style = ttk.Style()
    style.configure("VetCare.Treeview",
                    font=FONT_SM, rowheight=26,
                    background=PALETTE["card"],
                    foreground=PALETTE["text"],
                    fieldbackground=PALETTE["card"])
    style.configure("VetCare.Treeview.Heading",
                    font=("Helvetica", 10, "bold"),
                    background=PALETTE["bg"],
                    foreground=PALETTE["text_m"])
    style.map("VetCare.Treeview",
              background=[("selected", PALETTE["accent"])],
              foreground=[("selected", "#FFFFFF")])

    tree = ttk.Treeview(parent, columns=cols, show="headings",
                        style="VetCare.Treeview", height=height)
    for c in cols:
        tree.heading(c, text=c.replace("_", " ").title())
        tree.column(c, width=110, anchor="w")

    sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return tree

def fill_tree(tree, rows: list):
    tree.delete(*tree.get_children())
    for r in rows:
        vals = list(r.values()) if isinstance(r, dict) else r
        tree.insert("", "end", values=vals)

def separador(parent):
    tk.Frame(parent, bg=PALETTE["border"], height=1).pack(
        fill="x", padx=0, pady=8)


# ═══════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════

class VetCareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VetCare — Sistema Clínica Veterinaria")
        self.geometry("1100x700")
        self.minsize(900, 580)
        self.configure(bg=PALETTE["bg"])
        self._init_bd()
        self._build_ui()
        self._mostrar_panel("dashboard")

    def _init_bd(self):
        inicializar_bd()
        ampliar_bd_sprint2()
        ampliar_bd_sprint3()
        ampliar_bd_sprint4()

    # ── Layout principal ──────────────────────────────────────────

    def _build_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=PALETTE["sidebar"], width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        tk.Label(self.sidebar, text="🐾 VetCare",
                 font=("Helvetica", 15, "bold"),
                 bg=PALETTE["sidebar"], fg="#FFFFFF",
                 pady=20).pack(fill="x", padx=18)

        tk.Frame(self.sidebar, bg="#3C3C3E", height=1).pack(
            fill="x", padx=16, pady=4)

        self._nav_items = {}
        nav = [
            ("dashboard",   "📊  Panel General"),
            ("pacientes",   "🐶  Pacientes"),
            ("citas",       "📅  Citas"),
            ("historial",   "📋  Historial Clínico"),
            ("inventario",  "💊  Inventario"),
            ("facturacion", "🧾  Facturación"),
            ("reportes",    "📈  Reportes"),
            ("usuarios",    "👤  Usuarios"),
        ]
        for key, label_txt in nav:
            b = tk.Button(self.sidebar, text=label_txt,
                          font=FONT_SM, anchor="w",
                          bg=PALETTE["sidebar"],
                          fg="#ADADAD",
                          activebackground=PALETTE["sidebar_h"],
                          activeforeground="#FFFFFF",
                          relief="flat", bd=0,
                          padx=20, pady=10, cursor="hand2",
                          command=lambda k=key: self._mostrar_panel(k))
            b.pack(fill="x")
            self._nav_items[key] = b

        # Área de contenido
        self.content = tk.Frame(self, bg=PALETTE["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        # Barra superior
        self.topbar = tk.Frame(self.content, bg=PALETTE["card"],
                               height=48)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)
        self.topbar.configure(highlightbackground=PALETTE["border"],
                              highlightthickness=1)

        self.lbl_titulo = tk.Label(self.topbar, text="Panel General",
                                   font=FONT_H2, bg=PALETTE["card"],
                                   fg=PALETTE["text"])
        self.lbl_titulo.pack(side="left", padx=20)

        self.lbl_usuario = tk.Label(self.topbar, text="Sin sesión",
                                    font=FONT_SM, bg=PALETTE["card"],
                                    fg=PALETTE["text_m"])
        self.lbl_usuario.pack(side="right", padx=20)

        # Panel de páginas
        self.main_frame = tk.Frame(self.content, bg=PALETTE["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=16)

        self._paginas = {}
        self._pagina_activa = None

    def _mostrar_panel(self, key: str):
        # Resaltar nav
        for k, b in self._nav_items.items():
            b.configure(bg=PALETTE["sidebar_h"] if k == key
                        else PALETTE["sidebar"],
                        fg="#FFFFFF" if k == key else "#ADADAD")

        titulos = {
            "dashboard":   "Panel General",
            "pacientes":   "Gestión de Pacientes",
            "citas":       "Gestión de Citas",
            "historial":   "Historial Clínico",
            "inventario":  "Inventario",
            "facturacion": "Facturación",
            "reportes":    "Reportes",
            "usuarios":    "Usuarios y Roles",
        }
        self.lbl_titulo.configure(text=titulos.get(key, key))

        # Destruir página anterior
        for w in self.main_frame.winfo_children():
            w.destroy()

        paginas = {
            "dashboard":   PanelDashboard,
            "pacientes":   PanelPacientes,
            "citas":       PanelCitas,
            "historial":   PanelHistorial,
            "inventario":  PanelInventario,
            "facturacion": PanelFacturacion,
            "reportes":    PanelReportes,
            "usuarios":    PanelUsuarios,
        }
        cls = paginas.get(key)
        if cls:
            cls(self.main_frame, self)

    def set_usuario(self, u):
        USUARIO_ACTIVO["data"] = u
        txt = f"{u['nombre']}  ·  {u['rol']}" if u else "Sin sesión"
        self.lbl_usuario.configure(text=txt)


# ═══════════════════════════════════════════════════════════════════
#  PANEL: DASHBOARD
# ═══════════════════════════════════════════════════════════════════

class PanelDashboard(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=PALETTE["bg"])
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        try:
            kpis = gr.panel_gerente()
        except Exception:
            kpis = {}

        cards_data = [
            ("Pacientes",           kpis.get("total_pacientes", 0),    PALETTE["accent"]),
            ("Citas hoy",           kpis.get("citas_hoy", 0),          "#185FA5"),
            ("Ingresos del mes",    f"${kpis.get('ingresos_mes',0):,.0f}", "#854F0B"),
            ("Stock bajo",          kpis.get("productos_stock_bajo", 0), PALETTE["danger"]),
            ("Facturas pendientes", kpis.get("facturas_pendientes", 0), "#993556"),
        ]

        label(self, "Resumen del sistema",
              font=FONT_H2, color=PALETTE["text_m"]).pack(
            anchor="w", pady=(0, 12))

        row = tk.Frame(self, bg=PALETTE["bg"])
        row.pack(fill="x")

        for titulo, valor, color in cards_data:
            c = card_frame(row)
            c.pack(side="left", padx=(0, 12), ipadx=12, ipady=10)
            tk.Label(c, text=str(valor),
                     font=("Helvetica", 22, "bold"),
                     bg=PALETTE["card"], fg=color).pack(anchor="w",
                                                         padx=16, pady=(12, 2))
            tk.Label(c, text=titulo, font=FONT_SM,
                     bg=PALETTE["card"],
                     fg=PALETTE["text_m"]).pack(anchor="w",
                                                padx=16, pady=(0, 12))

        separador(self)

        # Agenda del día
        label(self, f"Agenda de hoy  —  {date.today().isoformat()}",
              font=FONT_H2).pack(anchor="w", pady=(0, 8))

        frame_tabla = tk.Frame(self, bg=PALETTE["bg"])
        frame_tabla.pack(fill="both", expand=True)

        cols = ["id", "hora", "mascota", "especie", "dueno",
                "veterinario", "motivo", "estado"]
        t = tabla(frame_tabla, cols, height=10)
        citas = gc.agenda_del_dia(date.today().isoformat())
        fill_tree(t, citas)


# ═══════════════════════════════════════════════════════════════════
#  PANEL: PACIENTES
# ═══════════════════════════════════════════════════════════════════

class PanelPacientes(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=PALETTE["bg"])
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        # Barra de acciones
        bar = tk.Frame(self, bg=PALETTE["bg"])
        bar.pack(fill="x", pady=(0, 10))

        self.busq = entry(bar, width=24)
        self.busq.insert(0, "Buscar mascota o dueño...")
        self.busq.pack(side="left", padx=(0, 8))
        btn(bar, "Buscar", self._buscar).pack(side="left", padx=(0, 8))
        btn(bar, "+ Nueva mascota", self._nueva_mascota).pack(side="left", padx=(0, 8))
        btn(bar, "+ Nuevo dueño", self._nuevo_dueno,
            color="#185FA5").pack(side="left")
        btn_ghost(bar, "Listar todos", self._listar).pack(side="right")

        # Tabla
        frame_t = tk.Frame(self, bg=PALETTE["bg"])
        frame_t.pack(fill="both", expand=True)
        cols = ["id", "nombre", "especie", "raza", "edad", "peso", "dueno"]
        self.tree = tabla(frame_t, cols)
        self._listar()

    def _listar(self):
        fill_tree(self.tree, gp.listar_mascotas())

    def _buscar(self):
        t = self.busq.get().strip()
        if t and t != "Buscar mascota o dueño...":
            fill_tree(self.tree, gp.buscar_mascota(t))

    def _nueva_mascota(self):
        dlg = FormDialog(self, "Registrar mascota", [
            ("Nombre", ""), ("Especie", ""), ("Raza", ""),
            ("Edad (años)", ""), ("Peso (kg)", ""), ("ID del dueño", "")
        ])
        self.wait_window(dlg)
        if dlg.resultado:
            n, esp, raza, edad, peso, did = dlg.resultado
            try:
                gp.registrar_mascota(n, esp, int(did),
                                     raza, float(edad or 0),
                                     float(peso or 0))
                self._listar()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _nuevo_dueno(self):
        dlg = FormDialog(self, "Registrar dueño", [
            ("Nombre", ""), ("Teléfono", ""),
            ("Correo", ""), ("Dirección", "")
        ])
        self.wait_window(dlg)
        if dlg.resultado:
            n, tel, correo, dir_ = dlg.resultado
            gp.registrar_dueno(n, tel, correo, dir_)
            messagebox.showinfo("OK", f"Dueño '{n}' registrado.")


# ═══════════════════════════════════════════════════════════════════
#  PANEL: CITAS
# ═══════════════════════════════════════════════════════════════════

class PanelCitas(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=PALETTE["bg"])
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        bar = tk.Frame(self, bg=PALETTE["bg"])
        bar.pack(fill="x", pady=(0, 10))

        label(bar, "Fecha:").pack(side="left", padx=(0, 4))
        self.fecha_var = tk.StringVar(value=date.today().isoformat())
        entry_f = entry(bar, width=14, textvariable=self.fecha_var)
        entry_f.pack(side="left", padx=(0, 8))
        btn(bar, "Ver agenda", self._ver_agenda).pack(side="left", padx=(0, 8))
        btn(bar, "+ Agendar cita", self._agendar).pack(side="left", padx=(0, 8))
        btn(bar, "Cancelar seleccionada", self._cancelar,
            color=PALETTE["danger"]).pack(side="left", padx=(0, 8))
        btn_ghost(bar, "Ver todas", self._ver_todas).pack(side="right")

        frame_t = tk.Frame(self, bg=PALETTE["bg"])
        frame_t.pack(fill="both", expand=True)
        cols = ["id", "fecha", "hora", "mascota",
                "dueno", "veterinario", "motivo", "estado"]
        self.tree = tabla(frame_t, cols)
        self._ver_agenda()

    def _ver_agenda(self):
        fill_tree(self.tree, gc.agenda_del_dia(self.fecha_var.get()))

    def _ver_todas(self):
        fill_tree(self.tree, gc.buscar_citas())

    def _agendar(self):
        dlg = FormDialog(self, "Agendar cita", [
            ("ID mascota", ""), ("ID veterinario", ""),
            ("Fecha (YYYY-MM-DD)", ""), ("Hora (HH:MM)", ""),
            ("Motivo", "")
        ])
        self.wait_window(dlg)
        if dlg.resultado:
            mid, vid, fecha, hora, motivo = dlg.resultado
            try:
                gc.agendar_cita(int(mid), int(vid), fecha, hora, motivo)
                self._ver_todas()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _cancelar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una cita.")
            return
        cid = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Cancelar cita ID {cid}?"):
            gc.cancelar_cita(int(cid))
            self._ver_todas()


# ═══════════════════════════════════════════════════════════════════
#  PANEL: HISTORIAL CLÍNICO
# ═══════════════════════════════════════════════════════════════════

class PanelHistorial(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=PALETTE["bg"])
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        bar = tk.Frame(self, bg=PALETTE["bg"])
        bar.pack(fill="x", pady=(0, 10))

        label(bar, "ID Mascota:").pack(side="left", padx=(0, 4))
        self.mid = entry(bar, width=8)
        self.mid.pack(side="left", padx=(0, 8))
        btn(bar, "Ver historial", self._ver_historial).pack(side="left", padx=(0, 8))
        btn(bar, "Ver vacunas", self._ver_vacunas).pack(side="left", padx=(0, 8))
        btn(bar, "+ Registrar consulta", self._registrar).pack(side="left", padx=(0, 8))
        btn(bar, "+ Registrar vacuna", self._reg_vacuna,
            color="#185FA5").pack(side="left")

        frame_t = tk.Frame(self, bg=PALETTE["bg"])
        frame_t.pack(fill="both", expand=True)
        self.cols_h = ["id", "fecha", "diagnostico",
                       "tratamiento", "observaciones"]
        self.tree = tabla(frame_t, self.cols_h)

    def _ver_historial(self):
        mid = self.mid.get().strip()
        if not mid:
            return
        rows = hc.consultar_historial(int(mid))
        for c in self.cols_h:
            self.tree.heading(c, text=c.replace("_", " ").title())
        fill_tree(self.tree, rows)

    def _ver_vacunas(self):
        mid = self.mid.get().strip()
        if not mid:
            return
        rows = hc.consultar_vacunas(int(mid))
        for c in ["id", "tipo_vacuna", "fecha_aplicacion", "proxima_dosis"]:
            self.tree.heading(c, text=c.replace("_", " ").title())
        fill_tree(self.tree, rows)

    def _registrar(self):
        dlg = FormDialog(self, "Registrar consulta", [
            ("ID mascota", ""), ("ID veterinario", ""),
            ("Diagnóstico", ""), ("Tratamiento", ""),
            ("Observaciones", "")
        ])
        self.wait_window(dlg)
        if dlg.resultado:
            mid, vid, diag, trat, obs = dlg.resultado
            hc.registrar_consulta(int(mid), int(vid), diag, trat, obs)
            self._ver_historial()

    def _reg_vacuna(self):
        dlg = FormDialog(self, "Registrar vacuna", [
            ("ID mascota", ""), ("ID veterinario", ""),
            ("Tipo de vacuna", ""), ("Próxima dosis (YYYY-MM-DD)", "")
        ])
        self.wait_window(dlg)
        if dlg.resultado:
            mid, vid, tipo, proxima = dlg.resultado
            hc.registrar_vacuna(int(mid), int(vid), tipo, proxima)
            messagebox.showinfo("OK", "Vacuna registrada.")


# ═══════════════════════════════════════════════════════════════════
#  PANEL: INVENTARIO
# ═══════════════════════════════════════════════════════════════════

class PanelInventario(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=PALETTE["bg"])
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        bar = tk.Frame(self, bg=PALETTE["bg"])
        bar.pack(fill="x", pady=(0, 10))

        btn(bar, "Listar todos", self._listar).pack(side="left", padx=(0, 8))
        btn(bar, "Stock bajo / alertas",
            self._alertas, color=PALETTE["warning"]).pack(side="left", padx=(0, 8))
        btn(bar, "+ Agregar producto",
            self._nuevo_producto).pack(side="left", padx=(0, 8))

        label(bar, "Mov. producto ID:").pack(side="left", padx=(8, 4))
        self.prod_id = entry(bar, width=6)
        self.prod_id.pack(side="left", padx=(0, 4))
        label(bar, "Cant:").pack(side="left", padx=(0, 4))
        self.cant = entry(bar, width=5)
        self.cant.pack(side="left", padx=(0, 4))
        btn(bar, "Entrada", lambda: self._movimiento("entrada"),
            color=PALETTE["success"]).pack(side="left", padx=(0, 4))
        btn(bar, "Salida", lambda: self._movimiento("salida"),
            color=PALETTE["danger"]).pack(side="left")

        frame_t = tk.Frame(self, bg=PALETTE["bg"])
        frame_t.pack(fill="both", expand=True)
        cols = ["id", "codigo", "nombre", "categoria",
                "stock_actual", "stock_minimo", "precio_venta",
                "fecha_vencimiento"]
        self.tree = tabla(frame_t, cols)
        self._listar()

    def _listar(self):
        fill_tree(self.tree, gi.listar_productos())

    def _alertas(self):
        alertas = gi.alertas_activas()
        if not alertas:
            messagebox.showinfo("Sin alertas", "No hay alertas activas.")
            return
        txt = "\n".join(f"• {a.get('mensaje', a)}" for a in alertas)
        messagebox.showwarning("Alertas de inventario", txt)

    def _nuevo_producto(self):
        dlg = FormDialog(self, "Agregar producto", [
            ("Código", ""), ("Nombre", ""),
            ("Categoría (medicamento/insumo/alimento)", ""),
            ("Precio compra", ""), ("Precio venta", ""),
            ("Stock inicial", ""), ("Stock mínimo", "5"),
            ("Unidad", "unidad"), ("Vencimiento (YYYY-MM-DD)", "")
        ])
        self.wait_window(dlg)
        if dlg.resultado:
            cod, nom, cat, pc, pv, si, smin, uni, venc = dlg.resultado
            gi.agregar_producto(cod, nom, cat, float(pc), float(pv),
                                int(si), int(smin or 5), uni, "", venc)
            self._listar()

    def _movimiento(self, tipo: str):
        pid = self.prod_id.get().strip()
        cant = self.cant.get().strip()
        if not pid or not cant:
            messagebox.showwarning("Aviso", "Ingresa ID de producto y cantidad.")
            return
        if tipo == "entrada":
            gi.registrar_entrada(int(pid), int(cant), "Reposición manual")
        else:
            gi.registrar_salida(int(pid), int(cant), "Consumo manual")
        self._listar()


# ═══════════════════════════════════════════════════════════════════
#  PANEL: FACTURACIÓN
# ═══════════════════════════════════════════════════════════════════

class PanelFacturacion(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=PALETTE["bg"])
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        bar = tk.Frame(self, bg=PALETTE["bg"])
        bar.pack(fill="x", pady=(0, 10))

        btn(bar, "Listar facturas", self._listar).pack(side="left", padx=(0, 8))
        btn(bar, "Pendientes",
            lambda: self._listar("Pendiente"),
            color=PALETTE["warning"]).pack(side="left", padx=(0, 8))
        btn(bar, "+ Nueva factura", self._nueva).pack(side="left", padx=(0, 8))
        btn(bar, "Registrar pago", self._pago,
            color=PALETTE["success"]).pack(side="left", padx=(0, 8))
        label(bar, "  Ver ID:").pack(side="left", padx=(8, 4))
        self.fid = entry(bar, width=6)
        self.fid.pack(side="left", padx=(0, 4))
        btn_ghost(bar, "Detalle", self._ver_detalle).pack(side="left")

        frame_t = tk.Frame(self, bg=PALETTE["bg"])
        frame_t.pack(fill="both", expand=True)
        cols = ["id", "numero", "cliente", "fecha",
                "total", "metodo_pago", "estado"]
        self.tree = tabla(frame_t, cols)
        self._listar()

    def _listar(self, estado=""):
        fill_tree(self.tree, gf.buscar_facturas(estado=estado))

    def _nueva(self):
        dlg = FormDialog(self, "Nueva factura", [
            ("ID dueño", ""), ("ID mascota", ""),
            ("Método de pago", "Efectivo"), ("Observaciones", "")
        ])
        self.wait_window(dlg)
        if dlg.resultado:
            did, mid, met, obs = dlg.resultado
            fid = gf.crear_factura(int(did), int(mid) if mid else None,
                                   met, obs)
            # Agregar ítems
            while messagebox.askyesno("Ítem", "¿Agregar un ítem a la factura?"):
                dlg2 = FormDialog(self, "Agregar ítem", [
                    ("Descripción", ""), ("Precio unitario", ""),
                    ("Cantidad", "1"), ("Tipo (servicio/producto)", "servicio")
                ])
                self.wait_window(dlg2)
                if dlg2.resultado:
                    desc, pu, cant, tipo = dlg2.resultado
                    gf.agregar_item(fid, desc, float(pu), int(cant), tipo)
            self._listar()

    def _pago(self):
        sel = self.tree.selection()
        fid = None
        if sel:
            fid = self.tree.item(sel[0])["values"][0]
        else:
            fid = simpledialog.askinteger("Pago", "ID de factura:")
        if fid:
            met = simpledialog.askstring("Método",
                                         "Método de pago:",
                                         initialvalue="Efectivo")
            gf.registrar_pago(int(fid), met or "Efectivo")
            self._listar()

    def _ver_detalle(self):
        fid = self.fid.get().strip()
        if not fid:
            return
        f = gf.ver_factura(int(fid))
        if not f:
            messagebox.showerror("Error", "Factura no encontrada.")
            return
        lines = [
            f"Factura:   {f['numero']}",
            f"Fecha:     {f['fecha']}",
            f"Cliente:   {f['cliente']}",
            f"Mascota:   {f.get('mascota','N/A')}",
            f"Pago:      {f['metodo_pago']}  |  Estado: {f['estado']}",
            "─" * 40,
        ]
        for it in f.get("items", []):
            lines.append(
                f"{it['descripcion'][:28]:<28} x{it['cantidad']}  "
                f"${it['precio_unitario']:,.0f}  =  ${it['subtotal']:,.0f}"
            )
        lines += [
            "─" * 40,
            f"Subtotal:  ${f['subtotal']:,.0f}",
            f"IVA 19%:   ${f['iva']:,.0f}",
            f"TOTAL:     ${f['total']:,.0f}",
        ]
        messagebox.showinfo(f"Factura {f['numero']}", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════
#  PANEL: REPORTES
# ═══════════════════════════════════════════════════════════════════

class PanelReportes(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=PALETTE["bg"])
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        bar = tk.Frame(self, bg=PALETTE["bg"])
        bar.pack(fill="x", pady=(0, 10))

        label(bar, "Desde:").pack(side="left", padx=(0, 4))
        self.desde = entry(bar, width=13)
        self.desde.insert(0, f"{date.today().year}-01-01")
        self.desde.pack(side="left", padx=(0, 8))
        label(bar, "Hasta:").pack(side="left", padx=(0, 4))
        self.hasta = entry(bar, width=13)
        self.hasta.insert(0, date.today().isoformat())
        self.hasta.pack(side="left", padx=(0, 12))

        btn(bar, "Reporte ventas", self._ventas).pack(side="left", padx=(0, 8))
        btn(bar, "Reporte citas", self._citas).pack(side="left", padx=(0, 8))
        btn(bar, "Panel KPIs", self._kpis, color="#185FA5").pack(side="left")

        self.out = tk.Text(self, font=FONT_MONO, bg=PALETTE["card"],
                           fg=PALETTE["text"], relief="flat",
                           wrap="word", state="disabled",
                           highlightbackground=PALETTE["border"],
                           highlightthickness=1)
        self.out.pack(fill="both", expand=True, pady=(12, 0))

    def _escribir(self, txt: str):
        self.out.configure(state="normal")
        self.out.delete("1.0", "end")
        self.out.insert("end", txt)
        self.out.configure(state="disabled")

    def _ventas(self):
        r = gr.reporte_ventas(self.desde.get(), self.hasta.get())
        res = r["resumen"]
        lines = [
            f"  REPORTE DE VENTAS  {r['periodo']}",
            "─" * 52,
            f"  Facturas pagadas  : {res['total_facturas']}",
            f"  Ingresos totales  : ${res['ingresos_totales']:,.0f}",
            f"  IVA recaudado     : ${res['total_iva']:,.0f}",
            f"  Ticket promedio   : ${res['ticket_promedio']:,.0f}",
            "",
            "  Por método de pago:",
        ]
        for m in r["por_metodo_pago"]:
            lines.append(f"    {m['metodo_pago']:<20} {m['cantidad']} facturas   ${m['monto']:,.0f}")
        self._escribir("\n".join(lines))

    def _citas(self):
        r = gr.reporte_citas(self.desde.get(), self.hasta.get())
        lines = [f"  REPORTE DE CITAS  {r['periodo']}", "─" * 52,
                 "  Por estado:"]
        for e in r["por_estado"]:
            lines.append(f"    {e['estado']:<20} {e['cantidad']}")
        lines += ["", "  Por veterinario:"]
        for v in r["por_veterinario"]:
            lines.append(f"    {v['veterinario']:<28} {v['citas']} citas")
        self._escribir("\n".join(lines))

    def _kpis(self):
        k = gr.panel_gerente()
        lines = [
            "  PANEL DE CONTROL — VETCARE",
            "─" * 52,
            f"  Pacientes registrados   : {k['total_pacientes']}",
            f"  Citas hoy               : {k['citas_hoy']}",
            f"  Ingresos del mes        : ${k['ingresos_mes']:,.0f}",
            f"  Productos stock bajo    : {k['productos_stock_bajo']}",
            f"  Facturas pendientes     : {k['facturas_pendientes']}",
            "",
            "  Especies más consultadas:",
        ]
        for e in k.get("top_especies_consultadas", []):
            lines.append(f"    {e['especie']:<20} {e['consultas']} consultas")
        self._escribir("\n".join(lines))


# ═══════════════════════════════════════════════════════════════════
#  PANEL: USUARIOS
# ═══════════════════════════════════════════════════════════════════

class PanelUsuarios(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=PALETTE["bg"])
        self.app = app
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        bar = tk.Frame(self, bg=PALETTE["bg"])
        bar.pack(fill="x", pady=(0, 10))

        btn(bar, "Listar usuarios", self._listar).pack(side="left", padx=(0, 8))
        btn(bar, "+ Registrar", self._registrar).pack(side="left", padx=(0, 8))
        btn(bar, "Iniciar sesión", self._login,
            color="#185FA5").pack(side="left", padx=(0, 8))
        btn(bar, "Cerrar sesión", self._logout,
            color=PALETTE["danger"]).pack(side="left")

        frame_t = tk.Frame(self, bg=PALETTE["bg"])
        frame_t.pack(fill="both", expand=True)
        cols = ["id", "nombre", "correo", "rol", "activo", "created_at"]
        self.tree = tabla(frame_t, cols)
        self._listar()

    def _listar(self):
        fill_tree(self.tree, gu.listar_usuarios())

    def _registrar(self):
        dlg = FormDialog(self, "Registrar usuario", [
            ("Nombre", ""), ("Correo", ""),
            ("Contraseña", ""),
            ("Rol (admin/veterinario/recepcionista/gerente/soporte)", "recepcionista")
        ])
        self.wait_window(dlg)
        if dlg.resultado:
            nom, correo, pwd, rol = dlg.resultado
            gu.registrar_usuario(nom, correo, pwd, rol)
            self._listar()

    def _login(self):
        correo = simpledialog.askstring("Login", "Correo:")
        if not correo:
            return
        pwd = simpledialog.askstring("Login", "Contraseña:", show="*")
        if not pwd:
            return
        u = gu.autenticar(correo, pwd)
        if u:
            self.app.set_usuario(u)
            messagebox.showinfo("Bienvenido",
                                f"Sesión iniciada como {u['nombre']} ({u['rol']})")
        else:
            messagebox.showerror("Error", "Credenciales incorrectas.")

    def _logout(self):
        self.app.set_usuario(None)
        messagebox.showinfo("Sesión", "Sesión cerrada.")


# ═══════════════════════════════════════════════════════════════════
#  DIÁLOGO GENÉRICO DE FORMULARIO
# ═══════════════════════════════════════════════════════════════════

class FormDialog(tk.Toplevel):
    """Ventana modal con campos configurables."""

    def __init__(self, parent, titulo: str, campos: list):
        super().__init__(parent)
        self.title(titulo)
        self.resizable(False, False)
        self.configure(bg=PALETTE["bg"])
        self.resultado = None
        self._entries = []
        self._build(titulo, campos)
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        x = parent.winfo_rootx() + 80
        y = parent.winfo_rooty() + 60
        self.geometry(f"+{x}+{y}")

    def _build(self, titulo, campos):
        tk.Label(self, text=titulo, font=FONT_H2,
                 bg=PALETTE["bg"], fg=PALETTE["text"],
                 pady=12).pack(fill="x", padx=24)

        tk.Frame(self, bg=PALETTE["border"], height=1).pack(
            fill="x", padx=16)

        form = tk.Frame(self, bg=PALETTE["bg"], padx=24, pady=12)
        form.pack(fill="x")

        for lbl, default in campos:
            row = tk.Frame(form, bg=PALETTE["bg"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=lbl, font=FONT_SM, width=38,
                     anchor="w", bg=PALETTE["bg"],
                     fg=PALETTE["text_m"]).pack(side="left")
            e = entry(row, width=26)
            e.insert(0, default)
            e.pack(side="left")
            self._entries.append(e)

        tk.Frame(self, bg=PALETTE["border"], height=1).pack(
            fill="x", padx=16)

        bbar = tk.Frame(self, bg=PALETTE["bg"], pady=10)
        bbar.pack(fill="x", padx=24)
        btn(bbar, "Guardar", self._guardar).pack(side="right", padx=(8, 0))
        btn_ghost(bbar, "Cancelar", self.destroy).pack(side="right")

    def _guardar(self):
        self.resultado = [e.get().strip() for e in self._entries]
        self.destroy()


# ═══════════════════════════════════════════════════════════════════
#  ENTRADA
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = VetCareApp()
    app.mainloop()
