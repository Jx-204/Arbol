import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta

class Nodo:
    def __init__(self, codigo, tipo, nombre, fecha, prioridad, etiquetas, notas):
        self.codigo = codigo
        self.tipo = tipo            # "Tarea" o "Proyecto"
        self.nombre = nombre
        self.fecha = fecha          # fecha de vencimiento
        self.prioridad = prioridad  # Alta, Media o Baja
        self.etiquetas = etiquetas  # lista de etiquetas
        self.notas = notas
        self.izquierdo = None
        self.derecho = None


class Arbol:
    def __init__(self):
        self.raiz = None

    def insertar(self, nodo):
        # Devuelve False si el código ya existe
        if self.raiz is None:
            self.raiz = nodo
            return True
        return self._insertar_recursivo(self.raiz, nodo)

    def _insertar_recursivo(self, nodo_actual, nodo):
        if nodo.codigo < nodo_actual.codigo:
            if nodo_actual.izquierdo is None:
                nodo_actual.izquierdo = nodo
                return True
            return self._insertar_recursivo(nodo_actual.izquierdo, nodo)
        elif nodo.codigo > nodo_actual.codigo:
            if nodo_actual.derecho is None:
                nodo_actual.derecho = nodo
                return True
            return self._insertar_recursivo(nodo_actual.derecho, nodo)
        else:
            return False

    def buscar(self, codigo):
        return self._buscar_recursivo(self.raiz, codigo)

    def _buscar_recursivo(self, nodo_actual, codigo):
        if nodo_actual is None:
            return None
        if nodo_actual.codigo == codigo:
            return nodo_actual
        if codigo < nodo_actual.codigo:
            return self._buscar_recursivo(nodo_actual.izquierdo, codigo)
        else:
            return self._buscar_recursivo(nodo_actual.derecho, codigo)

    def eliminar(self, codigo):
        self.raiz = self._eliminar_recursivo(self.raiz, codigo)

    def _eliminar_recursivo(self, nodo_actual, codigo):
        if nodo_actual is None:
            return None
        if codigo < nodo_actual.codigo:
            nodo_actual.izquierdo = self._eliminar_recursivo(nodo_actual.izquierdo, codigo)
        elif codigo > nodo_actual.codigo:
            nodo_actual.derecho = self._eliminar_recursivo(nodo_actual.derecho, codigo)
        else:
            # Caso 1 y 2: sin hijos o con un solo hijo
            if nodo_actual.izquierdo is None:
                return nodo_actual.derecho
            if nodo_actual.derecho is None:
                return nodo_actual.izquierdo
            # Caso 3: dos hijos, se usa el menor del lado derecho
            sucesor = nodo_actual.derecho
            while sucesor.izquierdo is not None:
                sucesor = sucesor.izquierdo
            nodo_actual.codigo = sucesor.codigo
            nodo_actual.tipo = sucesor.tipo
            nodo_actual.nombre = sucesor.nombre
            nodo_actual.fecha = sucesor.fecha
            nodo_actual.prioridad = sucesor.prioridad
            nodo_actual.etiquetas = sucesor.etiquetas
            nodo_actual.notas = sucesor.notas
            nodo_actual.derecho = self._eliminar_recursivo(nodo_actual.derecho, sucesor.codigo)
        return nodo_actual

    def inorden(self):
        lista = []
        self._inorden_recursivo(self.raiz, lista)
        return lista

    def _inorden_recursivo(self, nodo_actual, lista):
        if nodo_actual is not None:
            self._inorden_recursivo(nodo_actual.izquierdo, lista)
            lista.append(nodo_actual)
            self._inorden_recursivo(nodo_actual.derecho, lista)


arbol = Arbol()

FONDO = "#0b1220"
LATERAL = "#0f172a"
TARJETA = "#162033"
CAMPO = "#1e2b42"
BORDE = "#2a3a57"
TEXTO = "#e5e9f2"
GRIS = "#8b98b3"
ACENTO = "#6366f1"
ROJO = "#ef4444"
FUENTE = "Segoe UI"

COLUMNAS = [("codigo", "Código", 60), ("tipo", "Tipo", 80), ("nombre", "Nombre", 190),
            ("fecha", "Vence", 90), ("prioridad", "Prioridad", 80), ("etiquetas", "Etiquetas", 140)]


# ---------------------------------------------------------------------------
# Componentes de interfaz
# ---------------------------------------------------------------------------

def crear_boton(padre, texto, comando, color=ACENTO):
    return tk.Button(padre, text=texto, command=comando, bg=color, fg="white",
                     activebackground=color, activeforeground="white", relief="flat",
                     cursor="hand2", font=(FUENTE, 10, "bold"), pady=8)


def crear_entrada(padre):
    return tk.Entry(padre, bg=CAMPO, fg=TEXTO, insertbackground=TEXTO, relief="flat",
                    font=(FUENTE, 11), highlightthickness=1,
                    highlightbackground=BORDE, highlightcolor=ACENTO)


def crear_campo(padre, texto):
    tk.Label(padre, text=texto, bg=FONDO, fg=GRIS, font=(FUENTE, 9, "bold")).pack(anchor="w", pady=(10, 3))
    entrada = crear_entrada(padre)
    entrada.pack(fill="x", ipady=5)
    return entrada


def crear_tabla(padre):
    marco = tk.Frame(padre, bg=BORDE)
    tabla_nueva = ttk.Treeview(marco, columns=[c[0] for c in COLUMNAS], show="headings", height=8)
    for clave, titulo, ancho in COLUMNAS:
        tabla_nueva.heading(clave, text=titulo, anchor="w")
        tabla_nueva.column(clave, width=ancho, anchor="w")
    barra = ttk.Scrollbar(marco, orient="vertical", command=tabla_nueva.yview)
    tabla_nueva.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y", padx=(0, 1), pady=1)
    tabla_nueva.pack(side="left", fill="both", expand=True, padx=1, pady=1)
    tabla_nueva.tag_configure("vencida", foreground="#f87171")
    return marco, tabla_nueva


def llenar_tabla(tabla_destino, lista):
    tabla_destino.delete(*tabla_destino.get_children())
    hoy = date.today()
    for n in lista:
        if n.fecha < hoy:
            marca = ("vencida",)
        else:
            marca = ()
        tabla_destino.insert("", "end", iid=str(n.codigo), tags=marca, values=(
            n.codigo, n.tipo, n.nombre, n.fecha.strftime("%d/%m/%Y"),
            n.prioridad, ", ".join(n.etiquetas)))


def refrescar():
    lista = arbol.inorden()
    llenar_tabla(tabla, lista)
    hoy = date.today()
    total_tareas = 0
    total_proyectos = 0
    total_vencidas = 0
    for n in lista:
        if n.tipo == "Tarea":
            total_tareas += 1
        else:
            total_proyectos += 1
        if n.fecha < hoy:
            total_vencidas += 1
    valores["total"].config(text=str(len(lista)))
    valores["tareas"].config(text=str(total_tareas))
    valores["proyectos"].config(text=str(total_proyectos))
    valores["vencidas"].config(text=str(total_vencidas))
    etiqueta_notas.config(text="Selecciona una fila para ver sus notas.")


def mostrar_notas(evento):
    seleccion = tabla.selection()
    if seleccion:
        nodo = arbol.buscar(int(seleccion[0]))
        if nodo is not None:
            etiqueta_notas.config(text="Notas de " + nodo.nombre + ": " + (nodo.notas or "Sin notas"))


def nueva_ventana(titulo, ancho, alto, subtitulo):
    ventana_op = tk.Toplevel()
    ventana_op.title(titulo)
    ventana_op.geometry(f"{ancho}x{alto}")
    ventana_op.resizable(False, False)
    ventana_op.configure(bg=FONDO)
    ventana_op.grab_set()

    encabezado = tk.Frame(ventana_op, bg=LATERAL)
    encabezado.pack(fill="x")
    tk.Frame(encabezado, bg=ACENTO, height=3).pack(fill="x")
    tk.Label(encabezado, text=titulo, bg=LATERAL, fg=TEXTO,
             font=(FUENTE, 15, "bold")).pack(anchor="w", padx=28, pady=(14, 0))
    tk.Label(encabezado, text=subtitulo, bg=LATERAL, fg=GRIS,
             font=(FUENTE, 9)).pack(anchor="w", padx=28, pady=(0, 14))
    return ventana_op


def elegir_opcion(opcion):
    if opcion == "tarea":
        ventana_crear("Tarea")
    elif opcion == "proyecto":
        ventana_crear("Proyecto")
    elif opcion == "editar":
        ventana_editar()
    elif opcion == "buscar":
        ventana_buscar()
    elif opcion == "eliminar":
        ventana_eliminar()
    elif opcion == "vencidas":
        ventana_vencidas()
    elif opcion == "etiquetas":
        ventana_etiquetas()


def ventana_editar(evento=None):
    # Edita la fila seleccionada en la tabla principal
    seleccion = tabla.selection()
    if not seleccion:
        messagebox.showinfo("Editar", "Primero selecciona una fila de la tabla.")
        return
    nodo = arbol.buscar(int(seleccion[0]))
    if nodo is not None:
        ventana_crear(nodo.tipo, nodo)


def ventana_crear(tipo, nodo_editar=None):
    # Si se recibe nodo_editar, el formulario funciona en modo edición
    editando = nodo_editar is not None
    if editando:
        ventana_op = nueva_ventana("Editar " + tipo.lower(), 420, 580,
                                   "Modifica los datos y pulsa Guardar cambios")
    else:
        ventana_op = nueva_ventana("Nueva " + tipo.lower(), 420, 580,
                                   "Completa los datos y pulsa Guardar")
    cuerpo = tk.Frame(ventana_op, bg=FONDO)
    cuerpo.pack(fill="both", expand=True, padx=28, pady=(0, 16))

    e_codigo = crear_campo(cuerpo, "CÓDIGO (NÚMERO)")
    e_nombre = crear_campo(cuerpo, "NOMBRE")
    e_fecha = crear_campo(cuerpo, "FECHA DE VENCIMIENTO (DD/MM/AAAA)")

    tk.Label(cuerpo, text="PRIORIDAD", bg=FONDO, fg=GRIS, font=(FUENTE, 9, "bold")).pack(anchor="w", pady=(10, 3))
    c_prioridad = ttk.Combobox(cuerpo, values=["Alta", "Media", "Baja"], state="readonly")
    c_prioridad.current(1)
    c_prioridad.pack(fill="x")

    e_etiquetas = crear_campo(cuerpo, "ETIQUETAS (SEPARADAS POR COMAS)")

    tk.Label(cuerpo, text="NOTAS", bg=FONDO, fg=GRIS, font=(FUENTE, 9, "bold")).pack(anchor="w", pady=(10, 3))
    t_notas = tk.Text(cuerpo, height=4, bg=CAMPO, fg=TEXTO, insertbackground=TEXTO, relief="flat",
                      font=(FUENTE, 10), highlightthickness=1, highlightbackground=BORDE)
    t_notas.pack(fill="x")

    if editando:
        # Se rellenan los campos con los datos actuales
        e_codigo.insert(0, str(nodo_editar.codigo))
        e_codigo.config(state="readonly", readonlybackground=CAMPO, fg=GRIS)  # el código no se cambia
        e_nombre.insert(0, nodo_editar.nombre)
        e_fecha.insert(0, nodo_editar.fecha.strftime("%d/%m/%Y"))
        c_prioridad.set(nodo_editar.prioridad)
        e_etiquetas.insert(0, ", ".join(nodo_editar.etiquetas))
        t_notas.insert("1.0", nodo_editar.notas)

    def guardar():
        if not editando:
            try:
                codigo = int(e_codigo.get())
            except ValueError:
                messagebox.showerror("Error", "El código debe ser un número entero.", parent=ventana_op)
                return
        nombre = e_nombre.get().strip()
        if nombre == "":
            messagebox.showerror("Error", "El nombre es obligatorio.", parent=ventana_op)
            return
        try:
            fecha = datetime.strptime(e_fecha.get().strip(), "%d/%m/%Y").date()
        except ValueError:
            messagebox.showerror("Error", "Fecha inválida. Usa el formato DD/MM/AAAA.", parent=ventana_op)
            return
        etiquetas = []
        for e in e_etiquetas.get().split(","):
            if e.strip() != "":
                etiquetas.append(e.strip().lower())
        notas = t_notas.get("1.0", "end").strip()

        if editando:
            nodo_editar.nombre = nombre
            nodo_editar.fecha = fecha
            nodo_editar.prioridad = c_prioridad.get()
            nodo_editar.etiquetas = etiquetas
            nodo_editar.notas = notas
            refrescar()
            tabla.selection_set(str(nodo_editar.codigo))   # mantiene la fila seleccionada
            ventana_op.destroy()
            return

        nodo = Nodo(codigo, tipo, nombre, fecha, c_prioridad.get(), etiquetas, notas)
        if arbol.insertar(nodo):
            refrescar()
            ventana_op.destroy()
        else:
            messagebox.showwarning("Aviso", f"El código {codigo} ya existe. No se puede registrar.",
                                   parent=ventana_op)

    botones = tk.Frame(cuerpo, bg=FONDO)
    botones.pack(fill="x", pady=(16, 0))
    texto_guardar = "Guardar cambios" if editando else "Guardar"
    crear_boton(botones, texto_guardar, guardar).pack(side="left", fill="x", expand=True, padx=(0, 6))
    crear_boton(botones, "Cancelar", ventana_op.destroy, CAMPO).pack(side="left", fill="x", expand=True)


def ventana_buscar():
    ventana_op = nueva_ventana("Buscar", 700, 450, "Busca por código o por nombre")
    cuerpo = tk.Frame(ventana_op, bg=FONDO)
    cuerpo.pack(fill="both", expand=True, padx=24, pady=16)

    fila = tk.Frame(cuerpo, bg=FONDO)
    fila.pack(fill="x")
    e_buscar = crear_entrada(fila)
    e_buscar.pack(side="left", fill="x", expand=True, ipady=5)

    marco, tabla_resultado = crear_tabla(cuerpo)

    def por_codigo():
        try:
            codigo = int(e_buscar.get())
        except ValueError:
            messagebox.showerror("Error", "Escribe un código numérico.", parent=ventana_op)
            return
        nodo = arbol.buscar(codigo)
        if nodo is None:
            llenar_tabla(tabla_resultado, [])
            messagebox.showinfo("Búsqueda", f"El código {codigo} no fue encontrado.", parent=ventana_op)
        else:
            llenar_tabla(tabla_resultado, [nodo])

    def por_nombre():
        texto = e_buscar.get().strip().lower()
        encontrados = []
        for n in arbol.inorden():
            if texto in n.nombre.lower():
                encontrados.append(n)
        llenar_tabla(tabla_resultado, encontrados)
        if len(encontrados) == 0:
            messagebox.showinfo("Búsqueda", "No se encontraron resultados.", parent=ventana_op)

    crear_boton(fila, "Por código", por_codigo).pack(side="left", padx=(8, 0))
    crear_boton(fila, "Por nombre", por_nombre, CAMPO).pack(side="left", padx=(6, 0))
    marco.pack(fill="both", expand=True, pady=(14, 0))


def ventana_eliminar():
    ventana_op = nueva_ventana("Eliminar", 420, 240, "Escribe el código a eliminar")
    cuerpo = tk.Frame(ventana_op, bg=FONDO)
    cuerpo.pack(fill="both", expand=True, padx=28, pady=(0, 16))

    e_codigo = crear_campo(cuerpo, "CÓDIGO")
    seleccion = tabla.selection()
    if seleccion:
        e_codigo.insert(0, seleccion[0])   # usa la fila elegida en la tabla principal

    def eliminar():
        try:
            codigo = int(e_codigo.get())
        except ValueError:
            messagebox.showerror("Error", "Escribe un código numérico.", parent=ventana_op)
            return
        nodo = arbol.buscar(codigo)
        if nodo is None:
            messagebox.showinfo("Eliminar", f"El código {codigo} no existe.", parent=ventana_op)
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar " + nodo.nombre + "?", parent=ventana_op):
            arbol.eliminar(codigo)
            refrescar()
            ventana_op.destroy()

    crear_boton(cuerpo, "Eliminar", eliminar, ROJO).pack(fill="x", pady=(16, 0))


def ventana_vencidas():
    ventana_op = nueva_ventana("Tareas vencidas", 700, 450, "Elementos cuya fecha ya pasó")
    cuerpo = tk.Frame(ventana_op, bg=FONDO)
    cuerpo.pack(fill="both", expand=True, padx=24, pady=16)

    hoy = date.today()
    vencidas = []
    for n in arbol.inorden():
        if n.fecha < hoy:
            vencidas.append(n)

    tk.Label(cuerpo, text=f"Total vencidas: {len(vencidas)}", bg=FONDO, fg="#f87171",
             font=(FUENTE, 10, "bold")).pack(anchor="w", pady=(0, 8))
    marco, tabla_resultado = crear_tabla(cuerpo)
    marco.pack(fill="both", expand=True)
    llenar_tabla(tabla_resultado, vencidas)


def ventana_etiquetas():
    ventana_op = nueva_ventana("Tareas por etiqueta", 700, 450, "Escribe una etiqueta y genera el reporte")
    cuerpo = tk.Frame(ventana_op, bg=FONDO)
    cuerpo.pack(fill="both", expand=True, padx=24, pady=16)

    fila = tk.Frame(cuerpo, bg=FONDO)
    fila.pack(fill="x")
    e_etiqueta = crear_entrada(fila)
    e_etiqueta.pack(side="left", fill="x", expand=True, ipady=5)
    marco, tabla_resultado = crear_tabla(cuerpo)

    def generar():
        etiqueta = e_etiqueta.get().strip().lower()
        if etiqueta == "":
            messagebox.showinfo("Aviso", "Escribe una etiqueta.", parent=ventana_op)
            return
        encontrados = []
        for n in arbol.inorden():
            if etiqueta in n.etiquetas:
                encontrados.append(n)
        llenar_tabla(tabla_resultado, encontrados)
        if len(encontrados) == 0:
            messagebox.showinfo("Reporte", "No hay elementos con esa etiqueta.", parent=ventana_op)

    crear_boton(fila, "Generar reporte", generar).pack(side="left", padx=(8, 0))
    marco.pack(fill="both", expand=True, pady=(14, 0))


# ---------------------------------------------------------------------------
# Ventana principal
# ---------------------------------------------------------------------------

ventana = tk.Tk()
ventana.title("GESTION DE TAREAS")
ventana.geometry("1000x550")
ventana.resizable(False, False)
ventana.configure(bg=FONDO)

estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("Treeview", background=TARJETA, fieldbackground=TARJETA, foreground=TEXTO,
                 rowheight=28, borderwidth=0, font=(FUENTE, 10))
estilo.configure("Treeview.Heading", background=CAMPO, foreground=GRIS,
                 font=(FUENTE, 9, "bold"), relief="flat")
estilo.map("Treeview", background=[("selected", ACENTO)])
estilo.configure("TCombobox", fieldbackground=CAMPO, background=CAMPO, foreground=TEXTO)

lateral = tk.Frame(ventana, bg=LATERAL)
lateral.place(x=0, y=0, width=230, height=550)
tk.Frame(lateral, bg=ACENTO, height=4).pack(fill="x")
tk.Label(lateral, text="GESTIÓN DE", bg=LATERAL, fg="#818cf8",
         font=(FUENTE, 9, "bold")).pack(anchor="w", padx=24, pady=(22, 0))
tk.Label(lateral, text="Tareas y\nProyectos", bg=LATERAL, fg=TEXTO, font=(FUENTE, 20, "bold"),
         justify="left").pack(anchor="w", padx=24)
tk.Label(lateral, text="Árbol Binario de Búsqueda", bg=LATERAL, fg=GRIS,
         font=(FUENTE, 9)).pack(anchor="w", padx=24, pady=(2, 20))

opciones = [("Nueva tarea", "tarea"), ("Nuevo proyecto", "proyecto"), ("Editar", "editar"),
            ("Buscar", "buscar"), ("Eliminar", "eliminar"), ("Tareas vencidas", "vencidas"),
            ("Tareas por etiqueta", "etiquetas")]
for texto_opcion, clave_opcion in opciones:
    crear_boton(lateral, texto_opcion, lambda o=clave_opcion: elegir_opcion(o),
                CAMPO).pack(fill="x", padx=16, pady=4)

panel = tk.Frame(ventana, bg=FONDO)
panel.place(x=230, y=0, width=770, height=550)
tk.Label(panel, text="Panel general", bg=FONDO, fg=TEXTO,
         font=(FUENTE, 20, "bold")).place(x=24, y=16)
tk.Label(panel, text="Tareas y proyectos ordenados por código (doble clic para editar)", bg=FONDO, fg=GRIS,
         font=(FUENTE, 10)).place(x=26, y=56)

fila_tarjetas = tk.Frame(panel, bg=FONDO)
fila_tarjetas.place(x=24, y=90, width=722, height=72)
fila_tarjetas.rowconfigure(0, weight=1)
valores = {}
datos_tarjetas = [("total", "Total", TEXTO), ("tareas", "Tareas", "#818cf8"),
                  ("proyectos", "Proyectos", "#34d399"), ("vencidas", "Vencidas", "#f87171")]
for i in range(4):
    clave, titulo, color = datos_tarjetas[i]
    fila_tarjetas.columnconfigure(i, weight=1, uniform="t")
    tarjeta = tk.Frame(fila_tarjetas, bg=TARJETA, highlightthickness=1, highlightbackground=BORDE)
    tarjeta.grid(row=0, column=i, sticky="nsew", padx=5)
    valores[clave] = tk.Label(tarjeta, text="0", bg=TARJETA, fg=color, font=(FUENTE, 22, "bold"))
    valores[clave].pack(anchor="w", padx=14, pady=(6, 0))
    tk.Label(tarjeta, text=titulo, bg=TARJETA, fg=GRIS, font=(FUENTE, 9)).pack(anchor="w", padx=14)

marco_tabla, tabla = crear_tabla(panel)
marco_tabla.place(x=24, y=176, width=722, height=286)
tabla.bind("<<TreeviewSelect>>", mostrar_notas)
tabla.bind("<Double-1>", ventana_editar)

caja_notas = tk.Frame(panel, bg=TARJETA, highlightthickness=1, highlightbackground=BORDE)
caja_notas.place(x=24, y=472, width=722, height=58)
etiqueta_notas = tk.Label(caja_notas, text="", bg=TARJETA, fg=GRIS, font=(FUENTE, 10),
                          anchor="w", justify="left", wraplength=690)
etiqueta_notas.pack(fill="both", expand=True, padx=14, pady=6)

# Datos de ejemplo: todo vive en el árbol, en memoria
hoy = date.today()
arbol.insertar(Nodo(8, "Proyecto", "Proyecto final", hoy + timedelta(days=14), "Alta",
                    ["universidad", "grupo"], "Aplicación en Python con ABB e interfaz gráfica."))
arbol.insertar(Nodo(3, "Tarea", "Programar el árbol ABB", hoy - timedelta(days=2), "Alta",
                    ["universidad", "código"], "Insertar, buscar y eliminar."))
arbol.insertar(Nodo(10, "Tarea", "Diseñar la interfaz", hoy + timedelta(days=5), "Media",
                    ["universidad", "diseño"], "Menú lateral y tabla."))
arbol.insertar(Nodo(1, "Tarea", "Pagar el internet", hoy - timedelta(days=5), "Baja",
                    ["casa"], "Se pasó la fecha de pago."))


refrescar()
ventana.mainloop()