# Issue #10 — Verify Chore Completion (Groomed)

## Goal
Let any other household member confirm that a chore was actually done.

---

## Dependencies

| Dependency | Status |
|---|---|
| #1 — Project setup | ✅ Done |
| #2 — User registration & login | ⬜ Not started |
| #3 — Household model | ⬜ Not started |
| #4 — Membership model | ⬜ Not started |
| #8 — Shared board (board shows the verify button) | ⬜ Not started |
| #9 — ChoreCompletion model and complete flow | ⬜ Not started |

---

## Behaviour

When a `ChoreCompletion` exists and `verified = False`:
- A **"Verify"** button is shown to every household member **except** the person who completed it (`completed_by`).
- Clicking the button sets `verified = True`.
- The board visually distinguishes unverified vs verified completions.

---

## View & URL

| View | Method | URL | Permission |
|---|---|---|---|
| `verify_completion` | POST | `/households/<pk>/completions/<completion_pk>/verify/` | login + **member** (not the completer) |

- If `request.user == completion.completed_by` → **403**.
- If already `verified = True` → idempotent (no error, no change, redirect back).
- Non-member → **403**.
- Anonymous → redirect to login.

---

## Board UI Changes

| State | What to Show |
|---|---|
| No completion | Status: `Pending` or `Overdue`, no verify button |
| Completion, `verified = False` | Status: `Done (unverified)`, "Verify" button for all members except completer |
| Completion, `verified = True` | Status: `Done ✓ (verified)` label/badge, no verify button |

---

## Acceptance Criteria

- [ ] A household member (not the completer) can POST to verify a completion.
  - [ ] `ChoreCompletion.verified` is set to `True`.
  - [ ] User is redirected to the board.
- [ ] The completer cannot verify their own completion (**403**).
- [ ] Non-member receives **403**.
- [ ] Anonymous user is redirected to login.
- [ ] Verifying an already-verified completion is idempotent (no error).
- [ ] The board visually distinguishes `Done (unverified)` from `Done ✓ (verified)`.
- [ ] The "Verify" button is not shown to the completer.
- [ ] `uv run python manage.py test` exits 0.

---

## Tests to Write

| Test | Type |
|---|---|
| Member verifies completion — `verified` set to `True` | Integration |
| Completer cannot verify their own completion (403) | Integration |
| Non-member receives 403 | Integration |
| Anonymous user redirected to login | Integration |
| Verifying already-verified completion is idempotent | Integration |
| Board shows verify button only to non-completers | Integration |
| Board shows different badge for verified vs unverified | Integration |

---

## Open Questions

1. Should only one verification be allowed, or can multiple members each verify? (One `verified` boolean field implies one verification. This is fine for now.)
2. Should there be a `verified_by` FK recorded for audit purposes? Not in scope per the task, but worth noting for later.
3. What happens if the verifier is the household owner but also the completer? (Same rule: owner cannot verify their own completion.)

---

## Out of Scope

- Verification bonus points (that's #12).
- Any undo/unverify mechanism.
