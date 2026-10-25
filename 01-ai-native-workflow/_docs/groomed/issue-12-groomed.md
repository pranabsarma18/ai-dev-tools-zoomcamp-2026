# Issue #12 — Points Tracking (Groomed)

## Goal
Award points to a user each time a (verified) chore completion is recorded.

---

## Dependencies

| Dependency | Status |
|---|---|
| #4 — Membership model | ⬜ Not started |
| #9 — ChoreCompletion model | ⬜ Not started |
| #10 — Verification flow (`verified` field) | ⬜ Not started |

---

## Model Change

Add `points` to `Membership`:

```python
class Membership(models.Model):
    household = models.ForeignKey(...)
    user      = models.ForeignKey(...)
    joined_at = models.DateTimeField(auto_now_add=True)
    points    = models.PositiveIntegerField(default=0)   # ← NEW
```

A new migration is required.

---

## Points Rules

| Event | Points Awarded |
|---|---|
| `ChoreCompletion` created | `chore.point_value` added to completing member's `Membership.points` |
| `ChoreCompletion.verified` set to `True` | Additional `floor(chore.point_value * 0.10)` added |

> [!IMPORTANT]
> The base points are awarded **when the completion is created** (in #9), not when verified. The verification bonus is awarded **when `verified` is set to `True`** (in #10). These are two separate events.

---

## Implementation Approach

### Option A — Django Signals (recommended)
- `post_save` on `ChoreCompletion`: award base points when `created=True`.
- `post_save` on `ChoreCompletion`: award bonus when `instance.verified` is `True` and `update_fields` includes `"verified"` (i.e. it just changed).

### Option B — In the view
- Call `award_points()` helper directly from `complete_chore` view and `verify_completion` view.

> [!NOTE]
> Option A keeps the awarding logic close to the model and avoids having to remember to call it from every future path. Option B is simpler to test. **Decide before implementation.**

---

## Helper Function (Recommended)

```python
def award_completion_points(completion: ChoreCompletion) -> None:
    """Award base points. Call when a ChoreCompletion is created."""
    membership = Membership.objects.get(
        household=completion.chore.household,
        user=completion.completed_by,
    )
    membership.points = models.F("points") + completion.chore.point_value
    membership.save(update_fields=["points"])


def award_verification_bonus(completion: ChoreCompletion) -> None:
    """Award 10% bonus. Call when verified is set to True."""
    bonus = completion.chore.point_value // 10   # floor division
    membership = Membership.objects.get(
        household=completion.chore.household,
        user=completion.completed_by,
    )
    membership.points = models.F("points") + bonus
    membership.save(update_fields=["points"])
```

---

## Acceptance Criteria

- [ ] `Membership.points` field exists (default `0`), migration applies cleanly.
- [ ] When a `ChoreCompletion` is created, the completing member's `points` increases by `chore.point_value`.
- [ ] When a `ChoreCompletion` is verified, the completing member's `points` increases by `floor(chore.point_value * 0.10)`.
- [ ] If `point_value = 5`, base award = `5`, verification bonus = `0` (floor of 0.5 = 0). **Confirm this is correct.**
- [ ] Points are never negative.
- [ ] `uv run python manage.py test` exits 0.

---

## Tests to Write

| Test | Type |
|---|---|
| Completion awards base `point_value` points | Unit |
| Verification awards `floor(point_value * 0.10)` bonus | Unit |
| `point_value = 5` → verification bonus = 0 | Unit |
| `point_value = 10` → verification bonus = 1 | Unit |
| `point_value = 100` → verification bonus = 10 | Unit |
| Points are cumulative across multiple completions | Unit |
| Points on other members' memberships are not affected | Unit |

---

## Open Questions

1. Should the verification bonus be `floor(point_value * 0.10)` or `round(...)`? The task says "rounded down" — floor division is correct. **Confirm `point_value = 5` → bonus = 0` is acceptable.**
2. What if the completing member has no `Membership` row? (Should not happen if #4 enforces it, but add a guard or let it raise.)
3. Should there be a `PointsTransaction` log table for audit purposes? Not in scope now, but useful for the leaderboard (#14) if per-chore breakdown is wanted later.

---

## Out of Scope

- Displaying points (that's #14 — leaderboard).
- Streak tracking (that's #13).
- Any point deduction or penalty.
