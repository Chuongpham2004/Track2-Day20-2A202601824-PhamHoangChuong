# 01 - Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **6 physical · 12 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 77.6 | 97% |
| 3 | 80.2 | 100% |
| 6 | 79.2 | 99% |
| 12 | 80.4 | 100% |
| 24 | 79.6 | 99% |

**Best**: `-t 12` at 80.4 tok/s
**Slowest tested**: `-t 1` at 77.6 tok/s (1.04x spread)
**Against the physical-core default** (`-t 6`, 79.2 tok/s): 1.01x

Use this in your run:

```bash
LAB_N_THREADS=12 make bench
```

## Your explanation

The thread sweep produces a remarkably flat throughput curve ranging from 77.6 tok/s (-t 1) to 80.4 tok/s (-t 12), representing only a 1.04x speedup spread. The reason for this flat behavior is that `ngl=99` fully offloads all model layers to the CUDA GPU (NVIDIA GeForce RTX 3050 Laptop GPU). 

Because matrix multiplications and KV cache attention kernels execute entirely on the GPU VRAM bandwidth, CPU threads are not on the critical path for token generation. CPU threads only handle lightweight prompt tokenization, CUDA kernel invocation launch overhead, and HTTP response handling. As a result, increasing threads from 1 to 12 provides a minor ~3.6% reduction in CPU dispatch latency, but does not suffer from thread context switching contention at 24 threads because the GPU handles the compute heavy lifting. Setting `-t 12` matching logical cores provides the peak 80.4 tok/s.
