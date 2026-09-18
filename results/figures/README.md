# Outcome overview / 結果總覽圖

![Bench27 descriptive outcome comparison](outcomes.png)

[Vector SVG](outcomes.svg) · [Input fingerprint](inputs.json) · [Numerical tables](../README.md)

Panel A counts tasks solved at least once among available repetitions (up to five). Panel B plots attempt-level accuracy on the 12 older and 12 recent tasks, with successful/valid attempt denominators printed next to each point. The three difficult case studies are included in A but excluded from B. The frontier is excluded because it uses a different scaffold.

This is a descriptive figure: no confidence intervals, hypothesis tests, causal contamination claims or process-score estimates are implied. Model names retain historical gateway labels. The inputs are validated against the same snapshot as the generated result tables.

左圖是最多五次有效嘗試中至少一次解出的題數；右圖是各分區的逐次成功率，點旁標出分子／分母。三題困難案例計入左圖，不計入新舊題比較。Frontier 因 scaffold 不同而不列入。此圖不表示信賴區間、因果推論或步驟覆蓋率。

Regenerate / 重建：

```bash
python -m pip install -r requirements-figures.txt
python scripts/plot_results.py
```

Matplotlib is optional and is not required for offline result validation. SVG is suitable for inclusion in research documents; PNG is used for repository previews.
