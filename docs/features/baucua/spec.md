# Specification: Vietnamese Bầu Cua Tôm Cá (cg bc)

## Overview
Implement a multiplayer, real-time Bầu Cua Tôm Cá game in Discord. Players can place bets on 6 symbols: Bầu, Cua, Cá, Gà, Tôm, Nai using their `chill_coin` balance.

## Requirements

### 1. Custom Discord Emojis
Use the following custom server emojis for the animal doors and rolled results:
*   **Bầu**: `<:bauxoanen:1534832016955277482>`
*   **Cua**: `<:cuaxoanen:1534832013192855552>`
*   **Nai**: `<:naixoanen:1534832015038218250>`
*   **Tôm**: `<:tomxoanen:1534831999049531482>`
*   **Gà**: `<:gaxoanen:1534832000861601842>`
*   **Cá**: `<:caxoanen:1534832002724003870>`

### 2. Game Session Command (`cg bc`)
*   Command starts a new session (e.g., Session #30).
*   **Single Active Session**: Only **one** active session can run in a channel/server at a time. If user B runs `cg bc` while a session is running, the bot replies:
    `Đã có một phiên chơi đang diễn ra, vui lòng đợi hết phiên chơi!`
*   **Betting Duration**: 40 seconds, showing a real-time countdown progress bar:
    `[▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▱▱] 32 giây`

### 3. Betting Board UI
*   The board is posted as a Discord message with an embed containing:
    *   Session Title (e.g. `🎲 PHIÊN BẦU CUA #30`)
    *   Payout rates:
        *   Trúng 1 matching dice: **x1.9**
        *   Trúng 2 matching dice: **x2.8**
        *   Trúng 3 matching dice: **x4.5**
    *   Real-time status: Number of participants and total coins wagered.
    *   A list of total bets placed on each symbol using the custom emojis.
*   **Interaction**: A select dropdown menu "Chọn cửa bạn muốn đặt cược..." showing the custom server emojis and text options.
*   **Image Attachment**: A dynamic rendering of `banco.png` displaying the current wagers written on each of the 6 cells.

### 4. Placing Bets
*   Selecting an option from the dropdown menu triggers a Modal: `Đặt cược Bầu Cua` showing the user's current wallet balance and a text field to enter the bet amount.
*   **Wager formats supported**:
    *   Plain numbers: e.g. `10000`
    *   Shorthand: e.g. `50k` (50,000), `1m` (1,000,000), `all` (user's entire balance).
*   **Bet Constraints**:
    *   Each user can bet on a maximum of **2 distinct animals** per session.
    *   **No Topping Up / Adding**: Once a player wagers on a specific animal door, they **cannot** place another wager on that same animal in this session (không được đặt đè thêm số tiền).
    *   Wagers must be positive integers.
    *   Wagers cannot exceed the user's available `chill_coin`.
*   After submitting the Modal:
    *   An ephemeral success message is sent (e.g., `Đã đặt 1,000 <:cs_coin:1495116560191324383> vào <:cuaxoanen:1534832013192855552> Cua!`).
    *   The main game board embed and attached image update in real-time.

### 5. Rolling and Results
*   **Dice shaking animation**: Once the betting timer expires, the main betting message is **deleted** and the bot sends a temporary message with `baucua.gif` to animate the dice shaking.
*   **Roll Emojis**: 3 random animals are selected (100% fair random selection from the 6 options).
*   **Result Image Rendering**: The bot generates a new image by pasting the 3 rolled transparent background animal images (e.g., `naixoanen.png`, `caxoanen.png`, etc.) onto `winer.png`.
*   **Results Message**: The bot deletes the shaking animation message and sends a new message containing:
    *   Title: `🏁 KẾT QUẢ BẦU CUA #30`
    *   The rendered result image as an attachment.
    *   Emojis of the 3 rolled results using the custom emojis.
    *   Text representation of the result.
    *   **Danh Sách Tham Gia**: A list of participants, their chosen symbol, and their win/loss outcome. E.g.:
        *   `✅ Quang Quằn Quẹo | <:cuaxoanen:1534832013192855552> | (+1,900 <:cs_coin:1495116560191324383>)`
        *   `❌ Kozzsuy | <:gaxoanen:1534832000861601842> | (-2,000 <:cs_coin:1495116560191324383>)`
