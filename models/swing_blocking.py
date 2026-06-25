"""
Модель для блокировки от качаний (ZIN/ZOUT)
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid


@dataclass
class SwingBlockingSettings:
    """
    Настройки блокировки от качаний
    """
    # Внутренняя зона качаний (ZIN)
    x1_zin: float = 37.0
    rfpp_zin: float = 164.0
    rfpe_zin: float = 135.0

    # Внешняя зона качаний (ZOUT)
    x1_zout: float = 55.0
    rfpp_zout: float = 200.0
    rfpe_zout: float = 180.0

    # Отстройка от нагрузки для ZIN
    rld_forward_zin: float = 96.0
    rld_reverse_zin: float = 96.0
    arg_load_zin: float = 35.0

    # Отстройка от нагрузки для ZOUT
    rld_forward_zout: float = 80.0
    rld_reverse_zout: float = 80.0
    arg_load_zout: float = 30.0

    # Общие параметры
    load_enabled: bool = True
    enabled: bool = True
    color_zin: str = '#FF5722'
    color_zout: str = '#FF9800'
    linestyle_zin: str = '-'
    linestyle_zout: str = '-'
    opacity_zin: float = 0.6
    opacity_zout: float = 0.4
    show_zin: bool = True
    show_zout: bool = True

    type: str = field(default="swing", init=False)


class SwingCalculator:
    """
    Калькулятор для блокировки от качаний
    """

    LOAD_SCALE = 1000
    K3 = 2 / np.sqrt(3)

    def __init__(self, settings: SwingBlockingSettings):
        self.settings = settings

    def get_zin_polygon_points(self) -> List[Tuple[float, float]]:
        """Получить точки полигона ZIN (внутренняя зона)"""
        return self._build_swing_polygon(
            self.settings.x1_zin,
            self.settings.rfpp_zin,
            self.settings.rfpe_zin,
            "ZIN"
        )

    def get_zout_polygon_points(self) -> List[Tuple[float, float]]:
        """Получить точки полигона ZOUT (внешняя зона)"""
        return self._build_swing_polygon(
            self.settings.x1_zout,
            self.settings.rfpp_zout,
            self.settings.rfpe_zout,
            "ZOUT"
        )

    def _build_swing_polygon(
            self,
            x1: float,
            rfpp: float,
            rfpe: float,
            zone_name: str
    ) -> List[Tuple[float, float]]:
        """
        Построение полигона для зоны качаний
        Используется та же логика, что и для 3-ph в фазовом селекторе
        """
        sin_30 = np.sin(np.radians(30.0))
        cos_30 = np.cos(np.radians(30.0))
        x_reach = 4 * x1 / 3
        k3 = self.K3

        # Используем rfpp для обеих сторон
        rf = rfpp
        rr = rfpp

        return [
            (0, x_reach),
            (0.5 * rf * k3 * cos_30, x_reach + 0.5 * rf * k3 * sin_30),
            (0.5 * rf * k3 * cos_30, 0.5 * rf * k3 * sin_30),
            (x1 * k3 * sin_30 + 0.5 * rf * k3 * cos_30,
             -x1 * k3 * cos_30 + 0.5 * rf * k3 * sin_30),
            (0, -x_reach),
            (-0.5 * rr * k3 * cos_30, -x_reach - 0.5 * rf * k3 * sin_30),
            (-0.5 * rr * k3 * cos_30, -0.5 * rf * k3 * sin_30),
            (-x1 * k3 * sin_30 - 0.5 * rr * k3 * cos_30,
             x1 * k3 * cos_30 - 0.5 * rf * k3 * sin_30),
        ]

    def get_load_polygons_zin(self) -> List[List[Tuple[float, float]]]:
        """Получить полигоны нагрузки для ZIN"""
        if not self.settings.load_enabled:
            return []

        return self._get_load_polygons_general(
            self.settings.rld_forward_zin,
            self.settings.rld_reverse_zin,
            self.settings.arg_load_zin
        )

    def get_load_polygons_zout(self) -> List[List[Tuple[float, float]]]:
        """Получить полигоны нагрузки для ZOUT"""
        if not self.settings.load_enabled:
            return []

        return self._get_load_polygons_general(
            self.settings.rld_forward_zout,
            self.settings.rld_reverse_zout,
            self.settings.arg_load_zout
        )

    def _get_load_polygons_general(
            self,
            rld_forward: float,
            rld_reverse: float,
            arg_load: float
    ) -> List[List[Tuple[float, float]]]:
        """Полигоны нагрузки для общих случаев"""
        arg = arg_load
        rld_fw = rld_forward
        rld_rv = rld_reverse

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

    def get_clipped_zin_points(self) -> List[Tuple[float, float]]:
        """Возвращает точки обрезанного ZIN полигона"""
        if not self.settings.load_enabled:
            return self.get_zin_polygon_points()

        polygon_points = self.get_zin_polygon_points()
        if not polygon_points:
            return []

        load_polygon = self._get_merged_load_polygon(
            self.get_load_polygons_zin()
        )
        if load_polygon is None or load_polygon.is_empty:
            return polygon_points

        return self._clip_polygon(polygon_points, load_polygon)

    def get_clipped_zout_points(self) -> List[Tuple[float, float]]:
        """Возвращает точки обрезанного ZOUT полигона"""
        if not self.settings.load_enabled:
            return self.get_zout_polygon_points()

        polygon_points = self.get_zout_polygon_points()
        if not polygon_points:
            return []

        load_polygon = self._get_merged_load_polygon(
            self.get_load_polygons_zout()
        )
        if load_polygon is None or load_polygon.is_empty:
            return polygon_points

        return self._clip_polygon(polygon_points, load_polygon)

    def _get_merged_load_polygon(self, load_polygons: List) -> Optional[Polygon]:
        """Объединяет все полигоны нагрузки в один"""
        if not load_polygons:
            return None

        polygons = [self._to_polygon(poly) for poly in load_polygons]
        merged = unary_union(polygons)
        return merged if not merged.is_empty else None

    def _clip_polygon(
            self,
            polygon_points: List[Tuple[float, float]],
            load_polygon: Polygon
    ) -> List[Tuple[float, float]]:
        """Обрезает полигон по полигону нагрузки"""
        selector_polygon = self._to_polygon(polygon_points)
        if selector_polygon.is_empty:
            return []

        result = selector_polygon.difference(load_polygon)
        return self._to_points(result)

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

    def get_all_clipped_data(self) -> dict:
        """Возвращает все данные для визуализации"""
        return {
            'zin_clipped': self.get_clipped_zin_points(),
            'zout_clipped': self.get_clipped_zout_points(),
            'zin_full': self.get_zin_polygon_points(),
            'zout_full': self.get_zout_polygon_points(),
            'load_zin': self.get_load_polygons_zin(),
            'load_zout': self.get_load_polygons_zout(),
            'is_clipped': self.settings.load_enabled
        }
