"""
Panel para mostrar reportes y estadísticas de viajes.
Punto 5 del proyecto: reportes finales.
"""
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Any, Optional


class PanelReportes(ttk.Frame):
	"""Panel para gestionar y mostrar reportes de viajes.

	Este panel mantiene una lista de reportes (cada reporte es un dict con
	información de la simulación). Funcionalidades principales:
	- Mostrar lista de reportes disponibles
	- Mostrar detalles del reporte seleccionado (JSON formateado)
	- Exportar reporte seleccionado a JSON o CSV
	- Importar/guardar múltiples reportes

	Estructura de ejemplo de un `report` (libre):
	{
		"id": "run-2025-11-08-01",
		"route": [1,2,3,5],
		"visited": [{"starId":1, "time":0, "life":100, "energy":50}, ...],
		"total_life_lost": 42.3,
		"total_energy_used": 120.0,
		"death": False,
		"notes": "..."
	}
	"""

	def __init__(self, parent, *args, **kwargs):
		super().__init__(parent, *args, **kwargs)
		self.reports: List[Dict[str, Any]] = []
		self._build_ui()

	def _build_ui(self) -> None:
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=3)
		self.rowconfigure(0, weight=1)

		# Left: list of reports
		left = ttk.Frame(self)
		left.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
		left.rowconfigure(0, weight=1)
		left.columnconfigure(0, weight=1)

		self.lb_reports = tk.Listbox(left, exportselection=False)
		self.lb_reports.grid(row=0, column=0, sticky="nsew")
		self.lb_reports.bind("<<ListboxSelect>>", self._on_select)

		scroll = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.lb_reports.yview)
		scroll.grid(row=0, column=1, sticky="ns")
		self.lb_reports.config(yscrollcommand=scroll.set)

		btn_frame = ttk.Frame(left)
		btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6,0))
		ttk.Button(btn_frame, text="Importar JSON", command=self.import_from_file).grid(row=0, column=0, padx=2)
		ttk.Button(btn_frame, text="Exportar seleccionado (JSON)", command=self.export_selected_json).grid(row=0, column=1, padx=2)
		ttk.Button(btn_frame, text="Exportar (CSV)", command=self.export_selected_csv).grid(row=0, column=2, padx=2)
		ttk.Button(btn_frame, text="Borrar seleccionado", command=self.delete_selected).grid(row=0, column=3, padx=2)

		# Right: details
		right = ttk.Frame(self)
		right.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
		right.rowconfigure(0, weight=1)
		right.columnconfigure(0, weight=1)

		self.txt_details = tk.Text(right, wrap="none", state="disabled")
		self.txt_details.grid(row=0, column=0, sticky="nsew")

		vscroll = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.txt_details.yview)
		vscroll.grid(row=0, column=1, sticky="ns")
		self.txt_details.config(yscrollcommand=vscroll.set)

		hscroll = ttk.Scrollbar(right, orient=tk.HORIZONTAL, command=self.txt_details.xview)
		hscroll.grid(row=1, column=0, sticky="ew")
		self.txt_details.config(xscrollcommand=hscroll.set)

		bottom = ttk.Frame(right)
		bottom.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6,0))
		ttk.Button(bottom, text="Guardar todos (.json)", command=self.save_all).grid(row=0, column=0, padx=2)
		ttk.Button(bottom, text="Limpiar lista", command=self.clear_reports).grid(row=0, column=1, padx=2)

	# ---- Report management API ----
	def add_report(self, report: Dict[str, Any]) -> None:
		"""Añade un reporte y lo muestra en la lista."""
		self.reports.append(report)
		title = self._report_title(report)
		self.lb_reports.insert(tk.END, title)

	def _report_title(self, report: Dict[str, Any]) -> str:
		rid = report.get("id") or report.get("timestamp") or f"run-{len(self.reports)+1}"
		summary = report.get("notes") or report.get("summary") or f"stars:{len(report.get('visited', []))}"
		return f"{rid} — {summary}"

	def get_selected_index(self) -> Optional[int]:
		sel = self.lb_reports.curselection()
		if not sel:
			return None
		return int(sel[0])

	def get_selected_report(self) -> Optional[Dict[str, Any]]:
		idx = self.get_selected_index()
		if idx is None:
			return None
		return self.reports[idx]

	def _on_select(self, _ev=None) -> None:
		r = self.get_selected_report()
		if r is None:
			self._set_details_text("")
			return
		formatted = json.dumps(r, indent=2, ensure_ascii=False)
		self._set_details_text(formatted)

	def _set_details_text(self, text: str) -> None:
		self.txt_details.config(state="normal")
		self.txt_details.delete("1.0", tk.END)
		self.txt_details.insert(tk.END, text)
		self.txt_details.config(state="disabled")

	# ---- IO ----
	def import_from_file(self) -> None:
		path = filedialog.askopenfilename(title="Importar reportes JSON", filetypes=[("JSON files","*.json"), ("All","*")])
		if not path:
			return
		try:
			with open(path, "r", encoding="utf-8") as f:
				data = json.load(f)
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
			return
		if isinstance(data, dict):
			# assume single report or wrapper
			if "reports" in data and isinstance(data["reports"], list):
				for r in data["reports"]:
					self.add_report(r)
			else:
				self.add_report(data)
		elif isinstance(data, list):
			for r in data:
				self.add_report(r)
		else:
			messagebox.showwarning("Formato desconocido", "El JSON seleccionado no contiene reportes válidos.")

	def save_all(self) -> None:
		if not self.reports:
			messagebox.showinfo("Sin reportes", "No hay reportes para guardar.")
			return
		path = filedialog.asksaveasfilename(title="Guardar reportes como", defaultextension=".json", filetypes=[("JSON files","*.json")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				json.dump({"reports": self.reports}, f, ensure_ascii=False, indent=2)
			messagebox.showinfo("Guardado", f"Reportes guardados en {path}")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def export_selected_json(self) -> None:
		r = self.get_selected_report()
		if r is None:
			messagebox.showinfo("Selecciona un reporte", "Selecciona un reporte para exportar.")
			return
		path = filedialog.asksaveasfilename(title="Exportar reporte JSON", defaultextension=".json", filetypes=[("JSON files","*.json")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				json.dump(r, f, ensure_ascii=False, indent=2)
			messagebox.showinfo("Exportado", f"Reporte exportado a {path}")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo exportar: {e}")

	def export_selected_csv(self) -> None:
		# Simple CSV: flatten visited list (if exists) into rows: starId,time,life,energy
		r = self.get_selected_report()
		if r is None:
			messagebox.showinfo("Selecciona un reporte", "Selecciona un reporte para exportar.")
			return
		visited = r.get("visited") or []
		if not visited:
			messagebox.showinfo("Sin datos", "El reporte no contiene información de visitas para exportar a CSV.")
			return
		path = filedialog.asksaveasfilename(title="Exportar reporte CSV", defaultextension=".csv", filetypes=[("CSV files","*.csv")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				# header
				f.write("starId,time,life,energy,notes\n")
				for v in visited:
					sid = v.get("starId")
					time = v.get("time")
					life = v.get("life")
					energy = v.get("energy") if v.get("energy") is not None else v.get("energy_used")
					notes = str(v.get("notes", "")).replace('\n', ' ')
					f.write(f"{sid},{time},{life},{energy},{notes}\n")
			messagebox.showinfo("Exportado", f"CSV exportado a {path}")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo exportar CSV: {e}")

	def delete_selected(self) -> None:
		idx = self.get_selected_index()
		if idx is None:
			return
		del self.reports[idx]
		self.lb_reports.delete(idx)
		self._set_details_text("")

	def clear_reports(self) -> None:
		self.reports.clear()
		self.lb_reports.delete(0, tk.END)
		self._set_details_text("")
