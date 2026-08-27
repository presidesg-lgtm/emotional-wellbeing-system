# Stage 15G Performance Results

Generated: 2026-08-28T02:34:28+05:30

## Test approach

This is a lightweight, non-destructive performance check. It measures
application creation, repeated GET rendering for the login and controlled
404 pages, risk-support classification, local model loading, and steady-state
emotion inference. It does not perform destructive load testing against live
appointment, payment, forum, or account records.

## Environment

- Python device selected by model: `cuda`
- CUDA available: `True`
- Active model directory: `selected-distilbert-emotion`

## Results

| Measurement | Result |
| --- | ---: |
| Flask application creation | 16.85 ms |
| `/login` average (25 GETs) | 0.99 ms |
| `/login` p95 | 0.76 ms |
| Controlled 404 average (25 GETs) | 0.76 ms |
| Controlled 404 p95 | 0.63 ms |
| Risk-support average (3000 calls) | 0.02 ms |
| Model/service cold load | 4028.88 ms |
| Warm model inference average (18 runs) | 21.86 ms |
| Warm model inference median | 19.62 ms |
| Warm model inference p95 | 24.67 ms |
| Warm model inference maximum | 58.11 ms |

## Interpretation

The measurements above are observed timings from the local development
environment and should not be represented as production guarantees. The
cold model-loading value is separated from warm inference because the
application lazily loads and then reuses the active transformer model.

No destructive concurrency or stress test is performed against the live
project database in order to protect demonstration data. Appointment slot
atomicity and duplicate-booking protection are instead covered by the
automated regression tests.
