"""
UUVSearch - 单回合可视化演示
用法:
  python scripts/render_episode.py --algo sac --checkpoint <path>
  python scripts/render_episode.py --algo dqn --checkpoint <path> --max-steps 200
"""
import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
matplotlib.use('TkAgg')
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
    parser.add_argument("--max-steps", type=int, default=300,
                        help="最大显示步数（默认匹配环境配置）")
    parser.add_argument("--env-config", type=str, default="config/env/continuous_square.yaml")
    args = parser.parse_args()

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
    x, y, _ = env.auv_state
    xs, ys = [x], [y]
    step = 0

    plt.ion()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_xlim(0, env.map.length)
    ax.set_ylim(0, env.map.length)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("AUV Search Demo (press 'q' to exit)")
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    # 障碍物背景
    grid = env.map.grid
    for r in range(grid.shape[0]):
        for c in range(grid.shape[1]):
            if grid[r, c] == 1:
                rx = c * env.map.resolution
                ry = r * env.map.resolution
                rect = plt.Rectangle((rx, ry), env.map.resolution, env.map.resolution,
                                     facecolor='gray', alpha=0.5, edgecolor='none')
                ax.add_patch(rect)

    # 目标
    target_x = (env.target_pos_grid[1] + 0.5) * env.map.resolution
    target_y = (env.target_pos_grid[0] + 0.5) * env.map.resolution
    ax.plot(target_x, target_y, 'y*', markersize=15, label='Target')
    traj_line, = ax.plot([], [], 'b-', linewidth=1.5, label='Path')
    auv_marker, = ax.plot([], [], 'ro', markersize=8, label='AUV')
    sonar_circle = plt.Circle((0, 0), env.sonar.max_range * env.map.resolution,
                              facecolor='cyan', alpha=0.15, edgecolor='cyan', linewidth=0.5)
    ax.add_patch(sonar_circle)
    ax.legend()

    while not done and step < args.max_steps:
        action = agent.select_action(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        x, y, _ = env.auv_state
        xs.append(x)
        ys.append(y)
        step += 1

        traj_line.set_data(xs, ys)
        auv_marker.set_data([x], [y])
        # 更新声呐范围圈
        sonar_circle.set_center((x, y))
        sonar_r = env.sonar.max_range * env.map.resolution
        ax.set_title(f"Step: {step} | Reward: {reward:.1f}"
                     f"{' | FOUND!' if env.found else ''}")

        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        plt.pause(0.1)

    plt.ioff()
    if env.found:
        ax.set_title(f"Target Found! Total Steps: {step}")
    else:
        ax.set_title(f"Not Found (Max Steps: {step})")
    plt.show(block=True)


if __name__ == "__main__":
    main()
