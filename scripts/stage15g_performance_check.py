"""
Stage 15G lightweight performance check.

This script is intentionally non-destructive:
- it does not create/update/delete database records;
- it does not submit appointments or payments;
- it benchmarks public Flask rendering, the risk-support service,
  and direct local emotion-model inference.

Run from the project root:
    python scripts/stage15g_performance_check.py
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import torch

from app import create_app
from app.services.emotion_analysis_service import EmotionAnalysisService
from app.services.risk_support_service import RiskSupportService


OUTPUT_DIR = PROJECT_ROOT / "documentation" / "reports"
JSON_OUTPUT = OUTPUT_DIR / "stage-15g-performance-results.json"
MD_OUTPUT = OUTPUT_DIR / "stage-15g-performance-results.md"

MODEL_SAMPLES = [
    "I feel calm and hopeful today.",
    "I am frustrated because the day has been difficult.",
    "I feel sad and lonely this evening.",
    "I am surprised by how well things worked out.",
    "I feel nervous about tomorrow but I am trying to manage.",
    "I really appreciate the people who supported me today.",
]


def milliseconds(seconds: float) -> float:
    return round(seconds * 1000.0, 2)


def summarize_ms(values: list[float]) -> dict:
    ordered = sorted(values)
    p95_index = max(
        0,
        min(
            len(ordered) - 1,
            int(round(0.95 * (len(ordered) - 1))),
        ),
    )

    return {
        "count": len(values),
        "min_ms": round(min(values), 2),
        "average_ms": round(statistics.mean(values), 2),
        "median_ms": round(statistics.median(values), 2),
        "p95_ms": round(ordered[p95_index], 2),
        "max_ms": round(max(values), 2),
    }


def benchmark_flask_routes() -> dict:
    started = time.perf_counter()
    app = create_app()
    create_app_ms = milliseconds(time.perf_counter() - started)

    app.config.update(TESTING=True)
    client = app.test_client()

    route_results = {}

    for path in ("/login", "/this-page-does-not-exist"):
        samples = []

        for _ in range(25):
            started = time.perf_counter()
            response = client.get(path)
            samples.append(
                milliseconds(time.perf_counter() - started)
            )

            if path == "/login":
                if response.status_code != 200:
                    raise RuntimeError(
                        f"{path} returned HTTP {response.status_code}"
                    )
            elif response.status_code != 404:
                raise RuntimeError(
                    f"{path} returned HTTP {response.status_code}"
                )

        route_results[path] = summarize_ms(samples)

    return {
        "create_app_ms": create_app_ms,
        "routes": route_results,
    }


def benchmark_risk_support() -> dict:
    service = RiskSupportService()
    texts = [
        "I had a busy day but I am managing.",
        "Everything feels hopeless and I feel completely alone.",
        "I want to die.",
    ]

    samples = []

    for index in range(3000):
        text = texts[index % len(texts)]
        started = time.perf_counter()
        service.assess_text(text)
        samples.append(
            milliseconds(time.perf_counter() - started)
        )

    return summarize_ms(samples)


def benchmark_model() -> dict:
    started = time.perf_counter()
    service = EmotionAnalysisService()
    model_load_ms = milliseconds(
        time.perf_counter() - started
    )

    # Warm-up once so steady-state inference is measured separately.
    service.analyse_text(MODEL_SAMPLES[0])

    timings = []
    predictions = []

    for index in range(18):
        text = MODEL_SAMPLES[index % len(MODEL_SAMPLES)]

        started = time.perf_counter()
        result = service.analyse_text(text)
        timings.append(
            milliseconds(time.perf_counter() - started)
        )

        if index < len(MODEL_SAMPLES):
            predictions.append(
                {
                    "text": text,
                    "emotion": result["emotion"],
                    "confidence": result["confidence"],
                }
            )

    return {
        "device": str(service.device),
        "cuda_available": bool(torch.cuda.is_available()),
        "model_directory": service.model_directory_name,
        "cold_service_and_model_load_ms": model_load_ms,
        "warm_inference": summarize_ms(timings),
        "sample_predictions": predictions,
    }


def write_markdown(results: dict) -> None:
    flask_data = results["flask"]
    login_data = flask_data["routes"]["/login"]
    missing_data = flask_data["routes"][
        "/this-page-does-not-exist"
    ]
    risk_data = results["risk_support"]
    model_data = results["model"]
    inference_data = model_data["warm_inference"]

    markdown = f"""# Stage 15G Performance Results

Generated: {results["generated_at"]}

## Test approach

This is a lightweight, non-destructive performance check. It measures
application creation, repeated GET rendering for the login and controlled
404 pages, risk-support classification, local model loading, and steady-state
emotion inference. It does not perform destructive load testing against live
appointment, payment, forum, or account records.

## Environment

- Python device selected by model: `{model_data["device"]}`
- CUDA available: `{model_data["cuda_available"]}`
- Active model directory: `{model_data["model_directory"]}`

## Results

| Measurement | Result |
| --- | ---: |
| Flask application creation | {flask_data["create_app_ms"]:.2f} ms |
| `/login` average (25 GETs) | {login_data["average_ms"]:.2f} ms |
| `/login` p95 | {login_data["p95_ms"]:.2f} ms |
| Controlled 404 average (25 GETs) | {missing_data["average_ms"]:.2f} ms |
| Controlled 404 p95 | {missing_data["p95_ms"]:.2f} ms |
| Risk-support average (3000 calls) | {risk_data["average_ms"]:.2f} ms |
| Model/service cold load | {model_data["cold_service_and_model_load_ms"]:.2f} ms |
| Warm model inference average (18 runs) | {inference_data["average_ms"]:.2f} ms |
| Warm model inference median | {inference_data["median_ms"]:.2f} ms |
| Warm model inference p95 | {inference_data["p95_ms"]:.2f} ms |
| Warm model inference maximum | {inference_data["max_ms"]:.2f} ms |

## Interpretation

The measurements above are observed timings from the local development
environment and should not be represented as production guarantees. The
cold model-loading value is separated from warm inference because the
application lazily loads and then reuses the active transformer model.

No destructive concurrency or stress test is performed against the live
project database in order to protect demonstration data. Appointment slot
atomicity and duplicate-booking protection are instead covered by the
automated regression tests.
"""

    MD_OUTPUT.write_text(markdown, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = {
        "generated_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "flask": benchmark_flask_routes(),
        "risk_support": benchmark_risk_support(),
        "model": benchmark_model(),
    }

    JSON_OUTPUT.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )
    write_markdown(results)

    print("\nStage 15G performance check completed.")
    print(f"JSON: {JSON_OUTPUT}")
    print(f"Markdown: {MD_OUTPUT}")

    print("\nKey results:")
    print(
        "Flask app creation:",
        f'{results["flask"]["create_app_ms"]:.2f} ms',
    )
    print(
        "Login average:",
        f'{results["flask"]["routes"]["/login"]["average_ms"]:.2f} ms',
    )
    print(
        "Model cold load:",
        f'{results["model"]["cold_service_and_model_load_ms"]:.2f} ms',
    )
    print(
        "Warm inference average:",
        f'{results["model"]["warm_inference"]["average_ms"]:.2f} ms',
    )
    print(
        "Warm inference p95:",
        f'{results["model"]["warm_inference"]["p95_ms"]:.2f} ms',
    )


if __name__ == "__main__":
    main()
