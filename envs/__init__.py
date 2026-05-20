"""
UUVSearch - 环境模块
"""
from .grid_env import GridEnv
from .continuous_env import ContinuousSearchEnv


_ENV_REGISTRY = {
    "grid": GridEnv,
    "continuous": ContinuousSearchEnv,
}


def create_environment(env_type: str, map_obj, config: dict):
    """工厂方法：根据类型创建环境实例"""
    if env_type not in _ENV_REGISTRY:
        raise ValueError(f"未知环境类型: {env_type}. 可选: {list(_ENV_REGISTRY.keys())}")
    env_class = _ENV_REGISTRY[env_type]
    return env_class(map_obj, config)