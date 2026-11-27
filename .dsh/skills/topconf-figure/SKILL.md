---
name: topconf-figure
description: 按 NeurIPS/ICML/ICLR/CVPR/ACL 主图规范，用 TikZ 从 scene.json 生成可编辑矢量图（Figure 1 teaser、系统框图、pipeline、architecture、taxonomy、concept）。Use when the user asks for a paper figure, teaser, system overview, method diagram, pipeline / framework / architecture figure, or wants to redraw a sketch into a publication-quality vector figure. 不用于数据图（曲线/散点/热力图），那些用 matplotlib。
---

# topconf-figure：顶会主图

把「图要表达什么」变成一份**可检查、可重排、可复现**的矢量图。模型只写 JSON，排版由 TikZ 完成——最终渲染里没有一次模型参与，所以每版图都可复现、可 diff、可微调坐标。

## 边界

- 做：Figure 1 / teaser、方法总览、系统架构、pipeline、模块细节图、taxonomy、概念示意。
- 不做：训练曲线、散点、热力图、柱状图（用 matplotlib / `academic-plotting`）。
- 不做：像素级复刻某张参考图。产出定位「可编辑初稿 + 明确修改点」。
- 参照图只用于分析构图，**永不嵌入**产物；照片类节点用用户自己的素材。

## 十条硬规则（统计 60 张 oral 主图得出）

1. **画布 2.2–2.5:1 横条**。单栏 88–90mm 宽，双栏 180–200mm；高度随之 36–80mm。
2. **主流程单向**：左输入 → 中处理 → 右输出，或上→下。不要环形、不要放射。
3. **3–5 个面板**，左下角标 `(a) (b) (c)`；面板内 2–4 个模块。
4. **分组用虚线圆角框**，group 不填充颜色；组间距 ≥6mm。
5. **颜色只表达 2–3 种语义**：data（蓝）/ model（灰）/ accent（橙，最多 1–2 个关键模块）。其余用 neutral / muted。
6. **箭头必有语义**：`data` 实线、`sup` 虚线、`feedback` 虚线弯箭头、`grad` 点线；两条箭头交叉必须用 `via` 绕开。
7. **阶段编号** ①②③ 或 `Step 1/2/3` 放在模块左上或组标题里，不要只靠位置暗示顺序。
8. **字号两级**：模块名 7–9pt、注释 6–7pt，<6pt 印刷会糊（check 会警告）。
9. **结果条挂底部**：关键数字或小样例图放面板底部，别塞进主流程。
10. **一图一论点**：读图人 5 秒内能说出「输入是什么、我们新增了什么、输出是什么」。

## 流程（每步都有产物）

### 0. 查参照（便宜）

```bash
python scripts/refs.py --pattern teaser -n 5          # 元数据卡片，不读图
python scripts/refs.py --theme control --keyword auv  # 按主题/关键词
python scripts/refs.py --need "underwater,sonar"      # 覆盖检查：有词 0 命中就 exit 3
python scripts/refs.py --pattern framework --json     # 机器可读
python scripts/refs.py --pack ocean -n 6              # 顶刊水下子集（JOE / T-RO）
```

两个包，按场景选：

| 包 | 内容 | 什么时候用 |
|---|---|---|
| 默认（画廊） | 87 张 NeurIPS/ICML/ICLR/CVPR/ACL 主图 + `ANALYSIS.md` | 会议论文、teaser、系统框图；配色鲜、三段式横条 |
| `--pack ocean` | 6 张 IEEE JOE / T-RO 水下主图（成像几何、机体标定、点云对照、因子图） | 投稿期刊、水下机器人类论文；偏「装置+量纲标注」，克制配色 |

卡片里选 1–2 张，再 `read_image <图片路径>` 看**构图**（不要看细节像素）。参照包在 `C:\Users\17053\Desktop\skills_manager\download\`（`topconf-figure-gallery\` 与 `ocean-figure-refs\`）。

**先跑 `--need`**：exit 3 表示有主题零覆盖 → 跳到下面「参照不够用」，别硬套。

### 1. 写 `brief.md`（人话，≤15 行）

```markdown
## 信息
一句话：<输入> → <我们做的关键处理> → <输出/收益>
## 原型
teaser | framework | pipeline | architecture | conceptual | taxonomy
## 面板
(a) ... (b) ... (c) ...
## 阅读顺序
1 → 2 → 3（标出必须最先看到的模块）
## 配色角色
data=观测输入；model=模块；accent=<唯一要强调的贡献>
## 箭头语义
实线=数据流；虚线=监督/反馈；点线=梯度
## 借哪张的什么
<ref id> 借三段式布局；<ref id> 借底部结果条
```

### 2. 写 `scene.json`

坐标单位 mm，原点左上、y 向下。完整字段见 `references/scene-schema.md`，最小骨架：

```json
{"canvas": {"width": 180, "height": 76},
 "nodes": [
   {"id": "g1", "type": "group", "x": 4, "y": 4, "w": 82, "h": 68, "label": "(a) 输入"},
   {"id": "a", "type": "box", "role": "data", "x": 44, "y": 20, "w": 44, "h": 10, "label": "声呐图像"},
   {"id": "b", "type": "box", "role": "model", "x": 108, "y": 20, "w": 44, "h": 10, "label": "编码器"},
   {"id": "e1", "type": "arrow", "from": "a", "to": "b", "kind": "data", "label": "特征"}
 ]}
```

### 3. check（几何错误先修）

```bash
python scripts/scene.py check scene.json
```

拦：重复 id、未知 type、箭头指向不存在节点、出画、box 重叠、文字超框、字号 <6pt。

### 4. render

```bash
python scripts/scene.py render scene.json --out build/fig1 --dpi 300
# 产出 build/fig1.pdf（投稿用矢量）+ build/fig1.png（预览）
python scripts/scene.py tikz scene.json --out build/fig1.tex   # 要手改时
```

依赖：TeX Live（xelatex + pdftoppm）。中文自动切 `ctex`（fontset=windows）。

### 5. 看一次，修 ≤3 轮

每轮只改坐标/标签/箭头，不改整张结构。看图用 `read_image build/fig1.png`。**不要**每轮都重新生成整张 scene——改 `scene.json` 的局部字段再渲染。

### 6. 交付

- `fig1.pdf`：投稿用（矢量，字体已嵌入）。
- `fig1.png`：给用户预览 / 放 PPT。
- `scene.json` + `brief.md`：留在项目里，下一版从这里改。
- 汇报时写清：本版表达什么、哪些位置建议人工微调（如模块间距、配色）。

## 参照不够用：必须停下报告（硬规则）

参照库是 87 张顶会主图 + 6 张水下顶刊图的**抽样**，不可能覆盖所有领域。遇到下面任一情况：

- 先查 `--need`，**两个包都查**：默认包零命中时再跑 `--pack ocean --need "..."`（水下/海洋类很多在 ocean 包里）；
- 两边都 0 命中（比如 subsea manipulation、多 AUV 协同）；
- 命中量 ≥1 但构图完全不适用（比如只有 LLM 的 teaser，没有机器人闭环的）；
- 用户要的风格（IEEE 机器人会议、期刊单栏）在库里没有样本。

**不许**拿相近原型硬套，**不许**自己编造「某顶会图是这样的」。必须停下来，向用户报告这张卡：

```
⚠ 参照库盖不住
需要：<具体缺什么>（为什么现有 87 张不合适，1–2 句）
已查：refs.py --need "..." → <命中数>
可选：
A. 在线补 1–2 张 —— 我用画廊在线库按主题找（要联网，约 2–3 分钟；只进参照包，不进产物）
B. 扩充参照包 —— 我改 tools/fetch_gallery_refs.py 的选图规则重抓（适合整类都缺）
C. 先按通用三段式出初稿 —— 标注「需人工确认」，图能用但领域感弱
你选哪个？（没回复我就先做 C）
```

选项 A 的执行命令（联网可用时）：

```bash
python "C:\Users\17053\Desktop\skills_manager\tools\fetch_gallery_refs.py" --pick <id>
# 或整包重抓 / 按新规则重选
python "C:\Users\17053\Desktop\skills_manager\tools\fetch_gallery_refs.py" --refresh
```

在线库地址 `https://qwdwqfwq.github.io/topconf-paper-figure-gallery/data/figures.json`（3449 条元数据，按标题/会议/年份过滤后挑 id 再 `--pick`）。

如果项目沙箱不许写 `C:\Users\17053\Desktop\skills_manager\`（补图要写那里），不要绕过：把上面两条命令原样贴回给用户，让主会话去跑。

**什么时候不用上报**：单个模块怎么画、箭头怎么走、字号配色——这些改 `scene.json` 就能解决，属于本 skill 份内，不要打扰用户。只有「整类构图缺失」才升级。

## 省 token（重要）

- 参照图只进 subagent，或用 `refs.py` 卡片代替读图；单图预算 ≤6 次读图、≤30k token。
- 读图前先缩到 640–800px；不要反复把渲染图喂回模型。
- 迭代只跑 `check` + 一次 `render`，别每改一个字都渲染。

## 常见错误

| 症状 | 原因 | 修法 |
|---|---|---|
| 箭头穿框 | 起点终点之间有模块 | 加 `"via": [[x,y]]` 绕行 |
| 图太挤 | 模块 >4 个/面板 或 字号 >9pt | 拆面板、删注释 |
| 图太散 | 组间距 <6mm 或画布过高 | 收紧画布高度到 2.3:1 |
| 颜色花 | role 用了 >3 种 | 保留 data/model/accent，其余 muted |
| 中文豆腐块 | 没装 ctex 字体 | 用 `fontset=windows`（默认） |
| 文字溢出框 | 标签太长 | 缩短标签或加宽 `w`，check 会报警 |
