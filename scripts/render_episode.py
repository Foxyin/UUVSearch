"""
UUVSearch - 单回合可视化演示（支持实时窗口 + MP4 录制）
用法:
  python scripts/render_episode.py --algo sac --checkpoint <path>
  python scripts/render_episode.py --algo dqn --checkpoint <path> --save-video demo.mp4
"""
import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
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
                        help="最大步数")
    parser.add_argument("--env-config", type=str, default="config/env/continuous_square.yaml")
    parser.add_argument("--save-video", type=str, default=None,
                        help="保存动画（.mp4 或 .gif），默认存到 experiments/figures/")
    args = parser.parse_args()

    # 录制模式用非交互后端
    if args.save_video:
        matplotlib.use('Agg')
        plt.ioff()
    else:
        matplotlib.use('TkAgg')
        plt.ion()

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
    frames_data = []  # 录制模式：存储每帧数据

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_xlim(0, env.map.length)
    ax.set_ylim(0, env.map.length)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
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

    target_x = (env.target_pos_grid[1] + 0.5) * env.map.resolution
    target_y = (env.target_pos_grid[0] + 0.5) * env.map.resolution
    ax.plot(target_x, target_y, 'y*', markersize=15, label='Target')
    traj_line, = ax.plot([], [], 'b-', linewidth=1.5, label='Path')
    auv_marker, = ax.plot([], [], 'ro', markersize=8, label='AUV')
    sonar_circle = plt.Circle((0, 0), env.sonar.max_range * env.map.resolution,
                              facecolor='none', edgecolor='cyan', linewidth=0.5, linestyle='--')
    ax.add_patch(sonar_circle)
    fov_patches = []
    ax.legend()

    ax.set_title("AUV Search Demo")

    while not done and step < args.max_steps:
        action = agent.select_action(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        x, y, _ = env.auv_state
        xs.append(x)
        ys.append(y)
        step += 1

        if args.save_video:
            # 录制模式：保存每帧的数据供 animation 使用
            grid_r = int(y / env.map.resolution)
            grid_c = int(x / env.map.resolution)
            heading_deg = np.rad2deg(env.auv_state[2]) % 360
            fov_cells = env.sonar.get_fov_cells((grid_r, grid_c), heading_deg, env.map.grid)
            frames_data.append({
                'xs': list(xs), 'ys': list(ys), 'x': x, 'y': y,
                'fov': fov_cells,
                'title': f"Step: {step} | Reward: {reward:.1f}"
                         f"{' | FOUND!' if env.found else ''}"
            })
        else:
            # 交互模式：实时更新
            traj_line.set_data(xs, ys)
            auv_marker.set_data([x], [y])
            sonar_circle.set_center((x, y))
            for p in fov_patches:
                p.remove()
            fov_patches.clear()
            grid_r = int(y / env.map.resolution)
            grid_c = int(x / env.map.resolution)
            heading_deg = np.rad2deg(env.auv_state[2]) % 360
            fov_cells = env.sonar.get_fov_cells((grid_r, grid_c), heading_deg, env.map.grid)
            for (fr, fc) in fov_cells:
                rx = fc * env.map.resolution
                ry = fr * env.map.resolution
                rect = plt.Rectangle((rx, ry), env.map.resolution, env.map.resolution,
                                     facecolor='lime', alpha=0.15, edgecolor='none')
                ax.add_patch(rect)
                fov_patches.append(rect)
            ax.set_title(f"Step: {step} | Reward: {reward:.1f}"
                         f"{' | FOUND!' if env.found else ''}")
            fig.canvas.draw_idle()
            fig.canvas.flush_events()
            plt.pause(0.1)

    if args.save_video and frames_data:
        # 默认路径
        video_path = args.save_video
        if not os.path.dirname(video_path):
            os.makedirs("experiments/figures", exist_ok=True)
            video_path = os.path.join("experiments", "figures", video_path)

        print(f"录制 {len(frames_data)} 帧 → {video_path}")

        def draw_frame(data):
            traj_line.set_data(data['xs'], data['ys'])
            auv_marker.set_data([data['x']], [data['y']])
            sonar_circle.set_center((data['x'], data['y']))
            # 清除旧 FOV
            for p in fov_patches:
                p.remove()
            fov_patches.clear()
            for (fr, fc) in data['fov']:
                rx = fc * env.map.resolution
                ry = fr * env.map.resolution
                rect = plt.Rectangle((rx, ry), env.map.resolution, env.map.resolution,
                                     facecolor='lime', alpha=0.15, edgecolor='none')
                ax.add_patch(rect)
                fov_patches.append(rect)
            ax.set_title(data['title'])
            return [traj_line, auv_marker, sonar_circle] + fov_patches

        ani = animation.FuncAnimation(fig, draw_frame, frames=frames_data,
                                      interval=200, blit=False, repeat=False)
        if video_path.endswith('.mp4'):
            # 指向 conda 环境中的 ffmpeg
            ffmpeg_path = os.path.join(os.path.dirname(sys.executable), 'Library', 'bin', 'ffmpeg.exe')
            if os.path.exists(ffmpeg_path):
                matplotlib.rcParams['animation.ffmpeg_path'] = ffmpeg_path
            ani.save(video_path, writer='ffmpeg', fps=5, dpi=150)
        else:
            if not video_path.endswith('.gif'):
                video_path = video_path.rsplit('.', 1)[0] + '.gif'
            ani.save(video_path, writer='pillow', fps=4, dpi=150)
        print(f"动画已保存: {video_path}")
    elif not args.save_video:
        plt.ioff()
        if env.found:
            ax.set_title(f"Target Found! Total Steps: {step}")
        else:
            ax.set_title(f"Not Found (Max Steps: {step})")
        plt.show(block=True)


if __name__ == "__main__":
    main()
