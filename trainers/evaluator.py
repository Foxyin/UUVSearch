"""
UUVSearch - 评估器
运行多回合确定性策略，统计成功率、平均步数，并保存轨迹数据。
"""
import numpy as np
import os
from utils.visualizer import plot_trajectory, plot_uncertainty_heatmap, plot_probability_heatmap


class Evaluator:
    def __init__(self, env, agent, config, exp_name="eval"):
        self.env = env
        self.agent = agent
        self.max_steps = config["simulation"]["max_steps"]
        self.fig_dir = os.path.join("experiments", "figures", exp_name)
        os.makedirs(self.fig_dir, exist_ok=True)

    def evaluate(self, num_episodes=100, save_fig_every=20):
        """运行多回合评估，返回统计结果"""
        results = {
            "success": [],
            "steps": [],
            "coverage": [],
            "trajectories": []
        }

        for ep in range(num_episodes):
            obs, info = self.env.reset(seed=ep)  # 固定种子可复现
            trajectory = []       # 记录 (x, y) 位置
            done = False
            step_count = 0

            while not done and step_count < self.max_steps:
                action = self.agent.select_action(obs, deterministic=True)
                trajectory.append(self.env.auv_state.copy())  # [x, y, psi]
                obs, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                step_count += 1

            success = self.env.found
            coverage = self.env.info_map.coverage.mean()

            results["success"].append(success)
            results["steps"].append(step_count)
            results["coverage"].append(coverage)
            results["trajectories"].append(np.array(trajectory))

            # 定期保存图片
            if (ep + 1) % save_fig_every == 0 or ep == 0:
                self._save_plots(ep, trajectory, success, step_count)

        # 统计
        success_array = np.array(results["success"])
        success_rate = success_array.mean()
        avg_steps = np.mean(results["steps"])
        std_steps = np.std(results["steps"])
        avg_coverage = np.mean(results["coverage"])

        print(f"=== 评估结果 ({num_episodes} 回合) ===")
        print(f"成功率: {success_rate:.2%}")
        print(f"平均步数: {avg_steps:.1f} ± {std_steps:.1f}")
        print(f"平均覆盖率: {avg_coverage:.3f}")

        return {
            "success_rate": success_rate,
            "avg_steps": avg_steps,
            "std_steps": std_steps,
            "avg_coverage": avg_coverage
        }

    def _save_plots(self, episode, trajectory, success, step_count):
        """保存三张关键图"""
        x, y = zip(*[(p[0], p[1]) for p in trajectory])

        # 轨迹图
        target_x = (self.env.target_pos_grid[1] + 0.5) * self.env.map.resolution
        target_y = (self.env.target_pos_grid[0] + 0.5) * self.env.map.resolution
        plot_trajectory(x, y, target_x, target_y,
                        title=f"Trajectory Episode {episode+1} ({'Found' if success else 'Not Found'}, Steps={step_count})",
                        save_path=os.path.join(self.fig_dir, f"trajectory_ep{episode+1}.png"))

        # 不确定热力图
        plot_uncertainty_heatmap(self.env.info_map.uncertainty,
                                 title=f"Uncertainty Map Episode {episode+1}",
                                 save_path=os.path.join(self.fig_dir, f"uncertainty_ep{episode+1}.png"))

        # 目标概率热力图
        plot_probability_heatmap(self.env.info_map.probability,
                                 title=f"Probability Map Episode {episode+1}",
                                 save_path=os.path.join(self.fig_dir, f"probability_ep{episode+1}.png"))