# scene.json 字段参考

坐标单位 **mm**，原点在**左上角**，y 轴**向下**（写图时和看图一致）。所有字段除 `id`/`type` 外都有默认值。

## 顶层

```json
{
  "canvas": {"width": 180, "height": 76},
  "style": {"font_size": 8, "stroke": 0.6, "radius": 1.2, "arrow_width": 0.7},
  "meta": {"title": "可选，不进图，只做注释"},
  "nodes": []
}
```

| 字段 | 默认 | 说明 |
|---|---|---|
| `canvas.width/height` | 180 / 80 | 画布尺寸；建议 2.2–2.5:1 |
| `style.font_size` | 8 | 默认字号（pt） |
| `style.stroke` | 0.6 | 框线宽（pt） |
| `style.radius` | 1.2 | 圆角半径（mm） |
| `style.arrow_width` | 0.7 | 箭头线宽（pt） |

## 节点通用字段

| 字段 | 适用 | 说明 |
|---|---|---|
| `id` | 全部 | 唯一；箭头用 `from`/`to` 引用 |
| `type` | 全部 | `box`（默认）/ `group` / `text` / `badge` / `arrow` / `image` |
| `x`, `y` | 除 arrow | box/badge/image 为**中心**；group 为**左上角**；text 为左对齐基线点 |
| `label` | box/group/text/badge | 图上的字 |
| `label_size` | box/text | 覆盖默认字号 |
| `bold` | box/text | 默认 box 粗体、text 常规 |
| `role` | box/badge | `data` / `model` / `accent` / `neutral` / `muted`，见配色 |
| `dashed` | box | 虚线边框 |
| `shape` | box | `round`（默认）/ `rect` / `ellipse` |
| `label_pos` | arrow | `above`（默认）/ `below` / `left` / `right` |
| `via` | arrow | `[[x,y], …]` 途经点，用来绕开模块 |

## 各类型

### box

```json
{"id": "enc", "type": "box", "role": "model", "x": 100, "y": 30,
 "w": 44, "h": 10, "label": "多模态编码器", "label_size": 7.5}
```

`w`/`h` 必填且 >0。文字宽估算：CJK 1em、拉丁 0.52em；超框宽 94% 会警告。

### group（面板虚线框）

```json
{"id": "ga", "type": "group", "x": 4, "y": 4, "w": 80, "h": 68, "label": "(a) 多源观测"}
```

`x,y` 是左上角，`w,h` 向右向下。不填充；标题贴在框内左上。组不参与重叠检测，子模块之间仍检测。

### text（注释）

```json
{"id": "t1", "type": "text", "x": 8, "y": 66, "label": "稀疏、弱纹理、异步", "label_size": 6.5}
```

`anchor=west`，`(x,y)` 是文字左侧中心点。

### badge（①②③ 编号）

```json
{"id": "s1", "type": "badge", "x": 12, "y": 12, "label": "1", "role": "accent"}
```

圆形 4.6mm 直径，白/橙底。也可写 `①`。

### arrow

```json
{"id": "e1", "type": "arrow", "from": "a", "to": "b", "kind": "data", "label": "特征"}
{"id": "e2", "type": "arrow", "from": "b3", "to": "c1", "kind": "sup", "via": [[137, 50], [137, 18]]}
```

| `kind` | 线型 | 用途 |
|---|---|---|
| `data`（默认） | 实线 | 数据流 |
| `sup` | 虚线 | 监督 / 损失 |
| `feedback` | 虚线 + 上方弯 | 闭环、回流 |
| `grad` | 点线 | 梯度、训练信号 |

- `from`/`to` 指向 box/badge 的 id，自动裁到边框。
- `feedback` 走两节点上方弧线（`out=90,in=90`），同行模块之间用。
- `via` 按顺序连接途经点（mm，同样左上原点、y 向下），最后指向 `to` —— **正交绕行**用：

```json
{"from": "left", "to": "right", "via": [[80, 40], [80, 20]]}
```

`check` 会验证 via 点不越界。

### image（照片/渲染结果）

```json
{"id": "im1", "type": "image", "x": 60, "y": 40, "w": 40, "h": 24, "src": "assets/teaser.png"}
```

`src` 相对 `scene.json` 所在目录。用于把实验结果、样例截图嵌进主图。

## 配色（内置五角色）

| role | 填充 | 描边 | 语义 |
|---|---|---|---|
| `data` | `#DCE8F7` 浅蓝 | `#5B84B8` | 输入、观测、数据 |
| `model` | `#EEF1F4` 浅灰 | `#7A828C` | 模块、网络 |
| `accent` | `#FBE3CB` 浅橙 | `#C8792A` | 唯一要强调的贡献 |
| `neutral` | 白 | `#9AA0A6` | 中性容器 |
| `muted` | `#F4F6F8` | `#C4C9CE` | 次要模块、结果条 |

规则：一张图里 role 不超过 3 种；`accent` 最多 1–2 个框。要换整套配色时改 `ROLES`（渲染时自动生成 `\definecolor`）。

## 线宽与字号约定

- 框线 0.6pt、箭头 0.7pt，全文统一（顶会印刷线的视觉重量差异很小）。
- 模块名 7–9pt 粗体；注释 6–7pt 常规；面板标 `(a)` 8pt 常规。
- 双栏图（180mm）模块名 8pt；单栏图（88mm）模块名 7pt、注释 6pt。

## 完整最小示例

见 `examples/underwater-pipeline/scene.json`（3 面板、跨面板正交路由、结果条）。
