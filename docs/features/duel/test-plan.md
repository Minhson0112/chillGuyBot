# Test Plan: PVP Duel Arena

## Verification Steps
1.  **Challenge Command**: Run `cg duel @user 100` and check if the embed appears.
2.  **Validation checks**:
    *   Verify player cannot challenge themselves.
    *   Verify challenge fails if challenger does not have enough `chill_coin`.
    *   Verify target player cannot accept if they don't have enough `chill_coin`.
3.  **Accept Challenge**: Click the Accept button, verify wagers are deducted, combat is animated, winner is declared, and winner's coins are updated.
4.  **Decline Challenge**: Click Decline, verify challenge is marked as cancelled.
5.  **Timeout**: Challenge is left for 60s, verify buttons disable.
