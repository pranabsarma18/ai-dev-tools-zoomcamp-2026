# Shared Household Chores Tool — Homework Scope

## Goal
Build an installable Progressive Web App (PWA) that helps family members living together share household chores fairly through scheduled rotation.

## Decisions Made

### 1. Target audience
- Family or household members living together.

### 2. Chore assignment
- Chores are assigned through automatic rotation.
- Each chore follows a fixed daily or weekly schedule.
- Responsibility moves to the next family member according to the schedule.

### 3. Chore visibility
- Use a shared household board.
- Everyone can see all chores, schedules, and the person responsible for each chore.

### 4. Completing chores
- The assigned member can mark their chore as complete.
- Other household members can optionally verify completion.

### 5. Household membership and invitations
- One person creates a household.
- The household creator shares an invite code with family members so they can join.

### 6. Missed or unfinished chores
- Unfinished chores carry forward and remain pending until the assigned person completes them.
- The regular rotation schedule continues independently.

### 7. Feature scope
Include essential chore-management features plus gamification.
- Core chore management and rotation
- Shared household board
- Completion status and optional verification
- Points, streaks, and a family leaderboard
- No reminders in the current scope

### 8. Gamification and points
- Points vary according to chore difficulty or estimated effort.
- Example: washing dishes could earn 10 points, while deep-cleaning a bathroom could earn 30 points.
- The household owner sets each chore's point value.

### 9. Permissions
- Only the household owner can create, edit, or delete chores.
- Members can view the shared board, complete assigned chores, and participate in gamification.

### 10. Leaderboard
- Show both total points and the number of completed chores.

### 11. Platform
- Build an installable Progressive Web App (PWA).
- It should work in a browser on phones and computers and support installation on compatible devices.

### 12. Authentication
- Users must register and log in before accessing household features.
- Household membership, assigned chores, and points are linked to each user's account.

## Open Decision

### Can a user belong to multiple households?
This has not been decided yet:
- **Option A — One household per user:** simpler to implement for homework.
- **Option B — Multiple households:** users can join and switch between households.

## Current Scope Summary
The project is a family-focused, account-based PWA for shared household chores. A household owner creates a household and invites family members using a code. The owner manages chores and their difficulty-based point values. Chores rotate automatically on fixed schedules, and unfinished chores remain pending until completed. All members can view the shared board, mark their own chores complete, optionally verify others' chores, and see a leaderboard based on both points and completed chore counts.

## Suggested Next Steps for Brainstorming
1. Decide whether users can belong to one or multiple households.
2. Define chore fields (for example: title, description, frequency, assigned members, point value, and next rotation date).
3. Define rotation rules precisely, including how the next person is selected.
4. Define how streaks work and when they reset.
5. Sketch the main pages and user flows.
6. Turn the agreed scope into requirements and a small implementation plan.
