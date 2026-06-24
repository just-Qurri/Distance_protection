"""
Модель данных для фазового селектора FDPSPDIS с отстройкой от нагрузки
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid


@dataclass
class SelectorSettings:
    """
    Модель данных для фазового селектора FDPSPDIS
    """
    # ===== Параметры фазового селектора =====
    x1: float = 37.0
    x0: float = 43.0
    rfpp_forward: float = 164.0
    rfpp_reverse: float = 164.0
    rfpe_forward: float = 135.0
    rfpe_reverse: float = 135.0

    # ===== Параметры отстройки от нагрузки =====
    rld_forward: float = 96.0
    rld_reverse: float = 96.0
    arg_load: float = 35.0
    arg_load_phph: float = 30
    load_enabled: bool = True

    # ===== Параметры отображения =====
    enabled: bool = True
    color: str = '#9C27B0'
    linestyle: str = '-'
    opacity: float = 0.8
    direction_mode: str = "non-directional"

    def _to_polygon(self, points: List[Tuple[float, float]]) -> Polygon:
        """Преобразует список точек в полигон Shapely"""
        if len(points) < 3:
            return Polygon()
        # Убеждаемся, что полигон замкнут
        if points[0] != points[-1]:
            points = points + [points[0]]
        poly = Polygon(points)
        if not poly.is_valid:
            poly = make_valid(poly)
        return poly

    def _to_points(self, polygon) -> List[Tuple[float, float]]:
        """Преобразует полигон Shapely в список точек"""
        if polygon.is_empty:
            return []

        if polygon.geom_type == 'Polygon':
            return list(polygon.exterior.coords[:-1])
        elif polygon.geom_type == 'MultiPolygon':
            # Объединяем все части или берем самую большую
            merged = unary_union(polygon)
            if merged.geom_type == 'Polygon':
                return list(merged.exterior.coords[:-1])
            else:
                # Берем самый большой полигон
                largest = max(polygon.geoms, key=lambda p: p.area)
                return list(largest.exterior.coords[:-1])
        return []

    def get_polygon_points(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """
        Возвращает точки полигона фазового селектора.
        """
        if fault_type == "phph":
            r_forward = self.rfpp_forward
            r_reverse = self.rfpp_reverse
        elif fault_type == "phe":
            r_forward = self.rfpe_forward
            r_reverse = self.rfpe_reverse
        else:
            K3 = 2 / np.sqrt(3)
            r_forward = K3 * self.rfpe_forward
            r_reverse = K3 * self.rfpe_reverse

        return self._build_selector(r_forward, r_reverse)

    def _build_selector(self, r_forward: float, r_reverse: float) -> List[Tuple[float, float]]:
        """6 точек фазового селектора (шестиугольник)"""
        x_reach = self.x1
        tan_60 = np.tan(np.radians(60.0))
        r_offset = x_reach / tan_60

        return [
            # ВЕРХНЯЯ ЧАСТЬ
            (-r_reverse / 2, x_reach),
            (r_forward / 2 + r_offset, x_reach),
            (r_forward / 2, 0),

            # НИЖНЯЯ ЧАСТЬ
            (r_forward / 2, -x_reach),
            (-r_reverse / 2 - r_offset, -x_reach),
            (-r_reverse / 2, 0),
        ]

    def get_load_encroachment_lines(self) -> List[Tuple[float, float, float, float]]:
        """
        Возвращает линии границ зоны нагрузки (только ребра полигонов).
        """
        if not self.load_enabled:
            return []

        # Получаем полигоны нагрузки
        load_polygons = self.get_load_encroachment_polygons()
        if not load_polygons:
            return []

        lines = []

        # Для каждого полигона берем его ребра
        for polygon in load_polygons:
            if len(polygon) < 3:
                continue

            # Проходим по всем вершинам полигона и берем ребра
            n = len(polygon)
            for i in range(n):
                p1 = polygon[i]
                p2 = polygon[(i + 1) % n]
                lines.append((p1[0], p1[1], p2[0], p2[1]))

        return lines

    def get_load_encroachment_polygons(self) -> List[List[Tuple[float, float]]]:
        """
        Полигоны сектора нагрузки для заливки.
        """
        if not self.load_enabled:
            return []

        # Метод должен применяться только для Ph-Ph

        # Начальные точки после поворота на 30 градусов отстройки от нагрузок
        length_vector_fw = abs(self.rld_forward * np.cos(np.radians(self.arg_load_phph)))
        length_vector_rv = abs(-self.rld_reverse * np.cos(np.radians(self.arg_load_phph)))
        new_fw_r = self.rld_forward * np.cos(np.radians(self.arg_load_phph)) * np.cos(np.radians(self.arg_load_phph))
        new_rv_r = -self.rld_reverse * np.cos(np.radians(self.arg_load_phph)) * np.cos(np.radians(self.arg_load_phph))
        new_fw_x = -self.rld_forward * np.cos(np.radians(self.arg_load_phph)) * np.sin(np.radians(self.arg_load_phph))
        new_rv_x = self.rld_reverse * np.cos(np.radians(self.arg_load_phph)) * np.sin(np.radians(self.arg_load_phph))

        print(new_fw_r, new_fw_x, new_rv_r, new_rv_x, length_vector_rv,
              length_vector_fw, "1")

        # Точки пересечения лучей нагрузки
        length_vector_ench_fw = length_vector_fw / np.cos(np.radians(self.arg_load))
        length_vector_ench_rv = length_vector_rv / np.cos(np.radians(self.arg_load))

        print(length_vector_ench_fw, length_vector_ench_rv)

        r_cord_arg_ench_1 = np.cos(np.radians(-self.arg_load_phph + self.arg_load)) * length_vector_ench_fw
        x_cord_arg_ench_1 = np.sin(np.radians(-self.arg_load_phph + self.arg_load)) * length_vector_ench_fw
        r_cord_arg_ench_2 = np.cos(np.radians(- self.arg_load_phph - self.arg_load)) * length_vector_ench_fw
        x_cord_arg_ench_2 = np.sin(np.radians(- self.arg_load_phph - self.arg_load)) * length_vector_ench_fw
        r_cord_arg_ench_3 = np.cos(np.radians(180 - self.arg_load_phph - self.arg_load)) * length_vector_ench_rv
        x_cord_arg_ench_3 = np.sin(np.radians(180 - self.arg_load_phph - self.arg_load)) * length_vector_ench_rv
        r_cord_arg_ench_4 = np.cos(np.radians(180 - self.arg_load_phph + self.arg_load)) * length_vector_ench_rv
        x_cord_arg_ench_4 = np.sin(np.radians(180 - self.arg_load_phph + self.arg_load)) * length_vector_ench_rv
        print(r_cord_arg_ench_1, r_cord_arg_ench_2, r_cord_arg_ench_3, r_cord_arg_ench_4)

        # Для отображения и масштаба
        const_scale = 100

        polygons = [
            [(new_fw_r, new_fw_x), (r_cord_arg_ench_1, x_cord_arg_ench_1),
             (r_cord_arg_ench_1 * const_scale, x_cord_arg_ench_1 * const_scale),
             (new_fw_r * const_scale, new_fw_x * const_scale),
             ],
            [(new_fw_r, new_fw_x), (r_cord_arg_ench_2, x_cord_arg_ench_2),
             (r_cord_arg_ench_2 * const_scale, x_cord_arg_ench_2 * const_scale),
             (new_fw_r * const_scale, new_fw_x * const_scale),
             ],
            [(new_rv_r, new_rv_x), (r_cord_arg_ench_3, x_cord_arg_ench_3),
             (r_cord_arg_ench_3 * const_scale, x_cord_arg_ench_3 * const_scale),
             (new_rv_r * const_scale, new_rv_x * const_scale),
             ],
            [(new_rv_r, new_rv_x), (r_cord_arg_ench_4, x_cord_arg_ench_4),
             (r_cord_arg_ench_4 * const_scale, x_cord_arg_ench_4 * const_scale),
             (new_rv_r * const_scale, new_rv_x * const_scale),
             ]

        ]

        return polygons

    def _get_merged_load_polygon(self) -> Optional[Polygon]:
        """Объединяет все полигоны нагрузки в один"""
        if not self.load_enabled:
            return None

        load_polygons = self.get_load_encroachment_polygons()
        if not load_polygons:
            return None

        # Создаем полигоны Shapely
        polygons = [self._to_polygon(poly) for poly in load_polygons]
        # Объединяем все полигоны
        merged = unary_union(polygons)
        return merged

    def get_clipped_selector_points(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """
        Возвращает точки периметра обрезанного фазового селектора.
        """
        if not self.load_enabled:
            return self.get_polygon_points(fault_type)

        selector_points = self.get_polygon_points(fault_type)
        if not selector_points:
            return []

        # Получаем объединенный полигон нагрузки
        load_polygon = self._get_merged_load_polygon()
        if load_polygon is None or load_polygon.is_empty:
            return selector_points

        # Создаем полигон селектора
        selector_polygon = self._to_polygon(selector_points)
        if selector_polygon.is_empty:
            return []

        # Вычитаем нагрузку из селектора
        result = selector_polygon.difference(load_polygon)

        # Возвращаем точки результата
        return self._to_points(result)

    def get_clipped_load_points(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """
        Возвращает точки зоны нагрузки, обрезанной селектором.
        """
        if not self.load_enabled:
            return []

        load_polygon = self._get_merged_load_polygon()
        if load_polygon is None or load_polygon.is_empty:
            return []

        selector_points = self.get_polygon_points(fault_type)
        if not selector_points:
            return []

        # Создаем полигон селектора
        selector_polygon = self._to_polygon(selector_points)
        if selector_polygon.is_empty:
            return []

        # Находим пересечение нагрузки с селектором
        result = load_polygon.intersection(selector_polygon)

        # Возвращаем точки результата
        return self._to_points(result)

    def get_selector_perimeter_without_load(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """
        Возвращает точки периметра селектора за вычетом зоны нагрузки.
        """
        return self.get_clipped_selector_points(fault_type)

    def get_intersection_points(self, fault_type: str = "phph") -> List[Tuple[float, float]]:
        """
        Возвращает точки пересечения границ селектора и нагрузки.
        """
        if not self.load_enabled:
            return []

        selector_points = self.get_polygon_points(fault_type)
        if not selector_points:
            return []

        load_polygon = self._get_merged_load_polygon()
        if load_polygon is None or load_polygon.is_empty:
            return []

        # Создаем полигон селектора
        selector_polygon = self._to_polygon(selector_points)
        if selector_polygon.is_empty:
            return []

        # Получаем границы полигонов
        selector_boundary = selector_polygon.boundary
        load_boundary = load_polygon.boundary

        # Находим точки пересечения границ
        intersection = selector_boundary.intersection(load_boundary)

        if intersection.is_empty:
            return []

        # Извлекаем точки
        points = []
        if intersection.geom_type == 'Point':
            points.append((intersection.x, intersection.y))
        elif intersection.geom_type == 'MultiPoint':
            points.extend([(p.x, p.y) for p in intersection.geoms])
        elif intersection.geom_type == 'GeometryCollection':
            for geom in intersection.geoms:
                if geom.geom_type == 'Point':
                    points.append((geom.x, geom.y))
                elif geom.geom_type == 'MultiPoint':
                    points.extend([(p.x, p.y) for p in geom.geoms])

        return points

    def get_all_clipped_data(self, fault_type: str = "phph") -> dict:
        """
        Возвращает все данные для визуализации обрезанных зон.
        """
        selector_full = self.get_polygon_points(fault_type)
        selector_clipped = self.get_clipped_selector_points(fault_type)

        return {
            'selector_clipped': selector_clipped,
            'load_clipped': self.get_clipped_load_points(fault_type),
            'intersection_points': self.get_intersection_points(fault_type),
            'selector_full': selector_full,
            'load_full': self.get_load_encroachment_polygons() if self.load_enabled else [],
            'is_clipped': self.load_enabled and len(selector_clipped) < len(selector_full)
        }
