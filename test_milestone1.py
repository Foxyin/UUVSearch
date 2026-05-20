"""
UUVSearch - 里程碑1 测试脚本
"""
import sys
import yaml
import numpy as np
from envs.maps import create_map
from envs.grid_env import GridEnv

# 加载配置
with open("config/env/grid_square.yaml", 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 创建地图
map_obj = create_map(config["map"]["type"], config["map"])

# 创建环境
env = GridEnv(map_obj, config)

# 运行随机策略
obs = env.reset()
print("初始信息:", obs)

for i in range(200):
    action = np.random.randint(0, 8)
    obs, reward, done, info = env.step(action)
    print(f"Step {obs['step']}: pos={obs['auv_pos']}, cov={obs['coverage']:.3f}, max_prob={obs['max_prob']:.4f}, reward={reward:.1f}")
    if done:
        if obs['target_found']:
            print(f"✅ 发现目标！总步数: {obs['step']}")
        else:
            print(f"⏰ 达到最大步数，目标未发现")
        break