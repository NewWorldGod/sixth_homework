# -*- coding: utf-8 -*-
"""绘制实验报告图表：各阶段正确率折线 + RSI 数据池规模增长（据实运行数据）"""
import matplotlib
import matplotlib.pyplot as plt

def setup_cjk():
    names = ['Microsoft YaHei', 'SimHei', 'SimSun']
    avail = [f.name for f in matplotlib.font_manager.fontManager.ttflist]
    for n in names:
        if n in avail:
            plt.rcParams['font.sans-serif'] = [n] + plt.rcParams['font.sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            return n

setup_cjk()

# —— 实测数据（log_eval_gpu.txt / log_rsi_gpu2.txt）——
stages = ['基线', 'SFT\n(60步)', 'SFT+\n纠错', 'RSI\n轮1', 'RSI\n轮2']
loc_acc = [0, 2, 3, 2, 2]        # loc 正确题数 / 8
exist_acc = [0, 3, 3, 0, 3]      # exist 正确题数 / 3
total_acc = [4, 9, 10, 6, 9]     # 总正确题数 / 15
pool_size = [15, 15, 15, 15, 15] # RSI 数据池规模（种子→轮1→轮2）

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

ax = axes[0]
x = range(len(stages))
ax.plot(x, total_acc, marker='o', color='#2b6cb0', linewidth=2, label='总正确数（/15）')
ax.plot(x, loc_acc, marker='s', color='#c05621', linewidth=2, label='loc 正确数（/8）')
ax.plot(x, exist_acc, marker='^', color='#38a169', linewidth=2, label='exist 正确数（/3）')
for i, (t, l) in enumerate(zip(total_acc, loc_acc)):
    ax.text(i, t + 0.35, str(t), ha='center', fontsize=9, color='#2b6cb0')
    ax.text(i, l - 0.75, str(l), ha='center', fontsize=9, color='#c05621')
ax.set_xticks(list(x)); ax.set_xticklabels(stages, fontsize=9)
ax.set_ylim(-1.5, 13); ax.set_ylabel('正确题数')
ax.set_title('各阶段评测正确数（15 题）')
ax.legend(fontsize=8, loc='upper left')
ax.grid(axis='y', alpha=0.3)

ax = axes[1]
rounds = ['初始（种子）', '第1轮', '第2轮']
ax.plot(rounds, pool_size[:1] + pool_size[3:], marker='o', color='#805ad5', linewidth=2)
for i, v in enumerate(pool_size[:1] + pool_size[3:]):
    ax.text(i, v + 0.25, str(v), ha='center', fontsize=9)
ax.set_ylabel('数据池样本数')
ax.set_title('RSI 数据池规模（两轮零增长）')
ax.set_ylim(10, 18)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('rsi_chart.png', dpi=150)
print('chart saved -> rsi_chart.png')
