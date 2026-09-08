"""Small manual screen for the one real Restoration recommendation flow."""

from __future__ import annotations

from pathlib import Path

from .druid_restoration_recommendation import (
    DruidRestorationRecommendationError,
    run_druid_restoration_recommendation,
)


class TkDruidRestorationWorkspace:
    """The player explicitly pastes the export and chooses both local paths."""

    def __init__(self, root: Path) -> None:
        import tkinter as tk
        from tkinter import filedialog, ttk

        self._root = root
        self._filedialog = filedialog
        self._tk = tk
        self._window = tk.Tk()
        self._window.title("DpsLab — Comparación de Restauración")
        self._window.geometry("760x560")
        self._window.minsize(620, 440)
        self._simc = tk.StringVar()
        self._addon = tk.StringVar()
        self._status = tk.StringVar(value="Pega la exportación real y elige SimulationCraft y el addon instalado.")
        frame = ttk.Frame(self._window, padding=18)
        frame.grid(sticky="nsew")
        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)
        ttk.Label(frame, text="Comparación real — Druida Restauración", font=("Segoe UI", 14, "bold")).grid(column=0, row=0, columnspan=3, sticky="w")
        ttk.Label(frame, text="SimulationCraft (simc.exe)").grid(column=0, row=1, pady=(14, 4), sticky="w")
        ttk.Entry(frame, textvariable=self._simc).grid(column=1, row=1, pady=(14, 4), sticky="ew")
        ttk.Button(frame, text="Elegir", command=self._choose_simc).grid(column=2, row=1, padx=(8, 0), pady=(14, 4))
        ttk.Label(frame, text="Carpeta del addon DpsLab").grid(column=0, row=2, pady=4, sticky="w")
        ttk.Entry(frame, textvariable=self._addon).grid(column=1, row=2, pady=4, sticky="ew")
        ttk.Button(frame, text="Elegir", command=self._choose_addon).grid(column=2, row=2, padx=(8, 0), pady=4)
        ttk.Label(frame, text="Exportación manual de DpsLab").grid(column=0, row=4, columnspan=3, pady=(12, 4), sticky="w")
        self._export = tk.Text(frame, height=16, wrap="word")
        self._export.grid(column=0, row=5, columnspan=3, sticky="nsew")
        ttk.Button(frame, text="Ejecutar comparación real", command=self._run).grid(column=0, row=6, pady=(12, 4), sticky="w")
        ttk.Label(frame, textvariable=self._status, wraplength=700).grid(column=0, row=7, columnspan=3, sticky="w")

    def _choose_simc(self) -> None:
        selected = self._filedialog.askopenfilename(title="Selecciona simc.exe", filetypes=[("SimulationCraft", "simc.exe"), ("Todos", "*")])
        if selected:
            self._simc.set(selected)

    def _choose_addon(self) -> None:
        selected = self._filedialog.askdirectory(title="Selecciona la carpeta DpsLab del addon")
        if selected:
            self._addon.set(selected)

    def _run(self) -> None:
        self._status.set("Ejecutando las dos simulaciones reales…")
        self._window.update_idletasks()
        try:
            result = run_druid_restoration_recommendation(
                self._export.get("1.0", "end-1c"),
                Path(self._simc.get()),
                Path(self._addon.get()),
                root=self._root,
            )
        except (DruidRestorationRecommendationError, OSError, ValueError) as exc:
            self._status.set(f"No se generó recomendación: {exc}")
            return
        self._status.set(f"{result.message} Ejecuta /reload y luego /dpslab result en WoW.")

    def run(self) -> None:
        self._window.mainloop()
