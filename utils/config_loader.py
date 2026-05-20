"""
UUVSearch - 配置加载与合并工具
支持从多个YAML文件加载并深度合并，后续可扩展命令行覆盖。
"""
import yaml
import copy


def load_config(*paths: str) -> dict:
    """按顺序加载多个YAML配置并深度合并，后面的覆盖前面的"""
    merged = {}
    for path in paths:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if data:
            merged = deep_merge(merged, data)
    return merged


def deep_merge(base: dict, override: dict) -> dict:
    """递归合并两个字典，override覆盖base中的值"""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result