"""
Panel de control para gestionar bloqueo/habilitación de caminos entre estrellas.
Debido a cometas y meteoritos, los caminos pueden ser bloqueados/habilitados en cualquier momento.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from typing import Dict, List, Callable, Optional


class PanelControlCaminos(tk.Frame):
    """
    Panel para bloquear/habilitar caminos entre estrellas.
    Permite a los científicos gestionar la seguridad de las rutas.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#0b0c10")
        
        # Datos del JSON cargado
        self.data = None
        self.json_path = None
        
        # Mapeo de items del tree a referencias de caminos
        self.item_to_camino = {}
        
        # Callback para notificar cambios
        self.on_cambio_callback: Optional[Callable] = None
        
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz del panel"""
        
        # Título
        titulo = tk.Label(
            self,
            text="🚧 Control de Caminos",
            bg="#0b0c10",
            fg="#00eaff",
            font=("Orbitron", 14, "bold")
        )
        titulo.pack(pady=10)
        
        # Descripción
        desc = tk.Label(
            self,
            text="Bloquea/habilita caminos entre estrellas\ndebido a cometas y meteoritos",
            bg="#0b0c10",
            fg="#888",
            font=("Arial", 9),
            justify="center"
        )
        desc.pack(pady=5)
        
        # Frame de búsqueda y filtros
        frame_filtros = tk.Frame(self, bg="#0b0c10")
        frame_filtros.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_filtros, text="Filtrar por estrella:", bg="#0b0c10", fg="white").pack(side="left", padx=5)
        self.entry_filtro = tk.Entry(frame_filtros, width=20)
        self.entry_filtro.pack(side="left", padx=5)
        self.entry_filtro.bind("<KeyRelease>", lambda e: self._actualizar_lista())
        
        btn_limpiar = ttk.Button(frame_filtros, text="Limpiar", command=self._limpiar_filtro)
        btn_limpiar.pack(side="left", padx=5)
        
        # Frame para la lista de caminos
        frame_lista = tk.LabelFrame(
            self,
            text="Caminos Disponibles",
            bg="#0b0c10",
            fg="white",
            font=("Arial", 10, "bold")
        )
        frame_lista.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview para mostrar caminos
        columns = ("origen", "destino", "distancia", "estado")
        self.tree = ttk.Treeview(frame_lista, columns=columns, show="headings", height=15)
        
        self.tree.heading("origen", text="Estrella Origen")
        self.tree.heading("destino", text="Estrella Destino")
        self.tree.heading("distancia", text="Distancia")
        self.tree.heading("estado", text="Estado")
        
        self.tree.column("origen", width=150)
        self.tree.column("destino", width=150)
        self.tree.column("distancia", width=100)
        self.tree.column("estado", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # Frame de acciones
        frame_acciones = tk.Frame(self, bg="#0b0c10")
        frame_acciones.pack(fill="x", padx=10, pady=10)
        
        self.btn_bloquear = tk.Button(
            frame_acciones,
            text="🚫 Bloquear Camino",
            command=self._bloquear_seleccionado,
            bg="#ff4444",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            state="disabled"
        )
        self.btn_bloquear.pack(side="left", padx=5)
        
        self.btn_habilitar = tk.Button(
            frame_acciones,
            text="✅ Habilitar Camino",
            command=self._habilitar_seleccionado,
            bg="#44ff44",
            fg="black",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            state="disabled"
        )
        self.btn_habilitar.pack(side="left", padx=5)
        
        self.btn_guardar = tk.Button(
            frame_acciones,
            text="💾 Guardar Cambios",
            command=self._guardar_cambios,
            bg="#00eaff",
            fg="black",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            state="disabled"
        )
        self.btn_guardar.pack(side="right", padx=5)
        
        # Estadísticas
        self.label_stats = tk.Label(
            self,
            text="Caminos: 0 | Bloqueados: 0 | Habilitados: 0",
            bg="#0b0c10",
            fg="#888",
            font=("Arial", 9)
        )
        self.label_stats.pack(pady=5)
        
        # Bind para selección
        self.tree.bind("<<TreeviewSelect>>", self._on_seleccion_cambiada)
    
    def cargar_datos(self, json_path: str, data: dict):
        """
        Carga los datos del JSON de constelaciones.
        
        Args:
            json_path: Ruta del archivo JSON
            data: Datos parseados del JSON
        """
        self.json_path = json_path
        self.data = data
        self._actualizar_lista()
        self.btn_guardar.config(state="normal")
    
    def _actualizar_lista(self):
        """Actualiza la lista de caminos en el TreeView"""
        if not self.data:
            return
        
        # Limpiar árbol y mapeo
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.item_to_camino = {}
        
        # Obtener filtro
        filtro = self.entry_filtro.get().lower()
        
        # Mapear IDs a nombres
        id_a_nombre = {}
        for const in self.data.get("constellations", []):
            for star in const.get("starts", []):
                id_a_nombre[star["id"]] = star["label"]
        
        # Agregar caminos
        total = 0
        bloqueados = 0
        habilitados = 0
        
        for const in self.data.get("constellations", []):
            for star in const.get("starts", []):
                origen_nombre = star["label"]
                
                # Aplicar filtro
                if filtro and filtro not in origen_nombre.lower():
                    continue
                
                for link in star.get("linkedTo", []):
                    destino_id = link["starId"]
                    destino_nombre = id_a_nombre.get(destino_id, f"ID:{destino_id}")
                    distancia = link["distance"]
                    bloqueado = link.get("blocked", False)
                    
                    estado = "🚫 BLOQUEADO" if bloqueado else "✅ HABILITADO"
                    
                    # Agregar al tree
                    item_id = self.tree.insert(
                        "",
                        "end",
                        values=(origen_nombre, destino_nombre, f"{distancia} ly", estado),
                        tags=("bloqueado" if bloqueado else "habilitado",)
                    )
                    
                    # Guardar referencia al camino en el diccionario
                    self.item_to_camino[item_id] = {
                        'origen_id': star['id'],
                        'destino_id': destino_id
                    }
                    
                    total += 1
                    if bloqueado:
                        bloqueados += 1
                    else:
                        habilitados += 1
        
        # Aplicar colores
        self.tree.tag_configure("bloqueado", foreground="#ff4444")
        self.tree.tag_configure("habilitado", foreground="#44ff44")
        
        # Actualizar estadísticas
        self.label_stats.config(
            text=f"Caminos: {total} | Bloqueados: {bloqueados} | Habilitados: {habilitados}"
        )
    
    def _limpiar_filtro(self):
        """Limpia el filtro de búsqueda"""
        self.entry_filtro.delete(0, tk.END)
        self._actualizar_lista()
    
    def _on_seleccion_cambiada(self, event):
        """Maneja el cambio de selección en el tree"""
        seleccion = self.tree.selection()
        if seleccion:
            self.btn_bloquear.config(state="normal")
            self.btn_habilitar.config(state="normal")
        else:
            self.btn_bloquear.config(state="disabled")
            self.btn_habilitar.config(state="disabled")
    
    def _bloquear_seleccionado(self):
        """Bloquea el camino seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        for item_id in seleccion:
            self._cambiar_estado_camino(item_id, True)
        
        self._actualizar_lista()
        
        if self.on_cambio_callback:
            self.on_cambio_callback()
    
    def _habilitar_seleccionado(self):
        """Habilita el camino seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        for item_id in seleccion:
            self._cambiar_estado_camino(item_id, False)
        
        self._actualizar_lista()
        
        if self.on_cambio_callback:
            self.on_cambio_callback()
    
    def _cambiar_estado_camino(self, item_id: str, bloquear: bool):
        """
        Cambia el estado de bloqueo de un camino.
        
        Args:
            item_id: ID del item en el tree
            bloquear: True para bloquear, False para habilitar
        """
        if not self.data:
            return
        
        # Obtener referencia al camino desde el diccionario
        if item_id not in self.item_to_camino:
            return
        
        camino_ref = self.item_to_camino[item_id]
        origen_id = camino_ref['origen_id']
        destino_id = camino_ref['destino_id']
        
        # Buscar y modificar el camino en los datos
        for const in self.data.get("constellations", []):
            for star in const.get("starts", []):
                if star["id"] == origen_id:
                    for link in star.get("linkedTo", []):
                        if link["starId"] == destino_id:
                            link["blocked"] = bloquear
                            return
    
    def _guardar_cambios(self):
        """Guarda los cambios en el archivo JSON"""
        if not self.data or not self.json_path:
            messagebox.showwarning("Advertencia", "No hay datos para guardar")
            return
        
        try:
            # Guardar JSON
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", "Cambios guardados correctamente en:\n" + self.json_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
    
    def set_on_cambio_callback(self, callback: Callable):
        """
        Establece un callback que se llamará cuando se bloquee/habilite un camino.
        
        Args:
            callback: Función a llamar cuando haya cambios
        """
        self.on_cambio_callback = callback