"""
UUVSearch - 消融实验批量运行脚本（支持多次重复 + 标准差）
用法:
  # 单次运行
  python scripts/run_ablation.py --algo sac --total-steps 100000 --episodes 50

  # 多次运行（5 次不同 seed，输出 mean ± std）
  python scripts/run_ablation.py --algo sac --total-steps 100000 --episodes 50 --repeat 5
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


ABLATION_GROUPS = {
    "full": {
        "coverage_gain": 1.0,
        "revisit_gain": 0.1,
        "find_target": 100.0,
        "collision_penalty": -2.0,
        "step_penalty": -0.05
    },
    "no_exploration_reward": {
        "coverage_gain": 0.0,
        "revisit_gain": 0.0,
        "find_target": 100.0,
        "collision_penalty": -2.0,
        "step_penalty": -0.05
    },
    "no_target_reward": {
        "coverage_gain": 1.0,
        "revisit_gain": 0.1,
        "find_target": 0.0,
        "collision_penalty": -2.0,
        "step_penalty": -0.05
    },
    "target_reward_only": {
        "coverage_gain": 0.0,
        "revisit_gain": 0.0,
        "find_target": 100.0,
        "collision_penalty": -1.0,    # 保留基本负反馈，否则无法避开障碍物
        "step_penalty": -0.01         # 保留微小步数惩罚，鼓励效率
    }
}


def run_experiment(name, rewards, algo_name, total_steps, eval_episodes, seed):
    env_config = load_config("config/env/continuous_square.yaml")
    algo_config = load_config(f"config/algo/{algo_name}.yaml")

    env_config["rewards"] = rewards
    # max_steps 沿用 YAML 配置值（当前为 300），不再硬编码覆盖

    full_config = {**env_config, "algo": algo_config, "simulation": env_config["simulation"]}
    full_config["total_steps"] = total_steps
    full_config["save_freq"] = total_steps

    # 固定全局 + 环境随机种子，确保消融完全可复现
    np.random.seed(seed)
    rng_state = np.random.RandomState(seed)

    exp_name = f"ablation_{algo_name}_{name}_seed{seed}"
    print(f"\n{'='*50}")
    print(f"实验: {exp_name}  (算法: {algo_name}, 奖励组: {name}, seed: {seed})")
    print(f"奖励配置: {rewards}")
    print(f"{'='*50}")

    map_obj = create_map(env_config["map"]["type"], env_config["map"])
    env = ContinuousSearchEnv(map_obj, env_config)
    env.np_random = rng_state  # 同步环境 RNG，确保 reset 可复现

    if algo_name == "sac":
        trainer = SACTrainer(env, full_config, exp_name=exp_name)
    elif algo_name == "dqn":
        trainer = DQNTrainer(env, full_config, exp_name=exp_name)
    else:
        raise ValueError(f"不支持的算法: {algo_name}")

    trainer.train()

    checkpoint_dir = f"experiments/checkpoints/{exp_name}"
    final_ckpt = os.path.join(checkpoint_dir, f"step_{total_steps}.pt")
    if not os.path.exists(final_ckpt):
        raise RuntimeError(f"checkpoint 未生成: {final_ckpt}")

    eval_env = ContinuousSearchEnv(map_obj, env_config)
    eval_env.np_random = rng_state  # 评估环境也用相同种子
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
        "seed": seed,
        "success_rate": stats["success_rate"],
        "avg_steps": stats["avg_steps"],
        "avg_coverage": stats["avg_coverage"]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", type=str, default="sac", choices=["sac", "dqn"],
                        help="选择算法 (sac 或 dqn)")
    parser.add_argument("--total-steps", type=int, default=100000,
                        help="每次训练的总步数（应与主实验一致）")
    parser.add_argument("--episodes", type=int, default=50,
                        help="评估回合数")
    parser.add_argument("--repeat", type=int, default=1,
                        help="每组实验重复次数（用于计算 mean ± std）")
    parser.add_argument("--base-seed", type=int, default=42,
                        help="基准随机种子（第 i 次重复使用 base_seed + i）")
    args = parser.parse_args()

    all_runs = []
    for name, rewards in ABLATION_GROUPS.items():
        group_runs = []
        for r in range(args.repeat):
            seed = args.base_seed + r
            try:
                res = run_experiment(name, rewards, args.algo, args.total_steps, args.episodes, seed)
                group_runs.append(res)
            except Exception as e:
                print(f"实验 {args.algo}_{name} (seed={seed}) 失败: {e}")

        if not group_runs:
            continue

        if args.repeat == 1:
            all_runs.append(group_runs[0])
        else:
            # 汇总多次运行的 mean ± std
            sr = [r["success_rate"] for r in group_runs]
            st = [r["avg_steps"] for r in group_runs]
            cv = [r["avg_coverage"] for r in group_runs]
            aggregated = {
                "experiment": f"{args.algo}_{name}",
                "algo": args.algo,
                "reward_group": name,
                "repeats": args.repeat,
                "success_rate_mean": np.mean(sr),
                "success_rate_std": np.std(sr),
                "avg_steps_mean": np.mean(st),
                "avg_steps_std": np.std(st),
                "avg_coverage_mean": np.mean(cv),
                "avg_coverage_std": np.std(cv),
            }
            all_runs.append(aggregated)
            print(f"  {name}: sr={np.mean(sr):.3f}±{np.std(sr):.3f}, "
                  f"steps={np.mean(st):.0f}±{np.std(st):.0f}, "
                  f"cov={np.mean(cv):.3f}±{np.std(cv):.3f}")

    df = pd.DataFrame(all_runs)
    output_dir = "experiments/ablation"
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"results_{args.algo}.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n所有实验结果已保存至 {csv_path}")
    print(df)


if __name__ == "__main__":
    main()
