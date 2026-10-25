# Issue #14 — Leaderboard (Groomed)

## Goal
Show a ranked list of household members by points and completed chore count.

---

## Dependencies

| Dependency | Status |
|---|---|
| #1 — Project setup | ✅ Done |
| #2 — User registration & login | ⬜ Not started |
| #3 — Household model | ⬜ Not started |
| #4 — Membership model | ⬜ Not started |
| #8 — Board (links to leaderboard) | ⬜ Not started |
| #9 — ChoreCompletion model (for completed chore count) | ⬜ Not started |
| #12 — Points on Membership | ⬜ Not started |
| #13 — `current_streak` on Membership | ⬜ Not started |

---

## View & URL

| View | URL | Auth |
|---|---|---|
| `leaderboard` | `GET /households/<pk>/leaderboard/` | login required + **member only** |

Non-member authenticated users → **403**.  
Anonymous users → redirect to login.

---

## Query

```python
from django.db.models import Count, Q

def get_leaderboard(household):
    return (
        Membership.objects
        .filter(household=household)
        .annotate(
            completed_chore_count=Count(
                "user__completions",
                filter=Q(user__completions__chore__household=household),
            )
        )
        .order_by("-points", "-completed_chore_count")
        .select_related("user")
    )
```

> [!NOTE]
> The query annotates each membership with the count of `ChoreCompletion` rows for that user within this household. Adjust the `filter` based on the actual related name structure from #9.

---

## Leaderboard Table Columns

| # | Column | Source |
|---|---|---|
| 1 | Rank | Row number (1-based) |
| 2 | Name | `membership.user.get_full_name()` or `username` |
| 3 | Total Points | `membership.points` |
| 4 | Completed Chores | `membership.completed_chore_count` |
| 5 | Current Streak | `membership.current_streak` |

The current user's row should be visually highlighted.

---

## Acceptance Criteria

- [ ] `GET /households/<pk>/leaderboard/` is accessible to all household members.
- [ ] Non-member authenticated users receive **403**.
- [ ] Anonymous users are redirected to login.
- [ ] Members are ranked by `points` descending; ties broken by `completed_chore_count` descending.
- [ ] Table shows: rank, name, total points, completed chore count, current streak.
- [ ] The board page (#8) links to the leaderboard.
- [ ] `uv run python manage.py test` exits 0.

---

## Tests to Write

| Test | Type |
|---|---|
| Member can access the leaderboard | Integration |
| Non-member receives 403 | Integration |
| Anonymous user redirected to login | Integration |
| Members ranked by points descending | Integration |
| Tie in points broken by completed chore count | Integration |
| Owner appears in the leaderboard | Integration |

---

## Open Questions

1. Should the owner always appear in the leaderboard even if they have 0 points and 0 completions? Yes — they should, because they have a `Membership` row (confirmed decision from #3 / #4).
2. Should "completed chore count" count **all** completions or only **verified** completions? The task doesn't specify; recommending all completions for simplicity.
3. Should the leaderboard be household-scoped (only completions within this household) or global? **Household-scoped** (as implied by the household URL parameter).

---

## Out of Scope

- Per-chore breakdown.
- Historical rankings or period filtering.
- Exporting the leaderboard.
