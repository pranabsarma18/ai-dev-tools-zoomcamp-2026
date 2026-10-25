# Issue #2 — User Registration and Login (Groomed)

## Goal
Allow a new user to create an account and log in.

---

## Dependencies

| Dependency | Status |
|---|---|
| #1 — Project setup | ✅ Done |

---

## Implementation Notes

Use Django's built-in `User` model (no custom user model needed). No new database models are required — Django's `auth` tables are already present.

### Views to Create

| View | URL | Template |
|---|---|---|
| `register` | `GET/POST /register/` | `chores/register.html` |
| `login` | `GET/POST /login/` | `chores/login.html` |
| `logout` | `POST /logout/` | — (redirect only) |
| `dashboard` | `GET /dashboard/` | `chores/dashboard.html` (placeholder) |

### Auth Flow

```
Register → auto-login → redirect to /dashboard/
Login    →             redirect to /dashboard/
Logout   →             redirect to /login/
```

### Key Django Helpers to Use

- `UserCreationForm` for registration (provides password validation and confirmation).
- `AuthenticationForm` + `login()` for the login view (as specified in the task).
- `logout()` for the logout view.
- `login_required` decorator on the dashboard.

---

## Acceptance Criteria

- [ ] `GET /register/` renders a registration form.
- [ ] `POST /register/` with valid data:
  - [ ] Creates a new `User` record.
  - [ ] Automatically logs the user in.
  - [ ] Redirects to `/dashboard/`.
- [ ] `POST /register/` with invalid data (e.g. mismatched passwords) re-renders the form with errors.
- [ ] `GET /login/` renders a login form.
- [ ] `POST /login/` with valid credentials logs the user in and redirects to `/dashboard/`.
- [ ] `POST /login/` with invalid credentials re-renders the form with an error.
- [ ] `POST /logout/` logs the user out and redirects to `/login/`.
- [ ] `/dashboard/` requires login; anonymous users are redirected to `/login/`.
- [ ] `uv run python manage.py test` exits 0 with all new tests passing.

---

## Tests to Write

| Test | Type |
|---|---|
| Valid registration creates user, logs in, redirects to dashboard | Integration |
| Invalid registration (password mismatch) shows form errors | Integration |
| Valid login redirects to dashboard | Integration |
| Invalid login shows form error | Integration |
| Logout redirects to login page | Integration |
| Anonymous access to dashboard redirects to login | Integration |

---

## Open Questions

1. Should the registration form use `UserCreationForm` (username + password) or also collect `email`? The task says "use Django's built-in `User` model", so `UserCreationForm` (username only) is the safe default unless email is wanted.
2. Is there a `next` redirect parameter to honour after login (standard Django behaviour)? Recommended: yes, use `next` so later protected views redirect correctly.
3. Should the dashboard stub display the username or just be an empty page?

---

## Out of Scope

- Email verification.
- Password reset.
- Social auth.
- Household-specific UI on the dashboard (that comes in #3 / #8).
