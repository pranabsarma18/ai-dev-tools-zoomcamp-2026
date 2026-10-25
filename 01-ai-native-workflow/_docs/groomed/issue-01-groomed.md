# Issue #1 — Project Setup with a Passing Test (Groomed)

## Status: ✅ DONE

## Goal
Confirm the Django project boots and the test suite runs green from a fresh clone.

---

## Dependencies
None — this is the foundation for all other issues.

---

## What Was Implemented

| Item | File |
|---|---|
| `chores` registered in `INSTALLED_APPS` | `household_chores/settings.py` |
| `index` view (placeholder `HttpResponse`) | `chores/views.py` |
| App URLconf wiring `GET /` → `index` | `chores/urls.py` (new) |
| Root URLconf includes `chores.urls` | `household_chores/urls.py` |
| `SmokeTest` — `GET /` returns `< 500` | `chores/tests.py` |
| `SanityTest` — `1 + 1 == 2` | `chores/tests.py` |
| Dev server command documented | `README.md` |

## Acceptance Criteria (all met)

- [x] `chores` registered in `INSTALLED_APPS`
- [x] `chores/urls.py` exists and is wired into root URL config
- [x] Smoke test: `GET /` does not return a 5xx response
- [x] Unit test: `1 + 1 == 2`
- [x] `uv run python manage.py test` exits 0
- [x] `uv run python manage.py runserver` documented in `README.md`

## Commit
`6933c49` — *Task 1: project setup with passing tests*

---

## Notes

- No new tests needed — issue is complete.
- All acceptance criteria are verified and committed.

