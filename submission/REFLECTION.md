# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.

**Họ Tên:** Phạm Hoàng Chương  
**Cohort:** Track2 - A20  
**Ngày submit:** 2026-08-20  

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** Windows 11 (AMD64)
- **CPU:** 11th Gen Intel(R) Core(TM) i5-11400H @ 2.70GHz
- **Cores:** 6 physical / 12 logical
- **CPU extensions:** AVX2 / FMA / F16C / SSE4.2
- **RAM:** 15.7 GB
- **Accelerator:** NVIDIA GeForce RTX 3050 Laptop GPU, 4096 MiB (CUDA 12.4)
- **llama.cpp asset đã tải:** `llama-b10488-bin-win-cuda-12.4-x64.zip`
- **Model đã dùng:** Gemma 4 E2B (`LAB_MODEL=gemma4-e2b`)
- **Quantization:** `gemma-4-E2B-it-UD-Q4_K_XL.gguf` (primary) + `gemma-4-E2B-it-UD-Q2_K_XL.gguf` (compare)

**Chạy ở đâu:** laptop của tôi

**Setup story** (≤ 80 chữ): Thực thi script `lab.ps1` với PowerShell trên Windows 11, thiết lập môi trường `PYTHONUTF8=1` để xử lý chuẩn mã hóa Unicode console. Hệ thống tự động cài đặt virtualenv, nhận diện GPU NVIDIA RTX 3050 và tải prebuilt release `llama.cpp` CUDA 12.4 binary cùng các DLLs runtime mà không cần compile.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 5864 | 239 / 504 | 13.4 / 15.2 | 1061 / 1360 / 1360 | 74.5 |
| UD-Q2_K_XL | 2.24 | 4271 | 237 / 344 | 13.2 / 13.5 | 1061 / 1164 / 1164 | 75.9 |

**Quan sát** (≤ 60 chữ): Bản 2-bit giúp tiết kiệm ~0.73 GB VRAM và load nhanh hơn ~1.6s, tốc độ decode gần như tương đương (~75.9 vs 74.5 tok/s). Tuy nhiên, bản 4-bit (UD-Q4_K_XL) cho chất lượng lập luận và câu trả lời mạch lạc hơn rõ rệt mà không tốn thêm chi phí tốc độ trên GPU RTX 3050, do đó UD-Q4_K_XL rất đáng dùng.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 2.15 | 3700 | 5400 | 5900 | 8.0 | 0.0% |
| 50 | 2.12 | 20000 | 22000 | 24000 | 38.1 | 0.0% |

- **Offered load tăng 5×, throughput thực tăng:** `0.99×`
- **P95 tăng:** `4.07×`
- **Effective concurrency ở 50 users:** `38.1` so với `--parallel` = `4` slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang chạy): `3.94` / `4` slots

**Saturation reading** (≤ 80 chữ): Server bão hòa ở mức 50 users khi throughput giữ nguyên ~2.12 RPS nhưng P95 phồng 4.07× lên 22,000 ms. Phần latency tăng thêm hoàn toàn là queue time do Effective Concurrency (38.1) vượt xa 4 slots. Để tăng goodput@SLO (6s), tôi sẽ điều chỉnh nâng `--parallel` từ 4 lên 8 slots trước tiên để tối ưu khả năng batching trên GPU.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | Cloud Infrastructure | stub |
| N17 Data pipeline | Data Ingestion | stub |
| N18 Lakehouse | Storage/Lakehouse | stub |
| N19 Vector + features | Keyword overlap retrieval | stub |
| N20 Serving | `llama-server` | real |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: `0.0 ms`
- retrieve: `0.1 ms`
- llm: `2920.5 ms`
- **stage chiếm nhiều nhất:** `llm` (`100.0%` của total)

**Reflection** (≤ 60 chữ): Bottleneck nằm 100% ở stage `llm` do tính toán suy luận transformer. Kết quả đúng như kỳ vọng vì tìm kiếm từ khóa nhẹ hơn rất nhiều so với prefill/decode. Để giảm 2× latency pipeline, tôi sẽ tấn công vào stage `llm` bằng cách thu gọn context prompt và áp dụng quantization UD-Q2_K_XL.

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** Điều chỉnh số lượng CPU threads (-t) từ 1 up to 12 matching logical cores trên CPU Intel i5-11400H (`ngl=99` GPU RTX 3050 offload).

```
before:  77.6 tok/s (-t 1)
after:   80.4 tok/s (-t 12)
speedup: 1.04×
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

Đường cong hiệu năng theo số thread rất phẳng (từ 77.6 tok/s lên 80.4 tok/s, mức chênh lệch 1.04×) là vì thông số `ngl=99` đã đẩy toàn bộ các lớp của model Gemma 4 E2B lên GPU NVIDIA GeForce RTX 3050 Laptop. 

Khi các phép nhân ma trận trọng số và KV cache attention được thực thi trực tiếp trên băng thông VRAM của GPU, các CPU threads không nằm trên luồng tính toán tới hạn (critical path) của quá trình decode. CPU threads chỉ đóng vai trò phân tích prompt, khởi chạy CUDA kernel launch calls và gửi HTTP response. Do đó, nâng số thread từ 1 lên 12 (khớp với số cores logic) giúp giảm bớt latency điều phối lệnh (dispatch overhead) mang lại speedup nhỏ 1.04×, đồng thời không bị giảm hiệu năng do context switching tại 24 threads vì GPU chịu trách nhiệm xử lý phần lớn công việc tính toán.

---

## 6. Bonus  *(optional — tối đa 20 điểm)*

> Bỏ trống nếu không làm. Xem `bonus/README.md`. Đừng làm hết — **một** finding sâu
> ăn điểm hơn năm bảng nông.

**Đã làm:** 

**Numbers:**

```
before:  
after:   
speedup: 
```

**Điều này nói lên gì mà deck chưa nói:**

_(để trống nếu bạn không làm phần này)_

---

## 7. Điều làm bạn ngạc nhiên nhất  *(optional)*

Tốc độ suy luận của model Gemma 4 E2B trên GPU laptop RTX 3050 đạt hơn 75-80 tok/s nhờ prebuilt `llama.cpp` CUDA binary. Đồng thời cơ chế Continuous Batching hoạt động cực kỳ mượt mà khi ghép tải 50 người dùng đồng thời đạt đỉnh slot utilization 3.94/4.

---

## 8. Self-check trước khi push

- [x] `hardware.json` committed
- [x] `models/active.json` committed
- [x] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [x] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [x] `benchmarks/02-server-results.md` committed (`make load-report`)
- [x] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [x] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md` đã được thay bằng nhận xét của bạn
- [x] 5 screenshots trong `submission/screenshots/`
- [x] `make verify` → **exit 0**
- [x] Repo GitHub ở chế độ **public**
- [x] Đã paste public URL vào VinUni LMS
- [x] **Không** commit `models/*.gguf` hay `runtime/` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không xem được → 0 điểm.
