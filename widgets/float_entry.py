"""
Виджет для ввода чисел с плавающей точкой (исправлен)
"""

import tkinter as tk
from tkinter import ttk


class FloatEntry(ttk.Frame):
    """Виджет для ввода чисел с плавающей точкой"""

    def __init__(self, parent, textvariable, width=8, on_change_callback=None):
        super().__init__(parent)
        self.textvariable = textvariable
        self.on_change_callback = on_change_callback

        vcmd = (self.register(self._validate), '%P')
        self.entry = ttk.Entry(
            self,
            width=width,
            validate='key',
            validatecommand=vcmd,
            justify=tk.RIGHT,
            font=('Segoe UI', 9)
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<Return>', self._on_enter_pressed)
        self.entry.bind('<KP_Enter>', self._on_enter_pressed)

        self._sync_from_variable()
        textvariable.trace('w', lambda *args: self._sync_from_variable())

    def _validate(self, value: str) -> bool:
        """Валидация вводимого значения"""
        if value == "" or value == "-" or value == ".":
            return True
        try:
            float(value.replace(',', '.'))
            return True
        except ValueError:
            return False

    def _sync_from_variable(self) -> None:
        """Синхронизация из внешней переменной"""
        try:
            value = self.textvariable.get()
            if value == "":
                self.entry.delete(0, tk.END)
            else:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, str(value))
        except (ValueError, tk.TclError):
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "0.00")

    def _on_focus_out(self, event) -> None:
        """Форматирование при потере фокуса"""
        self._apply_value()

    def _on_enter_pressed(self, event):
        """Обработка нажатия Enter"""
        self._apply_value()
        try:
            self.entry.tk_focusNext().focus_set()
        except Exception:
            pass
        return "break"

    def _apply_value(self) -> None:
        """Применить значение"""
        try:
            value = self.entry.get().replace(',', '.')
            if value == "" or value == "-":
                self.textvariable.set(0.0)
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "0.00")
                return

            float_value = float(value)
            formatted = f"{float_value:.2f}"
            self.entry.delete(0, tk.END)
            self.entry.insert(0, formatted)
            self.textvariable.set(float_value)

            if self.on_change_callback:
                self.on_change_callback()

        except ValueError:
            self.textvariable.set(0.0)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "0.00")

    def get(self) -> float:
        """Получение значения"""
        try:
            return float(self.textvariable.get())
        except (ValueError, tk.TclError):
            return 0.00

    def set(self, value: float) -> None:
        """Установка значения"""
        self.textvariable.set(value)

    def focus_set(self) -> None:
        """Передача фокуса"""
        self.entry.focus_set()

    def tk_focusNext(self):
        """Следующий виджет в фокусе"""
        return self.entry.tk_focusNext()

    def bind(self, sequence, func, add=None):
        """Привязка событий к Entry"""
        return self.entry.bind(sequence, func, add)
