import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from typing import Dict, Any


class ResearchEditor(tk.Toplevel):
    """Dialog para revisar y editar los parámetros de investigación por estrella."""

    def __init__(self, parent: tk.Tk, data: Dict[str, Any]):
        super().__init__(parent)
        self.title('Editor de investigación por estrella')
        self.geometry('700x420')
        self.parent = parent
        # trabajamos sobre la referencia del dict en memoria
        self.data = data

        frm = tk.Frame(self)
        frm.pack(fill='both', expand=True, padx=8, pady=8)

        cols = ('id', 'label', 'coord', 'research_cost', 'research_life', 'research_health')
        self.tree = ttk.Treeview(frm, columns=cols, show='headings', selectmode='browse')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120 if c not in ('label', 'research_health') else 180)
        self.tree.pack(side='left', fill='both', expand=True)

        scr = ttk.Scrollbar(frm, orient='vertical', command=self.tree.yview)
        scr.pack(side='left', fill='y')
        self.tree.configure(yscrollcommand=scr.set)

        right = tk.Frame(self)
        right.pack(side='right', fill='y', padx=8)

        tk.Label(right, text='ID').pack(anchor='w')
        self.var_id = tk.StringVar()
        tk.Entry(right, textvariable=self.var_id, state='readonly').pack(fill='x')

        tk.Label(right, text='Label').pack(anchor='w')
        self.var_label = tk.StringVar()
        tk.Entry(right, textvariable=self.var_label, state='readonly').pack(fill='x')

        tk.Label(right, text='Research energy cost / time').pack(anchor='w', pady=(8,0))
        self.var_cost = tk.DoubleVar(value=0.0)
        tk.Entry(right, textvariable=self.var_cost).pack(fill='x')

        tk.Label(right, text='Research life delta / time').pack(anchor='w', pady=(8,0))
        self.var_life = tk.DoubleVar(value=0.0)
        tk.Entry(right, textvariable=self.var_life).pack(fill='x')

        tk.Label(right, text='Research health delta / time (int)').pack(anchor='w', pady=(8,0))
        self.var_health = tk.IntVar(value=0)
        tk.Entry(right, textvariable=self.var_health).pack(fill='x')

        btn_frame = tk.Frame(right)
        btn_frame.pack(fill='x', pady=12)
        ttk.Button(btn_frame, text='Guardar cambios', command=self.on_save).pack(fill='x')
        ttk.Button(btn_frame, text='Guardar JSON...', command=self.on_save_file).pack(fill='x', pady=(6,0))
        ttk.Button(btn_frame, text='Cerrar', command=self.destroy).pack(fill='x', pady=(6,0))

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        self.populate()

    def populate(self):
        # limpiar
        for r in self.tree.get_children():
            self.tree.delete(r)
        # llenar con estrellas (agrupar por constelación)
        for c in self.data.get('constellations', []):
            for s in c.get('starts', []):
                sid = int(s.get('id'))
                label = s.get('label', '')
                coord = s.get('coordenates', {})
                coord_str = f"{coord.get('x',0)},{coord.get('y',0)}"
                cost = s.get('research_energy_cost_per_time', 0)
                life = s.get('research_life_delta_per_time', 0)
                health = s.get('research_health_delta_per_time', 0)
                self.tree.insert('', 'end', iid=str(sid), values=(sid, label, coord_str, cost, life, health))

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        sid = int(sel[0])
        star = self.find_star_by_id(sid)
        if not star:
            return
        self.var_id.set(str(star.get('id')))
        self.var_label.set(star.get('label',''))
        self.var_cost.set(float(star.get('research_energy_cost_per_time', 0)))
        self.var_life.set(float(star.get('research_life_delta_per_time', 0)))
        self.var_health.set(int(star.get('research_health_delta_per_time', 0)))

    def find_star_by_id(self, sid: int):
        for c in self.data.get('constellations', []):
            for s in c.get('starts', []):
                if int(s.get('id')) == sid:
                    return s
        return None

    def on_save(self):
        sid = self.var_id.get()
        if not sid:
            messagebox.showinfo('Info', 'Selecciona una estrella primero')
            return
        star = self.find_star_by_id(int(sid))
        if not star:
            messagebox.showerror('Error', 'No se encontró la estrella')
            return
        # validar y guardar
        try:
            cost = float(self.var_cost.get())
            life = float(self.var_life.get())
            health = int(self.var_health.get())
        except Exception:
            messagebox.showerror('Error', 'Valores inválidos, deben ser numéricos')
            return
        star['research_energy_cost_per_time'] = cost
        star['research_life_delta_per_time'] = life
        star['research_health_delta_per_time'] = health
        # actualizar fila (incluye health)
        self.tree.item(str(star['id']), values=(star['id'], star.get('label',''), f"{star.get('coordenates',{}).get('x',0)},{star.get('coordenates',{}).get('y',0)}", cost, life, health))
        messagebox.showinfo('Guardado', f'Parámetros guardados para estrella {star.get("label")}')

    def on_save_file(self):
        path = filedialog.asksaveasfilename(title='Guardar constelaciones como...', defaultextension='.json', filetypes=[('JSON','*.json')])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo('Guardado', f'Archivo guardado en {path}')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo guardar el archivo:\n{e}')
