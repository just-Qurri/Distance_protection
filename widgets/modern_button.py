# -*- coding: utf-8 -*-
"""
Современные стилизованные кнопки
"""

import tkinter as tk
from tkinter import ttk


class ModernButton(ttk.Frame):
    """Современная стилизованная кнопка с иконкой и текстом"""

    def __init__(self, parent, text="", icon="", command=None,
                 style="primary", width=100, **kwargs):
        """
        Инициализация современной кнопки

        Args:
            parent: Родительский виджет
            text: Текст кнопки
            icon: Иконка (эмодзи)
            command: Функция при нажатии
            style: Стиль ("primary", "success", "danger", "warning", "info")
            width: Ширина кнопки
        """
        super().__init__(parent, **kwargs)
        self.command = command

        # Цвета для разных стилей
        colors = {
            "primary": {"bg": "#2196F3", "fg": "white", "hover": "#1976D2"},
            "success": {"bg": "#4CAF50", "fg": "white", "hover": "#388E3C"},
            "danger": {"bg": "#F44336", "fg": "white", "hover": "#D32F2F"},
            "warning": {"bg": "#FF9800", "fg": "white", "hover": "#F57C00"},
            "info": {"bg": "#00BCD4", "fg": "white", "hover": "#0097A7"},
            "default": {"bg": "#E0E0E0", "fg": "#333333", "hover": "#BDBDBD"}
        }

        self.style_colors = colors.get(style, colors["default"])

        # Внутренняя кнопка
        self.button = tk.Button(
            self,
            text=f"{icon} {text}" if icon else text,
            font=('Segoe UI', 10, 'bold'),
            bg=self.style_colors["bg"],
            fg=self.style_colors["fg"],
            relief='flat',
            bd=0,
            padx=10,
            pady=5,
            width=width,
            cursor='hand2',
            command=self._on_click
        )
        self.button.pack(fill=tk.BOTH, expand=True)

        # Эффекты наведения
        self.button.bind("<Enter>", self._on_enter)
        self.button.bind("<Leave>", self._on_leave)

    def _on_click(self):
        """Обработка нажатия"""
        if self.command:
            self.command()

    def _on_enter(self, event):
        """Эффект при наведении"""
        self.button.config(bg=self.style_colors["hover"])

    def _on_leave(self, event):
        """Эффект при уходе мыши"""
        self.button.config(bg=self.style_colors["bg"])

    def configure(self, **kwargs):
        """Передача конфигурации кнопке"""
        self.button.configure(**kwargs)


class IconButton(ttk.Frame):
    """Кнопка только с иконкой"""

    def __init__(self, parent, icon="", command=None, tooltip="", **kwargs):
        """
        Инициализация кнопки-иконки

        Args:
            parent: Родительский виджет
            icon: Иконка (эмодзи)
            command: Функция при нажатии
            tooltip: Подсказка при наведении
        """
        super().__init__(parent, **kwargs)
        self.command = command

        self.button = tk.Button(
            self,
            text=icon,
            font=('Segoe UI', 14),
            bg='#f5f5f5',
            fg='#555555',
            relief='flat',
            bd=0,
            padx=8,
            pady=2,
            cursor='hand2',
            command=self._on_click
        )
        self.button.pack(fill=tk.BOTH, expand=True)

        # Эффекты наведения
        self.button.bind("<Enter>", self._on_enter)
        self.button.bind("<Leave>", self._on_leave)

        # Подсказка
        if tooltip:
            self.tooltip = tooltip
            self.button.bind("<Enter>", self._show_tooltip)
            self.button.bind("<Leave>", self._hide_tooltip)
            self.tooltip_window = None

    def _on_click(self):
        """Обработка нажатия"""
        if self.command:
            self.command()

    def _on_enter(self, event):
        """Эффект при наведении"""
        self.button.config(bg='#e0e0e0', fg='#333333')

    def _on_leave(self, event):
        """Эффект при уходе мыши"""
        self.button.config(bg='#f5f5f5', fg='#555555')

    def _show_tooltip(self, event):
        """Показ подсказки"""
        x = self.button.winfo_rootx() + 20
        y = self.button.winfo_rooty() + 30

        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip_window,
            text=self.tooltip,
            background='#333333',
            foreground='white',
            font=('Segoe UI', 9),
            padx=5,
            pady=2
        )
        label.pack()

    def _hide_tooltip(self, event):
        """Скрытие подсказки"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None