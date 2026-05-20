"""
UUVSearch - 算法模块工厂
"""
from .base_algo import BaseAlgorithm
from .random_search import RandomSearch
from .lawnmower import LawnmowerSearch

_ALGO_REGISTRY = {
    "random": RandomSearch,
    "lawnmower": LawnmowerSearch,
    # 未来添加: "dqn", "sac" 等
}

def create_algorithm(algo_name: str, config: dict = None) -> BaseAlgorithm:
    """根据名称创建算法实例"""
    if algo_name not in _ALGO_REGISTRY:
        raise ValueError(f"未知算法: {algo_name}. 可选: {list(_ALGO_REGISTRY.keys())}")
    return _ALGO_REGISTRY[algo_name](config or {})