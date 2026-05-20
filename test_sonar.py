"""测试声纳FOV"""
import numpy as np
from envs.sonar_model import SonarModel

# 构造一个简单网格 (10x10)，中间有一条障碍物墙
grid = np.zeros((10, 10), dtype=np.int8)
grid[5, 3:7] = 1  # 一堵墙

sonar = SonarModel({"type": "circle", "max_range": 5, "sector_angle": 120})

# 测试圆形声纳（从(2,5)探测）
fov = sonar.get_fov_cells((2, 5), 0, grid)
print("圆形FOV (共{} 格)".format(len(fov)))
# 手动验证 (2,5) 到墙后的格子 (8,5) 是否在FOV内
print("(8,5) 在FOV中:", (8,5) in fov)  # 预期 False (被墙阻挡)

# 测试扇形声纳（朝向右侧0°）
sonar2 = SonarModel({"type": "sector", "max_range": 5, "sector_angle": 90})
fov2 = sonar2.get_fov_cells((2, 5), 0, grid)
print("扇形FOV (共{} 格)".format(len(fov2)))