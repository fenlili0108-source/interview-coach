# 飞书同步流程（可选功能）

> 本文档定义如何把本地 `<sessions_dir>/<公司名>/` 的内容同步到飞书知识库。
> **前提**：`config.md` 里 `lark_enabled=true`，且已装好 lark-cli 并完成 `lark-cli auth login`。
> 所有飞书参数（`space_id` / `domain`）一律从 `config.md` 读取，**不要硬编码任何具体 ID**。

## 飞书目标位置（从 config.md 读取）

| 字段 | 来源 |
|-|-|
| 知识库 `space_id` | `config.md` 的 `lark_space_id` |
| 飞书域名 | `config.md` 的 `lark_domain`（`feishu.cn` 或 `larksuite.com`）|
| 创建位置 | **知识库根目录**（不挂在任何父节点下）|
| 文档命名 | `<公司名>`（公司短称，如 `XX科技`、`XX公司-某事业部`）|
| 文档类型 | `docx`（飞书云文档）|
| 一公司一文档 | ✅ 所有轮次 + 调研 + 复盘累积到同一篇 |

## 触发时机

| 何时调用 | 动作 |
|-|-|
| Mode A 完成，本地 5 个文件已生成 | **创建新文档**（若同名已存在则复用，在末尾追加新内容）|
| Mode C 完成，本地 06-08 已生成 | 找到该公司文档，**追加复盘 section** |
| 用户说"同步 X 到飞书" | 手动触发，行为同 Mode A 完成的同步 |
| `lark_enabled=false` 或用户说"飞书别同步" | 跳过本次同步 |

---

## Mode A 后的同步流程

### Step 1：检查文档是否已存在

```bash
# 列出知识库根节点下所有子节点（space_id 取自 config.md）
lark-cli wiki nodes list --as user \
  --params '{"space_id":"<lark_space_id>"}' \
  --format json
```

遍历返回的 items，看是否有 `title === <公司名>` 的节点。

- ✅ 存在 → 拿到 `obj_token`（docx 的 token），走 **Step 2-追加**
- ❌ 不存在 → 走 **Step 2-新建**

### Step 2-新建：创建并迁入

⚠️ **重要 trick**：`lark-cli docs +create --doc-format markdown` 不会把 markdown 第一行的 `# 标题` 设为飞书文档标题（会显示成 "Untitled"）；`--new-title` 参数也无效。**必须用「先 XML overwrite 设 title → 再 markdown append 内容」的两步法**。

```bash
# 1) 合并本地 5 个文件（<sessions_dir> 取自 config.md）
cat <sessions_dir>/<公司名>/01-公司画像.md > /tmp/_sync.md
echo "" >> /tmp/_sync.md && echo "---" >> /tmp/_sync.md && echo "" >> /tmp/_sync.md
cat <sessions_dir>/<公司名>/02-JD拆解与匹配点.md >> /tmp/_sync.md
echo "" >> /tmp/_sync.md && echo "---" >> /tmp/_sync.md && echo "" >> /tmp/_sync.md
cat <sessions_dir>/<公司名>/03-Q&A预测.md >> /tmp/_sync.md
echo "" >> /tmp/_sync.md && echo "---" >> /tmp/_sync.md && echo "" >> /tmp/_sync.md
cat <sessions_dir>/<公司名>/04-反问板块.md >> /tmp/_sync.md
echo "" >> /tmp/_sync.md && echo "---" >> /tmp/_sync.md && echo "" >> /tmp/_sync.md
cat <sessions_dir>/<公司名>/05-话术速查.md >> /tmp/_sync.md

# 2) 创建飞书文档（用 XML 设置 title，内容先留个 callout 占位）
cat > /tmp/_xml_head.txt << EOF
<title><公司名></title>
<callout emoji="📌">
<p>R1 · 岗位:<岗位名> · 薪资 <薪资> · 整理日期 <日期></p>
</callout>
EOF
lark-cli docs +create --api-version v2 --doc-format xml \
  --as user --content "$(cat /tmp/_xml_head.txt)"
# → 返回 document_id 记下来，此时 title 已被正确设为 <公司名>

# 3) 把完整内容 append 到文档末尾
lark-cli docs +update --api-version v2 --doc <document_id> \
  --as user --command append --doc-format markdown \
  --content "$(cat /tmp/_sync.md)"

# 4) 移到知识库根目录（target-space-id 取自 config.md 的 lark_space_id）
lark-cli wiki +move --as user \
  --obj-type docx \
  --obj-token <document_id> \
  --target-space-id <lark_space_id>
```

### Step 2-追加（同名已存在）

```bash
# 直接 append 新内容到末尾，带分隔线和时间戳
lark-cli docs +update --api-version v2 --doc <obj_token> \
  --as user --doc-format markdown --command append \
  --content "$(cat /tmp/_append.md)"
```

其中 `/tmp/_append.md` 是新增的 5 个文件内容，前面加：
```markdown
---

## 📅 <YYYY-MM-DD> 第 X 次更新

[新内容]
```

---

## Mode C 后的同步流程

### Step 1：定位该公司的飞书文档

按 Step 1 同 Mode A，**该公司文档必然已存在**（因为 Mode A 已经创建过）。如果不存在，先把 Mode A 的内容补同步，再做 Step 2。

### Step 2：append 复盘内容

```bash
cat > /tmp/_review.md << 'EOF'

---

# 📋 R<X> 面试复盘 · <YYYY-MM-DD>

## 一、实录 Q&A
[06-面试实录Q&A.md 内容]

## 二、薄弱点与改进
[07-薄弱点与改进.md 内容]

## 三、后续行动
[08-后续行动清单.md 内容]
EOF

lark-cli docs +update --api-version v2 --doc <obj_token> \
  --as user --doc-format markdown --command append \
  --content "$(cat /tmp/_review.md)"
```

---

## 完成后输出给用户

简洁汇报：
```
📂 已同步到飞书知识库
🔗 文档链接:https://<lark_domain>/wiki/<node_token>
```

链接构造方式：从 `wiki +move` 或 `wiki nodes list` 返回的 `node_token` 取值，拼成 `https://<lark_domain>/wiki/<node_token>`（`lark_domain` 取自 config.md）。

---

## 错误处理

| 错误 | 处理 |
|-|-|
| `need_user_authorization` | 提示用户跑 `lark-cli auth login --domain wiki,docs,drive` |
| `wiki +move` 异步任务超时 | 用 `drive +task_result --scenario wiki_move --task-id <id>` 续查 |
| 同名文档已存在但 token 拿不到 | 退回到 append 模式，在用户面前留 warning |
| `lark_enabled=false` 或用户说"不同步飞书" | 跳过，仅本地完成 |
| `lark_space_id` 未填 | 提示用户去 config.md 填，本次跳过同步 |

---

## ⚠️ 注意事项

- 飞书同步是**可选功能**，只在 `lark_enabled=true` 时执行；不要因为同步失败而阻塞用户主流程：即使同步失败，本地 5 个文件已经写好，用户仍可使用
- **不要把 profile/ 里的个人信息同步到飞书**（那是 skill 的底层知识，不是面试内容）
- **不要同步 00-基础信息.md**（里面可能含 HR 联系方式、薪资等敏感信息）
- 飞书的文档命名只用**公司名**，不加"面试准备"等后缀，以便后续轮次的复盘自然追加
