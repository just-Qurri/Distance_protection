"""
Виджет выбора типа терминала (исправлен)
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

# Исправлен импорт
try:
    from models.terminal_types import TERMINAL_TYPES, get_terminal_names
except ImportError:
    # Для обратной совместимости
    from ..models.terminal_types import TERMINAL_TYPES, get_terminal_names


class TerminalSelector(ttk.Frame):
    """Виджет для выбора типа терминала"""

    def __init__(self, parent, on_change: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.current_terminal = tk.StringVar(value="rel670")
        self._create_ui()

    def _create_ui(self):
        """Создание UI"""
        main_frame = ttk.LabelFrame(self, text="Тип терминала", padding=10)
        main_frame.pack(fill=tk.X)

        terminal_frame = ttk.Frame(main_frame)
        terminal_frame.pack(fill=tk.X)

        ttk.Label(terminal_frame, text="Выберите тип:", font=('Segoe UI', 10)).pack(side=tk.LEFT)

        self.combo = ttk.Combobox(
            terminal_frame,
            textvariable=self.current_terminal,
            values=get_terminal_names(),
            state="readonly",
            width=20
        )
        self.combo.pack(side=tk.LEFT, padx=10)
        self.combo.bind('<<ComboboxSelected>>', self._on_terminal_change)

        self.info_frame = ttk.Frame(main_frame)
        self.info_frame.pack(fill=tk.X, pady=(10, 0))

        self.info_label = ttk.Label(
            self.info_frame,
            text="",
            font=('Segoe UI', 9),
            foreground='#666666'
        )
        self.info_label.pack(fill=tk.X)

        self._update_info()

    def _on_terminal_change(self, event=None):
        """Обработка изменения терминала"""
        self._update_info()
        if self.on_change:
            self.on_change(self.get_terminal_code())

    def _update_info(self):
        """Обновление информации о терминале"""
        code = self.get_terminal_code()
        terminal = TERMINAL_TYPES.get(code)
        if terminal:
            self.info_label.config(
                text=f"{terminal.description} | K_ZIN={terminal.k_zin}, K_ZOUT={terminal.k_zout}"
            )

    def get_terminal_code(self) -> str:
        """Получить код текущего терминала"""
        name = self.current_terminal.get()
        for code, terminal in TERMINAL_TYPES.items():
            if terminal.name == name:
                return code
        return "rel670"

    def set_terminal(self, code: str) -> None:
        """Установить терминал по коду"""
        terminal = TERMINAL_TYPES.get(code)
        if terminal:
            self.current_terminal.set(terminal.name)
            self._update_info()
