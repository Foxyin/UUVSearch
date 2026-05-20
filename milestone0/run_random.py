"""
UUVSearch - 里程碑0：随机游走仿真
===================================
让AUV在网格世界中随机移动，用matplotlib实时绘制地图和AUV位置。
探测到目标后停止并打印成功信息。
"""
import numpy as np
import matplotlib
matplotlib.use('TkAgg')   # 强制使用Tkinter后端，避免无显示问题
import matplotlib.pyplot as plt
from world_simple import World
from auv_simple import AUV

# 初始化世界
world = World(size=20)

# 放置AUV在某个自由格子上（尽量远离障碍物）
start_x, start_y = 1, 1
while not world.is_free(start_x, start_y) or world.grid[start_x, start_y] == 2:
    start_x, start_y = np.random.randint(0, world.size, 2)
auv = AUV((start_x, start_y))

# 探测函数：扫描3x3区域
def detect_around(auv, world):
    """探测以AUV为中心的3x3区域，返回是否发现目标"""
    x, y = auv.get_pos()
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < world.size and 0 <= ny < world.size:
                if world.grid[nx, ny] == 2:   # 发现目标
                    return True
                elif world.grid[nx, ny] == 0: # 自由格子，标记已访问
                    world.grid[nx, ny] = 3
    return False

# 设置绘图
plt.ion()  # 开启交互模式
fig, ax = plt.subplots(figsize=(7, 7))

# 自定义颜色映射：0白 1黑 2金 3淡蓝
cmap = plt.cm.colors.ListedColormap(['white', 'black', 'gold', 'lightblue'])
bounds = [0, 1, 2, 3, 4]
norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)

found = False
step_count = 0
max_steps = 500  # 防止无限循环

while not found and step_count < max_steps:
    # 随机选择动作
    action = np.random.randint(0, 4)
    auv.step(action, world)

    # 探测
    found = detect_around(auv, world)
    step_count += 1

    # 绘制地图
    ax.clear()
    display_grid = world.grid.copy()
    ax.imshow(display_grid.T, origin='lower', cmap=cmap, norm=norm,
              extent=[0, world.size, 0, world.size])
    # 绘制AUV位置（红点）
    ax.plot(auv.x, auv.y, 'ro', markersize=12, markeredgecolor='darkred',
            markeredgewidth=1.5)
    ax.set_xlim(0, world.size)
    ax.set_ylim(0, world.size)
    ax.set_xticks(range(world.size))
    ax.set_yticks(range(world.size))
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_title(f"UUV Search - Step: {step_count}")
    plt.pause(0.3)  # 每步暂停0.3秒

if found:
    ax.set_title(f"✅ Target Found! Total Steps: {step_count}")
    print(f"成功！目标在 {step_count} 步后被发现。")
else:
    ax.set_title(f"❌ Target Not Found in {max_steps} Steps")
    print(f"失败：在 {max_steps} 步内未找到目标。")

plt.ioff()       # 关闭交互模式
plt.show()       # 保持图像显示