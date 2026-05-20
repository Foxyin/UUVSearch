"""
UUVSearch - 消融实验批量运行脚本（支持多算法）
用法:
  python scripts/run_ablation.py --algo sac --total-steps 15000 --episodes 50
  python scripts/run_ablation.py --algo dqn --total-steps 10000 --episodes 50
"""
import sys
import os
import argparse
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config_loader import load_config
from envs.maps import create_map
from envs.continuous_env import ContinuousSearchEnv
from algorithms.sac.agent import SACAgent
from algorithms.dqn.agent import DQNAgent
from trainers.sac_trainer import SACTrainer
from trainers.dqn_trainer import DQNTrainer
from trainers.evaluator import Evaluator


# 奖励消融分组（通用）
ABLATION_GROUPS = {
    "full": {
        "coverage_gain": 1.0,
        "revisit_gain": 0.1,
        "find_target": 100.0,
        "collision_penalty": -2.0,
        "step_penalty": -0.05
    },
    "no_coverage": {
        "coverage_gain": 0.0,
        "revisit_gain": 0.0,
        "find_target": 100.0,
        "collision_penalty": -2.0,
        "step_penalty": -0.05
    },
    "no_target": {
        "coverage_gain": 1.0,
        "revisit_gain": 0.1,
        "find_target": 0.0,
        "collision_penalty": -2.0,
        "step_penalty": -0.05
    },
    "target_only": {
        "coverage_gain": 0.0,
        "revisit_gain": 0.0,
        "find_target": 100.0,
        "collision_penalty": 0.0,
        "step_penalty": 0.0
    }
}


def run_experiment(name, rewards, algo_name, total_steps, eval_episodes):
    # 加载环境配置
    env_config = load_config("config/env/continuous_square.yaml")

    # 加载算法配置
    algo_config = load_config(f"config/algo/{algo_name}.yaml")

    # 覆盖奖励参数
    env_config["rewards"] = rewards
    env_config["simulation"]["max_steps"] = 200  # 训练时每回合最大步数

    # 合并总配置
    full_config = {**env_config, "algo": algo_config, "simulation": env_config["simulation"]}
    full_config["total_steps"] = total_steps
    full_config["save_freq"] = total_steps  # 结束时保存一次

    exp_name = f"ablation_{algo_name}_{name}"
    print(f"\n{'='*50}")
    print(f"开始实验: {exp_name}  (算法: {algo_name}, 奖励组: {name})")
    print(f"奖励配置: {rewards}")
    print(f"{'='*50}")

    # 创建地图和环境
    map_obj = create_map(env_config["map"]["type"], env_config["map"])
    env = ContinuousSearchEnv(map_obj, env_config)

    # 根据算法名选择训练器
    if algo_name == "sac":
        trainer = SACTrainer(env, full_config, exp_name=exp_name)
    elif algo_name == "dqn":
        trainer = DQNTrainer(env, full_config, exp_name=exp_name)
    else:
        raise ValueError(f"不支持的算法: {algo_name}")

    trainer.train()

    # 加载最终 checkpoint
    checkpoint_dir = f"experiments/checkpoints/{exp_name}"
    final_ckpt = os.path.join(checkpoint_dir, f"step_{total_steps}.pt")
    if not os.path.exists(final_ckpt):
        raise RuntimeError(f"checkpoint 未生成: {final_ckpt}")

    # 创建评估环境与 Agent
    eval_env = ContinuousSearchEnv(map_obj, env_config)
    obs_dim = eval_env.observation_space.shape[0]
    action_dim = eval_env.action_space.n

    if algo_name == "sac":
        agent = SACAgent(obs_dim, action_dim, algo_config)
    elif algo_name == "dqn":
        agent = DQNAgent(obs_dim, action_dim, algo_config)
    else:
        raise ValueError(f"不支持的算法: {algo_name}")

    agent.load(final_ckpt)

    evaluator = Evaluator(eval_env, agent, env_config, exp_name=f"eval_{exp_name}")
    stats = evaluator.evaluate(num_episodes=eval_episodes, save_fig_every=20)

    return {
        "experiment": f"{algo_name}_{name}",
        "algo": algo_name,
        "reward_group": name,
        "success_rate": stats["success_rate"],
        "avg_steps": stats["avg_steps"],
        "avg_coverage": stats["avg_coverage"]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", type=str, default="sac", choices=["sac", "dqn"],
                        help="选择算法 (sac 或 dqn)")
    parser.add_argument("--total-steps", type=int, default=15000)
    parser.add_argument("--episodes", type=int, default=50)
    args = parser.parse_args()

    results = []
    for name, rewards in ABLATION_GROUPS.items():
        try:
            res = run_experiment(name, rewards, args.algo, args.total_steps, args.episodes)
            results.append(res)
        except Exception as e:
            print(f"实验 {args.algo}_{name} 失败: {e}")

    df = pd.DataFrame(results)
    output_dir = "experiments/ablation"
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"results_{args.algo}.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n所有实验结果已保存至 {csv_path}")
    print(df)


if __name__ == "__main__":
    main()