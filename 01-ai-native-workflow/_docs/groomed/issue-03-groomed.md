# Issue #3 — Household Model and Creation (Groomed)

## Goal
Let an authenticated user create a named household and become its owner.

---

## Dependencies

| Dependency | Status |
|---|---|
| #1 — Project setup | ✅ Done |
| #2 — User registration & login | ⬜ Not started |

> [!IMPORTANT]
> Requires #2 so that the "create household" view can use `request.user` as the owner, and so there is a login page to redirect to.

---

## Model

```python
import secrets

class Household(models.Model):
    name        = models.CharField(max_length=100)
    owner       = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.CASCADE,
                      related_name="owned_households",
                  )
    invite_code = models.CharField(max_length=32, unique=True, editable=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = secrets.token_urlsafe(8)  # ~11 chars, URL-safe
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
```

> [!NOTE]
> `invite_code` uses `secrets.token_urlsafe` (stdlib, no new dependency). `unique=True` prevents collision — a retry loop may be added later if needed, but collisions are negligible at this scale.

---

## Open Decision — Multi-Household (Must Resolve Here or in #4)

The task says *"leave the multi-household decision open at the model level"* — meaning **no model-level constraint** on how many households a user can own. The view enforces the single-household rule for now:

```python
if Household.objects.filter(owner=request.user).exists():
    # show error or redirect
```

This decision must be finalised in **#4** before writing the `Membership` migration.

---

## Views & URLs

| View | URL | Auth |
|---|---|---|
| `create_household` | `GET/POST /households/create/` | login required |
| `household_detail` | `GET /households/<pk>/` | login required, member only |

### Flow

```
GET  /households/create/  → render form
POST /households/create/  → validate → save → redirect to /households/<pk>/
  └─ if user already owns a household → show error (do not save)
```

---

## Acceptance Criteria

- [ ] `Household` model exists with `name`, `owner` (FK), `invite_code` (auto-generated, unique), and `created_at`.
- [ ] Migration applies cleanly.
- [ ] `invite_code` is generated automatically on first save and is never empty.
- [ ] Two households cannot share the same `invite_code` (DB unique constraint).
- [ ] A logged-in user can submit the create-household form.
  - [ ] On success, a `Household` row is created and user is redirected to the detail page.
  - [ ] If the user already owns a household, creation is blocked with a clear message.
- [ ] The household detail page shows at least: name, invite code, owner name.
- [ ] Both views require login.
- [ ] `uv run python manage.py test` exits 0 with all new tests passing.

---

## Tests to Write

| Test | Type |
|---|---|
| `invite_code` is auto-populated on save | Unit (model) |
| Two saves don't overwrite an existing `invite_code` | Unit (model) |
| Owner can create a household; redirect to detail page | Integration |
| Owner blocked from creating a second household | Integration |
| Anonymous user redirected to login | Integration |
| Detail page shows household name and invite code | Integration |

---

## Open Questions

1. Should creating a household also create a `Membership` row for the owner (so that #4's member listing is uniform)? **Recommended: yes** — create the `Membership` in a `post_save` signal or inside the view, after the `Household` is saved. Resolve this before starting #4.
2. What length / format should `invite_code` be? `secrets.token_urlsafe(8)` gives ~11 chars. A shorter, human-typeable code (e.g. 6 uppercase letters) might be friendlier. Decide before writing the model test.
3. Should the detail page be accessible to non-members at this stage, or gated to members? (Members gate comes fully in #4/#8; for now, owner-only is fine.)

---

## Out of Scope

- Editing or deleting a household.
- Regenerating the invite code.
- Household membership listing (that's #4).
