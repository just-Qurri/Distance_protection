# -*- coding: utf-8 -*-
"""
Виджет для ввода чисел с плавающей точкой
Поддерживает разделители . и ,
"""

import tkinter as tk
from tkinter import ttk


class FloatEntry(ttk.Frame):
    """Виджет для ввода чисел с плавающей точкой (поддерживает . и ,)"""

    def __init__(self, parent, textvariable, width=8, **kwargs):
        """
        Инициализация виджета

        Args:
            parent: Родительский виджет
            textvariable: Переменная tkinter для хранения значения
            width: Ширина поля ввода
        """
        super().__init__(parent)
        self.textvariable = textvariable
        self.variable = tk.StringVar()
        self.variable.trace('w', self._validate)

        self.entry = ttk.Entry(self, textvariable=self.variable, width=width,
                               justify=tk.RIGHT, font=('Segoe UI', 9))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Инициализируем значением
        self.variable.set(textvariable.get())

    def _validate(self, *args):
        """Валидация ввода - разрешаем цифры, точку, запятую и минус"""
        value = self.variable.get()
        if value == "" or value == "-":
            return

        # Заменяем запятую на точку
        normalized = value.replace(',', '.')

        # Проверяем, что это число
        try:
            float(normalized)
            # Обновляем основную переменную
            self.textvariable.set(normalized)
        except ValueError:
            # Если не число, восстанавливаем предыдущее значение
            current = self.textvariable.get()
            self.variable.set(current)