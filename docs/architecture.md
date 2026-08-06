# ChillGuyBot Architecture

## Overview
ChillGuyBot is a Discord bot built with `discord.py`. It features a mini-farming game, custom voice/chat tracking, minigames (slot, blackjack, coinflip, bingo, mine, merge game), a couple/proposal system, and a quiz game.

## Project Structure
- `bot/main.py`: Entry point. Registers commands, tasks, events, and persistent views.
- `bot/commands/`: Cog-based commands organized by feature (e.g. `farm`, `funny`, `minigame`, `quiz`, `server`, `wordChain`).
- `bot/models/`: SQLAlchemy database models.
- `bot/repository/`: Data Access Layer (DAL) wrapping SQLAlchemy sessions.
- `bot/services/`: Business logic services that interact with repositories and external APIs.
- `bot/tasks/`: Background asyncio tasks (e.g. daily resets, voice state checks, starvation events).
- `bot/events/`: Event handlers for discord events (e.g. member joins, messages, voice state updates).
- `bot/views/`: Discord interactive UI components (Buttons, Select Menus, Modals).
- `bot/config/`: Configuration parameters (channel IDs, emojis, DB session getter).
