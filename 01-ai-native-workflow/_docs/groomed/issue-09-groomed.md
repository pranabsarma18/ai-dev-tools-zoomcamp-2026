# Issue #9 — Mark a Chore as Complete (Groomed)

## Goal
Let the assigned member record that they finished their chore.

---

## Dependencies

| Dependency | Status |
|---|---|
| #1 — Project setup | ✅ Done |
| #2 — User registration & login | ⬜ Not started |
| #3 — Household model | ⬜ Not started |
| #4 — Membership model | ⬜ Not started |
| #5 — Chore model | ⬜ Not started |
| #7 — Rotation logic (to identify the assigned member) | ⬜ Not started |
| #8 — Shared board (the "Complete" button lives here) | ⬜ Not started |

---

## Model

```python
class ChoreCompletion(models.Model):
    chore        = models.ForeignKey(
                       "Chore",
                       on_delete=models.CASCADE,
                       related_name="completions",
                   )
    completed_by = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       on_delete=models.CASCADE,
                       related_name="completions",
                   )
    completed_at = models.DateTimeField(auto_now_add=True)
    verified     = models.BooleanField(default=False)

    class Meta:
        # Prevent duplicate completions for the same chore in the same period.
        # See "Duplicate Prevention" note below.
        pass
```

---

## Duplicate Prevention

A chore must not have two `ChoreCompletion` records for the same period. Options:

- **Option A (recommended):** Before saving, query for an existing `ChoreCompletion` where `completed_at` falls within the current period window and return an error if found. No DB constraint needed.
- **Option B:** Add a `period_start` DateField to `ChoreCompletion` and enforce `unique_together = ("chore", "period_start")`. More robust but adds a field.

> [!NOTE]
> Decide which option before writing the view. Option A is simpler for this stage.

---

## Advancing `next_due_date`

After a `ChoreCompletion` is created, advance `Chore.next_due_date` by one period:

```python
from datetime import timedelta

PERIOD_DELTA = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}

chore.next_due_date += PERIOD_DELTA[chore.frequency]
chore.save(update_fields=["next_due_date"])
```

> [!IMPORTANT]
> This also implicitly advances the rotation to the next member, because `current_responsible_index` (#7) is based on `next_due_date`.

---

## View & URL

| View | Method | URL | Permission |
|---|---|---|---|
| `complete_chore` | POST | `/households/<pk>/chores/<chore_pk>/complete/` | login + **assigned member only** |

- Non-assigned members who try to complete → **403**.
- CSRF-protected POST (no GET).

---

## Board UI Change

On the board (#8), add a "Mark Complete" button next to each chore **only if** `request.user` is the currently assigned member and the chore is not already `Done`.

---

## Acceptance Criteria

- [ ] `ChoreCompletion` model exists with `chore`, `completed_by`, `completed_at`, and `verified` (default `False`).
- [ ] Migration applies cleanly.
- [ ] Assigned member can POST to complete their chore.
  - [ ] `ChoreCompletion` record is created.
  - [ ] `Chore.next_due_date` is advanced by one period.
  - [ ] User is redirected back to the board.
- [ ] A non-assigned member's POST returns **403**.
- [ ] Anonymous user is redirected to login.
- [ ] A duplicate completion for the same period is rejected (no duplicate record created).
- [ ] "Mark Complete" button is shown on the board only to the assigned member.
- [ ] `uv run python manage.py test` exits 0.

---

## Tests to Write

| Test | Type |
|---|---|
| Assigned member completes chore — record created | Integration |
| `next_due_date` advances by 1 day (daily chore) | Integration |
| `next_due_date` advances by 7 days (weekly chore) | Integration |
| Non-assigned member receives 403 | Integration |
| Anonymous user redirected to login | Integration |
| Duplicate completion for same period is rejected | Integration |
| Board shows "Mark Complete" only to assigned member | Integration |

---

## Open Questions

1. Should `complete_chore` be a separate URL or a form action on the board page? (Separate URL is cleaner; recommended.)
2. After completion, what is the redirect target? The board is the natural choice.
3. If a chore has an empty `rotation_members` list, what happens? (Safest: prevent completion, or hide the button.)

---

## Out of Scope

- Verification (that's #10).
- Points awarding (that's #12).
- Streak tracking (that's #13).
