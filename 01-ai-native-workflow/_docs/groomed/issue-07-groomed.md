# Issue #7 — Chore Rotation Logic (Groomed)

## Goal
Compute which household member is currently responsible for a chore.

---

## Dependencies

| Dependency | Status |
|---|---|
| #5 — Chore model (defines `rotation_members`, `next_due_date`, `frequency`) | ⬜ Not started |

> [!NOTE]
> This issue is **pure Python** — no ORM calls, no views, no migrations. It can be written as soon as the `Chore` field contracts are agreed in #5, even before the model migration is applied. It can be worked in parallel with #6.

---

## Function Contract

```python
from datetime import date
from typing import Literal

Frequency = Literal["daily", "weekly"]

def current_responsible_index(
    rotation_members: list[int],
    next_due_date: date,
    frequency: Frequency,
    reference_date: date,
) -> int:
    """
    Return the index into `rotation_members` of the member currently
    responsible for the chore.

    Parameters
    ----------
    rotation_members : list of user PKs in rotation order (length >= 1)
    next_due_date    : the date the chore is next due (as stored on Chore)
    frequency        : "daily" or "weekly"
    reference_date   : the date to evaluate against (typically date.today())

    Returns
    -------
    int — index into rotation_members (0-based, wraps around)

    Raises
    ------
    ValueError  if rotation_members is empty
    """
```

### Algorithm Sketch

1. Compute `period_length` = 1 day (daily) or 7 days (weekly).
2. Compute `periods_elapsed` = how many full periods have passed since `next_due_date` up to `reference_date`. If `reference_date < next_due_date`, `periods_elapsed = 0` (chore not yet due; first member is responsible).
3. Return `periods_elapsed % len(rotation_members)`.

> [!NOTE]
> The "current responsible" member is the one for the **current period**, not the one for the overdue period. Decide: if `reference_date` is 3 periods past `next_due_date`, do we return the member for the 3rd period (overdue) or the member for the 4th (the current one)? The task says "overdue by more than one period" is a test case — clarify the expected return value before writing.

---

## Suggested File Location

```
chores/rotation.py   ← pure function lives here
```

No imports from `models` or `django` — keeps it fully unit-testable without a database.

---

## Acceptance Criteria

- [ ] `current_responsible_index` exists in `chores/rotation.py`.
- [ ] Takes `rotation_members`, `next_due_date`, `frequency`, `reference_date` as parameters.
- [ ] Returns the correct 0-based index (wrapping around the list).
- [ ] Raises `ValueError` if `rotation_members` is empty.
- [ ] Unit tests pass for all cases listed below.
- [ ] **No ORM calls or Django imports** inside the function.
- [ ] `uv run python manage.py test` exits 0.

---

## Tests to Write

| Scenario | Input | Expected index |
|---|---|---|
| First slot — chore not yet due | `next_due_date` in the future | `0` |
| First slot — chore due today | `reference_date == next_due_date` | `0` |
| Second member — one period elapsed | `reference_date` = `next_due_date + 1 period` | `1` |
| Wrap-around — last member + 1 period | index would exceed list length | `0` |
| Overdue by more than one period | `reference_date` many periods past due | correct wrapped index |
| Single-member list always returns `0` | any dates | `0` |
| Empty list raises `ValueError` | `[]` | raises `ValueError` |

---

## Open Questions

1. **Overdue interpretation:** when a chore is overdue by N periods, do we return the member for the Nth period (the one who *should have done it*) or the (N+1)th (the one *next in line*)? This must be decided before writing the tests — it changes the algorithm.
2. Should the function handle `frequency` values other than `"daily"`/`"weekly"` (e.g. raise `ValueError`)? Recommended: yes, to make it robust.

---

## Out of Scope

- Wiring into views (that's #8).
- Advancing `next_due_date` (that's #9).
- Streak / points logic (that's #12 / #13).
