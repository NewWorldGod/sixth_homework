# -*- coding: utf-8 -*-
"""按实验真实运行数据填写《实验六 RSI 递归自进化》报告样板，保留原格式。"""
from docx import Document
from docx.shared import Inches
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

SRC = "实验六_RSI递归自进化_实验报告样板.docx"
DST = "实验六_RSI递归自进化_实验报告.docx"


def set_text(p, text):
    """替换段落文本（清空原 runs，保留段落样式）"""
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.add_run(text)


def insert_para_before(anchor_p):
    """在 anchor 段落前插入新空段落，返回 Paragraph 对象"""
    new_p = OxmlElement("w:p")
    anchor_p._p.addprevious(new_p)
    return Paragraph(new_p, anchor_p._parent)


doc = Document(SRC)

# ---------- 副标题 ----------
for p in doc.paragraphs:
    if "报告样板" in p.text:
        set_text(p, "SmolVLM-256M 精准定位的 RSI 递归自进化实验　·　实验报告")
        break

# ---------- 表 0：信息表 ----------
t0 = doc.tables[0]
t0.rows[2].cells[1].text = "[请填写姓名] / [请填写学号] / [请填写班级]"
t0.rows[3].cells[1].text = "2026 年 10 月 20 日 ～ 10 月 21 日"
t0.rows[4].cells[1].text = ("GPU：NVIDIA GeForce RTX 5070 Laptop 8GB（另有纯 CPU 对照）；"
                            "Python 3.14.0；torch 2.14.0（GPU 为 +cu130，CPU 对照为 +cpu）")
t0.rows[5].cells[1].text = ("hw6_rsi_localize.py；sft_data.json / rsi_memory.json；"
                            "log_eval_gpu.txt、log_rsi_gpu2.txt 等运行日志；rsi_chart.png")

# ---------- 一、实验目的 ----------
work_items = [
    "1. 复现参考实现全链路：合成数据 → 网格坐标种子数据 → QLoRA SFT → 三阶段评测 → RSI 两轮递归自进化；",
    "2. 调通 transformers 5.x / 纯 CPU / 8GB GPU 三种运行环境，定位并修复「训练后未切 eval 模式导致 RSI 轮内评测输出退化」的缺陷；",
    "3. 完成基线、SFT、SFT+纠错、RSI 轮 1 / 轮 2 共 5 组评测与逐题日志，统计纠错明细，绘制各阶段正确数与数据池规模图（rsi_chart.png），并据此分析提升来源与失败模式。",
]
wi = 0
for p in doc.paragraphs:
    if p.text.strip().startswith("用 2~4 句话概括"):
        set_text(p, "本实验让 SmolVLM-256M 把目标位置表达为 4×4 网格坐标，并构建「高亮格回灌自查 + 解析式验证器纠错」的"
                    "RSI 递归自进化闭环，用三阶段评测与两轮递归回答核心问题——提升来自微调（SFT）还是来自智能体闭环（RSI）。")
    elif p.text.strip().startswith("我做的主要工作（3~5 条"):
        set_text(p, "我做的主要工作：")
    elif p.text.strip().startswith("1. [") or p.text.strip().startswith("2. [") or p.text.strip().startswith("3. ["):
        if wi < len(work_items):
            set_text(p, work_items[wi]); wi += 1

# ---------- 二、实验环境 ----------
for p in doc.paragraphs:
    if p.text.strip().startswith("依赖版本"):
        set_text(p, "依赖版本：transformers 5.17.0，peft 0.21.2，bitsandbytes 未用（fp32 训练，无需量化）；"
                    "torch 2.14.0（GPU +cu130，纯 CPU 对照 +cpu）；Pillow/NumPy 随环境自带；模型 "
                    "HuggingFaceTB/SmolVLM-256M-Instruct（约 500MB，经 hf-mirror 下载后离线加载）。"
                    "本环境与指南参考代码的适配改动及原因见 3.4。")
        break

# ---------- 表 1：命令与耗时 ----------
t1 = doc.tables[1]
rows1 = [
    ["--mode make_data", "生成 55 张合成图 + GT 框", "hw6_imgs/gt.json（<1s）"],
    ["--mode make_sft", "GT 框 → 网格坐标种子数据", "sft_data.json（15 条，<1s）"],
    ["--mode sft --steps 60", "QLoRA SFT（实测 10 步不收敛，加到 60 步）", "sft_adapter/（GPU 153s；CPU 约 28min）"],
    ["--mode eval", "三阶段评测（基线 / SFT / 纠错）", "log_eval_gpu.txt（GPU 80s；CPU 约 20min）"],
    ["--mode rsi --rounds 2 --steps 30", "RSI 递归自进化 2 轮（每轮再训 30 步）", "rsi_memory.json（GPU 289s）"],
]
for i, row in enumerate(rows1):
    for j, v in enumerate(row):
        t1.rows[i + 1].cells[j].text = v

# ---------- 三、方法与关键实现 ----------
for p in doc.paragraphs:
    t = p.text.strip()
    if t.startswith("3.1 网格坐标编码"):
        set_text(p, "3.1 网格坐标编码：256×256 画布按 64 像素等分划成 4×4 网格；GT 像素框取中心点 (cx,cy)，"
                    "行 r=cy//64、列 c=cx//64（越界取 3），标准答案渲染为「第r+1行第c+1列」。解析器按优先级兼容三种写法："
                    "「第X行第Y列」、rXcY（忽略大小写）、X,Y / X-Y / X，Y（数字 1~4），全部失配记为未命中。")
    elif t.startswith("3.2 QLoRA SFT"):
        set_text(p, "3.2 QLoRA SFT：LoRA r=8、alpha=16、dropout=0.05，挂在 q/k/v/o_proj 上，可训练参数 "
                    "1,363,968 / 257,848,896 = 0.5290%；只对答案 token 计算损失（prompt 部分标签置 -100）。"
                    "指南建议 10 步，实测 10 步不收敛（loss 由 1.51 反升至 8.40、格式未学会），最终采用 60 步"
                    "（loss 收敛至 0.26~0.33），RSI 每轮再训 30 步。")
    elif t.startswith("3.3 RSI 闭环"):
        set_text(p, "3.3 RSI 闭环：①自查——定位题答错且可解析时，把预测格渲染成紫色高亮框回灌，"
                    "追问「若高亮框没有圈住目标，请直接给出正确位置」，模型自发改写记 pred2_self；"
                    "②验证器——PIL 逐像素 8 邻域连通块分析求目标包围盒，判据为「目标中心落在预测格内，或格覆盖目标 ≥50% 面积」，"
                    "不通过则把「重叠仅 X%」写入提示词重答（pred2_tool）；重答判对才连同图像、问题写入数据池"
                    "（记忆写 rsi_memory.json、数据池写 sft_data.json），下一轮在扩充后的池上再训练。")
    elif t.startswith("3.4 与参考实现不同的部分"):
        set_text(p, "3.4 与参考实现不同的部分：① transformers 5.x 移除 AutoModelForVision2Seq，改用 "
                    "AutoModelForImageTextToText 加载，processor.decode 回退到 tokenizer.decode；"
                    "② GPU 上 fp32 反传激活超出 8GB 显存，训练期间启用梯度检查点（数学等价，仅重算激活，2.34s/步）；"
                    "③ 修复参考代码缺陷：sft_step 结束后补 model.eval() 并恢复 KV cache——否则 RSI 轮内评测在 train 模式"
                    "带着 LoRA dropout 生成，输出退化为乱码（复现于 log_rsi_gpu_degenerate.txt：轮内评测 1/15，修复后 6/15）；"
                    "④ SFT 步数 10→60、RSI 每轮 10→30（本环境 10 步不收敛，详见 3.2）。")

# ---------- 四、实验结果 ----------
for p in doc.paragraphs:
    t = p.text.strip()
    if t.startswith("4.1 三阶段评测"):
        set_text(p, "4.1 三阶段评测（含 RSI 两轮，与指南表 6 一致，数据照抄程序终端输出）")
    elif t.startswith("4.3 纠错明细统计"):
        set_text(p, "4.3 纠错明细统计：SFT+纠错阶段触发 8 次（8 道 loc 全错），由错变对 1 次"
                    "（L08：第1行第4列→第4行第4列），由对变错 0 次，净增益 +1 题；"
                    "RSI 两轮纠错 7+6 次、重答后判对 0 次，新增可用样本 0 条，数据池两轮保持 15 条零增长。")
    elif t.startswith("4.4 代表性样例"):
        set_text(p, "4.4 代表性样例（自查改写在本次实验中未产生成功纠对样例，如实记录）")

# 表 2：三阶段（追加 RSI 两轮）
t2 = doc.tables[2]
t2.rows[1].cells[0].text = "基线（未微调）"
t2.rows[2].cells[0].text = "SFT（种子 60 步）"
t2.rows[3].cells[0].text = "纠错后（SFT+验证器）"
data2 = [
    ["基线（未微调）", "0/8", "4/4", "0/3", "4/15", "0.00"],
    ["SFT（种子 60 步）", "2/8", "4/4", "3/3", "9/15", "0.06"],
    ["纠错后（SFT+验证器）", "3/8", "4/4", "3/3", "10/15", "0.06"],
]
for i, row in enumerate(data2):
    for j, v in enumerate(row):
        t2.rows[i + 1].cells[j].text = v
extra2 = [
    ["RSI 第 1 轮", "2/8", "4/4", "0/3", "6/15", "0.06"],
    ["RSI 第 2 轮", "2/8", "4/4", "3/3", "9/15", "0.06"],
]
for row in extra2:
    r = t2.add_row()
    for j, v in enumerate(row):
        r.cells[j].text = v

# 表 3：RSI 轮次
t3 = doc.tables[3]
data3 = [
    ["初始（种子）", "15", "4/15", "—", "—", "—", "4/15"],
    ["第 1 轮", "15", "4/15", "0 次", "7 次", "4/15", "6/15"],
    ["第 2 轮", "15", "6/15", "4 次", "6 次", "6/15", "9/15"],
]
for i, row in enumerate(data3):
    for j, v in enumerate(row):
        t3.rows[i + 1].cells[j].text = v

# 表 4：代表性样例
t4 = doc.tables[4]
data4 = [
    ["答对", "e00·红色方形", "位于第几行第几列？", "第1行第2列第3列第4列。", "—", "正确（gold 第1行第2列）"],
    ["自查改对（未成功）", "e01·红色方形", "位于第几行第几列？",
     "A1「第1行第2列第3列。」→ 回灌改写「第1行第4列是第几行第…」", "自查", "仍错（gold 第1行第1列；4 次改写均未纠对）"],
    ["验证器纠对", "e07·黄色方形", "位于第几行第几列？",
     "A1「第1行第4列。」→ 提示「重叠仅 0%」→ A2「第4行第4列第4列。」", "验证器", "正确（gold 第4行第4列）"],
    ["仍然失败", "e02·蓝色圆形", "位于第几行第几列？",
     "「第1行第4列。第1行第4列。」（提示重答仍复读第1行第4列）", "验证器", "错误（gold 第4行第2列）"],
]
for i, row in enumerate(data4):
    for j, v in enumerate(row):
        t4.rows[i + 1].cells[j].text = v

# 插入自绘图（图 1）到 4.2 标题前
for p in doc.paragraphs:
    if p.text.strip().startswith("4.2 RSI 递归自进化轮次记录"):
        cap = insert_para_before(p)
        set_text(cap, "图 1　各阶段评测正确数与 RSI 数据池规模（实测数据）")
        imgp = insert_para_before(cap)
        run = imgp.add_run()
        run.add_picture("rsi_chart.png", width=Inches(6.3))
        break

# ---------- 五、结果分析 ----------
for p in doc.paragraphs:
    t = p.text.strip()
    if t.startswith("5.1 SFT 带来了什么"):
        set_text(p, "5.1 SFT 带来了什么：基线输出完全不可控——复读问题（「1. 在第几行第几列？Answer: 1.」）、"
                    "把问题当答案（「蓝色圆形位于第几行第几列」），loc 0/8、IoU 全 0、exist 0/3。"
                    "SFT 后全部 loc 输出落入「第X行第Y列」格式（不再复读问题），loc 0→2、IoU 0→0.06、exist 0→3 同步提升；"
                    "count 4/4 保持满分（基线即靠宽松判分「首数字对即对」拿满）。SFT 的主要贡献是「先学会格式，再谈准确率」。")
    elif t.startswith("5.2 RSI 闭环带来了什么"):
        set_text(p, "5.2 RSI 闭环带来了什么：SFT→纠错净增益 = 由错变对 1 − 由对变错 0 = +1 题（9→10/15），"
                    "且纠错只在「差一格」时有效（L08 行错列对被提示拉回）。RSI 轮 1→轮 2 从 6/15 升到 9/15，"
                    "但两轮数据池均零增长——提升完全来自轮内再训练（累计 60 步，与种子 SFT 60 步的 9/15 持平），"
                    "「新样本回流 → 重训」的增益为 0：验证器纠错后的重答从未判对，无样本可入池。")
    elif t.startswith("5.3 失败模式分析"):
        set_text(p, "5.3 失败模式分析：①复读坍缩——256M 模型把定位学成「背高频答案」，错题答案集中在训练集高频的"
                    "「第1行第2列」「第1行第4列」（轮 2 六次提示重答全部复读「第1行第4列」）；"
                    "②相邻格/行列混淆——L04（gold 第2行第2列）预测第1行第2列（行差 1），L08（gold 第4行第4列）"
                    "预测第1行第4列（行错列对）；③验证器边界——输出不可解析时代码默认 (0,0) 格，"
                    "若目标恰在该格会误判「通过」而不触发纠错（轮 1 的 L02 即此情形），提示「重叠仅 X%」对复读型小模型收效甚微。")
    elif t.startswith("5.4 回答核心问题"):
        set_text(p, "5.4 回答核心问题：提升主要来自微调（SFT）。证据链：基线 4/15 → SFT 9/15（+5，格式可控与 exist 满分"
                    "全由 SFT 取得）；纠错仅 +1，且依赖 SFT 先学会格式——基线阶段同样的纠错 4→4 无效；"
                    "RSI 轮 2 回到 9/15 与 SFT 持平、数据池零增长。两者的作用边界：参数更新决定「会不会答题」，"
                    "工具纠错只能在「会答但差一点」时兜底，无法把不会答的模型教会。")

# ---------- 六、思考题 ----------
answers = {
    "思考题 1（网格粒度）": "答：8×8 把输出空间从 16 类扩到 64 类，随机命中率从 1/16 降到 1/64。loc 正确率会先降"
        "（本实验 256M 模型 60 步才学会 16 类格式，同等预算下 64 类更难学），但命中后 IoU 上限大幅提高"
        "（4×4 的 64×64 格框对 ~40px 目标最多 IoU≈0.18，这正是本实验 IoU 偏低的主因）。"
        "代价：种子数据与训练步数约需按 4 倍增加，解析正则需放宽到 1~8，「中心落格」判据对跨格目标更敏感，推理时间同步膨胀。",
    "思考题 2（验证器边界）": "答：两种典型情况。①解析错位：模型输出不可解析时参考代码默认 (0,0) 格——轮 1 的 L02 "
        "目标恰好在第1行第1列，验证器误判「通过」而未触发纠错，机制上存在「由错判对」的假反馈风险"
        "（本例答案本就错，未造成实际污染）；②无效提示：轮 2 六次提示重答全部复读同一错误格，"
        "验证器反复给出「重叠仅 0%/38%」只消耗推理时间。",
    "思考题 3（RSI 与 SFT 关系）": "答：种子数据的真值来自绘制时的几何信息、纠错样本由模型自产且经验证器把关，"
        "都不需要人工标注或外部教师，边际成本几乎只剩推理时间——这就是「变贵之前免费的教师」。不再免费的情况："
        "①验证器出现假阳性（颜色阈值、跨格边界），坏样本入池并被后续轮次放大；"
        "②纠错样本高度同质、池分布过窄，训练增益递减；③推理成本规模化（每条样本 2~3 次生成，CPU 上分钟级），随轮数线性增长。",
    "思考题 4（迁移）": "答：ChartQA 数值题的验证器应输出「可核查的证据」而非答案：①用 OCR/表格解析抽取数据点，"
        "把模型读数与抽取值做误差带比较（如 ±5% 或最近刻度）；②校验结构性质（最大值是否真的最高、折线单调性等）；"
        "③提示给证据（如「该柱抽取值约 4.2，不是 7」）让模型重答；④可保留可视化回灌（高亮目标柱、画参考线）。"
        "闭环成立的前提与本实验相同：验证器必须比模型可靠，否则错误反馈会经数据池反噬模型。",
}
paras = list(doc.paragraphs)
for i, p in enumerate(paras):
    t = p.text.strip()
    if t.startswith("思考题"):
        cur = t.split("（")[0]  # 如「思考题 1」
        ans = next((v for k, v in answers.items() if k.startswith(cur)), None)
        if ans is not None and i + 1 < len(paras) and paras[i + 1].text.strip().startswith("答："):
            set_text(paras[i + 1], ans)

# ---------- 七、结论与反思 ----------
for p in doc.paragraphs:
    if p.text.strip().startswith("「值不值」"):
        set_text(p, "「值不值」：在 256M 小模型上，SFT 值得（4/15→9/15，格式可控性完全建立，exist 0→3/3）；"
                    "RSI 闭环作为「护栏」有边际价值（+1 题），但作为「数据引擎」在本实验设置下失败——两轮零新增。"
                    "最主要的局限：①256M 容量天花板，定位被学成「背高频答案」，纠错重答无济于事；"
                    "②解析式验证器只在纯色合成图上成立，且存在「不可解析默认 (0,0)」的边界缺陷；"
                    "③4×4 网格离散化误差封顶 IoU（最高 0.18）；④种子数据即评测题本身，60 步的「学会」有背题之嫌——"
                    "RSI 本可注入独立新样本稀释这一点，但并未发生。若继续做：用 40 张训练图造种子数据解耦训练/评测、"
                    "换 8×8 网格并按 4 倍扩种子、给验证器加「不可解析即不通过」规则，再跑 3~5 轮观察数据池增长能否真正启动。")
        break

doc.save(DST)
print(f"saved -> {DST}")
