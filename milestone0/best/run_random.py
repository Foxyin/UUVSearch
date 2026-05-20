import numpy as np
import matplotlib

matplotlib.use('TkAgg')  # ← 关键修复：强制使用交互式后端，必须在 pyplot 之前
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from world_simple import GridWorld
from auv_simple import SimpleAUV


def main():
    np.random.seed(42)

    print("Initializing grid world...")
    world = GridWorld(size=20, obstacle_ratio=0.10)
    auv = SimpleAUV(world, start_pos=(0, 0))

    print(f"Target position: {world.target_pos}")
    print(f"AUV start: (0, 0)")
    print("Starting random search...\n")

    # 颜色映射：白=自由, 黑=障碍物, 红=目标, 浅蓝=已访问, 绿=AUV
    colors = ['white', 'black', 'red', 'lightblue', 'green']
    cmap = ListedColormap(colors)

    # 开启交互模式
    plt.ion()
    fig, ax = plt.subplots(figsize=(7, 7))

    step = 0
    max_steps = 500

    while step < max_steps:
        action = np.random.randint(0, 4)
        obs, reward, done, info = auv.move(action)
        step += 1

        # 获取渲染网格
        render_grid = world.get_render_grid(auv.get_pos())

        # 清除并重绘
        ax.clear()
        im = ax.imshow(render_grid, cmap=cmap, vmin=0, vmax=4)
        ax.set_title(f"Step: {step} | AUV: {auv.get_pos()} | Reward: {reward:.1f}", fontsize=12)
        ax.set_xticks(range(world.size))
        ax.set_yticks(range(world.size))
        ax.grid(True, alpha=0.3, color='gray')

        # 英文图例，避免字体缺失警告
        legend_text = "Black=Obstacle  Red=Target  Green=AUV  Blue=Visited"
        fig.text(0.5, 0.02, legend_text, ha='center', fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # 强制刷新显示
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.15)

        if done:
            if info.get("found"):
                print(f"SUCCESS! Target found at {world.target_pos}")
                print(f"Total steps: {step}")
                plt.pause(2)
            break

    if not done:
        print(f"Max steps reached ({max_steps}), target not found.")
        print(f"Target was at: {world.target_pos}")

    print("\nDone. Close the window to exit.")
    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()