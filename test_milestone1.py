"""网格环境随机策略测试"""
import yaml
import numpy as np
from envs.maps import create_map
from envs.grid_env import GridEnv

with open("config/env/grid_square.yaml", 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

map_obj = create_map(config["map"]["type"], config["map"])
env = GridEnv(map_obj, config)

obs, info = env.reset()
print("初始信息:", obs)

for i in range(200):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"Step {obs['step']}: pos={obs['auv_pos']}, cov={obs['coverage']:.3f}, "
          f"max_prob={obs['max_prob']:.4f}, reward={reward:.1f}")
    if terminated or truncated:
        if obs['target_found']:
            print(f"Found target! Steps: {obs['step']}")
        else:
            print(f"Max steps reached, target not found")
        break
