"""Local synthetic window adapter for the semantic review ceremony."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol


ROLES = (
    "article_title",
    "publication_label",
    "article_body",
    "non_content_metadata",
    "unknown",
    "rejected",
)
REASONS = (
    "direct_visual_confirmation",
    "ambiguous_visual_structure",
    "not_content_bearing",
    "reviewer_rejected",
)


class SemanticReviewWindowError(ValueError):
    pass


class ReviewPort(Protocol):
    def present(self, model: "ReviewWindowModel") -> dict[str, str] | None: ...


@dataclass(frozen=True)
class ReviewWindowModel:
    title: str
    mode_label: str
    slot_id: str
    content: str
    roles: tuple[str, ...]
    reasons: tuple[str, ...]
    initial_role: str
    initial_reason: str
    continue_requires_explicit_choices: bool


def build_synthetic_window_model(slot_id: str, content: memoryview) -> ReviewWindowModel:
    if not isinstance(slot_id, str) or not slot_id.startswith("slot.path_"):
        raise SemanticReviewWindowError("slot_id_invalid")
    if not isinstance(content, memoryview) or not content.readonly:
        raise SemanticReviewWindowError("readonly_memoryview_required")
    try:
        visible = bytes(content).decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise SemanticReviewWindowError("content_utf8_invalid") from error
    if not visible:
        raise SemanticReviewWindowError("content_empty")
    return ReviewWindowModel(
        title="DpsLab \u2014 Revisi\u00f3n sem\u00e1ntica sint\u00e9tica",
        mode_label="MODO SINT\u00c9TICO \u2014 NO ES INFORMACI\u00d3N REAL",
        slot_id=slot_id,
        content=visible,
        roles=ROLES,
        reasons=REASONS,
        initial_role="",
        initial_reason="",
        continue_requires_explicit_choices=True,
    )


def request_synthetic_decision(
    slot_id: str, content: memoryview, *, port: ReviewPort
) -> dict[str, str] | None:
    model = build_synthetic_window_model(slot_id, content)
    decision = port.present(model)
    if decision is None:
        return None
    if not isinstance(decision, dict) or set(decision) != {"role", "reason_code"}:
        raise SemanticReviewWindowError("decision_shape_invalid")
    if decision["role"] not in ROLES or decision["reason_code"] not in REASONS:
        raise SemanticReviewWindowError("decision_value_invalid")
    return dict(decision)


class TkReviewPort:
    """Visible Tk adapter. The caller owns lifecycle and content zeroization."""

    def present(self, model: ReviewWindowModel) -> dict[str, str] | None:
        import tkinter as tk
        from tkinter import ttk

        result: dict[str, str] | None = None
        window = tk.Tk()
        window.title(model.title)
        window.geometry("760x560")
        window.minsize(640, 480)
        window.columnconfigure(0, weight=1)
        window.rowconfigure(2, weight=1)

        ttk.Label(window, text=model.mode_label, foreground="#9b1c1c").grid(
            row=0, column=0, padx=24, pady=(20, 8), sticky="w"
        )
        ttk.Label(window, text=f"Ranura: {model.slot_id}").grid(
            row=1, column=0, padx=24, pady=4, sticky="w"
        )
        text = tk.Text(window, wrap="word", padx=12, pady=12)
        text.grid(row=2, column=0, padx=24, pady=8, sticky="nsew")
        text.insert("1.0", model.content)
        text.configure(state="disabled")

        controls = ttk.Frame(window)
        controls.grid(row=3, column=0, padx=24, pady=8, sticky="ew")
        controls.columnconfigure((1, 3), weight=1)
        role = tk.StringVar(value=model.initial_role)
        reason = tk.StringVar(value=model.initial_reason)
        ttk.Label(controls, text="Rol").grid(row=0, column=0, padx=(0, 8))
        role_box = ttk.Combobox(controls, textvariable=role, values=model.roles, state="readonly")
        role_box.grid(row=0, column=1, sticky="ew")
        ttk.Label(controls, text="Raz\u00f3n").grid(row=0, column=2, padx=8)
        reason_box = ttk.Combobox(controls, textvariable=reason, values=model.reasons, state="readonly")
        reason_box.grid(row=0, column=3, sticky="ew")

        buttons = ttk.Frame(window)
        buttons.grid(row=4, column=0, padx=24, pady=(8, 20), sticky="e")
        continue_button = ttk.Button(buttons, text="Continuar", state="disabled")

        def refresh(*_: object) -> None:
            continue_button.configure(state="normal" if role.get() and reason.get() else "disabled")

        def accept() -> None:
            nonlocal result
            if role.get() and reason.get():
                result = {"role": role.get(), "reason_code": reason.get()}
                window.destroy()

        ttk.Button(buttons, text="Cancelar", command=window.destroy).grid(row=0, column=0, padx=8)
        continue_button.configure(command=accept)
        continue_button.grid(row=0, column=1)
        role.trace_add("write", refresh)
        reason.trace_add("write", refresh)
        window.protocol("WM_DELETE_WINDOW", window.destroy)
        window.mainloop()
        return result


def synthetic_demo() -> dict[str, str] | None:
    """Launch the visible adapter with fixed, non-authoritative content."""
    buffer = bytearray(
        "Este contenido es sint\u00e9tico y solo permite comprobar el dise\u00f1o visual. "
        "No proviene de Blizzard ni contiene informaci\u00f3n real.".encode("utf-8")
    )
    try:
        return request_synthetic_decision(
            "slot.path_01", memoryview(buffer).toreadonly(), port=TkReviewPort()
        )
    finally:
        buffer[:] = b"\x00" * len(buffer)


if __name__ == "__main__":
    synthetic_demo()
