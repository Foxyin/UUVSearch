"""
UUVSearch - DQN 训练入口
用法:
  python scripts/train_dqn.py --exp-name my_first_run --total-steps 50000
"""
import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config_loader import load_config
from envs.maps import create_map
from envs.continuous_env import ContinuousSearchEnv
from trainers.dqn_trainer import DQNTrainer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp-name", type=str, default="dqn_square")
    parser.add_argument("--total-steps", type=int, default=50000)
    args = parser.parse_args()

    # 加载环境配置 + 算法配置
    env_config = load_config("config/env/continuous_square.yaml")
    algo_config = load_config("config/algo/dqn.yaml")
    full_config = {**env_config, "algo": algo_config, "simulation": env_config["simulation"]}
    full_config["total_steps"] = args.total_steps

    # 创建地图与环境
    map_obj = create_map(env_config["map"]["type"], env_config["map"])
    env = ContinuousSearchEnv(map_obj, env_config)

    # 训练
    trainer = DQNTrainer(env, full_config, exp_name=args.exp_name)
    trainer.train()

if __name__ == "__main__":
    main()