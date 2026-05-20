"""
UUVSearch - 地图模块工厂
"""
from .base_map import BaseMap
from .square_map import SquareMap
from .irregular_map import IrregularMap

_MAP_REGISTRY = {
    "square": SquareMap,
    "irregular": IrregularMap,   # 新增
}

def create_map(map_type: str, config: dict) -> BaseMap:
    """根据配置创建地图实例"""
    if map_type not in _MAP_REGISTRY:
        raise ValueError(f"未知地图类型: {map_type}。可用类型: {list(_MAP_REGISTRY.keys())}")
    return _MAP_REGISTRY[map_type](config)