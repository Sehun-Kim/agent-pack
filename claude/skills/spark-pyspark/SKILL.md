---
name: spark-pyspark
description: Work safely on Spark/PySpark jobs (driver OOM safety + performance checklist).
---

## Safety defaults
- Avoid `collect()` / `toPandas()` on large DataFrames.
- For exploration: use `sample()` / `limit()`; inspect schema/plan first.
- Be cautious with `show()` on large DataFrames (use `limit`).

## Performance checklist
- Check for shuffle, skew, and partition counts.
- Prefer built-in functions over Python UDFs.
- Cache/persist only when reused and expensive to recompute.
- Consider broadcast joins when one side is small enough.

## Notebooks
- Keep notebooks for orchestration/exploration/visualization.
- Move reusable transformations into versioned `.py` modules.
