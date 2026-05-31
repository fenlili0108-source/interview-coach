# interview-coach Skill · 使用说明

> 通用 AI 求职面试助手 — 适配任何岗位与行业。
> 所有定制化能力来自**你自己填写的资料**，skill 本身不含任何个人信息。

这是一个 [Claude Code](https://claude.com/claude-code) **Skill**：在面试前帮你做公司调研、JD 拆解、Q&A 预测、反问设计，面试中给临场话术，面试后做录音复盘与薄弱点诊断。开箱即用、隐私本地化，填入你自己的资料即可。

## 安装

把本仓库放到 Claude Code 的 skills 目录下即可（目录名就叫 `interview-coach`）：

```bash
# 全局安装（对所有项目可用）
git clone https://github.com/fenlili0108-source/interview-coach.git ~/.claude/skills/interview-coach

# 或：项目级安装（只对当前项目可用）
git clone https://github.com/fenlili0108-source/interview-coach.git .claude/skills/interview-coach
```

装好后按下面「三步开始用」填资料即可。所有面试产物默认存在你 `config.md` 指定的目录，`.gitignore` 已确保你的真实资料不会被误传回仓库。

---

## 🚀 三步开始用

1. **填配置** → 打开 [`config.md`](config.md)，填好 `sessions_dir`（会话存哪）、`user_name`、`target_role`。需要飞书同步的话把 `lark_enabled` 设为 `true` 并填 `lark_space_id`。
2. **填资料** → 把 `profile/` 下四个文件里的 `<尖括号>` 占位符换成你自己的真实信息（profile / projects 必填，talking-points 建议填，qa-bank 不用预填）。
3. **直接说人话** → "准备一下 X 公司的面试，JD 是……"，skill 自动开工。

> ⚠️ 没填资料就用，skill 只能给空泛模板。填得越细，输出越定制。

## 目录结构

```
interview-coach/
├── SKILL.md                       # 主入口（Claude 读这个找触发逻辑）
├── README.md                      # 本文件（给你看的）
├── config.md                      # ★ 首次使用必填：路径/身份/飞书配置
├── profile/                       # ★ 你的个人资料（Claude 必读）
│   ├── profile.md                 # 专业背景全集
│   ├── projects.md                # 项目/经历完整 STAR
│   ├── talking-points.md          # 标准话术库
│   └── qa-bank.md                 # 高频 Q&A 沉淀（会随复盘自动增长）
├── references/                    # 4 种 Mode 的执行流程
│   ├── mode-a-pre-interview.md    # 面试前调研
│   ├── mode-b-live-rescue.md      # 面试中临时求助
│   ├── mode-c-post-interview.md   # 面试后录音复盘
│   ├── mode-d-pipeline.md         # 多面试组合管理
│   └── lark-sync.md               # 飞书同步流程（可选）
└── templates/                     # 输出文件模板
    ├── company-profile.md
    ├── jd-mapping.md
    ├── qa-prediction.md
    ├── rebuttal.md
    └── post-interview-qa.md

# 面试产物存在 config.md 里 sessions_dir 指定的目录：
<sessions_dir>/<公司名>/
    ├── 00-基础信息.md
    ├── 01-公司画像.md  ~  05-话术速查.md      # 面试前（Mode A）
    └── 06-面试实录Q&A.md ~ 08-后续行动清单.md  # 面试后（Mode C）
```

## 如何触发（直接说人话）

### 场景 1：准备面试

> "准备一下 X 公司的面试，岗位是 <岗位>，薪资 <区间>，JD 内容:..."

→ 进入 Mode A，生成 5 个本地文件到 `<sessions_dir>/X公司/`（开了飞书同步则同时建文档）

### 场景 2：面试中急救

> "面试中，刚被问到 <某问题>，怎么答?"

→ 进入 Mode B，直接给 ≤250 字话术，不生成文件

### 场景 3：面试后复盘

> "刚跟 X 公司 HR 聊完，这是录音文字稿:..."

→ 进入 Mode C，生成 06-08 三个本地文件 + 自动追加到 qa-bank.md（开了飞书则追加到同公司文档末尾）

### 场景 4：看 pipeline

> "我现在面着哪几家?下周要准备哪个?"

→ 进入 Mode D，扫 sessions/ 给汇总表

---

## 飞书同步规则（可选，默认关闭）

- **开启方式**：在 `config.md` 把 `lark_enabled` 设为 `true`，填好 `lark_space_id`，并先完成 `lark-cli auth login`
- **位置**：你配置的飞书知识库根目录
- **命名**：一公司一文档，文档名 = 公司短称
- **累积**：同一家公司所有轮次的调研 + 复盘累积到同一篇，用 `---` + 时间戳分节
- **不同步内容**:`profile/` 个人信息 + `00-基础信息.md`（含薪资/HR 联系方式等敏感信息）
- **手动跳过**:对 Mode A/C 说"不要同步飞书" / "skip 飞书"即可

---

## 你需要做的维护动作

### 每周（5 分钟）
- 看一眼 sessions/ 下各公司的 00-基础信息.md
- 把状态过期的公司归档或删掉（避免 Pipeline 太乱）

### 每场面试前
- 把 HR 发来的 JD 完整复制粘贴
- 告诉 skill 面试官姓名 / title（如果有）

### 每场面试后
- 录音转文字稿后，粘贴给 skill
- 告诉 skill「这是 X 公司 R<X> 轮」和你的自我感觉

### 不定期
- 如果 profile.md 中的数据有更新（新项目 / 新成果 / 新简历版本），告诉 skill"更新 profile"

---

## 隐私 / 数据说明

- ✅ 这个 skill 只在你**本地** `.claude/skills/` 下运行
- ✅ 默认不上传任何外部服务器（除非你主动开启飞书同步）
- ❌ skill 内部**不存联系方式**（手机/邮箱/微信），如需在简历中填，自行手动添加
- ⚠️ 如果用第三方录音/转写工具，注意他们的隐私政策

---

## 这个 skill 通用吗？

通用。它不绑定任何行业或岗位 —— 所有专业内容都来自你填写的 `profile/`。
无论你面的是产品、研发、设计、运营、市场还是其他岗位，填好自己的资料即可使用。
默认的 4 轮面试模型也可以在 `config.md` 里按你的目标行业调整。
