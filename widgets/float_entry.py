"""
Виджет для ввода чисел с плавающей точкой, поддерживает разделители "." и ","
Также работает на input для ввода float чисел
"""

import tkinter as tk
from tkinter import ttk


class FloatEntry(ttk.Frame):

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

        try:
            value = float(textvariable.get())
            initial_value = f"{value:.2f}"
        except (ValueError, tk.TclError):
            initial_value = "0.00"
            textvariable.set(0.00)

        self.variable = tk.StringVar()
        self.variable.trace('w', self._validate)

        # Сохраняем ссылку на Entry для доступа извне
        self.entry = ttk.Entry(
            self,
            textvariable=self.variable,
            width=width,
            justify=tk.RIGHT,
            font=('Segoe UI', 9),
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Привязываем события валидации на уровне Entry
        self.entry.bind('<Key>', self._on_key, add='+')
        self.entry.bind('<FocusOut>', self._on_focus_out)

        # Инициализируем значением
        self.variable.set(textvariable.get())

    def _on_key(self, event):
        """Обработка нажатия клавиш с валидацией"""
        # Пропускаем специальные клавиши
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab', 'Return', 'KP_Enter'):
            return

        # Получаем текущее значение и новое
        current = self.variable.get()
        char = event.char

        # Если нажата клавиша без символа (например, Shift)
        if not char:
            return

        # Формируем новое значение
        if event.keysym == 'BackSpace':
            new_value = current[:-1]
        elif event.keysym == 'Delete':
            # Получаем позицию курсора
            try:
                pos = self.entry.index(tk.INSERT)
                new_value = current[:pos] + current[pos + 1:]
            except:
                new_value = current
        else:
            # Вставляем символ в позицию курсора
            try:
                pos = self.entry.index(tk.INSERT)
                new_value = current[:pos] + char + current[pos:]
            except:
                new_value = current + char

        # Проверяем новое значение
        if not self._validate_value(new_value):
            return "break"

    def _validate_value(self, value):
        """Проверка корректности значения"""
        # Пустое поле разрешаем
        if value == "":
            return True

        # Один минус разрешаем
        if value == "-":
            return True

        # Заменяем запятую на точку для проверки
        test_value = value.replace(',', '.')

        try:
            float(test_value)

            # Проверяем, что только одна точка
            if test_value.count('.') > 1:
                return False

            # Проверяем минус: если есть, то только один и в начале
            if test_value.startswith('-') and test_value.count('-') > 1:
                return False

            if not test_value.startswith('-') and '-' in test_value:
                return False

            return True

        except ValueError:
            return False

    def _validate(self, *args):
        """
        Обновляет внешнюю переменную при изменении внутренней.
        """
        value = self.variable.get()

        if value == "-":
            return

        if value == "":
            self.textvariable.set(0.00)
            return

        normalized = value.replace(',', '.')

        try:
            float_value = float(normalized)
            self.textvariable.set(float_value)
            formatted_value = f"{float_value:.2f}"
            if self.variable.get() != normalized:
                self.variable.set(normalized)
        except ValueError:
            current = self.textvariable.get()
            self.variable.set(str(current))

    def _on_focus_out(self, event):
        """
        Вызывается, когда поле ввода теряет фокус.
        Форматирует число для красивого отображения.
        """
        try:
            value = float(self.get())
            self.variable.set(f"{value:.2f}")
            self.textvariable.set(value)
        except ValueError:
            self.set(0.00)

    def get(self):
        """
        Возвращает текущее значение как число с плавающей точкой.
        """
        try:
            return float(self.textvariable.get())
        except (ValueError, tk.TclError):
            return 0.00

    def set(self, value):
        """
        Устанавливает новое значение виджета.
        """
        try:
            float_value = float(value)
            self.textvariable.set(float_value)
            self.variable.set(str(float_value))
        except (ValueError, TypeError):
            self.textvariable.set(0.00)
            self.variable.set("0.00")

    def focus_set(self):
        """Передача фокуса внутреннему Entry"""
        self.entry.focus_set()

    def tk_focusNext(self):
        """Возвращает следующий виджет в фокусе"""
        return self.entry.tk_focusNext()
