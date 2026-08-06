# Tasks: Bầu Cua Tôm Cá (cg bc)

- [ ] Create Bầu Cua command file `bot/commands/minigame/baucua.py`
- [ ] Define symbols, emojis, and paths to assets (in `bot/config/imagePaths.py` or directly in code)
- [ ] Implement `BauCuaSession` model to track channel sessions and active bets
- [ ] Implement `BauCuaView` select dropdown with Bầu Cua emojis and callbacks
- [ ] Implement `BauCuaBetModal` with input validations, parsing shorthand (`k`, `m`, `all`), and 2-animal limit
- [ ] Implement dynamic board rendering using PIL to write bets on `banco.png` cells
- [ ] Implement real-time countdown task updating progress bar, betting stats, and board image
- [ ] Implement dice roll logic (100% fair random)
- [ ] Implement result image rendering: overlay transparent assets on `winer.png`
- [ ] Implement result message listing winners, dice emojis, and payout rates
- [ ] Register `bot.commands.minigame.baucua` in `bot/main.py`
