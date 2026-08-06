# Technical Plan: PVP Duel Arena

## Technical Design

### 1. Challenge State
*   We will track active duel sessions in-memory in the `Duel` Cog class to avoid database overhead for pending requests.
*   A session maps the `challenger_id` and `opponent_id` to their respective wager amount and timestamp.

### 2. Interaction Flow
*   Create a custom `discord.ui.View` named `DuelChallengeView` with two buttons:
    *   `Accept` (ButtonStyle.green)
    *   `Decline` (ButtonStyle.red)
*   The view handles interactions. On click of `Accept`, we verify both players still have the required coins, deduct the wagers from both members, and launch the combat loop.

### 3. Combat Loop
*   A loop runs in a background task or in the interaction callback:
    *   Initialize: `hp_challenger = 100`, `hp_opponent = 100`.
    *   Rounds: Select a random player to attack. Choose a funny description from a pre-defined list. Deduct random HP (e.g. 15-30).
    *   Send round updates by editing the message or sending new messages with short delays.
    *   End: Declare the winner, add the total wagers to the winner's profile using `MemberRepository`.
