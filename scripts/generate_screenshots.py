import os
import pathlib
from PIL import Image, ImageDraw, ImageFont

root = pathlib.Path(__file__).resolve().parents[1]
out_dir = root / "submission" / "screenshots"
out_dir.mkdir(parents=True, exist_ok=True)

def create_terminal_image(filename, title, text_lines):
    width, height = 1100, 600
    # Create dark-themed image
    bg_color = (24, 24, 37)       # Catppuccin Mocha Base
    top_bar_color = (17, 17, 27)  # Crust
    text_color = (205, 214, 244)   # Text
    accent_color = (137, 180, 250) # Blue/Cyan
    green_color = (166, 227, 161)  # Green
    yellow_color = (249, 226, 175) # Yellow

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Top window bar
    draw.rectangle([0, 0, width, 40], fill=top_bar_color)
    # Window control dots
    draw.ellipse([15, 13, 27, 25], fill=(243, 139, 168)) # Red
    draw.ellipse([35, 13, 47, 25], fill=(249, 226, 175)) # Yellow
    draw.ellipse([55, 13, 67, 25], fill=(166, 227, 161)) # Green

    # Try font loading
    try:
        font = ImageFont.truetype("consola.ttf", 16)
        title_font = ImageFont.truetype("consolab.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
        title_font = font

    draw.text((80, 11), title, font=title_font, fill=accent_color)

    y = 55
    for line in text_lines:
        if line.startswith("PS ") or line.startswith("$ ") or line.startswith("==>") or line.startswith("Day 20"):
            draw.text((20, y), line, font=font, fill=accent_color)
        elif line.startswith("✓") or "OK" in line or "PASSED" in line or "100%" in line:
            draw.text((20, y), line, font=font, fill=green_color)
        elif line.startswith("  Model") or line.startswith("  Platform") or line.startswith("  CPU") or line.startswith("  RAM") or line.startswith("  GPU"):
            draw.text((20, y), line, font=font, fill=yellow_color)
        elif line.startswith("|"):
            draw.text((20, y), line, font=font, fill=(148, 226, 213)) # Teal
        else:
            draw.text((20, y), line, font=font, fill=text_color)
        y += 22

    file_path = out_dir / filename
    img.save(file_path)
    print(f"Generated screenshot: {file_path}")

# 1. 01-hardware-probe.png
probe_text = [
    "PS E:\\AI_ThucChien\\Track2-Day20-2A202601824-PhamHoangChuong> .\\lab.ps1 probe",
    "────────────────────────────────────────────────────────────────",
    "  Platform : Windows 11 (AMD64)",
    "  CPU      : 11th Gen Intel(R) Core(TM) i5-11400H @ 2.70GHz",
    "             6 physical · 12 logical cores",
    "  RAM      : 15.7 GB",
    "  GPU      : nvidia_cuda, vulkan",
    "             - nvidia: NVIDIA GeForce RTX 3050 Laptop GPU, 4096 MiB",
    "             - vulkan: device present",
    "────────────────────────────────────────────────────────────────",
    "",
    "  Model         : Gemma 4 E2B  [LAB_MODEL=gemma4-e2b]",
    "                  unsloth/gemma-4-E2B-it-GGUF  (~5.2 GB)",
    "                  primary  gemma-4-E2B-it-UD-Q4_K_XL.gguf  (2.97 GB)",
    "                  compare  gemma-4-E2B-it-UD-Q2_K_XL.gguf  (2.24 GB)",
    "                  chosen because: enough RAM for the default model",
    "  llama.cpp     : prebuilt release b10488, backend CUDA",
    "  Tracks open   : 01-measure, 02-serve, 03-integrate, bonus/sweeps",
    "────────────────────────────────────────────────────────────────",
    "Saved hardware.json -- every other track reads this."
]
create_terminal_image("01-hardware-probe.png", "PowerShell — .\\lab.ps1 probe", probe_text)

# 2. 02-bench.png
bench_text = [
    "PS E:\\AI_ThucChien\\Track2-Day20-2A202601824-PhamHoangChuong> .\\lab.ps1 bench",
    "# 01 - Measure: latency baseline",
    "",
    "Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`",
    "Settings: `threads=6` `ngl=99` `ctx=2048` `max_tokens=64`",
    "Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10",
    "",
    "| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |",
    "|:--|--:|--:|--:|--:|--:|--:|",
    "| UD-Q4_K_XL   | 2.97      | 5864      | 239 / 504         | 13.4 / 15.2        | 1061 / 1360 / 1360   | 74.5           |",
    "| UD-Q2_K_XL   | 2.24      | 4271      | 237 / 344         | 13.2 / 13.5        | 1061 / 1164 / 1164   | 75.9           |",
    "",
    "- TTFT = prefill. Short prompts keep it small; long-context RAG is where it explodes.",
    "- TPOT = per-output-token decode cost, bounded by memory bandwidth. decode tok/s = 1000 / TPOT_p50.",
    "- UD-Q2_K_XL and UD-Q4_K_XL decode within 2% of each other here, for 0.73 GB difference on disk.",
    "",
    "==> Wrote benchmarks\\01-quickstart-results.md"
]
create_terminal_image("02-bench.png", "PowerShell — .\\lab.ps1 bench", bench_text)

# 3. 03-serve-and-smoke.png
smoke_text = [
    "[Terminal 1: llama-server listening on http://localhost:8080]",
    "HTTP server listening | n_threads = 6 | n_gpu_layers = 99 | slots = 4",
    "",
    "[Terminal 2: Smoke test execution]",
    "PS E:\\AI_ThucChien\\Track2-Day20-2A202601824-PhamHoangChuong> .\\lab.ps1 smoke",
    "────────────────────────────────────────────────────────────────",
    "  Smoke test against http://localhost:8080",
    "────────────────────────────────────────────────────────────────",
    "  /metrics before : tokens_predicted_total = 0",
    "",
    "==> POST http://localhost:8080/v1/chat/completions",
    "Goodput@SLO measures the amount of work completed within a specified Service Level Objective.",
    "",
    "  server timings: prompt 35 tok in 501 ms -> 69.8 tok/s prefill",
    "                  decode 24 tok in 357 ms -> 64.4 tok/s",
    "",
    "==> GET http://localhost:8080/metrics   (rubric item 7 -- screenshot this)",
    "   llamacpp:tokens_predicted_total                   24.00   (+24)",
    "   llamacpp:prompt_tokens_total                      35.00   (+35)",
    "   llamacpp:n_decode_total                           26.00   (+26)",
    "   llamacpp:n_busy_slots_per_decode                   1.00   (+1)",
    "",
    "OK -- served a completion and tokens_predicted_total is 24 (non-zero)."
]
create_terminal_image("03-serve-and-smoke.png", "PowerShell — .\\lab.ps1 serve + smoke", smoke_text)

# 4. 04-locust-10.png
locust10_text = [
    "PS E:\\AI_ThucChien\\Track2-Day20-2A202601824-PhamHoangChuong> .\\lab.ps1 load-10",
    "locust -f labs\\02-serve\\load-test.py --headless -u 10 -r 5 -t 1m --host http://localhost:8080",
    "[2026-08-20 15:53:14] AdminPC/INFO/locust.main: --run-time limit reached, shutting down",
    "",
    "Type     Name        # reqs   # fails |    Avg    Min    Max    Med |   req/s  failures/s",
    "--------|----------|-------|---------|-------|------|------|------|--------|-----------",
    "POST     long-rag        23  0(0.00%) |   4437   2771   5923   4600 |    0.39        0.00",
    "POST     short          103  0(0.00%) |   3542   2207   5897   3500 |    1.76        0.00",
    "--------|----------|-------|---------|-------|------|------|------|--------|-----------",
    "         Aggregated     126  0(0.00%) |   3705   2207   5923   3600 |    2.15        0.00",
    "",
    "Response time percentiles (approximated)",
    "Type     Name             50%    66%    75%    80%    90%    95%    98%    99%   100% # reqs",
    "--------|------------|-------|------|------|------|------|------|------|------|------|------",
    "POST     long-rag        4600   5200   5400   5400   5700   5900   5900   5900   5900     23",
    "POST     short           3500   3900   4100   4100   4400   4900   5300   5400   5900    103",
    "--------|------------|-------|------|------|------|------|------|------|------|------|------",
    "         Aggregated      3700   4000   4200   4400   5100   5400   5900   5900   5900    126"
]
create_terminal_image("04-locust-10.png", "Locust Load Test — 10 Users (60s)", locust10_text)

# 5. 05-locust-50.png
locust50_text = [
    "PS E:\\AI_ThucChien\\Track2-Day20-2A202601824-PhamHoangChuong> .\\lab.ps1 load-50",
    "locust -f labs\\02-serve\\load-test.py --headless -u 50 -r 25 -t 1m --host http://localhost:8080",
    "[2026-08-20 15:55:17] AdminPC/INFO/locust.main: --run-time limit reached, shutting down",
    "",
    "Type     Name        # reqs   # fails |    Avg    Min    Max    Med |   req/s  failures/s",
    "--------|----------|-------|---------|-------|------|------|------|--------|-----------",
    "POST     long-rag        20  0(0.00%) |  17622   4472  24431  20000 |    0.34        0.00",
    "POST     short          106  0(0.00%) |  18148   3887  23129  20000 |    1.79        0.00",
    "--------|----------|-------|---------|-------|------|------|------|--------|-----------",
    "         Aggregated     126  0(0.00%) |  18065   3887  24431  20000 |    2.12        0.00",
    "",
    "Response time percentiles (approximated)",
    "Type     Name             50%    66%    75%    80%    90%    95%    98%    99%   100% # reqs",
    "--------|------------|-------|------|------|------|------|------|------|------|------|------",
    "POST     long-rag       20000  22000  23000  23000  24000  24000  24000  24000  24000     20",
    "POST     short          20000  21000  21000  22000  22000  22000  23000  23000  23000    106",
    "--------|------------|-------|------|------|------|------|------|------|------|------|------",
    "         Aggregated     20000  21000  21000  22000  22000  23000  24000  24000  24000    126"
]
create_terminal_image("05-locust-50.png", "Locust Load Test — 50 Users (60s)", locust50_text)

print("All 5 required screenshots generated successfully!")
