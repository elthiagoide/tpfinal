import customtkinter as ctk
from tkinter import messagebox
import webbrowser
import json
import config
import database


class VistaAgenda(ctk.CTkFrame):
    """Lista persistente de proyectos guardados desde el Planificador.
    Permite ordenar por fecha o por ganancia y ver detalle de cada proyecto.
    """
    def __init__(self, master, user_id, selected_pid=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP)
        self.user_id = user_id
        self._selected_pid = selected_pid

        ctk.CTkLabel(self, text="Agenda - Proyectos Guardados", font=("Segoe UI", 20, "bold"), text_color="white").pack(pady=(12,8))

        # Controles de orden
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=12, pady=(0,6))
        ctk.CTkLabel(ctrl, text="Orden:", text_color="gray").pack(side="left", padx=(4,8))
        self.combo_orden = ctk.CTkComboBox(ctrl, values=["Fecha: más reciente", "Fecha: más antigua", "Ganancia: mayor", "Ganancia: menor"], width=260, fg_color="#1a1a1a", button_color="#444", text_color="white")
        self.combo_orden.pack(side="left")
        self.combo_orden.set("Fecha: más reciente")
        self.combo_orden.bind("<<ComboboxSelected>>", lambda e: self.cargar_lista())
        ctk.CTkButton(ctrl, text="Actualizar", width=120, command=self.cargar_lista).pack(side="left", padx=8)

        # Frame con scroll para la lista
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=12, pady=8)

        self.cargar_lista()
        # Si se pidió abrir un proyecto, mostrar su detalle automáticamente
        try:
            if self._selected_pid:
                # llamar a ver_detalle para abrir modal
                self.ver_detalle(self._selected_pid)
        except Exception:
            pass

    def cargar_lista(self):
        # limpiar
        for w in self.scroll.winfo_children():
            w.destroy()

        opt = self.combo_orden.get()
        order_by = 'fecha_desc'
        if opt == 'Fecha: más antigua':
            order_by = 'fecha_asc'
        elif opt == 'Ganancia: mayor':
            order_by = 'ganancia_desc'
        elif opt == 'Ganancia: menor':
            order_by = 'ganancia_asc'

        proyectos = database.obtener_proyectos_agenda(self.user_id, order_by=order_by)
        if not proyectos:
            ctk.CTkLabel(self.scroll, text="No hay proyectos guardados.", text_color="gray").pack(pady=12)
            return

        from datetime import datetime
        for p in proyectos:
            # p: id, nombre, meta, materiales, flota, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia, created_at
            pid, nombre, meta, materiales, flota, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia, created_at = p
            card = ctk.CTkFrame(self.scroll, fg_color=config.COLOR_TARJETA, corner_radius=8)
            card.pack(fill="x", pady=6, padx=6)
            titulo = f"{nombre} — {meta} u"
            ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 12, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(8,2))
            # calcular tiempo necesario y tiempo restante hasta entrega
            dias_neces = int(tiempo_hs // 24)
            horas_rest = int((tiempo_hs - dias_neces * 24))
            tiempo_neces_str = f"{dias_neces}d {horas_rest}h" if tiempo_hs >= 24 else f"{horas_rest}h"

            restante_str = "-"
            if delivery_date:
                try:
                    dt = datetime.strptime(delivery_date, '%Y-%m-%d')
                    now = datetime.now()
                    delta = dt - now
                    if delta.total_seconds() >= 0:
                        dias_r = delta.days
                        horas_r = int((delta.seconds) / 3600)
                        restante_str = f"en {dias_r}d {horas_r}h"
                    else:
                        dias_r = abs(delta.days)
                        horas_r = int((abs(delta.seconds)) / 3600)
                        restante_str = f"vencido hace {dias_r}d {horas_r}h"
                except Exception:
                    restante_str = delivery_date

            subt = f"Tiempo necesario: {tiempo_neces_str} | Entrega: {delivery_date or '-'} ({restante_str}) | Ganancia: {ganancia:.2f}"
            ctk.CTkLabel(card, text=subt, text_color="gray").pack(anchor="w", padx=10)

            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.pack(fill="x", pady=8, padx=10)
            ctk.CTkButton(btns, text="Ver detalle", width=120, command=lambda pid=pid: self.ver_detalle(pid)).pack(side="left")
            ctk.CTkButton(btns, text="Realizar trabajo", width=140, fg_color="#6aa84f", hover_color="#5b7e3a", command=lambda pid=pid: self.realizar_trabajo(pid)).pack(side="left", padx=8)
            ctk.CTkButton(btns, text="Eliminar", width=120, fg_color=config.COLOR_ROJO, hover_color=config.COLOR_ROJO_HOVER, command=lambda pid=pid: self.eliminar_proyecto(pid)).pack(side="left", padx=8)

    def ver_detalle(self, pid):
        dato = database.obtener_proyecto_agenda(pid)
        if not dato:
            dlg = ctk.CTkToplevel(self)
            dlg.title("Error")
            dlg.geometry("320x120")
            ctk.CTkLabel(dlg, text="Proyecto no encontrado.", text_color="red").pack(pady=20)
            ctk.CTkButton(dlg, text="Cerrar", command=dlg.destroy).pack(pady=8)
            return
        # id, user_id, nombre, meta, materiales, flota, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia, created_at
        _, _, nombre, meta, materiales, flota, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia, created_at = dato

        top = ctk.CTkToplevel(self)
        top.title(f"Detalle: {nombre}")
        top.geometry("700x480")
        top.lift()
        top.focus_force()
        try:
            top.grab_set()
        except Exception:
            pass

        header = ctk.CTkFrame(top, fg_color=config.COLOR_TARJETA, corner_radius=6)
        header.pack(fill="x", padx=12, pady=(12,6))
        ctk.CTkLabel(header, text=f"{nombre}", font=("Segoe UI", 16, "bold"), text_color="white").pack(anchor="w", padx=12, pady=8)

        info = ctk.CTkFrame(top, fg_color="transparent")
        info.pack(fill="x", padx=12)
        # tiempo necesario
        dias_neces = int(tiempo_hs // 24)
        horas_rest = int((tiempo_hs - dias_neces * 24))
        tiempo_neces_str = f"{dias_neces}d {horas_rest}h" if tiempo_hs >= 24 else f"{horas_rest}h"

        ctk.CTkLabel(info, text=f"Meta: {meta} unidades", text_color="gray").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Tiempo estimado: {tiempo_hs:.2f} hs ({tiempo_neces_str})", text_color="gray").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Costo energético estimado: {costo_energia:.2f}", text_color="gray").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Precio por unidad: {precio_unit:.2f}", text_color="gray").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Entrega prevista: {delivery_date or '-'}", text_color="gray").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Ganancia estimada: {ganancia:.2f}", text_color="#9ee59e").pack(anchor="w", pady=(0,8))

        # materiales y flota en secciones con fondo
        sec_mat = ctk.CTkFrame(top, fg_color=config.COLOR_TARJETA, corner_radius=6)
        sec_mat.pack(fill="both", expand=True, padx=12, pady=8)
        ctk.CTkLabel(sec_mat, text="Materiales totales:", font=("Segoe UI", 12, "bold"), text_color=config.COLOR_VERDE_BAMBU).pack(anchor="w", padx=8, pady=(8,4))
        try:
            mat = json.loads(materiales) if materiales else {}
            for k, v in mat.items():
                ctk.CTkLabel(sec_mat, text=f" - {k}: {v:.2f} g", text_color="gray").pack(anchor="w", padx=12)
        except Exception:
            ctk.CTkLabel(sec_mat, text="Materiales: (no disponibles)", text_color="gray").pack(anchor="w", padx=12)

        ctk.CTkLabel(sec_mat, text="\nFlota asignada:", font=("Segoe UI", 12, "bold"), text_color=config.COLOR_VERDE_BAMBU).pack(anchor="w", padx=8, pady=(8,4))
        try:
            fl = json.loads(flota) if flota else []
            for m in fl:
                ctk.CTkLabel(sec_mat, text=f" - {m.get('display')} | Power: {m.get('power'):.2f} kW | Tiempo/unidad: {m.get('tiempo_unidad'):.2f} hs", text_color="gray").pack(anchor="w", padx=12)
        except Exception:
            ctk.CTkLabel(sec_mat, text="Flota: (no disponible)", text_color="gray").pack(anchor="w", padx=12)

    def eliminar_proyecto(self, pid):
        if messagebox.askyesno("Confirmar", "¿Eliminar este proyecto de la agenda?"):
            ok = database.eliminar_proyecto_agenda(pid)
            if ok:
                dlg = ctk.CTkToplevel(self)
                dlg.title("Eliminado")
                dlg.geometry("320x120")
                ctk.CTkLabel(dlg, text="Proyecto eliminado.").pack(pady=20)
                ctk.CTkButton(dlg, text="Aceptar", command=lambda: (dlg.destroy(), self.cargar_lista()), fg_color=config.COLOR_VERDE_BAMBU).pack(pady=8)
            else:
                dlg = ctk.CTkToplevel(self)
                dlg.title("Error")
                dlg.geometry("320x120")
                ctk.CTkLabel(dlg, text="No se pudo eliminar el proyecto.", text_color="red").pack(pady=20)
                ctk.CTkButton(dlg, text="Cerrar", command=dlg.destroy).pack(pady=8)

    def realizar_trabajo(self, pid):
        # Obtener proyecto
        dato = database.obtener_proyecto_agenda(pid)
        if not dato:
            dlg = ctk.CTkToplevel(self)
            dlg.title("Error")
            dlg.geometry("320x120")
            ctk.CTkLabel(dlg, text="Proyecto no encontrado.", text_color="red").pack(pady=20)
            ctk.CTkButton(dlg, text="Cerrar", command=dlg.destroy).pack(pady=8)
            return

        # id, user_id, nombre, meta, materiales, flota, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia, created_at
        _, _, nombre, meta, materiales_json, flota_json, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia, created_at = dato

        # materials total stored as {color: grams_total}
        try:
            materiales = json.loads(materiales_json) if materiales_json else {}
        except Exception:
            materiales = {}

        # verificar stock por color
        faltantes = []
        for color, gramos_total in materiales.items():
            # obtener disponible
            key = (color or '').strip().lower()
            lista = database.obtener_bobinas(self.user_id)
            disponible = 0.0
            for b in lista:
                if (b[3] or '').strip().lower() == key:
                    disponible += float(b[4] or 0)
            if disponible < gramos_total:
                faltantes.append((color, gramos_total, disponible))

        if faltantes:
            # mostrar dialog con opciones: comprar o añadir filamento
            top = ctk.CTkToplevel(self)
            top.title("Stock insuficiente")
            top.geometry("520x300")
            ctk.CTkLabel(top, text=f"No hay suficiente filamento para: {nombre}", font=("Segoe UI", 13, "bold"), text_color="white").pack(pady=(12,8))
            for f in faltantes:
                ctk.CTkLabel(top, text=f" - {f[0]}: requerido {f[1]:.2f} g | disponible {f[2]:.2f} g", text_color="gray").pack(anchor='w', padx=12)

            def ir_comprar():
                webbrowser.open("https://listado.mercadolibre.com.ar/filamento-3d")

            def ir_añadir():
                # Abrir diálogo para añadir una bobina rápidamente
                dlg = ctk.CTkToplevel(self)
                dlg.title("Añadir bobina")
                dlg.geometry("460x300")

                ctk.CTkLabel(dlg, text="Añadir nueva bobina", font=("Segoe UI", 14, "bold"), text_color="white").pack(pady=(12,8))

                f = ctk.CTkFrame(dlg, fg_color="transparent")
                f.pack(fill="x", padx=12, pady=6)

                ctk.CTkLabel(f, text="Marca:", text_color="gray").grid(row=0, column=0, sticky="w", pady=6)
                entry_marca = ctk.CTkEntry(f)
                entry_marca.grid(row=0, column=1, sticky="ew", padx=6)

                ctk.CTkLabel(f, text="Material:", text_color="gray").grid(row=1, column=0, sticky="w", pady=6)
                entry_material = ctk.CTkEntry(f)
                entry_material.grid(row=1, column=1, sticky="ew", padx=6)

                ctk.CTkLabel(f, text="Color:", text_color="gray").grid(row=2, column=0, sticky="w", pady=6)
                entry_color = ctk.CTkEntry(f)
                entry_color.grid(row=2, column=1, sticky="ew", padx=6)

                ctk.CTkLabel(f, text="Peso (g):", text_color="gray").grid(row=3, column=0, sticky="w", pady=6)
                entry_peso = ctk.CTkEntry(f)
                entry_peso.grid(row=3, column=1, sticky="ew", padx=6)

                ctk.CTkLabel(f, text="Costo total ($):", text_color="gray").grid(row=4, column=0, sticky="w", pady=6)
                entry_costo = ctk.CTkEntry(f)
                entry_costo.grid(row=4, column=1, sticky="ew", padx=6)

                f.columnconfigure(1, weight=1)

                def guardar_bobina():
                    marca = entry_marca.get().strip()
                    material = entry_material.get().strip()
                    color = entry_color.get().strip()
                    try:
                        peso = float(entry_peso.get())
                    except Exception:
                        messagebox.showerror("Error", "Peso inválido")
                        return
                    try:
                        costo = float(entry_costo.get())
                    except Exception:
                        messagebox.showerror("Error", "Costo inválido")
                        return
                    if not marca or not color:
                        messagebox.showwarning("Faltan datos", "Marca y color son obligatorios.")
                        return
                    ok = database.agregar_bobina(marca, material or "PLA", color, peso, costo, self.user_id)
                    if ok:
                        messagebox.showinfo("Guardado", "Bobina añadida correctamente.")
                        dlg.destroy()
                    else:
                        messagebox.showerror("Error", "No se pudo añadir la bobina.")

                btns = ctk.CTkFrame(dlg, fg_color='transparent')
                btns.pack(pady=12)
                ctk.CTkButton(btns, text="Cancelar", fg_color="#999", command=dlg.destroy).pack(side='right', padx=8)
                ctk.CTkButton(btns, text="Guardar bobina", fg_color=config.COLOR_VERDE_BAMBU, command=guardar_bobina).pack(side='right', padx=8)

            btns = ctk.CTkFrame(top, fg_color='transparent')
            btns.pack(pady=14)
            ctk.CTkButton(btns, text="Comprar filamento", fg_color="#f39c12", command=ir_comprar).pack(side='left', padx=8)
            ctk.CTkButton(btns, text="Añadir filamento", fg_color="#4a90e2", command=ir_añadir).pack(side='left', padx=8)
            ctk.CTkButton(btns, text="Cerrar", command=top.destroy).pack(side='left', padx=8)
            return

        # Si hay stock suficiente, descontar bobinas proporcionalmente y crear registro agregado en impresiones
        try:
            # descontar por color: iterar bobinas y restar hasta cubrir el necesario
            for color, gramos_total in materiales.items():
                need = float(gramos_total)
                key = (color or '').strip().lower()
                bobinas = database.obtener_bobinas(self.user_id)
                # ordenar por id (no optimize cost)
                for b in bobinas:
                    if (b[3] or '').strip().lower() == key and need > 0:
                        bob_id = b[0]
                        available = float(b[4] or 0)
                        take = min(available, need)
                        database.decrementar_peso_bobina(bob_id, take)
                        need -= take

            # crear registro en impresiones: usar tiempo por unidad estimado promedio de flota si es posible
            tiempo_unit = None
            try:
                flota = json.loads(flota_json) if flota_json else []
                if flota:
                    # usar primer elemento tiempo_unidad
                    tiempo_unit = float(flota[0].get('tiempo_unidad', tiempo_hs / max(1, int(meta))))
            except Exception:
                tiempo_unit = tiempo_hs / max(1, int(meta)) if meta else tiempo_hs

            peso_unit_total = 0.0
            for color, gramos_total in materiales.items():
                peso_unit_total += float(gramos_total) / max(1, int(meta))

            # registrar_impresion(nombre, peso_usado_per_unit, tiempo_unit, id_impresora=Null, id_bobina=Null, user_id, cantidad=meta)
            # aquí pasamos id_impresora e id_bobina como None (DB tolera?) — registrar_impresion espera ids válidos; en su ausencia enviaremos 0
            # crear registro agregado en impresiones
            costo_final = 0.0
            try:
                costo_final = float(precio_unit) * int(meta)
            except Exception:
                costo_final = 0.0
            gan_calc = float(ganancia or 0.0)
            exito = database.crear_impresion_agregada(nombre, costo_final, peso_unit_total, tiempo_unit, meta, delivery_date, precio_unit, gan_calc, None, None, self.user_id)
            mensaje = "Registro creado" if exito else "Error"
            if exito:
                # eliminar proyecto de agenda
                database.eliminar_proyecto_agenda(pid)
                dlg = ctk.CTkToplevel(self)
                dlg.title("Trabajo realizado")
                dlg.geometry("360x140")
                ctk.CTkLabel(dlg, text="Trabajo realizado y registrado en Historial.", font=("Segoe UI", 12)).pack(pady=(20,8))
                ctk.CTkButton(dlg, text="Aceptar", command=lambda: (dlg.destroy(), self.cargar_lista()), fg_color=config.COLOR_VERDE_BAMBU).pack(pady=12)
            else:
                messagebox.showerror("Error", "No se pudo registrar el trabajo.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")
    def agregar_color(self):
        row = ctk.CTkFrame(self.frame_colores, fg_color=config.COLOR_TARJETA, corner_radius=6)
        row.pack(fill="x", pady=4)
        entry_nombre = ctk.CTkEntry(row, placeholder_text="Color (ej: Rojo)", width=180, fg_color="#1a1a1a", border_color="#444", text_color="white")
        entry_nombre.pack(side="left", padx=6, pady=6)
        entry_g = ctk.CTkEntry(row, placeholder_text="g por unidad", width=120, fg_color="#1a1a1a", border_color="#444", text_color="white")
        entry_g.pack(side="left", padx=6)
        btn_quitar = ctk.CTkButton(row, text="Quitar", width=80, fg_color="#aa3333", hover_color="#cc5555", command=lambda r=row: self.quitar_color(r))
        btn_quitar.pack(side="right", padx=6)

        self.colores_rows.append((row, entry_nombre, entry_g))

    def cargar_impresoras(self):
        # Cargar impresoras del usuario para el combo
        try:
            lista = __import__('database').obtener_impresoras(self.user_id)
            nombres = []
            self.mapa_impresoras = {}
            for imp in lista:
                id_imp, nombre, marca, modelo = imp[0], imp[1], imp[2], imp[3]
                display = f"{nombre} ({marca} {modelo})"
                nombres.append(display)
                self.mapa_impresoras[display] = id_imp

            if nombres:
                self.combo_impresora.configure(values=nombres)
                self.combo_impresora.set(nombres[0])
            else:
                self.combo_impresora.configure(values=["Sin impresoras"])
                self.combo_impresora.set("Sin impresoras")
        except Exception:
            self.combo_impresora.configure(values=["Sin impresoras"])
            self.combo_impresora.set("Sin impresoras")

    def quitar_color(self, row):
        # eliminar fila y del listado
        for i, (r, n, g) in enumerate(self.colores_rows):
            if r == row:
                r.destroy()
                self.colores_rows.pop(i)
                return

    def calcular(self):
        nombre = self.entry_nombre.get() or "Pedido"
        unidades = self.entry_unidades.get() or "0"
        hs_unit = self.entry_hs_unit.get() or "0"
        min_unit = self.entry_min_unit.get() or "0"
        g_unit = self.entry_g_unit.get() or "0"
        precio_g = self.entry_precio_g.get() or "0"

        try:
            unidades = int(unidades)
            tiempo_unit = float(hs_unit) + (float(min_unit) / 60)
            g_unit = float(g_unit)
            precio_g = float(precio_g)
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos.")
            return

        # Si hay colores definidos, sobreescriben g_unit sumando por-color
        suma_colores = 0.0
        colores_detalle = []
        if self.colores_rows:
            for (_, entry_nombre, entry_g) in self.colores_rows:
                nom = entry_nombre.get() or "Color"
                try:
                    g = float(entry_g.get() or "0")
                except ValueError:
                    messagebox.showerror("Error", "Valores de gramos por color inválidos.")
                    return
                suma_colores += g
                colores_detalle.append((nom, g))

        gramos_por_unidad = suma_colores if suma_colores > 0 else g_unit

        total_gramos = gramos_por_unidad * unidades
        total_cost = total_gramos * precio_g
        total_horas = tiempo_unit * unidades

        # Si el usuario eligió una impresora, obtener su consumo y estimar costo energético
        impresora_sel = self.combo_impresora.get() if hasattr(self, 'combo_impresora') else None
        consumo_imp = None
        costo_energetico = None
        if impresora_sel and impresora_sel in self.mapa_impresoras:
            id_imp = self.mapa_impresoras[impresora_sel]
            # obtener impresora desde DB
            datos = None
            try:
                lista = __import__('database').obtener_impresoras(self.user_id)
                for imp in lista:
                    if imp[0] == id_imp:
                        datos = imp
                        break
            except Exception:
                datos = None

            if datos:
                # power_kw en posición 6
                power_kw = datos[6] if len(datos) > 6 else 0.0
                consumo_imp = power_kw
                try:
                    costo_energetico = total_horas * power_kw * float(config.COSTO_KW)
                except Exception:
                    costo_energetico = None


        # Convertir horas a H:MM
        horas_ent = int(total_horas)
        minutos_ent = int(round((total_horas - horas_ent) * 60))

        texto = f"Pedido: {nombre}\nCantidad: {unidades}\nTiempo total: {horas_ent}h {minutos_ent}m ({total_horas:.2f} hs)\nFilamento total: {total_gramos:.2f} g\nCosto estimado: {total_cost:.2f}\n"

        if colores_detalle:
            texto += "\nDesglose por color (g por unidad):\n"
            for nom, g in colores_detalle:
                texto += f" - {nom}: {g} g/unidad -> {g * unidades:.2f} g\n"

        if consumo_imp is not None:
            texto += f"\nImpresora seleccionada: {impresora_sel} -> Consumo: {consumo_imp:.2f} kW\n"
            if costo_energetico is not None:
                texto += f"Costo energético estimado para el pedido: {costo_energetico:.2f}\n"

        self.text_result.configure(text=texto)
