START TRANSACTION;

INSERT INTO giftcodes (
    code,
    reward_chill_coin,
    expired_at
)
VALUES (
    'chillfarm',
    1000,
    '2026-07-04'
)
ON DUPLICATE KEY UPDATE
    reward_chill_coin = VALUES(reward_chill_coin),
    expired_at = VALUES(expired_at),
    id = LAST_INSERT_ID(id);

SET @giftcode_id = LAST_INSERT_ID();

INSERT INTO giftcode_rewards (
    giftcode_id,
    item_id,
    quantity
)
SELECT
    @giftcode_id,
    id,
    1
FROM items
WHERE code = 'iron_rod'
ON DUPLICATE KEY UPDATE
    quantity = VALUES(quantity);

COMMIT;
