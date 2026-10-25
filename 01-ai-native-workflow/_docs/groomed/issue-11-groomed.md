# Issue #11 — Carry-Forward Pending Chores (Groomed)

## Goal
Ensure an unfinished chore remains visible as pending (overdue) even after its due date passes.

---

## Dependencies

| Dependency | Status |
|---|---|
| #5 — Chore model (`next_due_date`, `frequency`) | ⬜ Not started |
| #8 — Board view (displays `Overdue` status) | ⬜ Not started |
| #9 — ChoreCompletion model | ⬜ Not started |

> [!NOTE]
> This issue adds a **management command** — no views or URLs. It can be developed largely in parallel with #10 once #5 and #9 are done.

---

## Behaviour

The command scans every chore where:
1. `next_due_date` is in the past (before the reference date).
2. There is **no `ChoreCompletion`** for the current period.

For matching chores, it **does NOT advance `next_due_date`** — leaving the date in the past so the board status logic in #8 marks it `Overdue`.

> [!IMPORTANT]
> The command must be idempotent — running it multiple times on the same chore with the same reference date must not change any data the second time.

---

## Management Command

```
python manage.py carry_forward_chores [--date YYYY-MM-DD]
```

- `--date` is optional; defaults to `date.today()`. Using a fixed date makes the command testable.
- Output: print a summary line per affected chore (e.g. `"Chore 'Dishes' is overdue as of 2026-10-25"`).

### File Location

```
chores/management/commands/carry_forward_chores.py
```

---

## "Current Period" Definition

A chore has a completion for the current period if a `ChoreCompletion` exists where:

```
period_start <= completed_at < period_end
```

Where:
- `period_start` = `chore.next_due_date` (the date currently stored — i.e. the overdue date)
- `period_end` = `period_start + timedelta(days=1)` (daily) or `timedelta(weeks=1)` (weekly)

> [!NOTE]
> This definition must be **identical** to the one used in #8 and #9 to avoid inconsistencies. Consider extracting a shared helper `chore_has_completion_for_period(chore, reference_date) -> bool` used by both the command and the board view.

---

## Acceptance Criteria

- [ ] Management command `carry_forward_chores` exists and is runnable.
- [ ] Command accepts an optional `--date` argument for a fixed reference date.
- [ ] For each chore where `next_due_date < reference_date` and no completion for that period:
  - [ ] `next_due_date` is **not changed**.
  - [ ] The chore is logged/printed as overdue.
- [ ] Chores with a valid completion for the current period are **not affected**.
- [ ] Running the command twice produces the same result (idempotent).
- [ ] The board (#8) correctly shows `Overdue` for chores left in this state.
- [ ] Unit test uses a fixed reference date and asserts correct chores are flagged.
- [ ] `uv run python manage.py test` exits 0.

---

## Tests to Write

| Test | Type |
|---|---|
| Overdue chore with no completion is flagged | Unit (command) |
| Chore with completion in the current period is not flagged | Unit (command) |
| Chore due today (not past) is not flagged | Unit (command) |
| Command is idempotent (second run changes nothing) | Unit (command) |
| Future chore is not flagged | Unit (command) |

All tests should use `--date` / a fixed reference date, not `date.today()`.

---

## Open Questions

1. Should the command also **rotate** the responsible member even for overdue chores (i.e. advance the rotation index without advancing `next_due_date`)? The task says "do not advance the due date" and the rotation function (#7) derives the current member from `next_due_date` — so leaving `next_due_date` unchanged also leaves the same member responsible. **Confirm this is the intended behaviour.**
2. Should there be a scheduled runner (e.g. cron, Celery beat) to call this command? Not in scope for this issue — just the command itself.
3. Should the command log to `stdout`, a logger, or both?

---

## Out of Scope

- Advancing `next_due_date` (only happens on completion in #9).
- Streak reset on overdue (that's #13 — the command in #13 will call or extend this one).
- Any email/push notifications.
