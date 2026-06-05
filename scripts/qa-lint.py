#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa-lint.py — interview-coach-generic Mode C 复盘产出的机械校验器(通用版)

为什么存在:模型在密集追问处会把连环追问折叠进上一题的 ### 子标题,导致
「漏整段」(题号跳号 / 静默折叠)和「答案截断」(第三人称「你答:」概括)。
让刚折叠完的模型自检会有同源盲区,所以用脚本做守门员、模型做射手,二者分开。

校验三件可机械验证的事:
  (a) 题号连续性:所有 ## Q[轮]-实录[全局序] 的全局序号 == 1..N 连续、无缺、无重
  (b) 模板完整性:每题核心三段必有;低分题(≤3)还须有 更优回答 + 关键改进点
  (c) 保真度 + 覆盖率:
      - 揪出第三人称「你答:」概括 与 省略号截断
      - 覆盖率锚点用「面试官发言轮次数」(不是数问号——追问常无问号),
        题数明显少于面试官发言轮次 = 疑似合并漏题

用法:
  python3 qa-lint.py <06-面试实录Q&A.md> [<_raw-transcript.md>]

退出码:全绿=0,任一项 ❌=1。stdout 原样贴回复盘流程(Step 3.5)。
"""

import re
import sys

# 每题必有的核心段(逐字匹配)。这三段任何题都不能省——它们正是折叠题被吞掉的部分。
CORE_SECTIONS = [
    "面试官原话",
    "你的回答(实录)",
    "我的评分",
]
# 「更优回答」「关键改进点」只对【低分题(评分 ≤ 3)】强制——高分题没有改进必要,
# 不该硬塞。这样既堵住折叠题(它们必然低分且缺这两段),又不误报满分题。
IMPROVE_SECTIONS = [
    "更优回答",
    "关键改进点",
]

# 近义替身 → 提示它顶替了哪个标准段(只用于给出更友好的报错)
ALIAS_HINTS = {
    "怎么修正": "更优回答",
    "怎么挽救": "更优回答",
    "这道题想看的": "更优回答",
    "根本问题": "关键改进点",
    "这一整段的根本问题": "关键改进点",
    "唯一遗憾": "关键改进点",
    "唯一改进点": "关键改进点",
}

# 题标题:## Q[轮次]-实录[全局序号]  例 ## Q2-实录5 / ## Q1-实录 / ## Q[R2]-实录3
# 轮次部分宽松(允许 1 / R2 / [R2] 等);全局序号必须是末尾的纯数字(无数字=旧式无序号,单独告警)
H2_QUESTION = re.compile(r'^##\s*Q\s*([^\-—]+?)\s*[-—]\s*实录\s*(\d*)\s*(.*)$')
H2_ANY = re.compile(r'^##\s+')
H3_SECTION = re.compile(r'^###\s*(.+?)\s*$')

# 第三人称概括 / 截断信号
THIRD_PERSON = re.compile(r'你答[:：]|你回答说|他说[:：]|她说[:：]|他答[:：]|她答[:：]')
TRUNCATION = re.compile(r'\.\.\.["」』\s]*$|…["」』\s]*$')  # 行尾省略号截断半句


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def split_question_blocks(lines):
    """切成 [(title_line_idx, title_text, [block_lines]), ...],每个 ## Q 题一块。"""
    blocks = []
    cur = None
    for i, line in enumerate(lines):
        if H2_ANY.match(line):
            # 任意 ## 开启新顶层块;但只有匹配题格式的才算"题"
            if cur is not None:
                blocks.append(cur)
            m = H2_QUESTION.match(line)
            cur = {"idx": i, "raw": line.rstrip(), "is_q": bool(m), "m": m, "lines": []}
        elif cur is not None:
            cur["lines"].append(line)
    if cur is not None:
        blocks.append(cur)
    return [b for b in blocks if b["is_q"]], [b for b in blocks if not b["is_q"]]


def block_score(b):
    """从某题块的「### 我的评分」段抽出分数(取首个 1-5 的数字),抽不到返回 None。"""
    in_score = False
    for ln in b["lines"]:
        ms = H3_SECTION.match(ln)
        if ms:
            name = ms.group(1).strip()
            in_score = name.startswith("我的评分") or name.startswith("评分")
            # 评分有时和段名同行后面,也扫一下本行
        if in_score:
            m = re.search(r'([1-5])(?:\.\d)?\s*/\s*5|\b([1-5])\s*分', ln)
            if m:
                return int(m.group(1) or m.group(2))
    return None


def check_numbering(qblocks):
    """(a) 全局序号 1..N 连续无缺无重。"""
    errs = []
    serials = []
    no_serial = 0
    for b in qblocks:
        rnd, serial, _rest = b["m"].group(1), b["m"].group(2), b["m"].group(3)
        if serial == "":
            no_serial += 1
            continue
        serials.append((int(serial), b["raw"]))

    # 全部题都用旧式 Q1-实录(无全局序号):整篇判 fail,提示迁移到双层编号
    if no_serial == len(qblocks) and len(qblocks) > 0:
        errs.append(
            f"  · 全部 {no_serial} 题用旧式「Q[轮]-实录」无全局序号格式,无法机械校验连续性。"
            f"\n    请改用「Q[轮]-实录[全局序号]」(如 Q1-实录1 / Q2-实录5),序号在整篇内 1..N 连续。"
        )
        return errs, 0
    if no_serial > 0:
        errs.append(f"  · {no_serial} 题缺全局序号(应为 Q[轮]-实录[数字]),与有序号题混排,先统一编号")

    nums = [n for n, _ in serials]
    n = len(nums)
    if not nums:
        return errs, 0
    seen = {}
    for num, raw in serials:
        seen.setdefault(num, []).append(raw)
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    for k, v in sorted(dups.items()):
        errs.append(f"  · 全局序号 实录{k} 重复 {len(v)} 次:{[x.strip() for x in v]}")
    expected = set(range(1, max(nums) + 1))
    missing = sorted(expected - set(nums))
    if missing:
        errs.append(f"  · 序号跳号 / 缺失:{['实录'+str(x) for x in missing]} —— 极可能被折叠进了相邻题,回 _raw-transcript.md 补出来")
    return errs, n


def check_sections(qblocks):
    """(b) 每题含核心三段;低分题(≤3)还须含改进两段。"""
    errs = []
    for b in qblocks:
        present = []
        for ln in b["lines"]:
            ms = H3_SECTION.match(ln)
            if ms:
                present.append(ms.group(1).strip())
        title = b["raw"].strip()
        score = block_score(b)
        # 核心三段:任何题都必须有
        required = list(CORE_SECTIONS)
        # 改进两段:只有低分题(≤3)或没抽到分数时才强制
        if score is None or score <= 3:
            required += IMPROVE_SECTIONS

        # 段名前缀匹配:允许「更优回答(补充说明)」这类带括号补充说明的标准段,
        # 但近义替身(怎么修正/唯一遗憾)因不以标准段名开头,仍会被判缺段。
        def has_section(std):
            return any(p == std or p.startswith(std) for p in present)
        missing = [s for s in required if not has_section(s)]
        if missing:
            hint = ""
            for p in present:
                if p in ALIAS_HINTS and ALIAS_HINTS[p] in missing:
                    hint += f"(疑似用「{p}」顶替了「{ALIAS_HINTS[p]}」)"
            sc = f"[评分{score}]" if score is not None else "[未抽到评分]"
            errs.append(f"  · 「{title}」{sc} 缺段:{missing} {hint}")
        # 嵌套新问题的征兆:子标题里出现 Q 编号或"接着问/又问"
        for p in present:
            if re.search(r'Q\s*\d|接着问|又问|追问.*Q|第[二三四五]个问题', p):
                errs.append(f"  · 「{title}」内出现可疑子标题「### {p}」—— 像是把新追问折叠成了 ### 子标题,应拆成独立 ## 题")
    return errs


def check_fidelity(qblocks):
    """(c-1) 第三人称概括(硬错误)/ 省略号截断(警告)。

    第三人称「你答:」一定是把回答压缩了 → 硬错误。
    省略号则要区分:口语里说到一半被打断/被接话很常见(真实记录,合理),
    只有当省略号 + 第三人称同现(说明是压缩转述)才算硬错误,否则降为警告。
    """
    errs = []
    warns = []
    for b in qblocks:
        for off, ln in enumerate(b["lines"]):
            is_third = bool(THIRD_PERSON.search(ln))
            is_trunc = bool(TRUNCATION.search(ln)) and (
                '>' in ln or '回答' in "".join(b["lines"][max(0, off - 2):off])
            )
            if is_third:
                errs.append(f"  · 「{b['raw'].strip()}」出现第三人称概括:{ln.strip()[:60]} —— 回原稿换成第一人称逐字实录")
            elif is_trunc:
                # 纯口语半句(无第三人称标志):很可能是被打断的真实原话,只提示不判错
                warns.append(f"  · 「{b['raw'].strip()}」回答含省略号:{ln.strip()[:50]} —— 若是被打断的真实原话可保留,若是你压缩了请补全")
    return errs, warns


def count_interviewer_turns(raw_text):
    """覆盖率锚点:数面试官发言轮次(连续同一说话人算一轮)。
    识别行首说话人标签:面试官 / HR / leader / CEO / 业务面 / 二面官 等。
    追问常无问号,所以用'发言轮次'而非'问号数'。
    通用版:用户本人侧标签用通用词(用户本人 / 我 / 候选人 / 你 / 发言人2)。"""
    interviewer = re.compile(
        r'^\s*[\*>#\-]*\s*(面试官|HR|hr|Leader|leader|领导|二面官|一面官|CTO|cto|CEO|ceo|老板|负责人|业务面|发言人\s*1)\s*[:：】\)]'
    )
    candidate = re.compile(
        r'^\s*[\*>#\-]*\s*(用户本人|候选人|我|你|发言人\s*2)\s*[:：】\)]'
    )
    turns = 0
    prev_was_interviewer = False
    for ln in raw_text.splitlines():
        if interviewer.match(ln):
            if not prev_was_interviewer:
                turns += 1
            prev_was_interviewer = True
        elif candidate.match(ln):
            prev_was_interviewer = False
    return turns


def main():
    if len(sys.argv) < 2:
        print("用法: qa-lint.py <06-面试实录Q&A.md> [<_raw-transcript.md>]")
        sys.exit(2)

    qa_path = sys.argv[1]
    raw_path = sys.argv[2] if len(sys.argv) > 2 else None

    text = read(qa_path)
    lines = text.splitlines(keepends=False)
    qblocks, _other = split_question_blocks(lines)

    print("🔎 qa-lint 实录自检")
    print(f"   文件: {qa_path}")
    print(f"   识别到 {len(qblocks)} 道 ## 题")
    print()

    fail = False

    # (a)
    num_errs, n = check_numbering(qblocks)
    if num_errs:
        fail = True
        print("(a) 题号连续性: ❌")
        for e in num_errs:
            print(e)
    else:
        print(f"(a) 题号连续性: ✅  实录1..实录{n} 连续无跳号无重号")

    # (b)
    sec_errs = check_sections(qblocks)
    if sec_errs:
        fail = True
        print("(b) 模板完整性: ❌")
        for e in sec_errs:
            print(e)
    else:
        print(f"(b) 模板完整性: ✅  {len(qblocks)}/{len(qblocks)} 题模板齐全")

    # (c-1) 保真度
    fid_errs, fid_warns = check_fidelity(qblocks)
    if fid_errs:
        fail = True
        print("(c1) 回答保真度: ❌")
        for e in fid_errs:
            print(e)
    else:
        print("(c1) 回答保真度: ✅  无「你答:」第三人称概括")
    for w in fid_warns:
        print("    ⚠️ " + w.strip())

    # (c-2) 覆盖率
    if raw_path:
        try:
            raw = read(raw_path)
            turns = count_interviewer_turns(raw)
            if turns == 0:
                print(f"(c2) 覆盖率: ⚠️  原稿未识别到带说话人标签的面试官发言,无法对账(建议喂稿时标注说话人)")
            elif n < turns * 0.7:  # 题数明显少于面试官发言轮次
                fail = True
                print(f"(c2) 覆盖率: ❌  原稿面试官发言 ≈ {turns} 轮,实录仅 {n} 题(< 70%)—— 疑似合并漏题,回 _question-list.md 重新穷举")
            else:
                print(f"(c2) 覆盖率: ✅  原稿面试官发言 ≈ {turns} 轮,实录 {n} 题")
        except FileNotFoundError:
            print(f"(c2) 覆盖率: ⚠️  找不到原稿 {raw_path},跳过覆盖率对账(Step 2.0 应已落盘)")
    else:
        print("(c2) 覆盖率: ⚠️  未传入 _raw-transcript.md,跳过覆盖率对账")

    print()
    if fail:
        print("结论: ❌ 未通过 —— 按上面逐条回原稿补齐 / 拆题 / 去概括,再重跑本脚本,全绿才能进 Step 4")
        sys.exit(1)
    else:
        print("结论: ✅ 全部通过 —— 可进 Step 4 薄弱点诊断")
        sys.exit(0)


if __name__ == "__main__":
    main()
