# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.1 | 3092.3 | 3092.4 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.1 | 2876.0 | 2876.2 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.1 | 2793.3 | 2793.4 |

Mean per stage (ms): embed **0.0** · retrieve **0.1** ·
llm **2920.5** · total **2920.7**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.

**What problem does PagedAttention actually solve?**

> PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.


## Which N16-N19 pieces are real

- N16 Cloud/IaC: Stub
- N17 Data pipeline: Stub
- N18 Lakehouse: Stub
- N19 Vector + features: Stub (Keyword overlap retrieval fallback)
- N20 Model Serving: **Real** (`llama-server` on port 8080)

The LLM generation stage (`llm`) is the overwhelming dominant bottleneck, consuming 2,920.5 ms out of 2,920.7 ms total latency (100.0% of total pipeline latency). The retrieval stage (`retrieve`) takes only 0.1 ms. This matches expectations because TF-IDF/keyword overlap search over local context docs is computationally trivial, whereas LLM prefill and token decoding require intensive transformer matrix operations.

To halve this pipeline's end-to-end latency by 2x, I would attack the **LLM stage**:
1. Enable speculative decoding or lower precision quantization (e.g. UD-Q2_K_XL).
2. Reduce prompt context size (`--ctx-size`) or prune retrieved contexts to minimize prefill computation.
3. Optimize decoding batch parameters (`--parallel`) on the serving engine.
