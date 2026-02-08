---
name: pyspark-optimize
description: Diagnose and optimize PySpark jobs safely (shuffle, skew, caching, joins).
---
Steps:
1) Gather context: dataset sizes, partitions, join keys, symptoms (OOM, slow stage).
2) Identify likely bottlenecks: shuffle, skew, wide transformations, UDFs.
3) Propose safe experiments: sample/limit first, then validate on full run.
4) Recommend optimizations with reasoning:
   - broadcast joins (when safe)
   - repartition/coalesce strategy
   - skew mitigation
   - replace UDFs with built-ins
   - caching only when reused
5) Provide a verification plan (Spark UI metrics to check).