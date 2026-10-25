# Issue #4 — Join a Household via Invite Code (Groomed)

## Goal
Let a logged-in user paste an invite code to become a member of an existing household.

---

## Dependencies

| Dependency | Status |
|---|---|
| #1 — Project setup (app boots, tests run) | ✅ Done |
| #2 — User registration & login | ⬜ Not started |
| #3 — Household model & creation (provides `invite_code`) | ⬜ Not started |

> [!IMPORTANT]
> This issue **cannot start** until #2 and #3 are merged. The `Membership` model FKs reference both `User` and `Household`.

---

## Open Decision — Must Resolve Before Implementation

**Can a user belong to multiple households?**

- **Option A — One household per user (recommended for homework):** A user who already belongs to a household (either as owner or member) cannot join a second. The unique constraint on `Membership.user` enforces this at the DB level.
- **Option B — Multiple households:** No such constraint; users can be members of many households. The UI would need a household-switcher.

The decision determines whether the `Membership` model carries a `unique_together = ('user',)` constraint or a `unique_together = ('household', 'user')` constraint.

> [!NOTE]
> Task #3 already defers this decision ("leave the multi-household decision open at the model level"). **This issue should resolve it and document the outcome in `plan.md`.**

---

## Model

```python
class Membership(models.Model):
    household = models.ForeignKey("Household", on_delete=models.CASCADE, related_name="memberships")
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # If Option A: unique_together = [("user",)]   — one household per user
        # If Option B: unique_together = [("household", "user")]   — no duplicate membership in same household
        unique_together = [("household", "user")]   # minimum constraint regardless of option chosen
```

---

## Acceptance Criteria

- [ ] `Membership` model exists with `household` (FK), `user` (FK), and `joined_at` (auto timestamp).
- [ ] A migration is generated and applies cleanly (`migrate` exits 0).
- [ ] A logged-in user can submit a form with an invite code.
  - [ ] If the code matches a household and the user is not already a member → `Membership` record is created; user is redirected (e.g. to the household board placeholder or dashboard).
  - [ ] If the code does not match any household → a clear error message is shown on the same form page.
  - [ ] If the user is already a member of that household → a clear error message is shown ("You are already a member of this household").
- [ ] The join view requires login (redirect to login page if anonymous).
- [ ] When listing members of a household, the **owner is treated as an implicit member** (i.e. the owner appears in member lists even if no `Membership` row exists for them, OR a `Membership` row is created automatically when the household is created in #3).
- [ ] `uv run python manage.py test` exits 0 with all new tests passing.

---

## Tests to Write

| Test | Type |
|---|---|
| Valid code creates a `Membership` row | Integration |
| Invalid code shows form error, no row created | Integration |
| Already-a-member shows form error, no duplicate row | Integration |
| Anonymous user is redirected to login | Integration |
| Owner appears in member list (implicit membership) | Unit |
| (If Option A) User already in another household is rejected | Integration |

---

## URL & View Sketch

```
GET/POST  /join/     → chores:join_household   (login_required)
```

The form has a single field: `invite_code` (CharField, max_length=32).

---

## Out of Scope for This Issue

- Displaying the household detail page (the redirect target can be the dashboard or a stub).
- The household detail page itself (covered in #3 or later issues).
- Removing / leaving a household.
- Revoking or regenerating invite codes.

---

## Questions for the Team

1. **Option A or B?** (one vs many households per user) — must be decided before writing the migration.
2. Should the owner automatically get a `Membership` row created in #3, or should the member-listing query handle it with a `UNION` / Python fallback? (The simpler approach is to create a `Membership` on household creation.)
3. What is the redirect destination after a successful join? (Placeholder dashboard is fine for now.)
