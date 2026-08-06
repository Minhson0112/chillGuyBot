# Technical Plan: Bầu Cua Tôm Cá (cg bc)

## 1. Custom Emoji Mapping
We will define the emoji mapping in the command file as follows:
```python
EMOJI_MAPPING = {
    "bau": "<:bauxoanen:1534832016955277482>",
    "cua": "<:cuaxoanen:1534832013192855552>",
    "ca": "<:caxoanen:1534832002724003870>",
    "ga": "<:gaxoanen:1534832000861601842>",
    "tom": "<:tomxoanen:1534831999049531482>",
    "nai": "<:naixoanen:1534832015038218250>",
}
```

## 2. Active Session Management
*   We will store active sessions in the `BauCua` Cog class: `self.active_sessions = {}` mapping `channel_id -> BauCuaSession`.
*   If `ctx.channel.id in self.active_sessions`, we block starting a new game and reply:
    `Đã có một phiên chơi đang diễn ra, vui lòng đợi hết phiên chơi!`

## 3. UI Layout & Embed
*   Embed details:
    ```
    🎲 PHIÊN BẦU CUA #<id>
    Tỉ lệ cược:
    • Trúng 1: x1.9 │ Trúng 2: x2.8 │ Trúng 3: x4.5

    ⏳ Thời gian cược: 32 giây
    [▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▱▱]

    👥 <count> người │ 💰 <total_coins> 
    ╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼
    <bau_emoji> Bầu :          <amount>
    <cua_emoji> Cua :          <amount>
    <ca_emoji> Cá  :          <amount>
    <ga_emoji> Gà  :          <amount>
    <tom_emoji> Tôm :          <amount>
    <nai_emoji> Nai :          <amount>
    ```
*   Select Dropdown: `Chọn cửa bạn muốn đặt cược...`
*   Attachment: Dynamically generated board image.

## 4. Betting Rules & Validations
*   Dropdown selection triggers `BauCuaBetModal`.
*   **Validation Rules**:
    1.  Max **2 distinct animals** per user in a session.
    2.  **No topping up**: If `chosen_animal in user_bets`, reject with: `Bạn không thể đặt cọc đè thêm tiền vào cửa đã chọn.`
    3.  Bet amount must be a positive integer.
    4.  Bet amount must be parsed for shorthand (e.g. `10k`, `1.5m`, `all`).
    5.  User must have enough coins.
*   Once validated, deduct `chill_coin` from `Member` profile.

## 5. Dynamic Rendering (PIL)
*   **Bet board rendering**:
    *   Load `banco.png` (1408x768).
    *   Draw the current bet numbers on top of the cells (Nai: `(235, 192)`, Bầu: `(704, 192)`, Gà: `(1173, 192)`, Cá: `(235, 576)`, Cua: `(704, 576)`, Tôm: `(1173, 576)`).
*   **Result rendering**:
    *   Load `winer.png` (1408x768).
    *   Apply auto-crop transparency to the 3 rolled items (`naixoanen.png`, etc.) using `getbbox()`, resize them keeping aspect ratio (max size `200x200`).
    *   Paste them centered in the three bamboo panels:
        *   **Dice 1**: `(385, 430)`
        *   **Dice 2**: `(704, 430)`
        *   **Dice 3**: `(1023, 430)`
