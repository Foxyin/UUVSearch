"""
UUVSearch - 单回合可视化演示（修复版）
用法:
  python scripts/render_episode.py --algo sac --checkpoint experiments/checkpoints/sac_test/step_50000.pt
  python scripts/render_episode.py --algo dqn --checkpoint ... --max-steps 200
"""
import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
matplotlib.use('TkAgg')  # 强制使用 Tkinter 后端，确保窗口正常显示
import matplotlib.pyplot as plt
import numpy as np
from utils.config_loader import load_config
from envs.maps import create_map
from envs.continuous_env import ContinuousSearchEnv
from algorithms.sac.agent import SACAgent
from algorithms.dqn.agent import DQNAgent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", type=str, required=True, choices=["dqn", "sac"])
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--max-steps", type=int, default=500, help="最大显示步数")
    parser.add_argument("--env-config", type=str, default="config/env/continuous_square.yaml")
    args = parser.parse_args()

    # 加载环境和算法
    env_config = load_config(args.env_config)
    map_obj = create_map(env_config["map"]["type"], env_config["map"])
    env = ContinuousSearchEnv(map_obj, env_config)

    obs_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n

    if args.algo == "sac":
        algo_config = load_config("config/algo/sac.yaml")
        agent = SACAgent(obs_dim, action_dim, algo_config)
    else:
        algo_config = load_config("config/algo/dqn.yaml")
        agent = DQNAgent(obs_dim, action_dim, algo_config)

    agent.load(args.checkpoint)
    print(f"模型加载成功: {args.checkpoint}")

    obs, info = env.reset()
    done = False
    xs, ys = [], []
    step = 0

    plt.ion()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_xlim(0, env.map.length)
    ax.set_ylim(0, env.map.length)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("AUV Search Demo (press 'q' to exit)")
    ax.grid(True, alpha=0.3)

    # 绘制目标
    target_x = (env.target_pos_grid[1] + 0.5) * env.map.resolution
    target_y = (env.target_pos_grid[0] + 0.5) * env.map.resolution
    target_marker, = ax.plot(target_x, target_y, 'y*', markersize=15, label='Target')
    # 轨迹线和当前位置
    traj_line, = ax.plot([], [], 'b-', linewidth=1.5, label='Path')
    auv_marker, = ax.plot([], [], 'ro', markersize=8, label='AUV')
    ax.legend()

    while not done and step < args.max_steps:
        action = agent.select_action(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        x, y, _ = env.auv_state
        xs.append(x)
        ys.append(y)
        step += 1

        # 更新绘图数据
        traj_line.set_data(xs, ys)
        auv_marker.set_data([x], [y])
        ax.set_title(f"Step: {step} | Reward: {reward:.1f}")

        fig.canvas.draw_idle()
        plt.pause(0.05)  # 控制播放速度，秒

    plt.ioff()
    if env.found:
        ax.set_title(f"✅ Target Found! Total Steps: {step}")
    else:
        ax.set_title(f"❌ Not Found (Max Steps: {step})")
    plt.show(block=True)


if __name__ == "__main__":
    main()