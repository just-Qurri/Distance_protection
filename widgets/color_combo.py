# -*- coding: utf-8 -*-
"""
Виджет для выбора цвета с отображением цветного квадратика и названия
"""

import tkinter as tk
from tkinter import ttk


class ColorCombo(ttk.Frame):
    """Комбобокс с отображением цвета и названия"""

    def __init__(self, parent, textvariable, colors, width=15):
        """
        Инициализация виджета

        Args:
            parent: Родительский виджет
            textvariable: Переменная tkinter для хранения кода цвета
            colors: Список кортежей (код_цвета, название)
            width: Ширина виджета
        """
        super().__init__(parent)
        self.textvariable = textvariable
        self.colors = colors
        self.display_var = tk.StringVar()

        # Фрейм для отображения цвета
        self.color_frame = tk.Frame(self, width=20, height=20, relief='solid', borderwidth=1)
        self.color_frame.pack(side=tk.LEFT, padx=(0, 5))
        self.color_frame.pack_propagate(False)

        # Метка с названием цвета
        self.label = ttk.Label(self, textvariable=self.display_var, width=width - 5)
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Кнопка для вызова меню
        self.btn = ttk.Button(self, text="▼", width=2, command=self.show_menu)
        self.btn.pack(side=tk.RIGHT)

        # Отслеживание изменений
        textvariable.trace('w', lambda *args: self._update_display())
        self._update_display()

    def _update_display(self):
        """Обновление отображаемого названия и цвета"""
        color_code = self.textvariable.get()
        for code, name in self.colors:
            if code == color_code:
                self.display_var.set(name)
                self.color_frame.configure(bg=color_code)
                break

    def show_menu(self):
        """Показ меню выбора цвета"""
        menu = tk.Menu(self, tearoff=0)
        for code, name in self.colors:
            menu.add_command(label=name,
                             command=lambda c=code: self.textvariable.set(c))
        # Позиционируем меню под кнопкой
        x = self.btn.winfo_rootx()
        y = self.btn.winfo_rooty() + self.btn.winfo_height()
        menu.post(x, y)