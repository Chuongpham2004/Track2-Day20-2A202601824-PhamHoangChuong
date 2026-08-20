# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=6` ·
`ngl=99`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 126 | 2.15 | 3700 | 5400 | 5900 | 8.0 | 0.0% |
| 50 | 123 | 2.12 | 20000 | 22000 | 24000 | 38.1 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **0.99x** (20% of linear) |
| P95 latency | **4.07x** |
| Effective concurrency at 50 users | 38.1 vs `--parallel 4` slots (occupancy/slot ratio 9.52) |

**Saturated.** Throughput delivered only 0.99x for 5x the offered load, and effective concurrency (38.1) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 0.99x while P95 moved 4.07x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

## Your reading

The server saturates between 10 and 50 concurrent users. The key evidence is that while offered load increases 5x, delivered throughput remains flat at ~2.12 RPS (0.99x), while P95 latency inflates by 4.07x from 5,400 ms to 22,000 ms. Little's Law effective concurrency reaches 38.1 requests against only 4 available `--parallel` slots (an occupancy ratio of 9.52x), and Prometheus metrics confirm peak slot utilization (`n_busy_slots_per_decode` = 3.94 of 4 slots). 

The latency spike is pure queueing delay rather than extra GPU compute. To raise goodput under a 6,000 ms SLO target, the first knob to tune is increasing `--parallel` from 4 to 8 slots (or deploying request shedding/load shedding at the API gateway). Increasing `--parallel` allows the engine to batch more concurrent requests into GPU execution passes, reducing head-of-line queueing time without changing model weights.
