# -*- coding: utf-8 -*-
"""
Вкладка для расчетных точек пересечений характеристик (оптимизирована)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple

from shapely.geometry import Polygon, Point

from models.calculation_points import CalculationPointsSettings
from ui.base_tab import BaseTab
from ui.constants import DEFAULT_POINTS_VALUES
from widgets.color_combo import ColorCombo
from widgets.float_entry import FloatEntry
from widgets.modern_button import ModernButton


class PointsTab(BaseTab):
    """Вкладка для расчетных точек пересечений характеристик"""

    def __init__(self, notebook: ttk.Notebook, settings: CalculationPointsSettings,
                 visualizer, colors: List, linestyles: List):
        self.points_settings = settings
        self.selected_index = tk.IntVar(value=-1)
        super().__init__(notebook, visualizer, colors, linestyles)
        self.viz.points_settings = settings

    def get_tab_name(self) -> str:
        return "📍 Расчетные точки"

    def _get_target_object(self):
        return self.points_settings

    def _create_ui(self):
        """Создание UI"""
        obj = self.points_settings

        self.vars.update({
            "enabled": tk.BooleanVar(value=obj.enabled),
            "show_labels": tk.BooleanVar(value=obj.show_labels),
            "marker_size": tk.StringVar(value=f"{obj.marker_size:.1f}"),
            "point_name": tk.StringVar(value=""),
            "point_r": tk.StringVar(value="0.0"),
            "point_x": tk.StringVar(value="0.0"),
            "point_color": tk.StringVar(value="#E91E63"),
        })

        self._create_title_frame("Расчетные точки пересечений", '#E91E63')
        self._create_main_controls()
        self._create_points_list()
        self._create_point_editor()

        self.vars["show_labels"].trace('w', lambda *args: self._on_show_toggle())
        self.vars["enabled"].trace('w', lambda *args: self._on_show_toggle())

    def _create_main_controls(self):
        """Создание основных элементов управления"""
        main_frame = ttk.LabelFrame(self.tab, text="Управление", padding=5)
        main_frame.pack(fill=tk.X, pady=5)

        check_frame = ttk.Frame(main_frame)
        check_frame.pack(fill=tk.X)

        ttk.Checkbutton(check_frame, text="Показать расчетные точки",
                        variable=self.vars["enabled"]).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(check_frame, text="Показывать подписи",
                        variable=self.vars["show_labels"]).pack(anchor=tk.W, pady=2)

        size_frame = ttk.Frame(main_frame)
        size_frame.pack(fill=tk.X, pady=5)

        ttk.Label(size_frame, text="Размер маркеров:", font=('Segoe UI', 9)).pack(side=tk.LEFT)
        size_entry = FloatEntry(size_frame, textvariable=self.vars["marker_size"], width=6,
                                on_change_callback=self._apply_changes)
        size_entry.pack(side=tk.LEFT, padx=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ModernButton(
            btn_frame,
            text="🔄 Рассчитать точки пересечений",
            icon="",
            style="primary",
            width=30,
            command=self._auto_calculate_intersections
        ).pack(side=tk.LEFT)

    def _create_points_list(self):
        """Создание списка точек"""
        list_frame = ttk.LabelFrame(self.tab, text="Список точек пересечений", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.points_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            height=8,
            font=('Segoe UI', 9)
        )
        self.points_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.points_listbox.yview)

        self.points_listbox.bind('<<ListboxSelect>>', self._on_select_point)

        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ModernButton(btn_frame, text="Добавить вручную", icon="➕",
                     style="success", width=15, command=self._add_point).pack(side=tk.LEFT, padx=2)
        ModernButton(btn_frame, text="Удалить", icon="➖",
                     style="danger", width=12, command=self._remove_point).pack(side=tk.LEFT, padx=2)
        ModernButton(btn_frame, text="Очистить", icon="🗑️",
                     style="warning", width=12, command=self._clear_points).pack(side=tk.LEFT, padx=2)

        self._update_points_list()

    def _create_point_editor(self):
        """Создание редактора точки"""
        editor_frame = ttk.LabelFrame(self.tab, text="Редактор точки", padding=5)
        editor_frame.pack(fill=tk.X, pady=5)

        # Имя
        name_frame = ttk.Frame(editor_frame)
        name_frame.pack(fill=tk.X, pady=2)
        ttk.Label(name_frame, text="Имя:", font=('Segoe UI', 9)).pack(side=tk.LEFT)
        ttk.Entry(name_frame, textvariable=self.vars["point_name"], width=15).pack(side=tk.LEFT, padx=5)

        # R
        r_frame = ttk.Frame(editor_frame)
        r_frame.pack(fill=tk.X, pady=2)
        ttk.Label(r_frame, text="R (Ом):", font=('Segoe UI', 9)).pack(side=tk.LEFT)
        FloatEntry(r_frame, textvariable=self.vars["point_r"], width=8,
                   on_change_callback=self._apply_changes).pack(side=tk.LEFT, padx=5)

        # X
        x_frame = ttk.Frame(editor_frame)
        x_frame.pack(fill=tk.X, pady=2)
        ttk.Label(x_frame, text="X (Ом):", font=('Segoe UI', 9)).pack(side=tk.LEFT)
        FloatEntry(x_frame, textvariable=self.vars["point_x"], width=8,
                   on_change_callback=self._apply_changes).pack(side=tk.LEFT, padx=5)

        # Цвет
        color_frame = ttk.Frame(editor_frame)
        color_frame.pack(fill=tk.X, pady=2)
        ttk.Label(color_frame, text="Цвет:", font=('Segoe UI', 9)).pack(side=tk.LEFT)
        ColorCombo(color_frame, textvariable=self.vars["point_color"],
                   colors=self.colors, width=12).pack(side=tk.LEFT, padx=5)

        # Кнопки
        btn_frame = ttk.Frame(editor_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ModernButton(btn_frame, text="Обновить", icon="✏️",
                     style="info", width=15, command=self._update_point).pack(side=tk.LEFT, padx=2)
        ModernButton(btn_frame, text="Добавить", icon="➕",
                     style="success", width=15, command=self._add_point).pack(side=tk.LEFT, padx=2)

    def _update_points_list(self):
        """Обновление списка точек"""
        self.points_listbox.delete(0, tk.END)
        for i, point in enumerate(self.points_settings.points):
            self.points_listbox.insert(tk.END, f"{i + 1}. {point.name} (R={point.r:.2f}, X={point.x:.2f})")

        if self.points_settings.points:
            self.points_listbox.selection_set(0)
            self._on_select_point(None)

    def _on_select_point(self, event):
        """Обработка выбора точки из списка"""
        selection = self.points_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_index.set(index)
            point = self.points_settings.get_point(index)
            if point:
                self._set_var("point_name", point.name)
                self._set_var("point_r", point.r)
                self._set_var("point_x", point.x)
                self._set_var("point_color", point.color)

    def _get_point_from_ui(self) -> Tuple[str, float, float, str]:
        """Получить данные точки из UI"""
        name = self.vars["point_name"].get().strip()
        if not name:
            name = f"Точка {len(self.points_settings.points) + 1}"
        r = float(self.vars["point_r"].get().replace(',', '.'))
        x = float(self.vars["point_x"].get().replace(',', '.'))
        color = self.vars["point_color"].get()
        return name, r, x, color

    def _add_point(self):
        """Добавление точки вручную"""
        try:
            name, r, x, color = self._get_point_from_ui()
            self.points_settings.add_point(name, r, x)
            self._update_points_list()
            self.viz.plot_characteristics(keep_limits=True)
            self.viz._update_status()
            self.viz._show_notification(f"Добавлена точка: {name}")
        except ValueError as e:
            self.viz._show_notification(f"Ошибка: {e}")

    def _update_point(self):
        """Обновление выбранной точки"""
        index = self.selected_index.get()
        if index < 0 or index >= len(self.points_settings.points):
            self.viz._show_notification("Выберите точку для обновления")
            return

        try:
            name, r, x, color = self._get_point_from_ui()
            point = self.points_settings.get_point(index)
            if point:
                point.name = name
                point.r = r
                point.x = x
                point.color = color
                self._update_points_list()
                self.viz.plot_characteristics(keep_limits=True)
                self.viz._update_status()
                self.viz._show_notification(f"Обновлена точка: {name}")
        except ValueError as e:
            self.viz._show_notification(f"Ошибка: {e}")

    def _remove_point(self):
        """Удаление выбранной точки"""
        index = self.selected_index.get()
        if index < 0 or index >= len(self.points_settings.points):
            self.viz._show_notification("Выберите точку для удаления")
            return

        point = self.points_settings.get_point(index)
        self.points_settings.remove_point(index)
        self._update_points_list()
        self.viz.plot_characteristics(keep_limits=True)
        self.viz._update_status()
        self.viz._show_notification(f"Удалена точка: {point.name if point else '?'}")

    def _clear_points(self):
        """Очистка всех точек"""
        if not self.points_settings.points:
            return

        if messagebox.askyesno("Подтверждение", "Удалить все расчетные точки?"):
            self.points_settings.points.clear()
            self._update_points_list()
            self.viz.plot_characteristics(keep_limits=True)
            self.viz._update_status()
            self.viz._show_notification("Все точки удалены")

    def _auto_calculate_intersections(self):
        """Автоматический расчет точек пересечений характеристик"""
        self.points_settings.points.clear()

        fault_type = self.viz.fault_type.get() if self.viz.fault_type else "ph-ph"
        polygons = self._collect_polygons(fault_type)

        intersection_points = self._find_polygon_intersections(polygons)

        for name, r, x, color in intersection_points:
            self.points_settings.add_point(name=name, r=r, x=x, description=f"Пересечение {name}")

        self._update_points_list()
        self.viz.plot_characteristics(keep_limits=True)
        self.viz._update_status()
        self.viz._show_notification(f"Найдено {len(intersection_points)} точек пересечений")

    def _collect_polygons(self, fault_type: str) -> List[dict]:
        """Сбор всех полигонов для поиска пересечений"""
        polygons = []

        # Зоны
        for zone in self.viz.zones:
            if zone.enabled:
                points = zone.get_polygon_points(fault_type)
                if points and len(points) >= 3:
                    polygons.append({
                        'name': f"Зона {zone.zone_id}",
                        'points': points,
                        'color': zone.color
                    })

        # Фазовый селектор
        if self.viz.selector and self.viz.selector.enabled and self.viz.selector_calculator:
            points = self.viz.selector_calculator.get_polygon_points(fault_type)
            if points and len(points) >= 3:
                polygons.append({
                    'name': "Фазовый селектор",
                    'points': points,
                    'color': self.viz.selector.color
                })

        # Блокировка от качаний
        if self.viz.swing_settings and self.viz.swing_settings.enabled and self.viz.swing_calculator:
            if self.viz.swing_settings.show_zin:
                points = self.viz.swing_calculator.get_zin_polygon_points()
                if points and len(points) >= 3:
                    polygons.append({
                        'name': "ZIN",
                        'points': points,
                        'color': self.viz.swing_settings.color_zin
                    })
            if self.viz.swing_settings.show_zout:
                points = self.viz.swing_calculator.get_zout_polygon_points()
                if points and len(points) >= 3:
                    polygons.append({
                        'name': "ZOUT",
                        'points': points,
                        'color': self.viz.swing_settings.color_zout
                    })

        return polygons

    def _find_polygon_intersections(self, polygons: List[dict]) -> List[Tuple[str, float, float, str]]:
        """Находит точки пересечения между полигонами"""
        if len(polygons) < 2:
            return []

        results = []
        for i in range(len(polygons)):
            for j in range(i + 1, len(polygons)):
                poly1 = self._points_to_polygon(polygons[i]['points'])
                poly2 = self._points_to_polygon(polygons[j]['points'])

                if poly1.is_empty or poly2.is_empty:
                    continue

                intersection = poly1.boundary.intersection(poly2.boundary)
                if intersection.is_empty:
                    continue

                points = self._extract_points(intersection)
                for r, x in points:
                    if (poly1.contains(Point(r, x)) or poly1.boundary.distance(Point(r, x)) < 0.001) and \
                            (poly2.contains(Point(r, x)) or poly2.boundary.distance(Point(r, x)) < 0.001):
                        results.append((
                            f"{polygons[i]['name']} ∩ {polygons[j]['name']}",
                            r, x, '#E91E63'
                        ))

        # Удаление дубликатов
        unique = []
        for point in results:
            if not any(abs(point[1] - p[1]) < 0.01 and abs(point[2] - p[2]) < 0.01 for p in unique):
                unique.append(point)

        return unique

    @staticmethod
    def _points_to_polygon(points: List[Tuple[float, float]]) -> Polygon:
        """Преобразует список точек в полигон Shapely"""
        if len(points) < 3:
            return Polygon()
        if points[0] != points[-1]:
            points = points + [points[0]]
        return Polygon(points)

    @staticmethod
    def _extract_points(geometry) -> List[Tuple[float, float]]:
        """Извлекает точки из геометрии Shapely"""
        points = []
        if geometry.geom_type == 'Point':
            points.append((geometry.x, geometry.y))
        elif geometry.geom_type == 'MultiPoint':
            points.extend([(p.x, p.y) for p in geometry.geoms])
        elif geometry.geom_type in ('LineString', 'MultiLineString'):
            coords = geometry.coords if geometry.geom_type == 'LineString' else []
            if not coords:
                for line in geometry.geoms:
                    points.extend([(p[0], p[1]) for p in line.coords])
            else:
                points.extend([(p[0], p[1]) for p in coords])
        elif geometry.geom_type == 'GeometryCollection':
            for geom in geometry.geoms:
                points.extend(PointsTab._extract_points(geom))
        return points

    def _on_show_toggle(self):
        """Обработка переключения отображения"""
        self.viz.plot_characteristics(keep_limits=True)
        self.viz._update_status()

    def _do_apply(self, obj):
        """Применение настроек точек"""
        obj.show_labels = self.vars["show_labels"].get()
        obj.marker_size = self._get_float_value("marker_size")

    def _do_cancel(self, obj):
        """Отмена настроек точек"""
        self._set_var("marker_size", obj.marker_size)
