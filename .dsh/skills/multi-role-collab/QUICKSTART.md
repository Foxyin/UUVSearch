# QUICKSTART — multi-role-collab

> 装完之后怎么用。完整纪律见 `SKILL.md`，四种角色的复制粘贴提示词见 `references/startup-prompts.md`。

## 30 秒版

1. 安装 skill → 2. 在项目根跑一次 `init_collab.py` 生成 `协作/` → 3. 每个角色开一个会话、粘贴对应启动提示词 → 4. 第一轮只回 6 行，确认后才写文件。

它不创建 agent、不调度、不强制权限。它只规定：角色文档记“谁做了什么”，项目事实另有单一来源。

## 1. 安装 + 初始化

在**目标项目根**执行（把 `<项目>` 换成真实路径）：

```powershell
python "C:\Users\17053\Desktop\skills_manager\tools\dsh_skill.py" install "<项目>" `
  "C:\Users\17053\Desktop\skills_manager\download\collab-skills\multi-role-collab" --apply
```

如果这个 skill 不是从本仓库装、而是从别的项目复制的，跳到第 2 步，用 `<项目>\.dsh\skills\multi-role-collab\scripts\init_collab.py` 即可。

```powershell
# 先 dry-run 看清单（默认不写盘）
python "<项目>\.dsh\skills\multi-role-collab\scripts\init_collab.py" --project "<项目>"
# 确认后写入
python "<项目>\.dsh\skills\multi-role-collab\scripts\init_collab.py" --project "<项目>" --apply
```

生成 13 个文件：

```text
<项目>\协作\
  协作规则.md        8 条纪律，所有角色先读
  角色注册表.md      角色 ID / 状态 / 当前接任
  变更日志.md        只追加
  启动提示词.md      四段提示词 A/B/C/D + 接任 E
  使用模板.md        开会话/换模式/收口
  角色\owner.md      已填好的 owner 角色文档
  角色\_模板.md
  讨论\_README.md
  评审\_模板.md + README.md
  提案\_README.md
  交接\_模板.md + README.md
```

脚本**只建模板和空索引，不写项目事实**。项目事实必须写进项目原有的入口/当前状态/方向文档。

## 2. 先补事实源（10 分钟）

| 文件 | 谁写 | 内容 |
|---|---|---|
| `项目说明.md` 或 README | 你 / owner | 项目是什么、做到哪一步 |
| `当前状态.md` | owner | 当前阶段、已定决策、下一步 |
| `方向.md` / `个人信息.md`（如有） | owner | 约束与方向 |

缺了这几份，角色只能瞎猜——这是最常见的失败原因。

## 3. 开一个角色会话

1. 打开 `协作\启动提示词.md`，选 A（owner）/ B（reviewer）/ C（auditor）/ D（red-team）。
2. 把 `{{PROJECT_ENTRY}}`、`{{CURRENT_STATE}}`、`{{OBJECT_PATH}}` 换成真实路径。
3. 粘进新会话。**第一轮它只回 6 行**：

```text
我是谁：
我这轮的任务：
我可以写：
我不能写：
我读到的当前状态：
我建议先做：
```

4. 你确认任务和输出路径后，它才落盘。首轮不写文件是硬规则。

## 4. 干活：一次只开一个模式

| 你说 | 模式 | 产物 |
|---|---|---|
| 「先发散，有哪些可能」 | `discuss` | `协作\讨论\<role>-YYYYMMDD-主题.md` |
| 「审这份实验设计 / 这个 claim」 | `review` | `协作\评审\review-YYYYMMDD-主题.md`（头 5 行：对象/任务/角色/是否借用/效力） |
| 「盘一下这些数据/代码能不能复用」 | `audit` | `协作\评审\asset-review-YYYYMMDD-主题.md` |
| 「给下一任/别的项目写交接」 | `handoff` | `协作\交接\<role>-YYYYMMDD.md` |

三个机制：

- **任务分诊**：不属于这个角色时只回 5 行（我是谁 / 这是什么 / 为什么不是我的 / 该谁做 / 能否只读帮忙），不写文件、不给结论。
- **单写者**：不是自己的文件，写 `协作\提案\`，owner 接受后再改。
- **评审效力**：`正式` / `provisional` / `参考`；错配时标 provisional——留证据，不作判决。

## 5. 收口 / 接任

换模型或上下文满时，角色做五件事：写完本轮产物 → 更新自己角色文档（状态 + 交接摘要）→ 写 `协作\交接\<role>-YYYYMMDD.md` → 变更日志加一行 → 报告产出与剩余。

接任时把提示词 E 附在后面：

```text
这是接任会话，不是新角色。先读上一任的 协作\交接\<role>-*.md 和角色文档"历任/交接摘要"；
第一句说明"我接任 <role>，不是新建角色"；不要重做上一任已完成的事。
```

## 6. 最小例子（一个项目、三个角色、一天）

```text
09:00  owner    提示词 A → 6 行 → 你确认"今天写 1 页方法"
10:00  reviewer 提示词 B（OBJECT_PATH=方法草稿.md）→ 6 行 → 你确认 → 评审\review-20260101-方法草稿.md
11:00  你让 reviewer 顺手评"这篇论文适不适合主线" → 触发分诊，回 5 行，建议找 auditor/red-team，不写文件
14:00  red-team 提示词 D → discuss → 讨论\challenger-20260101-替代解释.md
17:00  三个会话各自收口，owner 更新 当前状态.md
```

## 7. 三个最容易用错的点

1. **把角色文档当事实**——角色文档写“谁做了什么”；状态变了改 `当前状态.md`。
2. **一轮混多个模式**——讨论 + 审查 + 交接混写出不了可追溯的产物；换模式先写 5 行过渡。
3. **角色越加越多**——默认活跃角色 ≤3；接任者（如“主持人2”）是同一角色的接任，不是新角色。

## 8. 什么时候别用

单个一次性任务、只有一个会话、就是改几行代码——直接做，不要建 `协作/`。这套东西的价值在“多会话共享一个项目状态”时才体现。
