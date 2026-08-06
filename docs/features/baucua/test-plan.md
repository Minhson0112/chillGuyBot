# Test Plan: Bầu Cua Tôm Cá (cg bc)

## Verification Cases

### 1. Betting Board Initialization
*   Run command `cg bc` and verify the embed renders:
    *   Title with session number.
    *   Betting rates info.
    *   Countdown bar starts at 40s and decreases dynamically.
    *   Dropdown menu with 6 symbols (Bầu 🍇, Cua 🦀, Cá 🐟, Gà 🐓, Tôm 🦐, Nai 🦌).
    *   Dynamic board image attachment loaded and visible in chat.

### 2. Validation Checks
*   **Insufficient coins**: Place a bet higher than owned `chill_coin` and verify error message.
*   **Invalid input**: Place a negative wager and verify error message.
*   **Shorthand parsing**: Input `10k`, `1.5m`, `all` and verify they parse correctly to `10000`, `1500000`, and user's full balance.
*   **Max distinct animals**: Place a bet on 2 animals (e.g. Bầu, Cua). Attempt to place a third bet (e.g. Cá) and verify it gets rejected with an informative error message.
*   **Multiple bets on same animal**: Verify a player can add more coins to their existing animal bet.

### 3. Payout and Cleanup
*   Wait for the 40s countdown to finish. Verify:
    *   The original betting board message is deleted.
    *   A temporary shaking GIF message is sent, then deleted.
    *   A new result message is posted.
    *   It lists 3 rolled emojis.
    *   It displays a winner summary list.
    *   Winning payouts are:
        *   1 match: +1.9x
        *   2 matches: +2.8x
        *   3 matches: +4.5x
    *   Losing wagers show net loss (negative amount).
    *   Database balances are updated correctly.
