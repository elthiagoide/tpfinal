import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import json
from datetime import datetime
try:
    from tkcalendar import DateEntry
    CALENDARIO_DISPONIBLE = True
except ImportError:
    CALENDARIO_DISPONIBLE = False
import config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

# --- CLASE VENTANA DETALLE (POPUP) ---
class VentanaDetalle(ctk.CTkToplevel):
    def __init__(self, parent, datos_proyecto):
        super().__init__(parent)

        # Configuración Ventana: NO usar overrideredirect para evitar problemas de visualización
        self.transient(parent)
        try:
            self.attributes('-topmost', True)
        except: pass
        bg_color = config.COLOR_FONDO_APP
        if isinstance(bg_color, tuple): bg_color = bg_color[1]
        self.configure(fg_color=bg_color)

        # Centrar
        w, h = 500, 550
        x = (self.winfo_screenwidth()/2) - (w/2)
        y = (self.winfo_screenheight()/2) - (h/2)
        self.geometry(f"{w}x{h}+{int(x)}+{int(y)}")

        # Frame Principal con borde
        self.frame = ctk.CTkFrame(self, fg_color=bg_color, border_width=2, border_color=config.COLOR_ACENTO, corner_radius=0)
        self.frame.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(self.frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(header, text="Detalle del Proyecto", font=config.FONT_SUBTITULO, text_color="white").pack(side="left")
        ctk.CTkButton(header, text="✕", width=30, fg_color="transparent", hover_color="#333", text_color="gray", 
                      font=("Arial", 16, "bold"), command=self.destroy).pack(side="right")

        # Scroll de contenido
        scroll = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=5)

        # Parsing de datos (JSON a Texto legible)
        try:
            # Intentamos cargar JSON, si falla usamos diccionarios vacíos
            mats = json.loads(datos_proyecto['materiales']) if isinstance(datos_proyecto['materiales'], str) else {}
            flota = json.loads(datos_proyecto['flota']) if isinstance(datos_proyecto['flota'], str) else []
        except:
            mats = {}
            flota = []

        # 1. Materiales
        ctk.CTkLabel(scroll, text="MATERIALES NECESARIOS:", font=config.FONT_BOTON, text_color=config.COLOR_ACENTO).pack(anchor="w", padx=10, pady=(10, 5))
        if mats:
            for color, gr in mats.items():
                ctk.CTkLabel(scroll, text=f"• {color}: {float(gr):.1f} gr totales", font=config.FONT_TEXTO, text_color="white").pack(anchor="w", padx=20)
        else:
            ctk.CTkLabel(scroll, text="• Sin materiales registrados", font=config.FONT_TEXTO, text_color="gray").pack(anchor="w", padx=20)

        # 2. Maquinaria
        ctk.CTkLabel(scroll, text="FLOTA ASIGNADA:", font=config.FONT_BOTON, text_color=config.COLOR_ACENTO).pack(anchor="w", padx=10, pady=(20, 5))
        if isinstance(flota, list) and len(flota) > 0:
            for maq in flota:
                nom = maq.get('nombre') or maq.get('display') or "Máquina"
                ctk.CTkLabel(scroll, text=f"• {nom}", font=config.FONT_TEXTO, text_color="white").pack(anchor="w", padx=20)
        else:
            ctk.CTkLabel(scroll, text="• Sin máquinas asignadas", font=config.FONT_TEXTO, text_color="gray").pack(anchor="w", padx=20)

        # 3. Financiero
        ctk.CTkLabel(scroll, text="FINANZAS:", font=config.FONT_BOTON, text_color=config.COLOR_ACENTO).pack(anchor="w", padx=10, pady=(20, 5))
        
        ganancia = datos_proyecto.get('ganancia', 0)
        energia = datos_proyecto.get('energia', 0)
        precio_u = datos_proyecto.get('precio_unit', 0)
        meta = datos_proyecto.get('meta', 0)
        ingreso_est = precio_u * meta

        ctk.CTkLabel(scroll, text=f"• Precio Venta Unitario: ${precio_u:.2f}", font=config.FONT_TEXTO, text_color="white").pack(anchor="w", padx=20)
        ctk.CTkLabel(scroll, text=f"• Ingreso Total Est.: ${ingreso_est:.2f}", font=config.FONT_TEXTO, text_color="white").pack(anchor="w", padx=20)
        ctk.CTkLabel(scroll, text=f"• Costo Energía: -${energia:.2f}", font=config.FONT_TEXTO, text_color="#e74c3c").pack(anchor="w", padx=20)
        
        ctk.CTkLabel(scroll, text=f"• GANANCIA FINAL: ${ganancia:.2f}", font=config.FONT_SUBTITULO, text_color="#ffd966").pack(anchor="w", padx=20, pady=10)

        # Delivery (editable)
        try:
            fecha_actual = datos_proyecto.get('delivery_date')
        except:
            fecha_actual = None
        ctk.CTkLabel(scroll, text=f"• Fecha de Entrega: {fecha_actual if fecha_actual else '-'}", font=config.FONT_TEXTO, text_color="white").pack(anchor="w", padx=20, pady=(6,2))
        ctk.CTkButton(scroll, text="Extender plazo", width=140, fg_color="#3a7bd5", hover_color="#285a9e", command=lambda: self._abrir_extender_plazo(parent, datos_proyecto)).pack(anchor="w", padx=20, pady=(4,12))

        # Botón Cerrar Abajo
        ctk.CTkButton(self.frame, text="Cerrar", fg_color=config.COLOR_ACENTO, font=config.FONT_BOTON, command=self.destroy).pack(pady=20)
        try:
            self.lift()
            self.grab_set()
        except: pass

    def _abrir_extender_plazo(self, parent, datos_proyecto):
        # Popup simple para seleccionar nueva fecha
        dlg = ctk.CTkToplevel(self)
        dlg.title("Extender plazo")
        dlg.geometry("360x180")
        dlg.transient(self)
        dlg.grab_set()
        ctk.CTkLabel(dlg, text="Selecciona nueva fecha de entrega:", font=config.FONT_TEXTO, text_color="white").pack(pady=(12,6))
        if CALENDARIO_DISPONIBLE:
            cal = DateEntry(dlg, width=16, background='#00965e', foreground='white', borderwidth=2, font=("Arial", 12))
            cal.pack(pady=6)
        else:
            ent = ctk.CTkEntry(dlg, placeholder_text="AAAA-MM-DD")
            ent.pack(pady=6)

        def on_guardar():
            if CALENDARIO_DISPONIBLE:
                fecha_str = cal.get_date().strftime("%Y-%m-%d")
            else:
                fecha_str = ent.get() or datetime.now().strftime("%Y-%m-%d")
            ok = database.actualizar_fecha_entrega(datos_proyecto.get('id'), fecha_str)
            if ok:
                messagebox.showinfo("Guardado", "Fecha de entrega actualizada.")
                try:
                    parent.cargar_lista()
                except: pass
                dlg.destroy()
                try: self.destroy()
                except: pass
            else:
                messagebox.showerror("Error", "No se pudo actualizar la fecha.")

        ctk.CTkButton(dlg, text="Guardar", fg_color=config.COLOR_ACENTO, command=on_guardar).pack(pady=(8,4))
        ctk.CTkButton(dlg, text="Cancelar", fg_color="transparent", command=dlg.destroy).pack()


# --- VISTA PRINCIPAL ---
class VistaAgenda(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP)
        self.user_id = user_id

        # Título
        ctk.CTkLabel(self, text="Agenda - Proyectos Guardados", font=config.FONT_TITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(20, 10))

        # Filtros
        frame_filter = ctk.CTkFrame(self, fg_color="transparent")
        frame_filter.pack(fill="x", padx=30, pady=5)
        
        ctk.CTkLabel(frame_filter, text="Orden:", font=config.FONT_TEXTO, text_color="gray").pack(side="left", padx=5)
        self.combo_sort = ctk.CTkComboBox(frame_filter, values=["Fecha: más reciente", "Fecha: más antigua", "Mayor Ganancia"], 
                                          font=config.FONT_TEXTO, width=180)
        self.combo_sort.pack(side="left", padx=5)
        
        ctk.CTkButton(frame_filter, text="Actualizar", width=100, fg_color="#3a7bd5", font=config.FONT_BOTON, 
                      command=self.cargar_lista).pack(side="left", padx=10)

        # Scroll
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.cargar_lista()

    def cargar_lista(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        # Obtener criterio
        criterio = self.combo_sort.get()
        order_sql = "ORDER BY created_at DESC"
        if "antigua" in criterio: order_sql = "ORDER BY created_at ASC"
        if "Ganancia" in criterio: order_sql = "ORDER BY ganancia DESC"

        proyectos = database.obtener_proyectos_agenda(self.user_id, order_by=order_sql)
        
        if not proyectos:
            ctk.CTkLabel(self.scroll, text="No hay proyectos en la agenda.", font=config.FONT_TITULO, text_color="gray").pack(pady=50)
            return

        for p in proyectos:
            # MAPA EXACTO DE INDICES DE LA BASE DE DATOS
            # 0:id, 1:user_id, 2:nombre, 3:meta, 4:materiales, 5:flota, 
            # 6:tiempo_hs, 7:costo_energia, 8:precio_unit, 9:delivery_date, 
            # 10:ganancia, 11:estado, 12:created_at
            
            try:
                pid = p[0]
                nombre = p[2]
                meta = p[3]
                materiales_raw = p[4]
                flota_raw = p[5]
                tiempo_hs = p[6]
                energia = p[7]
                precio_u = p[8]
                fecha_entrega = p[9]
                ganancia = p[10]
            except IndexError:
                continue # Saltar registros corruptos

            # Si el proyecto ya no está pendiente, lo ignoramos en la lista
            estado = None
            try:
                # algunos esquemas llevan 'estado' en el índice 12, otros en 11
                candidatos = []
                if len(p) > 12: candidatos.append(p[12])
                if len(p) > 11: candidatos.append(p[11])
                # Normalizar y decidir si ya está terminado
                terminado = False
                for c in candidatos:
                    try:
                        s = str(c).lower()
                        if s.startswith('term') or s.startswith('realiz') or s.startswith('done'):
                            terminado = True
                            break
                    except:
                        pass
                if terminado:
                    continue
            except:
                pass

            # --- TARJETA ---
            card = ctk.CTkFrame(self.scroll, fg_color=config.COLOR_TARJETA, corner_radius=10, 
                                border_width=2, border_color=config.COLOR_ACENTO)
            card.pack(fill="x", pady=8, padx=5)

            # Fila 1: Título y Cantidad
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(10, 5))
            
            ctk.CTkLabel(header, text=f"{nombre} — {meta} u", font=config.FONT_SUBTITULO, text_color="white").pack(side="left")
            
            # Fila 2: Detalles (Tiempo y Vencimiento)
            try:
                t_val = int(float(tiempo_hs)) # Asegurar conversión segura
            except: t_val = 0
            
            info_text = f"Hs Máquina: {t_val}h | Entrega: {fecha_entrega}"
            
            # Calcular vencimiento
            color_fecha = "gray"
            texto_extra = ""
            try:
                if fecha_entrega and len(str(fecha_entrega)) >= 10:
                    dt_entrega = datetime.strptime(str(fecha_entrega)[:10], "%Y-%m-%d")
                    delta = dt_entrega - datetime.now()
                    dias = delta.days
                    if dias < 0:
                        texto_extra = f" (vencido hace {abs(dias)}d)"
                        color_fecha = "#e74c3c" # Rojo
                    else:
                        texto_extra = f" (faltan {dias}d)"
                        color_fecha = "#f1c40f" # Amarillo/Naranja
            except: pass

            info_row = ctk.CTkFrame(card, fg_color="transparent")
            info_row.pack(fill="x", padx=15, pady=(0, 10))
            
            ctk.CTkLabel(info_row, text=info_text, font=config.FONT_TEXTO, text_color="gray").pack(side="left")
            ctk.CTkLabel(info_row, text=texto_extra, font=config.FONT_TEXTO, text_color=color_fecha).pack(side="left")
            ctk.CTkLabel(info_row, text=f" | Ganancia: ${float(ganancia):.2f}", font=config.FONT_TEXTO, text_color="white").pack(side="left")

            # Fila 3: Botones
            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(fill="x", padx=15, pady=(0, 15))

            # Datos para pasar al detalle
            datos_dict = {
                "id": pid,
                "materiales": materiales_raw,
                "flota": flota_raw,
                "ganancia": float(ganancia),
                "energia": float(energia),
                "precio_unit": float(precio_u),
                "meta": int(meta),
                "delivery_date": fecha_entrega
            }

            # Botón Ver Detalle (Azul)
            ctk.CTkButton(btn_row, text="Ver detalle", width=100, height=32, 
                          fg_color="#3a7bd5", hover_color="#285a9e", font=config.FONT_BOTON,
                          command=lambda d=datos_dict: VentanaDetalle(self, d)).pack(side="right", padx=5)

            # Botón Realizar (Verde)
            ctk.CTkButton(btn_row, text="Realizar trabajo", width=120, height=32, 
                          fg_color=config.COLOR_ACENTO, hover_color=config.COLOR_ACENTO_HOVER, font=config.FONT_BOTON,
                          command=lambda i=pid: self.realizar_trabajo(i)).pack(side="right", padx=5)

            # Botón Eliminar (Rojo)
            ctk.CTkButton(btn_row, text="Eliminar", width=90, height=32, 
                          fg_color="#e74c3c", hover_color="#c0392b", font=config.FONT_BOTON,
                          command=lambda i=pid: self.eliminar(i)).pack(side="right", padx=5)

    def eliminar(self, pid):
        if messagebox.askyesno("Confirmar", "¿Eliminar este proyecto de la agenda?"):
            database.eliminar_pedido(pid) 
            self.cargar_lista()

    def realizar_trabajo(self, pid):
        if messagebox.askyesno("Completar", "¿Marcar trabajo como realizado? (Se archivará) "):
            try:
                ok = database.archivar_proyecto_como_impresion(pid)
                if ok:
                    messagebox.showinfo("Listo", "Trabajo archivado y marcado como terminado.")
                else:
                    messagebox.showerror("Error", "No se pudo archivar el proyecto.")
                self.cargar_lista()
            except Exception as e:
                messagebox.showerror("Error", str(e))