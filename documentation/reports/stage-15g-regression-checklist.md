# Stage 15G Full Regression Checklist

Use this checklist after the automated suite and performance script pass.
The purpose is to verify that the main user-facing workflows still operate
after the Stage 15 security and reliability changes.

Record screenshots only where they add useful evidence. Do not create
unnecessary duplicate data solely for screenshots.

## Automated regression

Run:

```bash
python -m unittest discover -s tests -v
```

Expected baseline after Stage 15F:

- 36 tests executed
- 36 tests passed
- 0 failures
- 0 errors

The reliability tests intentionally log simulated internal exceptions. They
are successful when the individual tests end in `ok` and the suite ends in
`OK`.

## Normal user regression

- Log in with an active normal-user account.
- Home/emotion-analysis page loads.
- Submit one ordinary non-sensitive test sentence and confirm an emotion,
  confidence, disclaimer, and support response are returned.
- Dashboard/history loads and the new entry is visible where expected.
- Counsellor list loads.
- Appointments page loads.
- Existing payment-proof state displays correctly.
- Anonymous forum loads.
- Existing post/reply discussion remains visible when not moderated.
- Profile page loads and existing profile information is displayed.

## Counsellor regression

- Log in as an active counsellor.
- Counsellor dashboard loads.
- Assigned/available appointment information remains scoped correctly.
- Counsellor availability/session workflow loads.
- Normal-user dashboard remains inaccessible.

## Administrator regression

- Log in as an administrator.
- Admin dashboard loads.
- User/counsellor/session management loads.
- Analytics/reporting loads.
- Forum moderation controls load.
- AI model-update management loads.
- Normal-user and counsellor-only routes remain inaccessible.

## Error/reliability regression

- Visit a made-up URL such as `/stage15g-not-found`.
- Confirm the controlled 404 page is displayed.
- Confirm the application starts with debug mode disabled unless
  `FLASK_DEBUG` is explicitly enabled.

## Evidence recommendation

A compact evidence set is sufficient:

1. terminal showing `Ran 36 tests ... OK`;
2. generated `stage-15g-performance-results.md`;
3. one normal-user regression screenshot;
4. one administrator/counsellor regression screenshot if useful.

The final report should distinguish automated tests, manual regression,
security/workflow tests, and local performance measurements rather than
presenting them as one test type.
