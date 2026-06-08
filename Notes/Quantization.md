# 🧩 LLM Quantization?

LLM quantization is a technique used to make large language models smaller and faster by reducing the precision of the numbers they use.

Normally, models store weights in:

- FP32 (32-bit floating point) → very accurate, but large and slow
- FP16 (16-bit floating point) → smaller and faster

Quantization reduces this further to:

- INT8 (8-bit integers)
- INT4 (4-bit integers)


## NF4 (Normal Float 4-bit)

It is is a special 4-bit data format used in LLM quantization. In regular INT4 it divides numbers evenly but in NF4 it Places more precision where weights are dense.

- Optimized for normally distributed weights
- Places more precision where weights are dense