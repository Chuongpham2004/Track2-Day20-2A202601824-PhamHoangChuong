# 02 - Continuous batching under load (u50)

Host `Windows-AMD64` · `--parallel 4` · 14 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.94 of 4 slots (99%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | 0.00 |
| `tokens_predicted_total` (final) | 13745 |

Highest sampled value was **3.94 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Your observation

The peak sampled average batch width was 3.94 of 4 slots (99% slot utilization), while `requests_deferred` peaked at 46 queued requests. This confirms that continuous batching was actively packing concurrent requests into shared decode steps under load. 

The peak batch width (3.94 slots) represents actual hardware execution concurrency bounded by `--parallel 4`, whereas Little's Law effective concurrency (38.1) in `02-server-results.md` counts total requests in flight (active decode slots + queued requests). I trust `n_busy_slots_per_decode` from Prometheus for physical GPU execution saturation (confirming slots are 99% full), and Little's Law for queueing pressure (showing ~34 requests waiting in queue).
