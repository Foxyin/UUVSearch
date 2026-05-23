"""
UUVSearch - 可视化工具
轨迹图（含障碍物背景）、不确定热力图、概率热力图。
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot_trajectory(x, y, target_x, target_y, grid=None, resolution=30.0,
                    sonar_range=None, fov_cells_list=None, title="Trajectory", save_path=None):
    """绘制AUV运动轨迹，可选叠加障碍物背景和实际FOV格子（含遮挡）"""
    plt.figure(figsize=(8, 6))

    rows, cols = (0, 0)
    if grid is not None:
        rows, cols = grid.shape
        for r in range(rows):
            for c in range(cols):
                if grid[r, c] == 1:
                    rx = c * resolution
                    ry = r * resolution
                    rect = plt.Rectangle((rx, ry), resolution, resolution,
                                         facecolor='gray', alpha=0.5, edgecolor='none')
                    plt.gca().add_patch(rect)

    plt.plot(x, y, 'b-', linewidth=1.5, label='AUV Path')
    plt.plot(x[0], y[0], 'go', markersize=8, label='Start')
    plt.plot(x[-1], y[-1], 'ro', markersize=8, label='End')
    plt.plot(target_x, target_y, 'y*', markersize=15, label='Target')

    # 终点位置：实际 FOV 格子 + 声呐最大范围虚线
    if fov_cells_list and sonar_range is not None:
        for (fr, fc) in fov_cells_list[-1]:
            rx = fc * resolution
            ry = fr * resolution
            rect = plt.Rectangle((rx, ry), resolution, resolution,
                                 facecolor='lime', alpha=0.15, edgecolor='none')
            plt.gca().add_patch(rect)
        circle = plt.Circle((x[-1], y[-1]), sonar_range * resolution,
                            facecolor='none', edgecolor='cyan', linewidth=1.0, linestyle='--')
        plt.gca().add_patch(circle)
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    if grid is not None:
        plt.xlim(0, cols * resolution)
        plt.ylim(0, rows * resolution)
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_uncertainty_heatmap(matrix, title="Uncertainty Map", save_path=None):
    plt.figure(figsize=(7, 6))
    plt.imshow(matrix, origin='upper', cmap='hot', interpolation='nearest')
    plt.colorbar(label='Uncertainty')
    plt.title(title)
    plt.xlabel('Grid Col')
    plt.ylabel('Grid Row')
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_probability_heatmap(matrix, title="Probability Map", save_path=None):
    plt.figure(figsize=(7, 6))
    plt.imshow(matrix, origin='upper', cmap='viridis', interpolation='nearest')
    plt.colorbar(label='Probability')
    plt.title(title)
    plt.xlabel('Grid Col')
    plt.ylabel('Grid Row')
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
