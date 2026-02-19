import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import os

# ==============================
# RUTA DEL LOGO (según tu estructura)
# ==============================

ruta_base = os.path.dirname(__file__)        # proyecto1
ruta_github = os.path.dirname(ruta_base)    # sube a GitHub
ruta_logo = os.path.join(ruta_github, "logo.jpg")  # cambia a .png si es necesario

# ==============================
# BASE DE DATOS
# ==============================

def crear_bd():
    conexion = sqlite3.connect("finanzas.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()

def insertar_movimiento(tipo, descripcion, monto):
    conexion = sqlite3.connect("finanzas.db")
    cursor = conexion.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO movimientos (tipo, descripcion, monto, fecha)
        VALUES (?, ?, ?, ?)
    """, (tipo, descripcion, monto, fecha))
    conexion.commit()
    conexion.close()

def obtener_movimientos():
    conexion = sqlite3.connect("finanzas.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM movimientos")
    datos = cursor.fetchall()
    conexion.close()
    return datos

def eliminar_movimiento(id_movimiento):
    conexion = sqlite3.connect("finanzas.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM movimientos WHERE id=?", (id_movimiento,))
    conexion.commit()
    conexion.close()

def calcular_balance():
    conexion = sqlite3.connect("finanzas.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT SUM(monto) FROM movimientos WHERE tipo='Ingreso'")
    ingresos = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(monto) FROM movimientos WHERE tipo='Gasto'")
    gastos = cursor.fetchone()[0] or 0
    conexion.close()
    return ingresos, gastos, ingresos - gastos

# ==============================
# FUNCIONES GUI
# ==============================

def guardar():
    tipo = combo_tipo.get()
    descripcion = entry_descripcion.get()
    monto = entry_monto.get()

    if descripcion == "" or monto == "":
        messagebox.showwarning("Error", "Todos los campos son obligatorios")
        return

    try:
        monto = float(monto)
        insertar_movimiento(tipo, descripcion, monto)
        messagebox.showinfo("Éxito", f"{tipo} guardado correctamente")
        entry_descripcion.delete(0, tk.END)
        entry_monto.delete(0, tk.END)
        mostrar_datos()
    except:
        messagebox.showerror("Error", "El monto debe ser numérico")

def eliminar():
    seleccionado = tabla.selection()

    if not seleccionado:
        messagebox.showwarning("Error", "Selecciona un registro para eliminar")
        return

    item = tabla.item(seleccionado)
    id_movimiento = item["values"][0]

    confirmar = messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este movimiento?")
    if confirmar:
        eliminar_movimiento(id_movimiento)
        mostrar_datos()

def mostrar_datos():
    for row in tabla.get_children():
        tabla.delete(row)

    datos = obtener_movimientos()
    for fila in datos:
        tabla.insert("", tk.END, values=fila)

    ingresos, gastos, balance = calcular_balance()
    label_ingresos.config(text=f"Ingresos: ${ingresos:,.2f}")
    label_gastos.config(text=f"Gastos: ${gastos:,.2f}")
    label_balance.config(text=f"Balance: ${balance:,.2f}")

# ==============================
# INTERFAZ
# ==============================

crear_bd()

ventana = tk.Tk()
ventana.title("Sistema de Finanzas Personales")
ventana.geometry("750x650")

# LOGO
try:
    imagen = Image.open(ruta_logo)
    imagen = imagen.resize((120, 120))
    logo_tk = ImageTk.PhotoImage(imagen)

    label_logo = tk.Label(ventana, image=logo_tk)
    label_logo.pack(pady=10)

except Exception as e:
    print("No se pudo cargar el logo:", e)

tk.Label(ventana, text="Sistema de Ingresos y Gastos", font=("Arial", 16)).pack(pady=5)

# Formulario
frame_form = tk.Frame(ventana)
frame_form.pack(pady=10)

tk.Label(frame_form, text="Tipo:").grid(row=0, column=0, padx=5, pady=5)
combo_tipo = ttk.Combobox(frame_form, values=["Ingreso", "Gasto"])
combo_tipo.current(0)
combo_tipo.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form, text="Descripción:").grid(row=1, column=0, padx=5, pady=5)
entry_descripcion = tk.Entry(frame_form)
entry_descripcion.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_form, text="Monto:").grid(row=2, column=0, padx=5, pady=5)
entry_monto = tk.Entry(frame_form)
entry_monto.grid(row=2, column=1, padx=5, pady=5)

tk.Button(ventana, text="Guardar Movimiento", command=guardar, bg="blue", fg="white").pack(pady=5)
tk.Button(ventana, text="Eliminar Seleccionado", command=eliminar, bg="red", fg="white").pack(pady=5)

# Tabla
tabla = ttk.Treeview(ventana, columns=("ID", "Tipo", "Descripción", "Monto", "Fecha"), show="headings")
for col in ("ID", "Tipo", "Descripción", "Monto", "Fecha"):
    tabla.heading(col, text=col)

tabla.pack(pady=10, fill="both", expand=True)

# Resumen
frame_resumen = tk.Frame(ventana)
frame_resumen.pack(pady=10)

label_ingresos = tk.Label(frame_resumen, text="Ingresos: $0", fg="green", font=("Arial", 12))
label_ingresos.grid(row=0, column=0, padx=20)

label_gastos = tk.Label(frame_resumen, text="Gastos: $0", fg="red", font=("Arial", 12))
label_gastos.grid(row=0, column=1, padx=20)

label_balance = tk.Label(frame_resumen, text="Balance: $0", font=("Arial", 12))
label_balance.grid(row=0, column=2, padx=20)

mostrar_datos()

ventana.mainloop()
