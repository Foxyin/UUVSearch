"""测试连续环境"""
import yaml
from envs.maps import create_map
from envs.continuous_env import ContinuousSearchEnv

with open("config/env/continuous_square.yaml", 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

map_obj = create_map(config["map"]["type"], config["map"])
env = ContinuousSearchEnv(map_obj, config)

obs, info = env.reset()
print("初始观测形状:", obs.shape)

for i in range(10):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"Step {i+1}: reward={reward:.1f}, done={terminated or truncated}")
    if terminated or truncated:
        break
print("连续环境测试通过")