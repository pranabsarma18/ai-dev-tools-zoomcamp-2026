# Issue #8 — Shared Household Board (Groomed)

## Goal
Show every household member the current state of all chores.

---

## Dependencies

| Dependency | Status |
|---|---|
| #1 — Project setup | ✅ Done |
| #2 — User registration & login | ⬜ Not started |
| #3 — Household model | ⬜ Not started |
| #4 — Membership model | ⬜ Not started |
| #5 — Chore model | ⬜ Not started |
| #7 — Rotation logic | ⬜ Not started |

> [!IMPORTANT]
> The board must call `current_responsible_index` from #7 for each chore. #9 adds `ChoreCompletion` — the board's status logic will reference it, but the basic board can be built without it by treating all chores as "Pending".

---

## View & URL

| View | URL | Auth |
|---|---|---|
| `board` | `GET /households/<pk>/board/` | login required + **member only** |

Non-members (authenticated but not in the household) → **403**.  
Anonymous users → redirect to login.

---

## Board Row Data (per chore)

```python
@dataclass
class ChoreRow:
    chore: Chore
    responsible_user: User       # resolved from rotation_members + rotation function
    status: Literal["Pending", "Done", "Overdue"]
    completion: ChoreCompletion | None   # None until #9 is merged
```

### Status Logic

| Condition | Status |
|---|---|
| `ChoreCompletion` exists for current period | `"Done"` |
| No completion AND `next_due_date` >= today | `"Pending"` |
| No completion AND `next_due_date` < today | `"Overdue"` |

> [!NOTE]
> "Current period" means: a `ChoreCompletion` whose `completed_at` falls within the current period window (from `next_due_date` to `next_due_date + frequency`). This logic must be consistent with #9 and #11.

---

## Template

`chores/templates/chores/board.html` — minimum columns:

| Column | Source |
|---|---|
| Title | `Chore.title` |
| Frequency | `Chore.frequency` |
| Points | `Chore.point_value` |
| Due date | `Chore.next_due_date` |
| Responsible | `User.get_full_name()` or `User.username` |
| Status | `"Pending"` / `"Done"` / `"Overdue"` badge |

---

## Acceptance Criteria

- [ ] `GET /households/<pk>/board/` is accessible to all household members (including the owner).
- [ ] Non-member authenticated users receive **403**.
- [ ] Anonymous users are redirected to login.
- [ ] Each chore row shows: title, frequency, point value, due date, responsible member name.
- [ ] Each chore is marked `Pending`, `Done`, or `Overdue` correctly.
- [ ] Board uses the `current_responsible_index` function from #7 (not duplicated logic).
- [ ] `uv run python manage.py test` exits 0 with all new tests passing.

---

## Tests to Write

| Test | Type |
|---|---|
| Member can access the board | Integration |
| Non-member receives 403 | Integration |
| Anonymous user redirected to login | Integration |
| Board shows all chores for the household | Integration |
| Chore with completion is marked Done | Integration |
| Chore past due date and no completion is marked Overdue | Integration |
| Chore not yet due and no completion is marked Pending | Integration |
| Responsible member name is correctly resolved | Integration |

---

## Open Questions

1. Should the board be at `/households/<pk>/board/` or just `/households/<pk>/`? Having the board **be** the household detail page is simpler. Decide before creating URLs so #3's detail redirect doesn't need changing.
2. Should chores be sorted by due date, status, or title on the board?
3. What happens on the board if `rotation_members` is empty for a chore? Show "Unassigned" or hide the chore?

---

## Out of Scope

- Action buttons (complete, verify) — those are #9 and #10.
- The leaderboard link — that's #14.
- The management command for overdue — that's #11.
