INSERT INTO server_item_master (
    name,
    type,
    price_cowoncy,
    price_chill_coin,
    is_active,
    icon_image_key,
    intimacy_points
)
SELECT
    'Chocolate',
    'gift',
    100000,
    600,
    1,
    'chocolate',
    10
WHERE NOT EXISTS (
    SELECT 1 FROM server_item_master WHERE icon_image_key = 'chocolate'
);

INSERT INTO server_item_master (
    name,
    type,
    price_cowoncy,
    price_chill_coin,
    is_active,
    icon_image_key,
    intimacy_points
)
SELECT
    'Gấu Bông',
    'gift',
    500000,
    3000,
    1,
    'bear',
    80
WHERE NOT EXISTS (
    SELECT 1 FROM server_item_master WHERE icon_image_key = 'bear'
);

INSERT INTO server_item_master (
    name,
    type,
    price_cowoncy,
    price_chill_coin,
    is_active,
    icon_image_key,
    intimacy_points
)
SELECT
    'Nhẫn Cỏ',
    'ring',
    1000000,
    6500,
    1,
    'grass_ring',
    500
WHERE NOT EXISTS (
    SELECT 1 FROM server_item_master WHERE icon_image_key = 'grass_ring'
);

INSERT INTO server_item_master (
    name,
    type,
    price_cowoncy,
    price_chill_coin,
    is_active,
    icon_image_key,
    intimacy_points
)
SELECT
    'Nhẫn Đồng',
    'ring',
    2000000,
    13000,
    1,
    'bronze_ring',
    1000
WHERE NOT EXISTS (
    SELECT 1 FROM server_item_master WHERE icon_image_key = 'bronze_ring'
);

INSERT INTO server_item_master (
    name,
    type,
    price_cowoncy,
    price_chill_coin,
    is_active,
    icon_image_key,
    intimacy_points
)
SELECT
    'Nhẫn Bạc',
    'ring',
    3000000,
    19500,
    1,
    'silver_ring',
    1500
WHERE NOT EXISTS (
    SELECT 1 FROM server_item_master WHERE icon_image_key = 'silver_ring'
);

INSERT INTO server_item_master (
    name,
    type,
    price_cowoncy,
    price_chill_coin,
    is_active,
    icon_image_key,
    intimacy_points
)
SELECT
    'Nhẫn Vàng',
    'ring',
    4000000,
    26000,
    1,
    'gold_ring',
    2000
WHERE NOT EXISTS (
    SELECT 1 FROM server_item_master WHERE icon_image_key = 'gold_ring'
);

INSERT INTO server_item_master (
    name,
    type,
    price_cowoncy,
    price_chill_coin,
    is_active,
    icon_image_key,
    intimacy_points
)
SELECT
    'Nhẫn Kim Cương',
    'ring',
    10000000,
    65000,
    1,
    'diamond_ring',
    5000
WHERE NOT EXISTS (
    SELECT 1 FROM server_item_master WHERE icon_image_key = 'diamond_ring'
);
