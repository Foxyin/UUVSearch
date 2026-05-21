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

    # 检测是否有 _mean/_std 列（多次运行模式）
    has_std = "success_rate_std" in df.columns

    if has_std:
        metric_pairs = [
            ("success_rate_mean", "success_rate_std"),
            ("avg_steps_mean", "avg_steps_std"),
            ("avg_coverage_mean", "avg_coverage_std"),
        ]
    else:
        metric_pairs = [
            ("success_rate", None),
            ("avg_steps", None),
            ("avg_coverage", None),
        ]
    titles = ["Success Rate", "Average Steps", "Average Coverage"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for i, (mean_col, std_col) in enumerate(metric_pairs):
        ax = axes[i]
        values = df[mean_col].values
        errors = df[std_col].values if std_col else None
        labels = df["experiment"].values
        colors = plt.cm.Set2(np.linspace(0, 1, len(labels)))
        bars = ax.bar(labels, values, yerr=errors, capsize=5, color=colors)
        ax.set_title(titles[i])
        ax.set_ylabel(titles[i])
        for bar, v in zip(bars, values):
            offset = (errors[list(bars).index(bar)] if errors is not None else 0) + 0.02
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + offset, f"{v:.2f}",
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    save_path = os.path.join(os.path.dirname(args.csv), "ablation_comparison.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"对比图已保存至 {save_path}")


if __name__ == "__main__":
    main()