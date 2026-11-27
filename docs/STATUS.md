# 当前状态（STATUS）

> **唯一事实源**，由 `owner` 维护。最后更新：2026-11-28。
> 接任者先读这一页；细节去 `docs/02-plan/`、`docs/03-decisions/`、`docs/01-review/`。

## 一句话

计划 v3.2 已闭环、协作四角色已建立，**Phase 0 未开工、没有任何新实验数据、没有论文**。下一步是从 `main` 开 `feat/gate1-protocol` 做协议实现（先不训练），然后 Gate 1。

## 现在在哪

| 阶段 | 状态 | 产物 |
|---|---|---|
| 侦察与旧结论复核 | ✅ 完成 | `docs/01-review/2026-11-27-audit.md` |
| 问题清单（44 条） | ✅ 完成 | `docs/01-review/2026-11-28-issues-checklist.md` |
| 计划 | ✅ v3.2（草案闭环） | `docs/02-plan/plan-2026-11-28.md` |
| 决策记录 | ✅ 至 §12-5 | `docs/03-decisions/2026-11-28-decisions.md` |
| 文档重组 + 根入口 | ✅ 完成 | `README.md`、`CLAUDE.md`、`docs/README.md` |
| 协作四角色 | ✅ 骨架完成 | `协作/` |
| Phase 0（协议实现） | ⬜ **未开始** | 分支 `feat/gate1-protocol`（未创建） |
| Gate 1 | ⬜ 未跑 | — |
| Gate 2 / 3 | ⬜ 未排期 | — |
| 论文 | ⬜ 未开始（用户要求等实验做完） | — |

## 已拍板（不要重开）

- 定位：**search-only 经验研究**，回答“检测退化（Pd/Pfa）+ 能量约束下，RL 何时优于经典搜索”；独立论文；不是别的课题的 confirm 底座，不是 Li et al. 2024 复现。
- 主指标：**KM 中位 time-to-find + 删失率**；成功率只作次要（已饱和）。
- 检测模型：`mode: deterministic | sampled`；`pd_curve: linear | steep`；**虚警走 A**（观测里自然出现，`odds *= Pd/Pfa`，不进奖励）。
- 观测对照：**加 C0c / C3c**（coverage-only，probability patch 置 0）。
- 训练地图：**先 M1**（后续可 M1–M3 轮换）。
- 结构化图：**先做一种**（管线 + 礁石带）。
- 能量：`E = 直行1.0 + 0.5·|Δψ|/45° + 碰撞1.0`，预算 = **× free_cells**（1.5/2.5/4 倍）。
- 算力：**CPU 多进程**（8–10 进程），不装 CUDA、不新建 conda 环境。
- 分支：`wip/fair-baselines` **只作参考、不整体合并**；主线从 `main` 开 `feat/gate1-protocol`。
- 期刊/署名：候选后定；署名最后定；写作等 Gate 3。
- 旧数字（DQN 95% / SAC 94%）**已撤回**，不得再当证据。

## 下一步（Phase 0，1–1.5 天，不训练）

1. 从 `main` 开 `feat/gate1-protocol`。
2. 地图工厂：M1（随机 10%，14×14，原图形状）、M2（随机 15%）、M3（管线+礁石）、M4（20×20 held-out）、M5（走廊 16×16 held-out）；固定 seed、局部 `RandomState`、导出 PNG+ASCII 到 `docs/04-maps/`。
3. 检测层：`detection:` 配置段；`deterministic` 档用**精确更新**（扫过自由格置 0）；`sampled` 档真目标 Bernoulli(Pd(d))、其他格 Bernoulli(Pfa)；每回合 `events.csv`。
4. 信念：odds 形式 `blip: ×Pd/Pfa`，`no blip: ×(1-Pd)/(1-Pfa)`；free 掩码归一化一次；维度仍 488。
5. 能量：按 §2.3 累计，超预算 truncate 记 censored；`max_steps = ceil(2×budget)`。
6. 基线：`info_gain`、`online_lawnmower`（只用已知自由格 + A*）、`lawnmower`（标 oracle）、`greedy_prob`、`bayes_myopic`、`random`。
7. 统一入口：`scripts/run_suite.py --suite gate1 --config config/suites/gate1.yaml`；`scripts/make_tables.py` 从 CSV 出表。
8. 自检：确定性档下 beliefs ≡ 1−coverage；C0 vs C0c 应无显著差异（负向自检）。

验收：一条命令跑完 Gate 1；`results/gate1/` 有 `episodes.csv / summary.json / meta.json`；表能从 CSV 重建。

## 未决（等用户）

1. **是否现在开工 Phase 0**（顺序已定：先审查 → 收口 → 再开工；等审查结果）。
2. `reviewer` 的“正式评审”是**建议**还是**可否决 Gate**（用户 2026-11-28：暂不定，过渡期按“不设否决权、必改项未修完不能过”执行）。
3. `experimenter` 的自主预算上限（比如 Gate 1 以内可自主跑，Gate 2 训练必须 owner 批）。

## 协作机制现状（2026-11-28）

- 四角色：`owner`（总讨论/PM，本会话）、`reviewer`（按需，新上下文）、`experimenter`（按需）、`writer`（idle，Gate 3 后）。
- 规则：`协作/协作规则.md`；注册表：`协作/角色注册表.md`；首次启动协议：`协作/入职与首个任务.md`。
- 当前动作：等用户新开 `reviewer` 会话 → 审计划 v3.2 覆盖性 → 一起收口 → 开 `experimenter` 做 Phase 0。

## 环境与运行（踩过的坑）

- 解释器：`D:\Anaconda\envs\UUVSearch\python.exe`（3.8.20，torch 2.4.1+**cpu**，gymnasium 1.1.1）。
- 默认 `python` 没 gymnasium；不要为 GPU 新建环境（CPU 8 进程 ≈800 步/s，优于单 GPU ≈220）。
- 从仓库根目录运行；`$env:PYTHONPATH="."`。
- 控制台 GBK：**不要** `Get-Content | Set-Content` 改含中文源码；改文件用编辑工具。
- 速度：DQN 单进程 ≈97 步/s；200k 步/run ≈35 min；8 进程并行。
- Git：`core.sshCommand` 已指向 `C:/Windows/System32/OpenSSH/ssh.exe`（沙箱内可用）；remote 已可 push。

## 关键路径

```
README.md                    入口
CLAUDE.md                    工程备忘录（事实 + 纪律）
docs/STATUS.md               本页（唯一事实源）
docs/00-handoff/             TAOLUN 交接（只读）
docs/01-review/              审计 + 44 条问题清单
docs/02-plan/                计划 v3.2
docs/03-decisions/           用户决策
docs/04-maps/                地图导出（Phase 0 后）
协作/                        四角色协作
results/<tag>/               实验产物
```

## 禁止

- 引用旧 95%/94% 当“RL 更优”证据。
- 单 seed、单地图下结论；挑最好 seed 报。
- 手填表；表必须由 `make_tables.py` 从 CSV 生成。
- 改 `docs/00-handoff/`；改 TAOLUN 目录任何文件。
- 把 `results/` 里 censored 回合当成功。
- 角色自我审查（写代码的人审自己的代码）。
- 角色宣布“项目完成”。

## 如果你是接任者（3 步恢复）

1. 读本页 → `docs/02-plan/plan-2026-11-28.md`（至少 §2/§5/§6）→ `docs/03-decisions/`。
2. `git log --oneline -15` 看提交；`git branch -a` 看分支；确认 `main` 干净。
3. 看 `协作/角色注册表.md` 拿到自己的角色帽，再读 `协作/角色/<role>.md` 与最近交接；按 `协作/启动提示词.md` 回 6 行，**不落盘**。
