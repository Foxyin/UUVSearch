"""
UUVSearch - 可视化工具
支持轨迹图、不确定热力图、概率热力图。
"""
import matplotlib
matplotlib.use('Agg')  # 非交互后端，适合服务器或批量生成
import matplotlib.pyplot as plt
import numpy as np


def plot_trajectory(x, y, target_x, target_y, title="Trajectory", save_path=None):
    """绘制AUV运动轨迹"""
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, 'b-', linewidth=1.5, label='AUV Path')
    plt.plot(x[0], y[0], 'go', markersize=8, label='Start')
    plt.plot(x[-1], y[-1], 'ro', markersize=8, label='End')
    plt.plot(target_x, target_y, 'y*', markersize=15, label='Target')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_uncertainty_heatmap(matrix, title="Uncertainty Map", save_path=None):
    """绘制不确定度热力图"""
    plt.figure(figsize=(7, 6))
    im = plt.imshow(matrix, origin='upper', cmap='hot', interpolation='nearest')
    plt.colorbar(im, label='Uncertainty')
    plt.title(title)
    plt.xlabel('Grid X')
    plt.ylabel('Grid Y')
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_probability_heatmap(matrix, title="Probability Map", save_path=None):
    """绘制目标存在概率热力图"""
    plt.figure(figsize=(7, 6))
    im = plt.imshow(matrix, origin='upper', cmap='viridis', interpolation='nearest')
    plt.colorbar(im, label='Probability')
    plt.title(title)
    plt.xlabel('Grid X')
    plt.ylabel('Grid Y')
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()