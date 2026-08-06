# Specification: PVP Duel Arena

## Overview
Implement a fun, interactive player-versus-player (PVP) command where users can challenge each other to a duel using `chill_coin` as wagers. The combat is text-based and displays funny narratives in the chat.

## Requirements

### 1. Challenge Command (`cg duel`)
*   Syntax: `cg duel @user <bet_amount>`
*   Validation:
    *   Wager must be a positive integer.
    *   Wager cannot exceed `MAX_BET` (e.g. 10 chill_coins).
    *   Both challenger and opponent must have enough `chill_coin` in their wallets.
    *   A player cannot duel themselves.
    *   A player cannot have more than one active challenge at a time.

### 2. Interaction Loop
*   When challenged, the target receives a message with an "Accept" button and a "Decline" button.
*   The challenge expires after 60 seconds if no action is taken.
*   If accepted, a simulated battle starts.
*   If declined or timed out, the challenge is cancelled.

### 3. Combat Simulation
*   The duel has a series of funny turn-based text descriptions (rounds).
*   Examples of actions:
    *   "slapping with a raw fish"
    *   "giving emotional damage by ignoring their chat"
    *   "sipping coffee nonchalantly to dodge"
*   Each user starts with 100 HP. Each round a random attack deducts random HP from the target.
*   The player whose HP drops to 0 first loses.
*   The winner receives the total pot of `chill_coin` wagers.
