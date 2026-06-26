"""
Калькулятор для фазового селектора
"""

from typing import List, Tuple, Optional

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

from models.selector_default_settings import SelectorSettings


class SelectorCalculator:
    """
    Калькулятор для вычисления геометрии фазового селектора
    """

    # Константы
    LOAD_SCALE = 1000  # Масштаб для отображения зоны нагрузки

    def __init__(self, settings: SelectorSettings):
        self.settings = settings

    def get_polygon_points(self, fault_type: str) -> List[Tuple[float, float]]:
        """
        Возвращает точки полигона фазового селектора
        """
        if fault_type == "ph-e":
            r_forward = self.settings.rfpe_forward
            r_reverse = self.settings.rfpe_reverse
        else:
            r_forward = self.settings.rfpp_forward
            r_reverse = self.settings.rfpp_reverse

        return self._build_selector(r_forward, r_reverse, fault_type)

    def _build_selector(
            self,
            r_forward: float,
            r_reverse: float,
            fault_type: str
    ) -> List[Tuple[float, float]]:
        """Построение шестиугольника фазового селектора"""
        koeff_pe = (self.settings.x0 - self.settings.x1) / 3
        tan_60 = np.tan(np.radians(60.0))

        if fault_type == "ph-ph":
            x_reach = self.settings.x1
            r_offset = x_reach / tan_60
            return [
                (-r_reverse / 2, x_reach),
                (r_forward / 2 + r_offset, x_reach),
                (r_forward / 2, 0),
                (r_forward / 2, -x_reach),
                (-r_reverse / 2 - r_offset, -x_reach),
                (-r_reverse / 2, 0),
            ]

        elif fault_type == "ph-e":
            x_reach = self.settings.x1 + koeff_pe
            r_offset = x_reach / tan_60
            return [
                (-r_reverse, x_reach),
                (r_forward + r_offset, x_reach),
                (r_forward, 0),
                (r_forward, -x_reach),
                (-r_reverse - r_offset, -x_reach),
                (-r_reverse, 0),
            ]

        elif fault_type == "3-ph":
            x_reach = 4 * self.settings.x1 / 3
            k3 = 2 / np.sqrt(3)
            sin_30 = np.sin(np.radians(self.settings.arg_load_3ph))
            cos_30 = np.cos(np.radians(self.settings.arg_load_3ph))
            rfpp = self.settings.rfpp_forward
            rfpr = self.settings.rfpp_reverse

            return [
                (0, x_reach),
                (0.5 * rfpp * k3 * cos_30, x_reach + 0.5 * rfpp * k3 * sin_30),
                (0.5 * rfpp * k3 * cos_30, 0.5 * rfpp * k3 * sin_30),
                (self.settings.x1 * k3 * sin_30 + 0.5 * rfpp * k3 * cos_30,
                 -self.settings.x1 * k3 * cos_30 + 0.5 * rfpp * k3 * sin_30),
                (0, -x_reach),
                (-0.5 * rfpr * k3 * cos_30, -x_reach - 0.5 * rfpp * k3 * sin_30),
                (-0.5 * rfpr * k3 * cos_30, -0.5 * rfpp * k3 * sin_30),
                (-self.settings.x1 * k3 * sin_30 - 0.5 * rfpr * k3 * cos_30,
                 self.settings.x1 * k3 * cos_30 - 0.5 * rfpp * k3 * sin_30),
            ]

        else:
            raise ValueError(f"Неправильный вид КЗ: {fault_type}")

    def get_load_encroachment_polygons(self, fault_type: str) -> List[List[Tuple[float, float]]]:
        """
        Полигоны сектора нагрузки для заливки
        """
        if not self.settings.load_enabled:
            return []

        if fault_type == "ph-ph":
            return self._get_load_polygons_phph()
        else:
            return self._get_load_polygons_general()

    def _get_load_polygons_phph(self) -> List[List[Tuple[float, float]]]:
        """Полигоны нагрузки для Ph-Ph"""
        # Начальные точки после поворота на 30 градусов
        cos_load = np.cos(np.radians(self.settings.arg_load_phph))
        sin_load = np.sin(np.radians(self.settings.arg_load_phph))

        length_fw = abs(self.settings.rld_forward * cos_load)
        length_rv = abs(-self.settings.rld_reverse * cos_load)

        new_fw_r = self.settings.rld_forward * cos_load * cos_load
        new_rv_r = -self.settings.rld_reverse * cos_load * cos_load
        new_fw_x = -self.settings.rld_forward * cos_load * sin_load
        new_rv_x = self.settings.rld_reverse * cos_load * sin_load

        # Точки пересечения лучей нагрузки
        length_fw_ench = length_fw / np.cos(np.radians(self.settings.arg_load))
        length_rv_ench = length_rv / np.cos(np.radians(self.settings.arg_load))

        angle = self.settings.arg_load_phph
        arg = self.settings.arg_load

        points = []
        for i, (length, angle_offset, r_start, x_start) in enumerate([
            (length_fw_ench, -angle + arg, new_fw_r, new_fw_x),
            (length_fw_ench, -angle - arg, new_fw_r, new_fw_x),
            (length_rv_ench, 180 - angle - arg, new_rv_r, new_rv_x),
            (length_rv_ench, 180 - angle + arg, new_rv_r, new_rv_x),
        ]):
            r_cord = np.cos(np.radians(angle_offset)) * length
            x_cord = np.sin(np.radians(angle_offset)) * length
            points.append([
                (r_start, x_start),
                (r_cord, x_cord),
                (r_cord * self.LOAD_SCALE, x_cord * self.LOAD_SCALE),
                (r_start * self.LOAD_SCALE, x_start * self.LOAD_SCALE),
            ])

        return points

    def _get_load_polygons_general(self) -> List[List[Tuple[float, float]]]:
        """Полигоны нагрузки для общих случаев"""
        arg = self.settings.arg_load
        rld_fw = self.settings.rld_forward
        rld_rv = self.settings.rld_reverse

        points = [
            (rld_fw, np.tan(np.radians(arg)) * rld_fw),
            (rld_fw, np.tan(np.radians(-arg)) * rld_fw),
            (-rld_rv, np.tan(np.radians(180 - arg)) * rld_rv),
            (-rld_rv, np.tan(np.radians(180 + arg)) * rld_rv),
        ]

        result = []
        for i, (r_cord, x_cord) in enumerate(points):
            r_start = rld_fw if i < 2 else -rld_rv
            x_start = 0
            result.append([
                (r_start, x_start),
                (r_cord, x_cord),
                (r_cord * self.LOAD_SCALE, x_cord * self.LOAD_SCALE),
                (r_start * self.LOAD_SCALE, x_start * self.LOAD_SCALE),
            ])

        return result

    def get_clipped_selector_points(self, fault_type: str) -> List[Tuple[float, float]]:
        """
        Возвращает точки обрезанного фазового селектора
        """
        if not self.settings.load_enabled:
            return self.get_polygon_points(fault_type)

        selector_points = self.get_polygon_points(fault_type)
        if not selector_points:
            return []

        load_polygon = self._get_merged_load_polygon(fault_type)
        if load_polygon is None or load_polygon.is_empty:
            return selector_points

        selector_polygon = self._to_polygon(selector_points)
        if selector_polygon.is_empty:
            return []

        result = selector_polygon.difference(load_polygon)
        return self._to_points(result)

    def get_intersection_points(self, fault_type: str) -> List[Tuple[float, float]]:
        """
        Возвращает точки пересечения границ селектора и нагрузки
        """
        if not self.settings.load_enabled:
            return []

        selector_points = self.get_polygon_points(fault_type)
        if not selector_points:
            return []

        load_polygon = self._get_merged_load_polygon(fault_type)
        if load_polygon is None or load_polygon.is_empty:
            return []

        selector_polygon = self._to_polygon(selector_points)
        if selector_polygon.is_empty:
            return []

        intersection = selector_polygon.boundary.intersection(load_polygon.boundary)

        if intersection.is_empty:
            return []

        return self._extract_points(intersection)

    def get_clipped_load_points(self, fault_type: str) -> List[Tuple[float, float]]:
        """
        Возвращает точки зоны нагрузки, обрезанной селектором
        """
        if not self.settings.load_enabled:
            return []

        load_polygon = self._get_merged_load_polygon(fault_type)
        if load_polygon is None or load_polygon.is_empty:
            return []

        selector_points = self.get_polygon_points(fault_type)
        if not selector_points:
            return []

        selector_polygon = self._to_polygon(selector_points)
        if selector_polygon.is_empty:
            return []

        result = load_polygon.intersection(selector_polygon)
        return self._to_points(result)

    def _get_merged_load_polygon(self, fault_type: str) -> Optional[Polygon]:
        """Объединяет все полигоны нагрузки в один"""
        if not self.settings.load_enabled:
            return None

        load_polygons = self.get_load_encroachment_polygons(fault_type)
        if not load_polygons:
            return None

        polygons = [self._to_polygon(poly) for poly in load_polygons]
        merged = unary_union(polygons)
        return merged if not merged.is_empty else None

    @staticmethod
    def _to_polygon(points: List[Tuple[float, float]]) -> Polygon:
        """Преобразует список точек в полигон Shapely"""
        if len(points) < 3:
            return Polygon()

        if points[0] != points[-1]:
            points = points + [points[0]]

        poly = Polygon(points)
        if not poly.is_valid:
            poly = make_valid(poly)
        return poly

    @staticmethod
    def _to_points(polygon) -> List[Tuple[float, float]]:
        """Преобразует полигон Shapely в список точек"""
        if polygon.is_empty:
            return []

        if polygon.geom_type == 'Polygon':
            return list(polygon.exterior.coords[:-1])
        elif polygon.geom_type == 'MultiPolygon':
            merged = unary_union(polygon)
            if merged.geom_type == 'Polygon':
                return list(merged.exterior.coords[:-1])
            else:
                largest = max(polygon.geoms, key=lambda p: p.area)
                return list(largest.exterior.coords[:-1])
        return []

    @staticmethod
    def _extract_points(geometry) -> List[Tuple[float, float]]:
        """Извлекает точки из геометрии Shapely"""
        points = []

        if geometry.geom_type == 'Point':
            points.append((geometry.x, geometry.y))
        elif geometry.geom_type == 'MultiPoint':
            points.extend([(p.x, p.y) for p in geometry.geoms])
        elif geometry.geom_type == 'GeometryCollection':
            for geom in geometry.geoms:
                if geom.geom_type == 'Point':
                    points.append((geom.x, geom.y))
                elif geom.geom_type == 'MultiPoint':
                    points.extend([(p.x, p.y) for p in geom.geoms])

        return points

    def get_all_clipped_data(self, fault_type: str) -> dict:
        """
        Возвращает все данные для визуализации
        """
        selector_full = self.get_polygon_points(fault_type)
        selector_clipped = self.get_clipped_selector_points(fault_type)

        return {
            'selector_clipped': selector_clipped,
            'load_clipped': self.get_clipped_load_points(fault_type),
            'intersection_points': self.get_intersection_points(fault_type),
            'selector_full': selector_full,
            'load_full': self.get_load_encroachment_polygons(fault_type) if self.settings.load_enabled else [],
            'is_clipped': self.settings.load_enabled and len(selector_clipped) < len(selector_full)
        }
