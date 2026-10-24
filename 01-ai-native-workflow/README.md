# Module 01 — AI-Native Workflow

This module covers the AI-native development workflow: using AI tools to brainstorm, plan, design, and build a project from scratch.

## 🏠 Homework Project — Shared Household Chores Tool

A family-focused, account-based **Progressive Web App (PWA)** that helps household members share chores fairly through automatic rotation, gamification, and a shared leaderboard.

### Key Features

- **Household management** — One person creates a household and shares an invite code with family members.
- **Chore rotation** — Chores follow a fixed daily or weekly schedule; responsibility rotates automatically to the next member.
- **Shared board** — Everyone can see all chores, schedules, and who is responsible for each one.
- **Completion & verification** — The assigned member marks their chore complete; others can optionally verify it.
- **Missed chores** — Unfinished chores remain pending until completed; rotation continues independently.
- **Gamification** — Points (weighted by difficulty), streaks, and a family leaderboard showing both total points and completed chore counts.
- **Permissions** — Only the household owner can create, edit, or delete chores.
- **Authentication** — Users register and log in; all data is linked to their account.
- **PWA** — Installable on phones and computers, works in any browser.

### Decisions Made

| # | Topic | Decision |
|---|-------|----------|
| 1 | Target audience | Family or household members living together |
| 2 | Chore assignment | Automatic rotation on a fixed schedule |
| 3 | Chore visibility | Shared household board visible to all members |
| 4 | Completing chores | Assigned member marks complete; others can verify |
| 5 | Household membership | Creator shares an invite code for others to join |
| 6 | Missed chores | Carry forward until completed; rotation continues |
| 7 | Feature scope | Core management + gamification; no reminders |
| 8 | Points | Vary by chore difficulty; set by the household owner |
| 9 | Permissions | Owner manages chores; members participate |
| 10 | Leaderboard | Shows total points and completed chore count |
| 11 | Platform | Installable PWA, browser on phones and computers |
| 12 | Authentication | Register/login required; data linked to account |

### Open Decision

**Can a user belong to multiple households?**
- **Option A — One household per user:** simpler to implement for homework.
- **Option B — Multiple households:** users can join and switch between households.

### Next Steps

1. Decide whether users can belong to one or multiple households.
2. Define chore fields (title, description, frequency, assigned members, point value, next rotation date).
3. Define rotation rules precisely (how the next person is selected).
4. Define how streaks work and when they reset.
5. Sketch the main pages and user flows.
6. Turn the agreed scope into requirements and a small implementation plan.

### Project Files

```
01-ai-native-workflow/
├── README.md          # This file
└── _docs/
    └── plan.md        # Full brainstorming notes and decisions
```
