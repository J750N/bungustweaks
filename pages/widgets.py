import customtkinter as ctk
from core import theme

ACCENT, ACCENT2 = theme.get_accent_colors()
BG_SIDEBAR, BG_CONTENT, CARD_BG = theme.get_bg_colors()
WARNING_COLOR = "#F59E0B"
SUCCESS_COLOR = "#22C55E"

RISK_COLORS = {
    "safe": "#22C55E",       # green
    "moderate": "#F59E0B",   # yellow/orange
    "risky": "#EF4444",      # red
}
RISK_LABELS = {
    "safe": "Safe to apply",
    "moderate": "Slightly risky",
    "risky": "Risky — read carefully",
}
RISK_EXPLAINERS = {
    "safe": "Low risk. Easy to reverse, no known downsides for most setups.",
    "moderate": "Generally fine, but has a minor tradeoff or edge case — read the note below.",
    "risky": "Meaningful downside if left on. Only apply if you understand what it disables.",
}


def _mix(hex1: str, hex2: str, t: float) -> str:
    """Blend two hex colors together (t=0 -> hex1, t=1 -> hex2). Returns a solid hex string
    (tkinter Canvas does not support 8-digit alpha hex colors)."""
    c1 = tuple(int(hex1[i:i + 2], 16) for i in (1, 3, 5))
    c2 = tuple(int(hex2[i:i + 2], 16) for i in (1, 3, 5))
    mixed = tuple(int(c1[j] * (1 - t) + c2[j] * t) for j in range(3))
    return "#%02x%02x%02x" % mixed


class GradientBar(ctk.CTkCanvas):
    """A thin horizontal gradient strip - used as an accent line under headers/logos."""

    def __init__(self, master, color1=None, color2=None, height=4, **kwargs):
        super().__init__(master, height=height, highlightthickness=0, bd=0, **kwargs)
        self.color1 = color1 or ACCENT
        self.color2 = color2 or ACCENT2
        self.bind("<Configure>", lambda e: self._draw())

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1:
            return
        steps = max(2, w // 3)
        for i in range(steps):
            t = i / (steps - 1)
            color = _mix(self.color1, self.color2, t)
            x0 = i * (w / steps)
            x1 = (i + 1) * (w / steps) + 1
            self.create_rectangle(x0, 0, x1, h, fill=color, outline=color)


class Tooltip:
    """A small floating popup shown on hover, positioned near the cursor.
    Includes a close (X) button as a fallback in case the mouse-leave event
    doesn't fire reliably (a known tkinter quirk with nested widgets)."""

    def __init__(self, widget, title, description, risk="safe", warning=None, tweak=None):
        self.widget = widget
        self.title = title
        self.description = description
        self.risk = risk
        self.warning = warning
        self.tweak = tweak
        self.tip_window = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, event=None):
        if self.tip_window is not None:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)

        frame = ctk.CTkFrame(tw, fg_color="#1C1C1F", corner_radius=10, border_width=1,
                              border_color="#3A3A40")
        frame.pack()

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 4))
        dot = ctk.CTkLabel(header, text="●", text_color=RISK_COLORS.get(self.risk, "#9CA3AF"),
                            font=("Segoe UI", 13))
        dot.pack(side="left")
        ctk.CTkLabel(header, text=self.title, font=("Segoe UI", 13, "bold")).pack(
            side="left", padx=(6, 0)
        )
        ctk.CTkButton(
            header, text="✕", width=20, height=20, fg_color="transparent",
            hover_color="#33333a", text_color="#9CA3AF", font=("Segoe UI", 11),
            command=self._hide,
        ).pack(side="right")

        ctk.CTkLabel(
            frame, text=self.description, font=("Segoe UI", 12), text_color="#D1D5DB",
            wraplength=280, justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 6))

        if self.tweak:
            from core.value_extract import get_default_and_recommended
            default_val, recommended_val = get_default_and_recommended(self.tweak)
            ctk.CTkLabel(
                frame, text=f"PC default: {default_val}   →   Recommended: {recommended_val}",
                font=("Segoe UI", 11, "bold"), text_color=ACCENT,
                wraplength=280, justify="left",
            ).pack(anchor="w", padx=14, pady=(0, 6))

        ctk.CTkLabel(
            frame, text=f"{RISK_LABELS.get(self.risk, '')} — {RISK_EXPLAINERS.get(self.risk, '')}",
            font=("Segoe UI", 11), text_color=RISK_COLORS.get(self.risk, "#9CA3AF"),
            wraplength=280, justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 6 if self.warning else 12))

        if self.warning:
            ctk.CTkLabel(
                frame, text=f"⚠ {self.warning}", font=("Segoe UI", 11), text_color=WARNING_COLOR,
                wraplength=280, justify="left",
            ).pack(anchor="w", padx=14, pady=(0, 12))

    def _hide(self, event=None):
        if self.tip_window is not None:
            self.tip_window.destroy()
            self.tip_window = None


class Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=CARD_BG, corner_radius=12, **kwargs)


class SectionHeader(ctk.CTkFrame):
    def __init__(self, master, title, subtitle=""):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text=title, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        GradientBar(self, height=3, width=64, bg=BG_CONTENT).pack(anchor="w", pady=(4, 0))
        if subtitle:
            ctk.CTkLabel(self, text=subtitle, font=("Segoe UI", 13), text_color="#9CA3AF").pack(
                anchor="w", pady=(6, 0)
            )


class TweakRow(Card):
    """A single tweak with a risk dot, title, description, optional warning, and a toggle switch.
    Hovering anywhere on the row shows a tooltip with the full description and safety info."""

    def __init__(self, master, name, description, warning, initial_on, on_toggle, risk="safe", tweak=None):
        super().__init__(master)
        self.on_toggle = on_toggle

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)
        inner.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(inner, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            title_row, text="●", text_color=RISK_COLORS.get(risk, "#9CA3AF"), font=("Segoe UI", 12),
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(title_row, text=name, font=("Segoe UI", 14, "bold")).pack(side="left")

        ctk.CTkLabel(
            inner, text=description, font=("Segoe UI", 12), text_color="#9CA3AF",
            wraplength=520, justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        next_row = 2
        if tweak:
            from core.value_extract import get_default_and_recommended
            default_val, recommended_val = get_default_and_recommended(tweak)
            ctk.CTkLabel(
                inner, text=f"PC default: {default_val}   →   Recommended: {recommended_val}",
                font=("Segoe UI", 10, "bold"), text_color=ACCENT,
            ).grid(row=next_row, column=0, sticky="w", pady=(4, 0))
            next_row += 1

        if warning:
            ctk.CTkLabel(
                inner, text=f"⚠ {warning}", font=("Segoe UI", 11), text_color=WARNING_COLOR,
                wraplength=520, justify="left",
            ).grid(row=next_row, column=0, sticky="w", pady=(4, 0))
            next_row += 1

        self.switch_var = ctk.BooleanVar(value=initial_on)
        self.switch = ctk.CTkSwitch(
            inner, text="", variable=self.switch_var, progress_color=ACCENT,
            command=self._toggled,
        )
        self.switch.grid(row=0, column=1, rowspan=max(next_row, 1), padx=(12, 0), sticky="e")

        Tooltip(self, name, description, risk=risk, warning=warning, tweak=tweak)

    def _toggled(self):
        self.on_toggle(self.switch_var.get(), self)

    def set_state(self, is_on: bool):
        self.switch_var.set(is_on)

    def set_enabled(self, enabled: bool):
        self.switch.configure(state="normal" if enabled else "disabled")


class ActionRow(Card):
    """A row with title/description and a button (used for Debloat / Fixes)."""

    def __init__(self, master, name, description, button_text, on_click, button_color=ACCENT):
        super().__init__(master)
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)
        inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(inner, text=name, font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(
            inner, text=description, font=("Segoe UI", 12), text_color="#9CA3AF",
            wraplength=520, justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.button = ctk.CTkButton(
            inner, text=button_text, width=110, fg_color=button_color,
            command=on_click,
        )
        self.button.grid(row=0, column=1, rowspan=2, padx=(12, 0), sticky="e")

    def set_button(self, text, color=None, enabled=True):
        self.button.configure(text=text, state="normal" if enabled else "disabled")
        if color:
            self.button.configure(fg_color=color)


class LogConsole(ctk.CTkTextbox):
    """A read-only scrolling console for showing live command output."""

    def __init__(self, master, height=160):
        super().__init__(master, height=height, font=("Consolas", 11), fg_color="#0A0A0B")
        self.configure(state="disabled")

    def log(self, line: str):
        self.configure(state="normal")
        self.insert("end", line + "\n")
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


def confirm_dialog(master, title, message, on_yes):
    """Simple Yes/No confirmation popup."""
    win = ctk.CTkToplevel(master)
    win.title(title)
    win.geometry("380x160")
    win.grab_set()
    ctk.CTkLabel(win, text=message, wraplength=340, justify="left").pack(padx=20, pady=(20, 10))
    btn_frame = ctk.CTkFrame(win, fg_color="transparent")
    btn_frame.pack(pady=10)

    def yes():
        win.destroy()
        on_yes()

    ctk.CTkButton(btn_frame, text="Yes", fg_color=ACCENT, command=yes, width=100).pack(
        side="left", padx=8
    )
    ctk.CTkButton(btn_frame, text="Cancel", fg_color="#374151", command=win.destroy, width=100).pack(
        side="left", padx=8
    )


class HistoryGraph(ctk.CTkFrame):
    """A rolling line-chart with min/avg/peak footer, similar to LuminApp's temp graphs.
    Call .push(value) to add a new sample (0-100 scale expected)."""

    def __init__(self, master, label, unit="%", color=None, max_points=60, height=110):
        super().__init__(master, fg_color=CARD_BG, corner_radius=12)
        color = color or ACCENT
        self.color = color
        self.unit = unit
        self.max_points = max_points
        self.values = []

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(header, text=label.upper(), font=("Segoe UI", 11), text_color="#9CA3AF").pack(
            side="left"
        )
        self.current_label = ctk.CTkLabel(header, text=f"0{unit}", font=("Segoe UI", 14, "bold"))
        self.current_label.pack(side="right")

        self.canvas = ctk.CTkCanvas(self, height=height, bg=BG_SIDEBAR, highlightthickness=0)
        self.canvas.pack(fill="x", padx=16, pady=8)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(0, 12))
        self.avg_label = ctk.CTkLabel(footer, text=f"AVG 0{unit}", font=("Segoe UI", 10), text_color="#9CA3AF")
        self.avg_label.pack(side="left")
        self.min_label = ctk.CTkLabel(footer, text=f"MIN 0{unit}", font=("Segoe UI", 10), text_color="#9CA3AF")
        self.min_label.pack(side="left", padx=16)
        self.peak_label = ctk.CTkLabel(footer, text=f"PEAK 0{unit}", font=("Segoe UI", 10), text_color="#9CA3AF")
        self.peak_label.pack(side="left")

        self.canvas.bind("<Configure>", lambda e: self._redraw())

    def push(self, value: float):
        self.values.append(value)
        if len(self.values) > self.max_points:
            self.values.pop(0)
        self.current_label.configure(text=f"{value:.0f}{self.unit}")
        if self.values:
            self.avg_label.configure(text=f"AVG {sum(self.values)/len(self.values):.0f}{self.unit}")
            self.min_label.configure(text=f"MIN {min(self.values):.0f}{self.unit}")
            self.peak_label.configure(text=f"PEAK {max(self.values):.0f}{self.unit}")
        self._redraw()

    def _redraw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1 or not self.values:
            return

        for frac in (0.0, 0.5, 1.0):
            y = h - frac * (h - 10) - 5
            self.canvas.create_line(0, y, w, y, fill=_mix(BG_SIDEBAR, "#ffffff", 0.12))

        n = len(self.values)
        gap = 2
        bar_w = max(2, (w / self.max_points) - gap)
        offset = self.max_points - n

        top_color = self.color
        bottom_color = _mix(self.color, BG_SIDEBAR, 0.75)

        for i, v in enumerate(self.values):
            x0 = (i + offset) * (w / self.max_points) + gap / 2
            x1 = x0 + bar_w
            bar_h = (max(0, min(100, v)) / 100) * (h - 10)
            y_top = h - bar_h - 5
            y_bottom = h - 5
            if bar_h <= 0:
                continue

            # vertical mini-gradient within the bar for a "glow" look
            steps = max(1, int(bar_h // 4))
            for s in range(steps):
                t = s / steps
                seg_color = _mix(top_color, bottom_color, t)
                seg_y0 = y_top + s * (bar_h / steps)
                seg_y1 = y_top + (s + 1) * (bar_h / steps) + 1
                self.canvas.create_rectangle(x0, seg_y0, x1, seg_y1, fill=seg_color, outline="")

            # bright highlight cap at the top of the bar
            self.canvas.create_rectangle(x0, y_top, x1, y_top + 2, fill="#FFFFFF", outline="", stipple="gray50")

        # glowing dot + value on the most recent sample
        last_v = self.values[-1]
        last_x = (n - 1 + offset) * (w / self.max_points) + bar_w / 2 + gap / 2
        last_y = h - (max(0, min(100, last_v)) / 100) * (h - 10) - 5
        self.canvas.create_oval(last_x - 4, last_y - 4, last_x + 4, last_y + 4, fill=top_color, outline="")
        self.canvas.create_oval(last_x - 7, last_y - 7, last_x + 7, last_y + 7, outline=top_color, width=1)


class DualActionRow(Card):
    """A row with title/description and TWO buttons - used for Debloat's Remove + Reinstall."""

    def __init__(self, master, name, description, primary_text, on_primary, secondary_text, on_secondary,
                 primary_color=None, secondary_color="#374151"):
        super().__init__(master)
        primary_color = primary_color or ACCENT

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)
        inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(inner, text=name, font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(
            inner, text=description, font=("Segoe UI", 12), text_color="#9CA3AF",
            wraplength=460, justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))

        self.secondary_button = ctk.CTkButton(
            btn_row, text=secondary_text, width=100, fg_color=secondary_color, command=on_secondary,
        )
        self.secondary_button.pack(side="left", padx=(0, 8))

        self.primary_button = ctk.CTkButton(
            btn_row, text=primary_text, width=100, fg_color=primary_color, command=on_primary,
        )
        self.primary_button.pack(side="left")

    def set_primary(self, text, color=None, enabled=True):
        self.primary_button.configure(text=text, state="normal" if enabled else "disabled")
        if color:
            self.primary_button.configure(fg_color=color)

    def set_secondary(self, text, color=None, enabled=True):
        self.secondary_button.configure(text=text, state="normal" if enabled else "disabled")
        if color:
            self.secondary_button.configure(fg_color=color)
