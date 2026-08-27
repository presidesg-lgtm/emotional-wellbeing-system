# Stage 15E Automated Tests

These tests use Python's built-in `unittest` framework so no new test
dependency is required.

Run the complete test suite from the project root:

```bash
python -m unittest discover -s tests -v
```

The suite intentionally avoids changing the live project database. Database
workflows are tested with mocks/fakes, while pure validation and safety
services are tested directly.

Coverage areas:

- CSRF validation and session invalidation
- payment-proof file validation
- risk-support classification
- model-directory validation and identifier redaction
- appointment slot atomicity / duplicate-booking protection
- payment ownership and invalid-payment workflow rules
