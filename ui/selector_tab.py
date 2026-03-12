# -*- coding: utf-8 -*-
"""
Вкладка для настройки фазового селектора FDPSPDIS
"""

import tkinter as tk
from tkinter import ttk
import numpy as np

from widgets.float_entry import FloatEntry
from widgets.color_combo import ColorCombo
from widgets.modern_button import ModernButton


class SelectorTab:
    """Вкладка для настройки фазового селектора FDPSPDIS"""

    def __init__(self, notebook, selector_settings, visualizer, colors, linestyles):
        """
        Инициализация вкладки фазового селектора

        Args:
            notebook: Виджет Notebook для добавления вкладки
            selector_settings: Объект SelectorSettings
            visualizer: Главный объект визуализатора
            colors: Список доступных цветов
            linestyles: Список доступных стилей линий
        """
        self.selector = selector_settings
        self.viz = visualizer
        self.colors = colors
        self.linestyles = linestyles

        self.tab = ttk.Frame(notebook, padding=15)
        notebook.add(self.tab, text="⚡ Фазовый селектор")

        self.vars = {}
        self._create_widgets()

        # Сохраняем ссылку на селектор в визуализаторе
        self.viz.selector = selector_settings

    def _create_widgets(self):
        """Создание виджетов на вкладке"""

        # Заголовок с описанием
        title_frame = ttk.Frame(self.tab)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        title_label = ttk.Label(
            title_frame,
            text="Фазовый селектор FDPSPDIS",
            font=('Segoe UI', 16, 'bold'),
            foreground='#9C27B0'
        )
        title_label.pack(side=tk.LEFT)

        # Информационная метка
        info_label = ttk.Label(
            title_frame,
            text="ⓘ Единая характеристика для всех 6 контуров",
            font=('Segoe UI', 10),
            foreground='#666666'
        )
        info_label.pack(side=tk.RIGHT)

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        # Включение/отключение
        enabled_frame = ttk.Frame(self.tab)
        enabled_frame.pack(fill=tk.X, pady=5)

        enabled_var = tk.BooleanVar(value=self.selector.enabled)
        ttk.Checkbutton(
            enabled_frame,
            text="Показать фазовый селектор на графике",
            variable=enabled_var,
            command=self._on_enabled_toggle
        ).pack(side=tk.LEFT)

        self.vars["enabled"] = enabled_var

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        # Основные параметры
        self._create_main_params()

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        # Параметры для Ph-Ph
        self._create_phph_params()

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        # Параметры для Ph-E
        self._create_phe_params()

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        # Токовые параметры
        self._create_current_params()

        ttk.Separator(self.tab).pack(fill=tk.X, pady=10)

        # Оформление
        self._create_style_params()

        # Кнопка сброса
        button_frame = ttk.Frame(self.tab)
        button_frame.pack(fill=tk.X, pady=20)

        ModernButton(
            button_frame,
            text="Сбросить к рекомендуемым",
            icon="↺",
            style="info",
            width=25,
            command=self._reset_to_default
        ).pack(side=tk.RIGHT)

    def _create_main_params(self):
        """Создание основных параметров"""
        main_frame = ttk.LabelFrame(self.tab, text="Основные параметры", padding=15)
        main_frame.pack(fill=tk.X, pady=5)

        # Сетка для параметров
        grid = ttk.Frame(main_frame)
        grid.pack(fill=tk.X)

        # X1
        ttk.Label(grid, text="X₁ (Ом/фаза):", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=8
        )
        x1_var = tk.StringVar(value=f"{self.selector.x1:.2f}")
        FloatEntry(grid, textvariable=x1_var, width=10).grid(
            row=0, column=1, sticky=tk.W, padx=10
        )
        self.vars["x1"] = x1_var

        # X0
        ttk.Label(grid, text="X₀ (Ом/фаза):", font=('Segoe UI', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=8
        )
        x0_var = tk.StringVar(value=f"{self.selector.x0:.2f}")
        FloatEntry(grid, textvariable=x0_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=10
        )
        self.vars["x0"] = x0_var

    def _create_phph_params(self):
        """Создание параметров для Ph-Ph"""
        phph_frame = ttk.LabelFrame(self.tab, text="Параметры для Ph-Ph", padding=15)
        phph_frame.pack(fill=tk.X, pady=5)

        # Заголовок с иконкой
        header = ttk.Frame(phph_frame)
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="∿", font=('Segoe UI', 14)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Междуфазные повреждения", font=('Segoe UI', 10, 'italic')).pack(side=tk.LEFT)

        # Сетка для параметров
        grid = ttk.Frame(phph_frame)
        grid.pack(fill=tk.X)

        # Прямое направление
        ttk.Label(grid, text="Прямое направление (RFFwPP):", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=8, columnspan=2
        )

        ttk.Label(grid, text="RFFwPP (Ом/петля):", font=('Segoe UI', 10)).grid(
            row=1, column=0, sticky=tk.W, padx=20, pady=5
        )
        fw_pp_var = tk.StringVar(value=f"{self.selector.rffw_pp:.2f}")
        FloatEntry(grid, textvariable=fw_pp_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=10
        )
        self.vars["rffw_pp"] = fw_pp_var

        # Разделитель
        ttk.Separator(grid, orient='horizontal').grid(
            row=2, column=0, columnspan=3, sticky=tk.EW, pady=10
        )

        # Обратное направление
        ttk.Label(grid, text="Обратное направление (RFRvPP):", font=('Segoe UI', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=8, columnspan=2
        )

        ttk.Label(grid, text="RFRvPP (Ом/петля):", font=('Segoe UI', 10)).grid(
            row=4, column=0, sticky=tk.W, padx=20, pady=5
        )
        rv_pp_var = tk.StringVar(value=f"{self.selector.rfrv_pp:.2f}")
        FloatEntry(grid, textvariable=rv_pp_var, width=10).grid(
            row=4, column=1, sticky=tk.W, padx=10
        )
        self.vars["rfrv_pp"] = rv_pp_var

    def _create_phe_params(self):
        """Создание параметров для Ph-E"""
        phe_frame = ttk.LabelFrame(self.tab, text="Параметры для Ph-E", padding=15)
        phe_frame.pack(fill=tk.X, pady=5)

        # Заголовок с иконкой
        header = ttk.Frame(phe_frame)
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="⏚", font=('Segoe UI', 14)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="Однофазные повреждения на землю", font=('Segoe UI', 10, 'italic')).pack(side=tk.LEFT)

        # Сетка для параметров
        grid = ttk.Frame(phe_frame)
        grid.pack(fill=tk.X)

        # Прямое направление
        ttk.Label(grid, text="Прямое направление (RFFwPE):", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=8, columnspan=2
        )

        ttk.Label(grid, text="RFFwPE (Ом/петля):", font=('Segoe UI', 10)).grid(
            row=1, column=0, sticky=tk.W, padx=20, pady=5
        )
        fw_pe_var = tk.StringVar(value=f"{self.selector.rffw_pe:.2f}")
        FloatEntry(grid, textvariable=fw_pe_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=10
        )
        self.vars["rffw_pe"] = fw_pe_var

        # Разделитель
        ttk.Separator(grid, orient='horizontal').grid(
            row=2, column=0, columnspan=3, sticky=tk.EW, pady=10
        )

        # Обратное направление
        ttk.Label(grid, text="Обратное направление (RFRvPE):", font=('Segoe UI', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=8, columnspan=2
        )

        ttk.Label(grid, text="RFRvPE (Ом/петля):", font=('Segoe UI', 10)).grid(
            row=4, column=0, sticky=tk.W, padx=20, pady=5
        )
        rv_pe_var = tk.StringVar(value=f"{self.selector.rfrv_pe:.2f}")
        FloatEntry(grid, textvariable=rv_pe_var, width=10).grid(
            row=4, column=1, sticky=tk.W, padx=10
        )
        self.vars["rfrv_pe"] = rv_pe_var

    def _create_current_params(self):
        """Создание токовых параметров"""
        current_frame = ttk.LabelFrame(self.tab, text="Токовые параметры", padding=15)
        current_frame.pack(fill=tk.X, pady=5)

        # Информация
        ttk.Label(
            current_frame,
            text="Параметры минимальных токов срабатывания и блокировки",
            font=('Segoe UI', 9, 'italic'),
            foreground='#666666'
        ).pack(anchor=tk.W, pady=(0, 10))

        # Сетка для параметров
        grid = ttk.Frame(current_frame)
        grid.pack(fill=tk.X)

        # IMinOpPP и IMinOpPE
        ttk.Label(grid, text="IMinOpPP (%):", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        imin_pp_var = tk.StringVar(value=f"{self.selector.imin_op_pp}")
        FloatEntry(grid, textvariable=imin_pp_var, width=8).grid(
            row=0, column=1, sticky=tk.W, padx=10
        )
        ttk.Label(grid, text="(мин. ток для Ph-Ph)", font=('Segoe UI', 8), foreground='#666').grid(
            row=0, column=2, sticky=tk.W, padx=5
        )

        ttk.Label(grid, text="IMinOpPE (%):", font=('Segoe UI', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        imin_pe_var = tk.StringVar(value=f"{self.selector.imin_op_pe}")
        FloatEntry(grid, textvariable=imin_pe_var, width=8).grid(
            row=1, column=1, sticky=tk.W, padx=10
        )
        ttk.Label(grid, text="(мин. ток для Ph-E)", font=('Segoe UI', 8), foreground='#666').grid(
            row=1, column=2, sticky=tk.W, padx=5
        )

        # Разделитель
        ttk.Separator(grid, orient='horizontal').grid(
            row=2, column=0, columnspan=3, sticky=tk.EW, pady=10
        )

        # INBlockPP и INReleasePE
        ttk.Label(grid, text="INBlockPP (%):", font=('Segoe UI', 10)).grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        in_block_var = tk.StringVar(value=f"{self.selector.in_block_pp}")
        FloatEntry(grid, textvariable=in_block_var, width=8).grid(
            row=3, column=1, sticky=tk.W, padx=10
        )
        ttk.Label(grid, text="(блокировка Ph-Ph)", font=('Segoe UI', 8), foreground='#666').grid(
            row=3, column=2, sticky=tk.W, padx=5
        )

        ttk.Label(grid, text="INReleasePE (%):", font=('Segoe UI', 10)).grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        in_release_var = tk.StringVar(value=f"{self.selector.in_release_pe}")
        FloatEntry(grid, textvariable=in_release_var, width=8).grid(
            row=4, column=1, sticky=tk.W, padx=10
        )
        ttk.Label(grid, text="(разрешение Ph-E)", font=('Segoe UI', 8), foreground='#666').grid(
            row=4, column=2, sticky=tk.W, padx=5
        )

        # Рекомендации
        ttk.Label(
            current_frame,
            text="Рекомендация: IMinOpPP = 2 × IMinOpPE, INBlockPP = 2 × INReleasePE",
            font=('Segoe UI', 9, 'italic'),
            foreground='#2196F3'
        ).pack(anchor=tk.W, pady=(10, 0))

        self.vars["imin_op_pp"] = imin_pp_var
        self.vars["imin_op_pe"] = imin_pe_var
        self.vars["in_block_pp"] = in_block_var
        self.vars["in_release_pe"] = in_release_var

    def _create_style_params(self):
        """Создание параметров оформления"""
        style_frame = ttk.LabelFrame(self.tab, text="Оформление", padding=15)
        style_frame.pack(fill=tk.X, pady=5)

        grid = ttk.Frame(style_frame)
        grid.pack(fill=tk.X)

        # Цвет
        ttk.Label(grid, text="Цвет:", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        color_var = tk.StringVar(value=self.selector.color)
        ColorCombo(grid, textvariable=color_var, colors=self.colors, width=20).grid(
            row=0, column=1, sticky=tk.W, padx=10
        )
        self.vars["color"] = color_var

        # Стиль линии
        ttk.Label(grid, text="Стиль линии:", font=('Segoe UI', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        style_var = tk.StringVar(value=self.selector.linestyle)
        style_combo = ttk.Combobox(
            grid,
            textvariable=style_var,
            values=[s[0] for s in self.linestyles],
            state="readonly",
            width=18
        )
        style_combo.grid(row=1, column=1, sticky=tk.W, padx=10)
        self.vars["linestyle"] = style_var

        # Прозрачность
        ttk.Label(grid, text="Прозрачность:", font=('Segoe UI', 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        opacity_var = tk.StringVar(value=f"{self.selector.opacity:.1f}")
        opacity_frame = ttk.Frame(grid)
        opacity_frame.grid(row=2, column=1, sticky=tk.W, padx=10)
        FloatEntry(opacity_frame, textvariable=opacity_var, width=6).pack(side=tk.LEFT)
        ttk.Label(opacity_frame, text="(0.0-1.0)", font=('Segoe UI', 8), foreground='#666').pack(side=tk.LEFT, padx=5)
        self.vars["opacity"] = opacity_var

        # Привязка отслеживания изменений
        self._bind_traces()

    def _bind_traces(self):
        """Привязка отслеживания изменений переменных"""

        def update_selector(*args):
            try:
                self.selector.enabled = self.vars["enabled"].get()
                self.selector.x1 = float(self.vars["x1"].get().replace(',', '.'))
                self.selector.x0 = float(self.vars["x0"].get().replace(',', '.'))
                self.selector.rffw_pp = float(self.vars["rffw_pp"].get().replace(',', '.'))
                self.selector.rfrv_pp = float(self.vars["rfrv_pp"].get().replace(',', '.'))
                self.selector.rffw_pe = float(self.vars["rffw_pe"].get().replace(',', '.'))
                self.selector.rfrv_pe = float(self.vars["rfrv_pe"].get().replace(',', '.'))
                self.selector.imin_op_pp = float(self.vars["imin_op_pp"].get().replace(',', '.'))
                self.selector.imin_op_pe = float(self.vars["imin_op_pe"].get().replace(',', '.'))
                self.selector.in_block_pp = float(self.vars["in_block_pp"].get().replace(',', '.'))
                self.selector.in_release_pe = float(self.vars["in_release_pe"].get().replace(',', '.'))
                self.selector.color = self.vars["color"].get()
                self.selector.linestyle = self.vars["linestyle"].get()
                self.selector.opacity = float(self.vars["opacity"].get().replace(',', '.'))

                # Обновляем график
                if self.viz.update_job:
                    self.viz.root.after_cancel(self.viz.update_job)
                self.viz.update_job = self.viz.root.after(100, self.viz.deferred_update)

            except ValueError:
                pass

        # Привязка ко всем переменным
        for var in self.vars.values():
            var.trace('w', update_selector)

    def _on_enabled_toggle(self):
        """Обработка включения/отключения селектора"""
        if self.viz.update_job:
            self.viz.root.after_cancel(self.viz.update_job)
        self.viz.update_job = self.viz.root.after(100, self.viz.deferred_update)

    def _reset_to_default(self):
        """Сброс к рекомендуемым значениям"""
        self.vars["x1"].set("5.0")
        self.vars["x0"].set("15.0")
        self.vars["rffw_pp"].set("8.0")
        self.vars["rfrv_pp"].set("4.0")
        self.vars["rffw_pe"].set("12.0")
        self.vars["rfrv_pe"].set("6.0")
        self.vars["imin_op_pp"].set("10")
        self.vars["imin_op_pe"].set("5")
        self.vars["in_block_pp"].set("40")
        self.vars["in_release_pe"].set("20")
        self.vars["color"].set("#9C27B0")
        self.vars["linestyle"].set("-")
        self.vars["opacity"].set("0.8")

        self._show_notification("Сброшено к рекомендуемым значениям")

    def _show_notification(self, message):
        """Показ временного уведомления"""
        if not self.viz.root:
            return

        notification = tk.Toplevel(self.viz.root)
        notification.overrideredirect(True)
        notification.geometry("+{}+{}".format(
            self.viz.root.winfo_rootx() + self.viz.root.winfo_width() - 300,
            self.viz.root.winfo_rooty() + 50
        ))

        frame = tk.Frame(
            notification,
            bg='#333333',
            padx=20,
            pady=10,
            relief='flat'
        )
        frame.pack()

        label = tk.Label(
            frame,
            text=message,
            bg='#333333',
            fg='white',
            font=('Segoe UI', 10)
        )
        label.pack()

        self.viz.root.after(2000, notification.destroy)