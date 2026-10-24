# Backlog — Shared Household Chores Tool

Each task is self-contained: the description includes enough context to implement it without reading the others.  
Stack: Django 6, Python 3.12, uv for dependency management, SQLite for development.

---

## 1. Project setup with a passing test
Goal: Confirm the Django project boots and the test suite runs green from a fresh clone.  
Description: Register the `chores` app in `INSTALLED_APPS`, add a `urls.py` inside the app and wire it into the root URL config. Write one smoke test (e.g. `GET /` returns any HTTP response without a server error) and one plain unit test that asserts `1 + 1 == 2`, so that `uv run python manage.py test` exits with code 0. Document the one-line command to run the dev server in the module README.

---

## 2. User registration and login
Goal: Allow a new user to create an account and log in.  
Description: Use Django's built-in `User` model and `AuthenticationForm`. Create register, login, and logout views with minimal HTML templates. After registration the user is automatically logged in and redirected to a placeholder dashboard page. After logout they are redirected to the login page.

---

## 3. Household model and creation
Goal: Let an authenticated user create a named household and become its owner.  
Description: Add a `Household` model with fields: `name`, `owner` (FK to `User`), `invite_code` (a short random string, generated automatically on save), and `created_at`. Create a form and view so a logged-in user can create a household; redirect them to the household detail page on success. A user who already owns a household should not be able to create a second one (enforce this in the view for now; leave the multi-household decision open at the model level).

---

## 4. Join a household via invite code
Goal: Let a user enter an invite code to become a member of an existing household.  
Description: Add a `Membership` model with fields: `household` (FK), `user` (FK), and `joined_at`. Create a view with a short form where a logged-in user pastes an invite code; if it matches a household they are not already a member of, a `Membership` record is created. Display a clear error if the code is wrong or they are already a member. The household owner is implicitly a member and should be included when listing members.

---

## 5. Chore model
Goal: Store the definition of a chore that belongs to a household.  
Description: Add a `Chore` model with fields: `household` (FK), `title`, `description` (optional), `frequency` (choices: `daily` / `weekly`), `point_value` (positive integer), `rotation_members` (ordered list of user PKs stored as a JSON field or a through model), and `next_due_date` (date). Write model-level unit tests that verify `point_value` must be positive and `frequency` only accepts the two allowed values.

---

## 6. Chore management — create, edit, delete (owner only)
Goal: Give the household owner a UI to manage chores.  
Description: Create views for listing, creating, editing, and deleting chores, accessible only to the household owner (return 403 for everyone else). Each form lets the owner set the title, description, frequency, point value, and initial rotation order among household members. Wire up the URLs and add links to the household detail page.

---

## 7. Chore rotation logic
Goal: Compute which household member is currently responsible for a chore.  
Description: Write a pure function (no Django ORM calls, easy to unit-test) that takes a chore's rotation list, its `next_due_date`, its `frequency`, and a reference date, and returns the index of the currently responsible member. Write unit tests covering: first slot, wrap-around to the start of the list, and a chore that is overdue by more than one period. Do not wire this into views yet.

---

## 8. Shared household board
Goal: Show every household member the current state of all chores.  
Description: Create a board view (login required, members only) that lists every chore in the household with its title, frequency, point value, due date, and the name of the currently responsible member (using the rotation function from Task 7). Mark each chore as **Pending**, **Done**, or **Overdue** based on its completion status and due date. No actions are needed on this page yet.

---

## 9. Mark a chore as complete
Goal: Let the assigned member record that they finished their chore.  
Description: Add a `ChoreCompletion` model with fields: `chore` (FK), `completed_by` (FK to `User`), `completed_at`, and `verified` (boolean, default `False`). Add a button on the board (visible only to the currently assigned member) that creates a `ChoreCompletion` record and advances the chore's `next_due_date` by one period. Prevent duplicate completions for the same period.

---

## 10. Verify chore completion
Goal: Let any other household member confirm that a chore was actually done.  
Description: When a `ChoreCompletion` record exists and `verified` is `False`, show a "Verify" button to every household member except the person who completed it. Clicking it sets `verified = True`. The board view should display a visual distinction between unverified and verified completions (e.g. a label or icon).

---

## 11. Carry-forward pending chores
Goal: Ensure an unfinished chore remains visible as pending even after its due date passes.  
Description: Write a management command (`python manage.py carry_forward_chores`) that scans all chores whose `next_due_date` is in the past and that have no `ChoreCompletion` for the current period, and marks them as overdue in-place (do not advance the due date). The board view from Task 8 should already display the **Overdue** state. Write a unit test for the command using a fixed reference date.

---

## 12. Points tracking
Goal: Award points to a user each time a verified chore completion is recorded.  
Description: Add a `points` integer field (default `0`) to the `Membership` model. When a `ChoreCompletion` is created, add the chore's `point_value` to the completing member's `points`. If the completion is later verified (Task 10), add a bonus of 10 % of the `point_value` (rounded down). Write unit tests for both the base award and the verification bonus.

---

## 13. Streaks
Goal: Track how many consecutive periods a member has completed their assigned chore without missing one.  
Description: Add a `current_streak` integer field (default `0`) to `Membership`. When a `ChoreCompletion` is saved, increment the streak for the completing member on that chore. When the carry-forward command (Task 11) marks a chore overdue and the assigned member did not complete it, reset their streak for that chore to `0`. Write unit tests covering: streak increment, streak reset after a miss, and streak unaffected when a different member completes a different chore.

---

## 14. Leaderboard
Goal: Show a ranked list of household members by points and completed chore count.  
Description: Create a leaderboard view (login required, members only) that lists every member of the household ranked by total points descending, with a secondary sort by number of completed chores. Display name, total points, completed chore count, and current streak for each member. Link to this view from the household board.

---

## 15. PWA — web app manifest and service worker
Goal: Make the app installable on phones and desktops as a Progressive Web App.  
Description: Add a `manifest.json` (name, short name, start URL, display `standalone`, theme colour, background colour, and at least one icon) served from a static files URL. Register a minimal service worker via a `<script>` tag in the base template that caches the app shell on install so the home page loads when offline. Verify the "Install" prompt appears in Chrome DevTools Application tab with no manifest errors.

---

## Notes

- Tasks 1–4 lay the foundation (project, auth, households).  
- Tasks 5–8 build the core data layer and read-only board.  
- Tasks 9–11 add the action layer (complete, verify, carry-forward).  
- Tasks 12–14 add gamification.  
- Task 15 adds PWA capabilities last, since it is independent of all business logic.
