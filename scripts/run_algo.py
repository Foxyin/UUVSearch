"""
UUVSearch - 里程碑2：算法测试脚本（修复版）
用法: python scripts/run_algo.py --algo random|lawnmower [--episodes N]
"""
import sys
import os
import argparse
import yaml
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from envs.maps import create_map
from envs.grid_env import GridEnv
from algorithms import create_algorithm


def run_episode(env, algo, max_steps=500, render=False):
    obs = env.reset()
    algo.reset()
    total_reward = 0.0
    for step in range(max_steps):
        action = algo.select_action(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        if render:
            print(f"Step {obs['step']}: pos={obs['auv_pos']}, cov={obs['coverage']:.3f}, "
                  f"prob={obs['max_prob']:.4f}, reward={reward:.1f}")
        if done:
            break
    return obs, total_reward


def main():
    parser = argparse.ArgumentParser(description="UUVSearch 算法测试")
    parser.add_argument("--algo", type=str, required=True, choices=["random", "lawnmower"],
                        help="选择算法")
    parser.add_argument("--episodes", type=int, default=5, help="运行回合数")
    parser.add_argument("--render", action="store_true", help="打印每步信息")
    args = parser.parse_args()

    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "env", "grid_square.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 创建地图
    map_obj = create_map(config["map"]["type"], config["map"])

    # 创建环境
    env = GridEnv(map_obj, config)

    # 创建算法
    algo_config = {}
    if args.algo == "lawnmower":
        algo_config["map_obj"] = map_obj   # 直接传入地图对象
    algo = create_algorithm(args.algo, algo_config)

    # 运行多个回合
    success_count = 0
    total_steps = 0
    for ep in range(args.episodes):
        obs, reward = run_episode(env, algo, render=args.render)
        if obs['target_found']:
            success_count += 1
        total_steps += obs['step']
        print(f"Episode {ep+1}: {'成功' if obs['target_found'] else '超时'}, "
              f"步数={obs['step']}, 覆盖率={obs['coverage']:.3f}, 累计奖励={reward:.1f}")

    print(f"\n=== 统计 (算法: {args.algo}) ===")
    print(f"成功率: {success_count}/{args.episodes}")
    print(f"平均步数: {total_steps/args.episodes:.1f}")


if __name__ == "__main__":
    main()