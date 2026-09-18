#!/usr/bin/env python3
"""Plot descriptive Bench27 outcomes from the validated snapshot; no model calls.

Run after installing requirements-figures.txt. The plot is not a process-score
heatmap, an uncertainty estimate, or a same-scaffold frontier comparison.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ais3_bench.report import artifacts
from ais3_bench.data import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/figures')
    args = parser.parse_args()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    summary = json.loads(artifacts()['summary.json'])
    models = sorted(summary['models'], key=lambda m: (-m['solved_tasks'], m['model']))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'svg.hashsalt': 'ais3-bench27-outcomes-v1',
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.spines.left': False, 'axes.edgecolor': '#d4dbe3',
                         'axes.labelcolor': '#3c4b5c', 'text.color': '#152a3c',
                         'xtick.color': '#4c5b6b', 'ytick.color': '#152a3c'})
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.9), gridspec_kw={'width_ratios': [1, 1.6]})
    fig.subplots_adjust(left=0.225, right=0.965, top=0.77, bottom=0.235, wspace=0.36)
    fig.suptitle('Bench27 | Final outcomes, two different denominators',
                 x=0.02, y=0.97, ha='left', fontsize=20, fontweight='bold')
    fig.text(0.02, 0.884, '27 tasks  /  6 evaluated model labels  /  803 retained attempts',
             fontsize=11, color='#526477')
    fig.text(0.02, 0.833, 'Historical project labels; exact provider revisions are unresolved.',
             fontsize=9, color='#526477')
    y = list(range(len(models)))
    ax = axes[0]
    ax.barh(y, [m['solved_tasks'] for m in models], color='#244866', height=0.46)
    ax.set_yticks(y, [m['model_full'] for m in models], fontsize=9)
    ax.invert_yaxis()
    ax.set_ylim(len(models)-0.45, -0.65)
    ax.set_xlim(0, 27)
    ax.set_xticks([0, 9, 18, 27])
    ax.set_xlabel('Tasks solved at least once / 27', labelpad=12)
    ax.set_title('A  Observed task coverage', loc='left', fontsize=12, pad=15, fontweight='bold')
    ax.tick_params(axis='y', length=0, pad=12)
    ax.grid(axis='x', color='#e7ecf0', linewidth=0.7)
    ax.set_axisbelow(True)
    for i, m in enumerate(models):
        ax.text(m['solved_tasks'] + 0.6, i, f"{m['solved_tasks']}/27", va='center', fontsize=10)
    ax = axes[1]
    old_color, new_color = '#244866', '#148578'
    for i, m in enumerate(models):
        old, new = m['arms']['contaminated'], m['arms']['recent2026']
        o, n = old['accuracy'] * 100, new['accuracy'] * 100
        ax.plot([n, o], [i, i], color='#c5d0d8', linewidth=2, zorder=1)
        ax.scatter([o], [i], color=old_color, s=65, label='Older public tasks' if i == 0 else None, zorder=3)
        ax.scatter([n], [i], color=new_color, s=65, marker='D', label='2026 tasks' if i == 0 else None, zorder=3)
        ax.annotate(f"{old['solved']}/{old['valid_attempts']}", (o, i), xytext=(0, 12),
                    textcoords='offset points', ha='center', color=old_color, fontsize=9)
        ax.annotate(f"{new['solved']}/{new['valid_attempts']}", (n, i), xytext=(0, -17),
                    textcoords='offset points', ha='center', color=new_color, fontsize=9)
    ax.set_xlim(-3, 70)
    ax.set_xticks([0, 20, 40, 60], ['0%', '20%', '40%', '60%'])
    ax.set_yticks(y, [])
    ax.set_ylim(len(models)-0.45, -0.65)
    ax.set_xlabel('Successful attempts / valid attempts in each cohort', labelpad=12)
    ax.set_title('B  Per-attempt cohort accuracy', loc='left', fontsize=12, pad=15, fontweight='bold')
    ax.tick_params(axis='y', length=0)
    ax.grid(axis='x', color='#e7ecf0', linewidth=0.7)
    ax.set_axisbelow(True)
    ax.legend(loc='upper left', bbox_to_anchor=(0, -0.18), ncol=2, frameon=False, fontsize=9)
    fig.text(0.02, 0.085, 'A: up to five valid attempts per task; not single-attempt accuracy.  '
             'B: 12 tasks per cohort; difficult case studies excluded.', fontsize=9, color='#526477')
    fig.text(0.02, 0.044, 'Descriptive comparison: task composition and scorers differ. '
             'No causal contamination inference. Frontier excluded because its scaffold differs.', fontsize=9, color='#526477')
    args.output.mkdir(parents=True, exist_ok=True)
    provenance = 'Generated from validated Bench27 snapshot; SHA-256 ' + summary['sources_sha256']['ctf/bench27/bench27_runs.json']
    fig.savefig(args.output / 'outcomes.svg', metadata={'Date': None, 'Description': provenance})
    svg = args.output / 'outcomes.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    fig.savefig(args.output / 'outcomes.png', dpi=180, metadata={'Description': provenance})
    plt.close(fig)
    (args.output / 'inputs.json').write_text(json.dumps({
        'description': 'Plot input fingerprint; scientific interpretation is described in figures/README.md.',
        'summary_sha256': hashlib.sha256(artifacts()['summary.json'].encode()).hexdigest(),
        'matplotlib': matplotlib.__version__,
        'models_in_plot_order': [m['model'] for m in models],
        'source_sha256': summary['sources_sha256'],
    }, indent=2) + '\n')
    print('Wrote outcomes.svg, outcomes.png and inputs.json to', args.output)


if __name__ == '__main__':
    main()
