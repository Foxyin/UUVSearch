"""
UUVSearch - 模型评估脚本（支持自定义实验名称）
用法:
  # 使用默认名称（从checkpoint目录自动提取）
  python scripts/evaluate.py --algo sac --checkpoint experiments/checkpoints/sac_test/step_50000.pt --episodes 100

  # 指定自定义实验名称
  python scripts/evaluate.py --algo dqn --checkpoint experiments/checkpoints/dqn_test/step_50000.pt --exp-name dqn_on_square --episodes 50

  # 可切换地图：通过 --env-config 指定环境配置文件
  python scripts/evaluate.py --algo sac --checkpoint ... --env-config config/env/continuous_irregular.yaml
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config_loader import load_config
from envs.maps import create_map
from envs.continuous_env import ContinuousSearchEnv
from algorithms.sac.agent import SACAgent
from algorithms.dqn.agent import DQNAgent
from trainers.evaluator import Evaluator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", type=str, required=True, choices=["dqn", "sac"],
                        help="算法名称")
    parser.add_argument("--checkpoint", type=str, required=True,
                        help="模型权重路径")
    parser.add_argument("--env-config", type=str, default="config/env/continuous_square.yaml",
                        help="环境配置文件路径（默认：正方形连续环境）")
    parser.add_argument("--episodes", type=int, default=100,
                        help="评估回合数")
    parser.add_argument("--save-fig-every", type=int, default=20,
                        help="每隔多少回合保存图片")
    parser.add_argument("--exp-name", type=str, default=None,
                        help="实验名称，用于保存图片的文件夹；不指定则从checkpoint路径自动生成")
    args = parser.parse_args()

    # 确定实验名称
    if args.exp_name is None:
        # 从 checkpoint 路径中提取父目录名，例如：experiments/checkpoints/sac_test/step_50000.pt -> sac_test
        exp_name = os.path.basename(os.path.dirname(args.checkpoint))
    else:
        exp_name = args.exp_name

    # 加载环境配置
    env_config = load_config(args.env_config)
    map_obj = create_map(env_config["map"]["type"], env_config["map"])
    env = ContinuousSearchEnv(map_obj, env_config)

    obs_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n

    # 加载算法配置（直接是参数字典，无嵌套）
    if args.algo == "sac":
        algo_config = load_config("config/algo/sac.yaml")
        agent = SACAgent(obs_dim, action_dim, algo_config)
    else:  # dqn
        algo_config = load_config("config/algo/dqn.yaml")
        agent = DQNAgent(obs_dim, action_dim, algo_config)

    agent.load(args.checkpoint)
    print(f"加载模型: {args.checkpoint}")

    evaluator = Evaluator(env, agent, env_config, exp_name=f"eval_{exp_name}")
    stats = evaluator.evaluate(num_episodes=args.episodes, save_fig_every=args.save_fig_every)
    print("评估完成，图片保存在 experiments/figures/ 下。")


if __name__ == "__main__":
    main()