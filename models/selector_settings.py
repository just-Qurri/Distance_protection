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
        Линии отстройки от нагрузки
        """
        if not self.load_enabled:
            return []

        tan_load = np.tan(np.radians(self.arg_load))
        max_r = max(self.rld_forward, self.rld_reverse) * 2.5

        r_fw = self.rld_forward
        r_rv = -self.rld_reverse

        return [
            # Лучи сектора (от начала координат)
            (0, 0, max_r, max_r * tan_load),  # Луч в I квадранте
            (0, 0, -max_r, max_r * tan_load),  # Луч в II квадранте
            (0, 0, -max_r, -max_r * tan_load),  # Луч в III квадранте
            (0, 0, max_r, -max_r * tan_load),  # Луч в IV квадранте

            # Перпендикуляры в точках RLdFw и RLdRv (границы сектора)
            (r_fw, -max_r * tan_load, r_fw, max_r * tan_load),  # Перпендикуляр в RLdFw
            (r_rv, -max_r * tan_load, r_rv, max_r * tan_load),  # Перпендикуляр в -RLdRv
        ]

    def get_load_encroachment_polygons(self) -> List[List[Tuple[float, float]]]:
        """
        Полигоны сектора нагрузки для заливки.
        """
        if not self.load_enabled:
            return []

        tan_load = np.tan(np.radians(self.arg_load))
        max_r = max(self.rld_forward, self.rld_reverse) * 2.5

        r_fw = self.rld_forward
        r_rv = -self.rld_reverse
        x_fw = r_fw * tan_load
        x_rv = abs(r_rv) * tan_load

        return [
            # I квадрант
            [(r_fw, 0), (r_fw, x_fw), (max_r, max_r * tan_load), (max_r, 0)],
            # II квадрант
            [(r_rv, 0), (r_rv, x_rv), (-max_r, max_r * tan_load), (-max_r, 0)],
            # III квадрант
            [(r_rv, 0), (r_rv, -x_rv), (-max_r, -max_r * tan_load), (-max_r, 0)],
            # IV квадрант
            [(r_fw, 0), (r_fw, -x_fw), (max_r, -max_r * tan_load), (max_r, 0)],
        ]

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
