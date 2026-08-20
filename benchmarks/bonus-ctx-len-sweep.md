# Bonus - Context-length sweep (prefill cost)

Host `Windows-AMD64` · llama.cpp `b10488` ·
`threads=6` `ngl=99` · RAM 15.7 GB

| Prompt tokens | Prefill (tok/s) | TTFT contribution (ms) | vs linear scaling |
|:--|--:|--:|--:|
| 256 | 1284.2 | 199.4 | 1.00x |
| 1024 | 2370.5 | 432.0 | 0.54x |
| 2048 | 2710.6 | 755.5 | 0.47x |
| 4096 | 2748.4 | 1490.3 | 0.47x |
| 8192 | 2657.2 | 3082.9 | 0.48x |

At 8192 tokens, prefill costs **3083 ms**, which is
**0.48x** linear scaling -- so on this hardware, over this range, prefill is
still growing **roughly linearly**, not quadratically.

That is the correct finding, not a failed experiment. Attention is O(N^2), but it is only
one term: the per-layer linear projections and MLP are O(N), and on a 2B-class model at
short prompts they dominate. The quadratic term only overtakes them once N gets large
enough. Your prefill cost is currently bounded by throughput, not by sequence length.

To find where it *does* bend, extend the grid:

```bash
python bonus/sweeps/ctx-len-sweep.py --grid 1024,4096,8192,16384,32768
```

Watch the "vs linear" column: the first row that climbs meaningfully above 1.0 is where
attention starts to matter on your machine. Report that crossover point.

Either way, this is the number to remember when someone proposes stuffing more retrieved
context into a RAG prompt "because the context window allows it". Prefill is paid in full,
on every request, before the first token appears.

## Your finding

On my RTX 3050 GPU (CUDA offload `ngl=99`), prefill latency scales near-linearly from 199.4 ms at 256 tokens to 3,082.9 ms at 8,192 tokens. The "vs linear scaling" ratio remains flat at ~0.47x–0.48x across 1,024 to 8,192 tokens, showing that matrix multiplications and MLP projections O(N) dominate compute over this sequence range rather than attention O(N^2). 

At 8,192 tokens, paying 3.08 seconds in prefill latency consumes over 50% of a typical 6-second SLO target before decoding a single output token. This demonstrates that even when context windows support 8k+ tokens, RAG pipelines should strictly cap retrieved context chunks (e.g. to <=2k tokens, ~755 ms prefill) to preserve low TTFT.
