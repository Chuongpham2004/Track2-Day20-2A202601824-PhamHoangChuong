# 01 - Measure: latency baseline

Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=6` `ngl=99` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 5864 | 239 / 504 | 13.4 / 15.2 | 1061 / 1360 / 1360 | 74.5 |
| UD-Q2_K_XL | 2.24 | 4271 | 237 / 344 | 13.2 / 13.5 | 1061 / 1164 / 1164 | 75.9 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` and `UD-Q4_K_XL` decode within 2% of each other here, for 0.73 GB difference on disk.

## Your observation

On my machine (RTX 3050 Laptop GPU 4GB), UD-Q2_K_XL saves ~0.73 GB VRAM/disk (2.24 GB vs 2.97 GB) and loads ~1.6s faster (4271 ms vs 5864 ms). Decode speed (TPOT P50 ~13.2 ms vs 13.4 ms, ~75.9 vs 74.5 tok/s) and TTFT P50 (~237 ms vs 239 ms) are nearly identical because GPU memory bandwidth on the RTX 3050 is sufficient for both weights. However, UD-Q4_K_XL offers noticeably better response quality and coherence without sacrificing speed, making UD-Q4_K_XL the superior choice for general inference on this GPU.
