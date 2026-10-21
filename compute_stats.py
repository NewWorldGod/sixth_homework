# -*- coding: utf-8 -*-
"""从 log_eval_gpu.txt 解析「SFT+纠错」阶段的 A2 答案，计算定位平均 IoU 与纠错统计"""
import re
import hw6_rsi_localize as hw

gt = hw.load_gt()
questions = {q["id"]: q for q in hw.build_questions(gt) if q["type"] == "loc"}

a2_map = {}
for line in open("log_eval_gpu.txt", encoding="utf-8"):
    m = re.match(r"\[(L\d+).loc\] (.) A1: (.*?) . A2: (.*?) \| gold", line)
    if m:
        a2_map[m.group(1)] = {"mark": m.group(2), "a2": m.group(4)}

ious = []
print("纠错后各 loc 题解析结果：")
for lid in sorted(a2_map):
    q = questions.get(lid)
    if q is None:
        continue
    i = hw.loc_iou(q, a2_map[lid]["a2"])
    ious.append(i)
    c = hw.parse_cell(a2_map[lid]["a2"])
    print(f"[{lid}] {'√' if a2_map[lid]['mark']=='√' else '×'} A2={a2_map[lid]['a2'][:30]!r} "
          f"cell={c} gold={tuple(q['cell'])} IoU={i:.3f}")
print(f"\n纠错后定位平均 IoU = {sum(ious)/len(ious):.3f}")
