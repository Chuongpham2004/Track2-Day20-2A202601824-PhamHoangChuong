# 01 - Measure: latency baseline

Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=6` `ngl=99` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 4032 | 241 / 383 | 13.1 / 13.4 | 1071 / 1207 / 1207 | 76.5 |
| UD-Q2_K_XL | 2.24 | 4278 | 246 / 466 | 13.4 / 14.0 | 1108 / 1336 / 1336 | 74.7 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.02x SLOWER** than `UD-Q4_K_XL` here, despite being 0.73 GB smaller. That is a real result, not a mistake: fewer bits only buys speed when decode is limited by memory bandwidth. On a machine that is compute-limited instead — few cores, no GPU offload — the extra dequantization work of a heavily-quantized format can cost more than the bytes it saves. Say which case yours is.

## Your observation

On my machine (RTX 3050 Laptop GPU 4GB), UD-Q2_K_XL saves ~0.73 GB VRAM/disk (2.24 GB vs 2.97 GB), but decodes slightly slower (~74.7 tok/s vs 76.5 tok/s) and has slightly higher TTFT P95 (466 ms vs 383 ms) due to extra dequantization overhead on CUDA kernels. Because GPU VRAM bandwidth on the RTX 3050 is sufficient for 4-bit weights, UD-Q4_K_XL provides both superior reasoning quality and slightly faster decode speed, making UD-Q4_K_XL the clear recommended choice.
