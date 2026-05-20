"""
UUVSearch - 统一实验入口脚本（修复版）
用法:
  python scripts/run_experiment.py --env grid --algo lawnmower --episodes 5 --render
  python scripts/run_experiment.py --env continuous --algo random --episodes 3 --render
"""
import sys
import os
import argparse
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config_loader import load_config
from envs.maps import create_map
from envs import create_environment
from algorithms import create_algorithm


def run_episode(env, algo, max_steps=500, render=False, env_type='grid'):
    """运行一个回合，返回 (final_obs_or_dict, total_reward, found)"""
    reset_output = env.reset()
    if env_type == 'continuous':
        obs, info = reset_output
        if hasattr(algo, 'reset'):
            algo.reset()
    else:
        obs = reset_output
        if hasattr(algo, 'reset'):
            algo.reset()

    total_reward = 0.0
    found = False
    for step in range(max_steps):
        action = algo.select_action(obs)

        if env_type == 'continuous':
            next_obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            if terminated and "detected" in info and info["detected"]:
                found = True
        else:
            next_obs, reward, done, info = env.step(action)

        total_reward += reward
        if render:
            if env_type == 'continuous':
                print(f"Step {step+1}: reward={reward:.1f}, done={done}")
            else:
                print(f"Step {obs['step']}: pos={obs['auv_pos']}, cov={obs['coverage']:.3f}, "
                      f"prob={obs['max_prob']:.4f}, reward={reward:.1f}")

        obs = next_obs
        if done:
            # 如果是因为发现目标而终止
            if env_type == 'continuous' and env.found:
                found = True
            elif env_type == 'grid' and obs.get('target_found', False):
                found = True
            break
    return obs, total_reward, found


def main():
    parser = argparse.ArgumentParser(description="UUVSearch 统一实验运行器")
    parser.add_argument("--env", type=str, required=True, choices=["grid", "continuous"],
                        help="环境类型")
    parser.add_argument("--algo", type=str, required=True, choices=["random", "lawnmower"],
                        help="算法名称 (目前连续环境仅支持 random)")
    parser.add_argument("--episodes", type=int, default=5, help="运行回合数")
    parser.add_argument("--render", action="store_true", help="打印每步信息")
    parser.add_argument("--config", type=str, default=None, help="额外配置文件（可选）")
    args = parser.parse_args()

    # 兼容性检查
    if args.env == "continuous" and args.algo != "random":
        print("错误：连续环境目前仅支持 random 算法（传统算法依赖网格观测）。")
        sys.exit(1)

    # 加载配置
    base_config_path = os.path.join(os.path.dirname(__file__), "..", "config", "env", f"{args.env}_square.yaml")
    config_paths = [base_config_path]
    if args.config:
        config_paths.append(args.config)
    config = load_config(*config_paths)

    # 创建地图
    map_obj = create_map(config["map"]["type"], config["map"])

    # 创建环境
    env = create_environment(args.env, map_obj, config)

    # 创建算法（传入动作数量）
    algo_config = {}
    if args.algo == "random":
        if args.env == "continuous":
            algo_config["num_actions"] = 5
        else:
            algo_config["num_actions"] = 8
    elif args.algo == "lawnmower":
        algo_config["map_obj"] = map_obj
    algo = create_algorithm(args.algo, algo_config)

    # 运行回合
    success_count = 0
    total_steps = 0
    for ep in range(args.episodes):
        final_obs, total_reward, found = run_episode(env, algo,
                                                     max_steps=config["simulation"]["max_steps"],
                                                     render=args.render,
                                                     env_type=args.env)
        if found:
            success_count += 1

        if args.env == "continuous":
            total_steps += env.step_count
            print(f"Episode {ep+1}: {'成功' if found else '未发现'}, "
                  f"步数={env.step_count}, 累计奖励={total_reward:.1f}")
        else:
            total_steps += final_obs["step"]
            print(f"Episode {ep+1}: {'成功' if found else '超时'}, "
                  f"步数={final_obs['step']}, 累计奖励={total_reward:.1f}")

    print(f"\n=== 统计 (环境: {args.env}, 算法: {args.algo}) ===")
    print(f"成功率: {success_count}/{args.episodes}")
    print(f"平均步数: {total_steps/args.episodes:.1f}")


if __name__ == "__main__":
    main()