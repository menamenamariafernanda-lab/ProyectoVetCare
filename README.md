<<<<<<< HEAD
# 🐾 VetCare — Sistema de Gestión para Clínica Veterinaria

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-36%2F36%20PASS-28A745?style=flat-square&logo=checkmarx&logoColor=white)
![Scrum](https://img.shields.io/badge/Metodología-Scrum-FF6D00?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Version](https://img.shields.io/badge/Versión-1.0.0-blue?style=flat-square)

> Sistema de información integral para la gestión clínica y administrativa de la **Clínica Veterinaria VetCare**. Desarrollado con metodología Scrum en 4 sprints — Ingeniería de Software III, FIS Tech & Engineering, 2026.

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Módulos del sistema](#-módulos-del-sistema)
- [Tecnologías](#-tecnologías)
- [Instalación rápida](#-instalación-rápida)
- [Ejecución](#-ejecución)
- [Pruebas](#-pruebas-automatizadas)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Equipo](#-equipo)
- [Documentación](#-documentación)
- [Licencia](#-licencia)

---

## 📌 Descripción

VetCare automatiza los procesos clave de una clínica veterinaria que anteriormente se manejaban en papel o en hojas de cálculo dispersas:

| Problema anterior | Solución implementada |
|---|---|
| Pérdida de citas y horarios duplicados | Agendamiento con validación automática de duplicados |
| Desorganización en historiales clínicos | Historial digital por mascota con diagnósticos y tratamientos |
| Falta de control de medicamentos | Inventario con alertas de stock bajo y vencimiento |
| Sin facturación sistemática | Facturas electrónicas con IVA 19% automático |
| Sin datos para decisiones gerenciales | Panel de KPIs y reportes exportables |

---

## 🧩 Módulos del sistema

```
VetCare v1.0.0
├── M01 — Gestión de Pacientes      (mascotas + dueños, búsqueda avanzada)
├── M02 — Historial Clínico         (diagnósticos, tratamientos, evolución)
├── M03 — Gestión de Citas          (agendamiento, reprogramación, cancelación)
├── M04 — Vacunas                   (registro, alertas de próxima dosis)
├── M05 — Cirugías                  (registro quirúrgico + postoperatorio)
├── M06 — Inventario                (productos, stock, movimientos, alertas)
├── M07 — Facturación               (facturas con IVA, pagos, búsqueda)
├── M08 — Reportes                  (ventas, citas, panel gerencial, JSON)
└── M09 — Usuarios y Roles          (auth SHA-256, roles, recuperación clave)
```

---

## 🛠 Tecnologías

| Componente | Tecnología | Versión |
|---|---|---|
| Lenguaje principal | Python | 3.11+ |
| Base de datos | SQLite3 | Incluido en Python |
| Hashing de contraseñas | hashlib (SHA-256) | Incluido en Python |
| Tokens seguros | secrets | Incluido en Python |
| Exportación de datos | json | Incluido en Python |
| Manejo de fechas | datetime, date | Incluido en Python |
| Generación de docs | Node.js + docx@9.6.1 | 18+ LTS |

> **Sin dependencias externas de Python** — corre en cualquier entorno con Python 3.11+ estándar.

---

## ⚡ Instalación rápida

### Prerequisitos
- Python 3.11 o superior
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/FISTech/vetcare-sistema.git
cd vetcare-sistema

# 2. (Opcional pero recomendado) Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Verificar dependencias (todas son stdlib)
python -c "import sqlite3, hashlib, secrets, json, datetime; print('✅ OK')"
```

---

## ▶ Ejecución

Los 4 sprints deben ejecutarse **en orden secuencial**. Cada uno extiende la base de datos del anterior:

```bash
python sprint1_vetcare.py   # Pacientes, Historial, Citas
python sprint2_vetcare.py   # Diagnósticos, Vacunas, Modificar citas
python sprint3_vetcare.py   # Inventario completo
python sprint4_vetcare.py   # Facturación, Reportes, Usuarios
```

> ⚠️ Para una demo limpia, elimine `vetcare.db` antes de ejecutar:
> ```bash
> rm vetcare.db && python sprint1_vetcare.py
> ```

### Salida esperada

```
════════════════════════════════════════════════════════════
  VETCARE - SPRINT 1 DEMO
════════════════════════════════════════════════════════════
✅ Base de datos inicializada correctamente.
✅ Dueño 'Carlos Ramírez' registrado con ID 1.
✅ Mascota 'Firulais' registrada con ID 1.
✅ Cita agendada con ID 1 para el 2026-04-20 a las 09:00.
❌ El veterinario ya tiene una cita el 2026-04-20 a las 09:00.
...
```

---

## 🧪 Pruebas Automatizadas

```bash
python test_vetcare.py
```

**Resultado esperado:**

```
============================================================
  VETCARE — SUITE DE PRUEBAS AUTOMATIZADAS
============================================================
── Módulo: Pacientes
  ✅ PASS  CP001 registrar_dueno valido
  ✅ PASS  CP002 registrar_mascota valida
  ...
── Módulo: Facturación
  ✅ PASS  CP031 calculo IVA correcto
  ✅ PASS  CP034 numeracion facturas unica

============================================================
  Resultados: 36/36 PASS  |  0 FAIL
  Cobertura ejecutada: 100%
============================================================
```

### Casos de prueba por módulo

| Módulo | Casos | Estado |
|---|---|---|
| Pacientes | CP001–CP009 | ✅ 9/9 PASS |
| Citas | CP010–CP015 | ✅ 6/6 PASS |
| Historial Clínico | CP016–CP018 | ✅ 3/3 PASS |
| Inventario | CP019–CP025 | ✅ 7/7 PASS |
| Usuarios y Roles | CP026–CP033 | ✅ 8/8 PASS |
| Facturación | CP034–CP037 | ✅ 4/4 PASS |
| Reportes | CP038–CP040 | ✅ 3/3 PASS |
| **Total** | **36** | **✅ 100% PASS** |

---

## 📁 Estructura del proyecto

```
vetcare-sistema/
│
├── sprint1_vetcare.py          # M01 Pacientes · M02 Historial · M03 Citas
├── sprint2_vetcare.py          # M04 Diagnósticos · M05 Vacunas · M06 Citas avanzadas
├── sprint3_vetcare.py          # M07 Inventario completo
├── sprint4_vetcare.py          # M08 Facturación · M09 Reportes · M10 Usuarios
├── test_vetcare.py             # Suite de 36 pruebas automatizadas (patrón AAA)
│
├── vetcare.db                  # Base de datos SQLite (generada al ejecutar)
│
├── docs/
│   ├── 1_ficha_catalogacion_vetcare.docx
│   ├── 2_manual_usuario_vetcare.docx
│   ├── 3_manual_instalacion_vetcare.docx
│   ├── 4_plan_pruebas_vetcare.docx
│   └── 5_documento_scrum_vetcare.docx
│
└── README.md
```

---

## 🏗 Arquitectura y Principios de Ingeniería

### Arquitectura en capas

```
┌─────────────────────────────────────┐
│        Capa de Presentación         │  (CLI — salida formateada en terminal)
├─────────────────────────────────────┤
│         Capa de Negocio             │  (Clases Python: GestionPacientes,
│                                     │   GestionInventario, GestionFacturacion...)
├─────────────────────────────────────┤
│         Capa de Datos               │  (SQLite3 — conexión centralizada,
│                                     │   FK habilitadas, row_factory)
└─────────────────────────────────────┘
```

### Principios aplicados

| Principio | Evidencia |
|---|---|
| **SRP** | Una clase = una responsabilidad (GestionInventario solo maneja inventario) |
| **DRY** | `get_connection()` centralizada; `_verificar_alertas()` reutilizada; `imprimir_tabla()` compartida |
| **KISS** | Sin frameworks externos; métodos < 30 líneas; lógica directa |
| **Naming** | `registrar_mascota()`, `agendar_cita()`, `alertas_activas()` — nombres descriptivos |
| **Robustez** | Validaciones antes de cada operación; try/except en IntegrityError; mensajes con ✅/❌ |

---

## 📅 Historial de sprints

| Sprint | Fechas | HU | Story Points | Estado |
|---|---|---|---|---|
| Sprint 0 | 01/03 – 14/03/2026 | Análisis y diseño | — | ✅ Completado |
| Sprint 1 | 01/04 – 15/04/2026 | HU-01, HU-02, HU-03 | 26 SP | ✅ Completado |
| Sprint 2 | 16/04 – 30/04/2026 | HU-04, HU-05, HU-06 | 18 SP | ✅ Completado |
| Sprint 3 | 01/05 – 15/05/2026 | HU-07, HU-08, HU-09 | 21 SP | ✅ Completado |
| Sprint 4 | 16/05 – 30/05/2026 | HU-10 a HU-14 | 29 SP | ✅ Completado |
| **Total** | | **14 HU** | **94 SP** | **✅ 100%** |

---

## 👥 Equipo

| Nombre | Rol | Responsabilidades |
|---|---|---|
| **Iván Nazareno** | Team Lead · Scrum Master · Arquitecto · Back-End | Arquitectura, BD, módulos core, coordinación |
| **Fernanda Mena** | Front-End · Diseño GUI · Analista Comercial | Interfaz, UX, documentación visual, reportes |
| **Santiago Pineda** | Back-End · Analista · QA/Tester | Lógica de negocio, suite de pruebas, análisis |

---

## 📚 Documentación

| Documento | Descripción |
|---|---|
| [Ficha de Catalogación](docs/1_ficha_catalogacion_vetcare.docx) | Metadatos del sistema, dependencias, licencia, versiones |
| [Manual de Usuario](docs/2_manual_usuario_vetcare.docx) | Guía funcional paso a paso para cada módulo |
| [Manual de Instalación](docs/3_manual_instalacion_vetcare.docx) | Despliegue técnico para administradores de sistemas |
| [Plan de Pruebas](docs/4_plan_pruebas_vetcare.docx) | Casos de prueba AAA, resultados, principios de ingeniería |
| [Documento Scrum](docs/5_documento_scrum_vetcare.docx) | Product Backlog, HU, Planning/Review/Retro de 4 sprints |

---

## 📜 Licencia

```
MIT License — Copyright © 2026 FIS Tech & Engineering

Se permite el uso, copia, modificación y distribución del software
con fines académicos e institucionales, siempre que se mantenga
el aviso de copyright original.
```

---

## 📞 Contacto

**FIS Tech & Engineering — Ingeniería de Software III**
Universidad · Grupo 8 · Entrega: 17 de abril de 2026

> *"El código limpio hace una cosa, y la hace bien."* — Robert C. Martin
=======
# ClinicaVetCare-
La Clinica VetCare implementa un sistema integral de gestión veterinaria que permita registrar mascotas y sus dueños, administrar historiales clínicos, programar citas, controlar inventarios, gestionar facturación y generar reportes administrativos
>>>>>>> aabde5fabb81cb5b314bd2dc442433637019468a
