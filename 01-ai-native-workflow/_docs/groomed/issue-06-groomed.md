# Issue #6 — Chore Management — Create, Edit, Delete (Owner Only) (Groomed)

## Goal
Give the household owner a UI to manage chores.

---

## Dependencies

| Dependency | Status |
|---|---|
| #1 — Project setup | ✅ Done |
| #2 — User registration & login | ⬜ Not started |
| #3 — Household model | ⬜ Not started |
| #4 — Membership model | ⬜ Not started |
| #5 — Chore model | ⬜ Not started |

---

## Views & URLs

| View | Method | URL | Permission |
|---|---|---|---|
| `chore_list` | GET | `/households/<pk>/chores/` | login + member |
| `chore_create` | GET/POST | `/households/<pk>/chores/create/` | login + **owner only** |
| `chore_edit` | GET/POST | `/households/<pk>/chores/<chore_pk>/edit/` | login + **owner only** |
| `chore_delete` | POST | `/households/<pk>/chores/<chore_pk>/delete/` | login + **owner only** |

> [!IMPORTANT]
> Non-owner authenticated users (including household members) must receive **HTTP 403**, not a redirect. Anonymous users must be redirected to the login page.

---

## Permission Helper

A reusable decorator or mixin is recommended:

```python
def owner_required(view_func):
    """Return 403 if the logged-in user is not the household owner."""
    ...
```

This keeps permission logic DRY across create/edit/delete views.

---

## Form

`ChoreForm` based on `ModelForm` for `Chore`, exposing:
- `title`
- `description`
- `frequency` (select from `Frequency.choices`)
- `point_value`
- `next_due_date` (date picker)
- `rotation_members` — ordered selection of current household members

> [!NOTE]
> The `rotation_members` field stores an ordered list of user PKs. The form widget needs to let the owner pick **and order** household members. A multi-select widget with a note about order is the minimum viable approach; a drag-and-drop list can come later.

---

## Acceptance Criteria

- [ ] Chore list page (`GET /households/<pk>/chores/`) shows all chores for the household.
- [ ] Owner can access the create, edit, and delete views.
- [ ] Non-owner member receives **403** on create, edit, and delete.
- [ ] Anonymous user is redirected to login.
- [ ] Create form saves all fields and redirects to the chore list.
- [ ] Edit form pre-fills existing values and saves changes.
- [ ] Delete removes the chore (POST only; no GET delete).
- [ ] The household detail page (from #3) links to the chore list and create form (owner only).
- [ ] `uv run python manage.py test` exits 0 with all new tests passing.

---

## Tests to Write

| Test | Type |
|---|---|
| Owner can create a chore | Integration |
| Member receives 403 on create | Integration |
| Anonymous redirected to login on create | Integration |
| Owner can edit a chore | Integration |
| Member receives 403 on edit | Integration |
| Owner can delete a chore | Integration |
| Member receives 403 on delete | Integration |
| Chore list shows all chores for the household | Integration |

---

## Open Questions

1. Should the chore list be restricted to **owners only** or visible to all **members**? The task says list is accessible to the owner — but the board (#8) will also show chores to all members. For UX consistency, the chore **list** should probably be member-visible (read-only), with create/edit/delete links shown only to the owner. **Decide before writing the list view.**
2. How should `rotation_members` ordering be set in the form? Minimum viable: a `<select multiple>` widget with a note that order matters. Confirm before building the form.
3. Can the owner add a chore with an empty `rotation_members` list? (Rotation with no members is meaningless.) Should the form validate that at least one member is selected?

---

## Out of Scope

- Chore completion (that's #9).
- The board view (that's #8).
- Rotation logic (that's #7).
