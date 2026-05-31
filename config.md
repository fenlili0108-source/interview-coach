# 配置文件（首次使用前必填）

> 这是 interview-coach 的全局配置。新用户拿到这个 skill 后，**先填这里**，再去填 `profile/` 里的个人资料。
> 所有 `<尖括号>` 包裹的都是占位符，需要你替换成自己的值。

---

## 一、基础路径（必填）

| 配置项 | 值 | 说明 |
|-|-|-|
| `sessions_dir` | `<你的会话目录绝对路径>` | 每场面试的产物存这里，例如 `/Users/yourname/interview/sessions` |

> 示例：`sessions_dir = /Users/yourname/interview/sessions`
> Claude 在 Mode A/C/D 写文件时一律用这个路径，不要再硬编码任何个人路径。

---

## 二、身份信息（必填，给输出文件用）

| 配置项 | 值 | 说明 |
|-|-|-|
| `user_name` | `<你的称呼>` | 出现在 Pipeline 标题等处，如「<你的称呼> 求职 Pipeline」 |
| `target_role` | `<你的求职意向岗位>` | 如「产品经理」「后端工程师」「市场运营」等，决定 Q&A 侧重 |

---

## 三、飞书同步（可选，不用就留空）

> 飞书同步默认**开启**，但需要你先配置。如果不想用飞书，把 `lark_enabled` 设为 `false`，skill 会自动只存本地。

| 配置项 | 值 | 说明 |
|-|-|-|
| `lark_enabled` | `false` | 设为 `true` 才会同步飞书；需先装好 lark-cli 并完成 `lark-cli auth login` |
| `lark_space_id` | `<你的飞书知识库 space_id>` | 在飞书知识库 URL 里能找到；只在 `lark_enabled=true` 时需要 |
| `lark_domain` | `feishu.cn` | 国内飞书用 `feishu.cn`，国际版 Lark 用 `larksuite.com` |

> 如何拿到 `space_id`：打开你的飞书知识库 → URL 形如 `https://xxx.feishu.cn/wiki/space/7xxxxxxxxxxxxx` → 末尾那串数字就是 space_id。

---

## 四、面试轮次模型（可按需调整）

默认 4 轮模型，适配大多数公司。如果你的目标行业轮次不同（如外企可能有更多技术轮），可在这里改：

| 轮次 | 名称 | 提问偏向 |
|-|-|-|
| R1 | HR 初筛 | 基础信息、离职原因、期望薪资、稳定性 |
| R2 | 业务/专业面（直属上级） | 项目深度、专业细节、case study、岗位判断 |
| R3 | 高管/总监面 | 长期动机、行业判断、文化匹配、视野 |
| R4 | HRBP/终面 | 谈薪、入职时间、背调、Offer 细节 |

---

## 五、填写检查清单

填完上面后，按顺序完成：

- [ ] 本文件的「基础路径」「身份信息」已填
- [ ] （可选）需要飞书同步的话，`lark_enabled=true` 且填好 `lark_space_id`
- [ ] `profile/profile.md` — 你的专业背景
- [ ] `profile/projects.md` — 你的项目/经历 STAR 拆解
- [ ] `profile/talking-points.md` — 你的标准话术（自我介绍/离职原因/薪资等）
- [ ] `profile/qa-bank.md` — 不用预填，会随复盘自动增长

填完即可直接说「准备一下 X 公司的面试，JD 是……」开始用。
