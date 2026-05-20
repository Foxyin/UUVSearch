"""
UUVSearch - 消融实验结果可视化
用法:
  python scripts/plot_results.py --csv experiments/ablation/results.csv
"""
import sys
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default="experiments/ablation/results.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    metrics = ["success_rate", "avg_steps", "avg_coverage"]
    titles = ["Success Rate", "Average Steps", "Average Coverage"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for i, metric in enumerate(metrics):
        ax = axes[i]
        values = df[metric].values
        labels = df["experiment"].values
        colors = plt.cm.Set2(np.linspace(0, 1, len(labels)))
        bars = ax.bar(labels, values, color=colors)
        ax.set_title(titles[i])
        ax.set_ylabel(titles[i])
        # 在柱子上方标数值
        for bar, v in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f"{v:.2f}",
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    save_path = os.path.join(os.path.dirname(args.csv), "ablation_comparison.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"对比图已保存至 {save_path}")


if __name__ == "__main__":
    main()