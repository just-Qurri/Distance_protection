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

        self.entry = ttk.Entry(
            self,
            textvariable=self.variable,
            width=width,
            justify=tk.RIGHT,
            font=('Segoe UI', 9),
            validate='key',
            validatecommand=(self.register(self._validate_key), '%P')
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind('<FocusOut>', self._on_focus_out)

        # Инициализируем значением
        self.variable.set(textvariable.get())

    def _validate_key(self, new_value):
        """Валидация ввода - разрешаем цифры, точку, запятую и минус"""

        # Пустое поле разрешаем (пользователь может стереть всё)
        if new_value == "":
            return True

        # Один минус разрешаем (начало ввода отрицательного числа)
        if new_value == "-":
            return True

        test_value = new_value.replace(',', '.')

        try:
            float(test_value)

            # Проверяем, что только одна точка (нельзя ввести "1.2.3")
            if test_value.count('.') > 1:
                return False

            # Проверяем минус: если есть, то только один и в начале
            if test_value.startswith('-') and test_value.count('-') > 1:
                return False

            # Проверяем, что минус один, но не вначале строки, что запрещено
            if not test_value.startswith('-') and '-' in test_value:
                return False

            return True

        except ValueError:
            return False

    def _validate(self, *args):
        """
        Обновляет внешнюю переменную при изменении внутренней.
        Вызывается автоматически при изменении self.variable.
        """
        # Получаем текущее значение из поля ввода
        value = self.variable.get()

        if value == "-":
            return

        # ОБРАБОТКА ПУСТОГО ПОЛЯ
        if value == "":
            # Если поле пустое, устанавливаем 0.0
            self.textvariable.set(0.00)
            return

        # Заменяем запятую на точку для корректного преобразования в число
        normalized = value.replace(',', '.')

        # СОХРАНЕНИЕ ВО ВНЕШНЮЮ ПЕРЕМЕННУЮ
        try:
            # Преобразуем в число
            float_value = float(normalized)
            # Сохраняем во внешнюю переменную (теперь там будет число)
            self.textvariable.set(float_value)
            formatted_value = f"{float_value:.2f}"
            if self.variable.get() != normalized:
                self.variable.set(normalized)
        except ValueError:
            # Восстанавливаем последнее корректное значение из внешней переменной
            current = self.textvariable.get()
            self.variable.set(str(current))

    def _on_focus_out(self, event):
        """
        Вызывается, когда поле ввода теряет фокус (пользователь кликнул вне поля).
        Форматирует число для красивого отображения.
        """
        try:
            # Пытаемся получить текущее значение как число
            value = float(self.get())
            # Например, "1.0" станет "1.0", а не "1"
            self.variable.set(f"{value:.2f}")
            self.textvariable.set(value)
        except ValueError:
            # Если не удалось преобразовать в число
            self.set(0.00)

    def get(self):
        """
        Возвращает текущее значение как число с плавающей точкой.
        Удобно использовать для получения значения: value = float_entry.get()
        """
        try:
            # Пробуем получить значение из внешней переменной
            return float(self.textvariable.get())
        except (ValueError, tk.TclError):
            # Если ошибка (например, переменная не установлена)
            return 0.00

    def set(self, value):
        """
        Устанавливает новое значение виджета.
        Можно использовать: float_entry.set(3.14)
        """
        try:
            # Пробуем преобразовать в число (на случай, если передали строку)
            float_value = float(value)
            # Обновляем внешнюю переменную
            self.textvariable.set(float_value)
            # Обновляем отображаемый текст
            self.variable.set(str(float_value))
        except (ValueError, TypeError):
            # Если передано некорректное значение
            self.textvariable.set(0.00)
            self.variable.set("0.00")
