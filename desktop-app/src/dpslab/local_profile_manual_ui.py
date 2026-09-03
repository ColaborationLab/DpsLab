"""Explicit, local-only Tk workspace for one protected character profile.

The module deliberately has no source discovery or default snapshot reader.
A caller may supply an already parsed, in-memory snapshot only after a user
requests a preview.  That boundary keeps this screen independent of WoW, the
addon, filesystem watchers, networking, and background collection.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .addon_profile_manual_transfer import (
    CREATE_CONFIRMATION,
    PREVIEW_CONFIRMATION,
    REPLACE_CONFIRMATION,
    LocalDisplayIdentity,
    ManualTransferPreview,
    apply_manual_identity_transfer,
    preview_manual_identity_transfer,
)
from .local_character_context_profile import (
    CharacterContextProfileError,
    DataProtector,
    clear_all_profiles,
    delete_selected_profile,
    inspect_profile,
)


DELETE_CONFIRMATION = "DELETE_LOCAL_CHARACTER_CONTEXT_PROFILE"
CLEAR_CONFIRMATION = "CLEAR_LOCAL_CHARACTER_CONTEXT_PROFILE"


@dataclass(frozen=True, repr=False)
class LocalProfileWorkspaceState:
    """Bounded visible state; profile identifiers and raw inputs remain private."""

    state: str
    reason: str | None
    display_name: str | None
    realm: str | None
    preview_ready: bool
    can_create: bool
    can_replace: bool
    can_delete: bool
    can_clear: bool


class LocalProfileManualController:
    """Headless controller for explicit profile inspection and transfer actions."""

    def __init__(
        self,
        root: Path,
        protector: DataProtector,
        *,
        expected_build: int,
        expected_interface_version: int,
        now_epoch: Callable[[], int],
        snapshot_supplier: Callable[[], object] | None = None,
    ) -> None:
        self._root = root
        self._protector = protector
        self._expected_build = expected_build
        self._expected_interface_version = expected_interface_version
        self._now_epoch = now_epoch
        self._snapshot_supplier = snapshot_supplier
        self._selected_profile_id: str | None = None
        self._preview: ManualTransferPreview | None = None

    @staticmethod
    def _state(
        state: str,
        reason: str | None = None,
        *,
        display_name: str | None = None,
        realm: str | None = None,
        preview_ready: bool = False,
        selected: bool = False,
    ) -> LocalProfileWorkspaceState:
        return LocalProfileWorkspaceState(
            state,
            reason,
            display_name,
            realm,
            preview_ready,
            preview_ready and not selected,
            preview_ready and selected,
            selected,
            selected,
        )

    def inspect(self) -> LocalProfileWorkspaceState:
        """Inspect only when the caller explicitly asks; never scan for roots."""
        self._preview = None
        self._selected_profile_id = None
        try:
            stored = inspect_profile(self._root, self._protector)
        except CharacterContextProfileError:
            return self._state("profile_unavailable", "profile_unavailable")
        if stored.state == "absent":
            return self._state("no_selected_profile")
        if stored.state != "selected" or stored.profile_id is None or stored.context is None:
            return self._state("profile_unavailable", "profile_unavailable")
        self._selected_profile_id = stored.profile_id
        return self._state(
            "selected_profile_available",
            display_name=stored.context.display_name,
            realm=stored.context.realm,
            selected=True,
        )

    def preview(self, display_name: object, realm: object, confirmation: object) -> LocalProfileWorkspaceState:
        """Request exactly one in-memory snapshot from the injected supplier."""
        self._preview = None
        if confirmation != PREVIEW_CONFIRMATION:
            return self._state("preview_unavailable", "consent_required", selected=self._selected_profile_id is not None)
        if self._snapshot_supplier is None:
            return self._state("preview_unavailable", "source_unavailable", selected=self._selected_profile_id is not None)
        try:
            snapshot = self._snapshot_supplier()
            now = self._now_epoch()
        except Exception:
            return self._state("preview_unavailable", "source_unavailable", selected=self._selected_profile_id is not None)
        candidate = preview_manual_identity_transfer(
            snapshot,
            LocalDisplayIdentity(display_name, realm),
            expected_build=self._expected_build,
            expected_interface_version=self._expected_interface_version,
            now_epoch=now,
            confirmation=confirmation,
        )
        if candidate.state != "ready":
            return self._state("preview_unavailable", candidate.reason, selected=self._selected_profile_id is not None)
        self._preview = candidate
        return self._state(
            "preview_ready",
            preview_ready=True,
            selected=self._selected_profile_id is not None,
        )

    def create(self, confirmation: object) -> LocalProfileWorkspaceState:
        result = apply_manual_identity_transfer(
            self._root, self._preview, self._protector, operation="create", confirmation=confirmation
        )
        if result.state != "created":
            return self._state("action_rejected", result.reason, selected=self._selected_profile_id is not None)
        return self.inspect()

    def replace(self, confirmation: object) -> LocalProfileWorkspaceState:
        result = apply_manual_identity_transfer(
            self._root,
            self._preview,
            self._protector,
            operation="replace",
            confirmation=confirmation,
            selected_profile_id=self._selected_profile_id,
        )
        if result.state != "replaced":
            return self._state("action_rejected", result.reason, selected=self._selected_profile_id is not None)
        return self.inspect()

    def delete(self, confirmation: object) -> LocalProfileWorkspaceState:
        if confirmation != DELETE_CONFIRMATION or self._selected_profile_id is None:
            return self._state("action_rejected", "delete_confirmation_required", selected=self._selected_profile_id is not None)
        try:
            delete_selected_profile(self._root, self._selected_profile_id, self._protector)
        except CharacterContextProfileError:
            return self._state("action_rejected", "profile_unavailable", selected=self._selected_profile_id is not None)
        return self.inspect()

    def clear_all(self, confirmation: object) -> LocalProfileWorkspaceState:
        if confirmation != CLEAR_CONFIRMATION:
            return self._state("action_rejected", "clear_confirmation_required", selected=self._selected_profile_id is not None)
        try:
            clear_all_profiles(self._root, confirmation)
        except CharacterContextProfileError:
            return self._state("action_rejected", "profile_unavailable", selected=self._selected_profile_id is not None)
        return self.inspect()


class TkLocalProfileManualWorkspace:
    """A visible adapter; the caller owns root selection and Tk lifecycle."""

    def __init__(self, controller: LocalProfileManualController) -> None:
        import tkinter as tk
        from tkinter import messagebox, ttk

        self._controller = controller
        self._tk = tk
        self._messagebox = messagebox
        self._window = tk.Tk()
        self._window.title("DpsLab — Perfil local")
        self._window.geometry("680x430")
        self._window.minsize(560, 360)
        self._window.columnconfigure(0, weight=1)
        self._status = tk.StringVar(value="Sin inspección. Selecciona Inspeccionar perfil.")
        self._name = tk.StringVar()
        self._realm = tk.StringVar()
        self._identity = tk.StringVar(value="La identidad se muestra solo tras inspección protegida.")
        frame = ttk.Frame(self._window, padding=20)
        frame.grid(sticky="nsew")
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Espacio local de perfil", font=("Segoe UI", 14, "bold")).grid(column=0, row=0, columnspan=2, sticky="w")
        ttk.Label(frame, textvariable=self._identity).grid(column=0, row=1, columnspan=2, pady=(8, 14), sticky="w")
        ttk.Label(frame, text="Nombre local").grid(column=0, row=2, sticky="w")
        ttk.Entry(frame, textvariable=self._name).grid(column=1, row=2, sticky="ew")
        ttk.Label(frame, text="Reino local").grid(column=0, row=3, pady=8, sticky="w")
        ttk.Entry(frame, textvariable=self._realm).grid(column=1, row=3, pady=8, sticky="ew")
        buttons = ttk.Frame(frame)
        buttons.grid(column=0, row=4, columnspan=2, pady=8, sticky="w")
        ttk.Button(buttons, text="Inspeccionar perfil", command=self._inspect).grid(column=0, row=0, padx=(0, 8))
        self._preview_button = ttk.Button(buttons, text="Vista previa manual", command=self._preview)
        self._create_button = ttk.Button(buttons, text="Crear", command=self._create)
        self._replace_button = ttk.Button(buttons, text="Reemplazar", command=self._replace)
        self._delete_button = ttk.Button(buttons, text="Eliminar", command=self._delete)
        self._clear_button = ttk.Button(buttons, text="Limpiar todo", command=self._clear)
        self._preview_button.grid(column=1, row=0, padx=8)
        self._create_button.grid(column=2, row=0, padx=8)
        self._replace_button.grid(column=3, row=0, padx=8)
        self._delete_button.grid(column=4, row=0, padx=8)
        self._clear_button.grid(column=5, row=0, padx=8)
        ttk.Label(frame, textvariable=self._status, wraplength=620).grid(column=0, row=5, columnspan=2, pady=(14, 0), sticky="w")
        self._update_actions(self._controller.inspect())

    def _update_actions(self, state: LocalProfileWorkspaceState) -> None:
        self._create_button.configure(state="normal" if state.can_create else "disabled")
        self._replace_button.configure(state="normal" if state.can_replace else "disabled")
        self._delete_button.configure(state="normal" if state.can_delete else "disabled")
        self._clear_button.configure(state="normal" if state.can_clear else "disabled")

    def _render(self, state: LocalProfileWorkspaceState) -> None:
        if state.state == "selected_profile_available":
            self._identity.set(f"Perfil local: {state.display_name} — {state.realm}")
        elif state.state == "no_selected_profile":
            self._identity.set("No hay perfil local seleccionado.")
        else:
            self._identity.set("La identidad local no está disponible.")
        self._status.set(state.reason or state.state)
        self._update_actions(state)

    def _inspect(self) -> None:
        self._render(self._controller.inspect())

    def _preview(self) -> None:
        if self._messagebox.askyesno("Vista previa manual", "¿Crear una vista previa local no durable?"):
            self._render(self._controller.preview(self._name.get(), self._realm.get(), PREVIEW_CONFIRMATION))

    def _create(self) -> None:
        if self._messagebox.askyesno("Crear perfil", "¿Crear el perfil local a partir de esta vista previa?"):
            self._render(self._controller.create(CREATE_CONFIRMATION))

    def _replace(self) -> None:
        if self._messagebox.askyesno("Reemplazar perfil", "¿Reemplazar el perfil local seleccionado?"):
            self._render(self._controller.replace(REPLACE_CONFIRMATION))

    def _delete(self) -> None:
        if self._messagebox.askyesno("Eliminar perfil", "¿Eliminar el perfil local seleccionado?"):
            self._render(self._controller.delete(DELETE_CONFIRMATION))

    def _clear(self) -> None:
        if self._messagebox.askyesno("Limpiar todo", "¿Confirmas eliminar todos los perfiles locales?"):
            self._render(self._controller.clear_all(CLEAR_CONFIRMATION))

    def run(self) -> None:
        self._window.mainloop()
