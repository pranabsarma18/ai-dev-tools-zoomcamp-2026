# Issue #13 — Streaks (Groomed)

## Goal
Track how many consecutive periods a member has completed their assigned chore without missing one.

---

## Dependencies

| Dependency | Status |
|---|---|
| #4 — Membership model | ⬜ Not started |
| #9 — ChoreCompletion model | ⬜ Not started |
| #11 — Carry-forward command (triggers streak reset) | ⬜ Not started |
| #12 — Points tracking (adds `points` to Membership; `current_streak` is added here) | ⬜ Not started |

---

## Model Change

Add `current_streak` to `Membership`:

```python
class Membership(models.Model):
    household      = models.ForeignKey(...)
    user           = models.ForeignKey(...)
    joined_at      = models.DateTimeField(auto_now_add=True)
    points         = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)   # ← NEW
```

A new migration is required (or add to the #12 migration if done atomically).

> [!NOTE]
> `current_streak` is a per-**member** field, not per-chore. This means a member has a single streak across all their chores. If the intent is per-chore streaks, the model needs a `ChoreStreak` through table. The task description is ambiguous — **decide before implementation.**

---

## Streak Rules

| Event | Effect |
|---|---|
| A `ChoreCompletion` is saved for the assigned member | `current_streak` for that member incremented by 1 |
| `carry_forward_chores` marks a chore overdue and the assigned member did not complete it | `current_streak` for that assigned member reset to `0` |
| A *different* member completes a *different* chore | No effect on other members' streaks |

---

## Key Design Ambiguity — Per-Member vs Per-Chore Streak

The task says:
> *"streak unaffected when a different member completes a different chore"*

This suggests the streak is **per member** (one streak number per `Membership` row). However, a member could be assigned to multiple chores. If they miss one but complete another, what happens?

- **Option A (per-member streak):** Missing *any* assigned chore resets the whole streak. Simpler, one field.
- **Option B (per-chore streak):** Each chore tracks independently. Requires a `ChoreStreak` model.

> [!IMPORTANT]
> Resolve this ambiguity before writing any code. The tests in the task description ("streak unaffected when a different member completes a different chore") are consistent with both options. The reset rule ("when carry-forward marks a chore overdue") implies a per-chore reset event — which could reset a per-member counter or a per-chore counter.

---

## Acceptance Criteria

- [ ] `Membership.current_streak` field exists (default `0`), migration applies cleanly.
- [ ] When a `ChoreCompletion` is saved for the assigned member, that member's `current_streak` increments by 1.
- [ ] When `carry_forward_chores` marks a chore overdue and the assigned member did not complete it, that member's `current_streak` resets to `0`.
- [ ] A completion or miss by member A has no effect on member B's streak.
- [ ] `uv run python manage.py test` exits 0.

---

## Tests to Write

| Test | Type |
|---|---|
| Completion by assigned member increments `current_streak` | Unit |
| Streak increments consecutively (1, 2, 3 ...) | Unit |
| `carry_forward_chores` resets streak for the assigned member who missed | Unit |
| Another member completing a different chore does not change the first member's streak | Unit |
| Streak is not reset when a completion exists (no miss) | Unit |

---

## Integration with `carry_forward_chores`

The #11 command must be **extended** to also reset streaks. Two approaches:

- **Option A:** Add streak reset logic directly into `carry_forward_chores`.
- **Option B:** Emit a signal or call a helper function from the command.

Recommended: a helper function `reset_streak_for_overdue_chore(chore)` called from the command, so it can be unit-tested independently.

---

## Open Questions

1. **Per-member or per-chore streak?** (See above — must decide before model migration.)
2. If a member has two assigned chores and misses one but completes the other in the same period — is their streak reset or not?
3. Should the streak be displayed on the board or only on the leaderboard (#14)?

---

## Out of Scope

- Displaying streaks (that's #14).
- Streak bonuses or point multipliers (not in the current scope).
- Historical best-streak tracking.
