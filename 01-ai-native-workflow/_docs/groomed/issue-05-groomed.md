# Issue #5 — Chore Model (Groomed)

## Goal
Store the definition of a chore that belongs to a household.

---

## Dependencies

| Dependency | Status |
|---|---|
| #1 — Project setup | ✅ Done |
| #3 — Household model | ⬜ Not started |
| #4 — Membership model | ⬜ Not started |

> [!IMPORTANT]
> `Chore.household` FKs to `Household` (#3). `Chore.rotation_members` references user PKs from household members (#4). Both must be merged before this migration is written.

---

## Model

```python
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings


class Chore(models.Model):
    class Frequency(models.TextChoices):
        DAILY  = "daily",  "Daily"
        WEEKLY = "weekly", "Weekly"

    household        = models.ForeignKey(
                           "Household",
                           on_delete=models.CASCADE,
                           related_name="chores",
                       )
    title            = models.CharField(max_length=200)
    description      = models.TextField(blank=True)
    frequency        = models.CharField(
                           max_length=10,
                           choices=Frequency.choices,
                       )
    point_value      = models.PositiveIntegerField(
                           validators=[MinValueValidator(1)],
                       )
    # Ordered list of User PKs — e.g. [3, 7, 2]
    rotation_members = models.JSONField(default=list)
    next_due_date    = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.household})"
```

> [!NOTE]
> `rotation_members` stores an **ordered list of integer user PKs**. This is simple and avoids a through-model for now. The rotation function (#7) works directly with this list. If the rotation order needs UI drag-and-drop later, consider a through model at that point.

---

## Key Design Decisions

| Question | Decision |
|---|---|
| `rotation_members` storage | `JSONField` (list of PKs) — simpler than a through model for this stage |
| `point_value` minimum | `1` (enforced by `MinValueValidator` + `PositiveIntegerField`) |
| `frequency` allowed values | `daily` / `weekly` only (enforced by `TextChoices`) |
| `description` required? | No — `blank=True` |

---

## Acceptance Criteria

- [ ] `Chore` model exists with all specified fields.
- [ ] Migration applies cleanly.
- [ ] `point_value = 0` fails model validation (raises `ValidationError`).
- [ ] `point_value = -1` fails model validation.
- [ ] `frequency = "monthly"` fails model validation.
- [ ] `frequency = "daily"` and `frequency = "weekly"` both pass.
- [ ] `description` is optional (blank is valid).
- [ ] `rotation_members` defaults to an empty list.
- [ ] `uv run python manage.py test` exits 0 with all new tests passing.

---

## Tests to Write

> [!NOTE]
> Read `_docs/testing-guidelines.md` before writing tests (if it exists by the time this is picked up).

| Test | Type |
|---|---|
| `point_value = 0` raises `ValidationError` | Unit (model) |
| `point_value = -1` raises `ValidationError` | Unit (model) |
| `point_value = 1` is valid | Unit (model) |
| `frequency = "monthly"` raises `ValidationError` | Unit (model) |
| `frequency = "daily"` is valid | Unit (model) |
| `frequency = "weekly"` is valid | Unit (model) |
| `rotation_members` defaults to `[]` | Unit (model) |

---

## Open Questions

1. Should `rotation_members` be validated to ensure all PKs belong to the household's members? (Recommended: not in this issue — defer to the chore management form in #6.)
2. Should `next_due_date` be auto-set based on `frequency` when a chore is created, or always provided by the owner? (Recommend: owner provides it in the creation form in #6; no default here.)
3. Is `point_value = 0` explicitly invalid? The task says "positive integer" — `PositiveIntegerField` in Django allows `0`. Use `MinValueValidator(1)` to enforce strictly positive. **This must be confirmed before writing tests.**

---

## Out of Scope

- CRUD views (that's #6).
- Rotation logic (that's #7).
- The chore's completion status (that's #9).
