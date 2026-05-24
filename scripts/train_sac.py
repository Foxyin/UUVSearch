"""
UUVSearch - SAC 训练入口
用法:
  python scripts/train_sac.py --exp-name sac_test --total-steps 50000
"""
import sys
import os
import argparse
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config_loader import load_config
from envs.maps import create_map
from envs.continuous_env import ContinuousSearchEnv
from trainers.sac_trainer import SACTrainer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp-name", type=str, default="sac_square")
    parser.add_argument("--total-steps", type=int, default=400000,
                        help="总训练步数")
    parser.add_argument("--seed", type=int, default=None,
                        help="随机种子（固定后训练可复现）")
    args = parser.parse_args()

    env_config = load_config("config/env/continuous_square.yaml")
    algo_config = load_config("config/algo/sac.yaml")
    full_config = {**env_config, "algo": algo_config, "simulation": env_config["simulation"]}
    full_config["total_steps"] = args.total_steps

    map_obj = create_map(env_config["map"]["type"], env_config["map"])
    env = ContinuousSearchEnv(map_obj, env_config)

    # 固定种子（numpy + torch + env + buffer，确保完全可复现）
    if args.seed is not None:
        import torch
        np.random.seed(args.seed)
        torch.manual_seed(args.seed)
        env.reset(seed=args.seed)

    trainer = SACTrainer(env, full_config, exp_name=args.exp_name)
    if args.seed is not None:
        trainer.agent.buffer.seed(args.seed)
    trainer.train()

if __name__ == "__main__":
    main()