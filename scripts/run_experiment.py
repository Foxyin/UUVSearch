"""
UUVSearch - 统一实验入口脚本（全部算法共用 Gymnasium 接口）
用法:
  python scripts/run_experiment.py --env grid --algo lawnmower --episodes 5 --render
  python scripts/run_experiment.py --env continuous --algo lawnmower --episodes 5 --render
  python scripts/run_experiment.py --env continuous --algo random --episodes 10
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


def run_episode(env, algo, max_steps=500, render=False, seed=None):
    if seed is not None:
        obs, info = env.reset(seed=seed)
    else:
        obs, info = env.reset()
    if hasattr(algo, 'reset'):
        algo.reset()

    total_reward = 0.0
    found = False
    for step in range(max_steps):
        action = algo.select_action(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

        if render:
            if isinstance(obs, dict):
                print(f"Step {obs['step']}: pos={obs['auv_pos']}, cov={obs['coverage']:.3f}, "
                      f"reward={reward:.1f}")
            else:
                print(f"Step {step+1}: reward={reward:.1f}")

        if terminated or truncated:
            if (terminated and info.get("detected", False)) or (isinstance(obs, dict) and obs.get("target_found", False)):
                found = True
            break
    return total_reward, found


def main():
    parser = argparse.ArgumentParser(description="UUVSearch 统一实验运行器")
    parser.add_argument("--env", type=str, required=True, choices=["grid", "continuous"],
                        help="环境类型")
    parser.add_argument("--algo", type=str, required=True,
                        choices=["random", "lawnmower", "greedy_prob"],
                        help="算法名称")
    parser.add_argument("--episodes", type=int, default=5, help="运行回合数")
    parser.add_argument("--seed", type=int, default=None,
                        help="随机种子（固定后结果可复现，与 evaluate.py 行为一致）")
    parser.add_argument("--render", action="store_true", help="打印每步信息")
    parser.add_argument("--config", type=str, default=None, help="额外配置文件（可选）")
    args = parser.parse_args()

    base_config_path = os.path.join(os.path.dirname(__file__), "..", "config", "env", f"{args.env}_square.yaml")
    config_paths = [base_config_path]
    if args.config:
        config_paths.append(args.config)
    config = load_config(*config_paths)

    map_obj = create_map(config["map"]["type"], config["map"])
    env = create_environment(args.env, map_obj, config)

    algo_config = {}
    if args.algo in ("random", "greedy_prob"):
        algo_config["num_actions"] = 5 if args.env == "continuous" else 8
    if args.algo in ("lawnmower", "greedy_prob"):
        algo_config["map_obj"] = map_obj
        if args.env == "continuous":
            algo_config["resolution"] = config["map"]["resolution"]
            algo_config["map_length"] = config["map"]["length"]
            algo_config["action_angles"] = [-90, -45, 0, 45, 90]

    algo = create_algorithm(args.algo, algo_config)

    if args.seed is not None:
        np.random.seed(args.seed)

    success_count = 0
    total_steps = 0
    for ep in range(args.episodes):
        ep_seed = (args.seed + ep) if args.seed is not None else None
        total_reward, found = run_episode(env, algo,
                                          max_steps=config["simulation"]["max_steps"],
                                          render=args.render,
                                          seed=ep_seed)
        if found:
            success_count += 1

        total_steps += env.step_count if hasattr(env, 'step_count') else 0
        if hasattr(env, 'step_count'):
            print(f"Episode {ep+1}: {'成功' if found else '未发现'}, "
                  f"步数={env.step_count}, 累计奖励={total_reward:.1f}")
        else:
            print(f"Episode {ep+1}: {'成功' if found else '未发现'}, "
                  f"累计奖励={total_reward:.1f}")

    print(f"\n=== 统计 (环境: {args.env}, 算法: {args.algo}) ===")
    print(f"成功率: {success_count}/{args.episodes}")
    print(f"平均步数: {total_steps/args.episodes:.1f}")


if __name__ == "__main__":
    main()
