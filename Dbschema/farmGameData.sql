START TRANSACTION;

INSERT INTO items (
    code,
    name,
    type_code,
    icon_image_key,
    description,
    render_scale,
    render_offset_y,
    sell_price,
    is_sellable,
    is_usable,
    is_active
) VALUES
('wheat_seed', 'hạt lúa mỳ giống', 'seed', 'item_wheat_seed', 'Hạt giống để trồng lúa mỳ', 1.0, 0, 0, 0, 1, 1),
('wheat', 'lúa mỳ', 'crop', 'item_wheat', 'lúa mỳ', 1.0, 0, 4, 1, 1, 1),

('corn_seed', 'hạt ngô giống', 'seed', 'item_corn_seed', 'Hạt giống để trồng ngô', 1.0, 0, 0, 0, 1, 1),
('corn', 'ngô', 'crop', 'item_corn', 'ngô', 1.0, 0, 10, 1, 1, 1),

('potato_seed', 'giống khoai tây', 'seed', 'item_potato_seed', 'Hạt giống để trồng khoai tây', 1.0, 0, 0, 0, 1, 1),
('potato', 'khoai tây', 'crop', 'item_potato', 'potato', 1.0, 0, 20, 1, 1, 1),

('parsnip_seed', 'hạt giống củ cải vàng', 'seed', 'item_parsnip_seed', NULL, 1.0, 0, 0, 0, 1, 1),
('parsnip', 'củ cải vàng', 'crop', 'item_parsnip', NULL, 1.0, 0, 30, 1, 1, 1),

('green_bean_seed', 'hạt giống đậu xanh', 'seed', 'item_green_bean_seed', 'hạt giống đậu xanh', 1.0, 0, 0, 0, 1, 1),
('green_bean', 'đậu xanh', 'crop', 'item_green_bean', NULL, 1.0, 0, 40, 1, 1, 1),

('hops_seed', 'hạt giống hoa bia', 'seed', 'item_hops_seed', NULL, 1.0, 0, 0, 0, 1, 1),
('hops', 'hoa bia', 'crop', 'item_hops', NULL, 1.0, 0, 50, 1, 1, 1),

('cauliflower_seed', 'hạt giống súp lơ', 'seed', 'item_cauliflower_seed', NULL, 1.0, 0, 0, 0, 1, 1),
('cauliflower', 'súp lơ', 'crop', 'item_cauliflower', NULL, 1.0, 0, 60, 1, 1, 1),

('garlic_seed', 'hạt giống tỏi', 'seed', 'item_garlic_seed', null, 1.0, 0, 0, 0, 1, 1),
('garlic', 'tỏi', 'crop', 'item_garlic', NULL, 1.0, 0, 65, 1, 1, 1),

('kale_seed', 'hạt giống cải xoăn', 'seed', 'item_kale_seed', NULL, 1.0, 0, 0, 0, 1, 1),
('kale', 'cải xoăn', 'crop', 'item_kale', NULL, 1.0, 0, 70, 1, 1, 1),

('rhubarb_seed', 'hạt giống đại hoàng', 'seed', 'item_rhubarb_seed', NULL, 1.0, 0, 0, 0, 1, 1),
('rhubarb', 'đại hoàng', 'crop', 'item_rhubarb', NULL, 1.0, 0, 80, 1, 1, 1),

('tomato_seed', 'hạt giống cà chua', 'seed', 'item_tomato_seed', NULL, 1.0, 0, 0, 0, 1, 1),
('tomato', 'cà chua', 'crop', 'item_tomato', NULL, 1.0, 0, 83, 1, 1, 1),

('melon_seed', 'hạt giống dưa lưới', 'seed', 'item_melon_seed', NULL, 1.0, 0, 0, 0, 1, 1),
('melon', 'dưa lưới', 'crop', 'item_melon', NULL, 1.0, 0, 90, 1, 1, 1)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    type_code = VALUES(type_code),
    icon_image_key = VALUES(icon_image_key),
    description = VALUES(description),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y),
    sell_price = VALUES(sell_price),
    is_sellable = VALUES(is_sellable),
    is_usable = VALUES(is_usable),
    is_active = VALUES(is_active);

INSERT INTO crops (
    code,
    name,
    seed_item_id,
    crop_item_id,
    harvest_quantity_per_plot,
    total_growth_seconds
) VALUES
(
    'wheat',
    'lúa mỳ',
    (SELECT id FROM items WHERE code = 'wheat_seed'),
    (SELECT id FROM items WHERE code = 'wheat'),
    2,
    300
),
(
    'corn',
    'ngô',
    (SELECT id FROM items WHERE code = 'corn_seed'),
    (SELECT id FROM items WHERE code = 'corn'),
    2,
    600
),
(
    'potato',
    'khoai tây',
    (SELECT id FROM items WHERE code = 'potato_seed'),
    (SELECT id FROM items WHERE code = 'potato'),
    2,
    720
),
(
    'parsnip',
    'củ cải vàng',
    (SELECT id FROM items WHERE code = 'parsnip_seed'),
    (SELECT id FROM items WHERE code = 'parsnip'),
    2,
    840
),
(
    'green_bean',
    'đậu xanh',
    (SELECT id FROM items WHERE code = 'green_bean_seed'),
    (SELECT id FROM items WHERE code = 'green_bean'),
    2,
    960
),
(
    'hops',
    'hoa bia',
    (SELECT id FROM items WHERE code = 'hops_seed'),
    (SELECT id FROM items WHERE code = 'hops'),
    2,
    1200
),
(
    'cauliflower',
    'súp lơ',
    (SELECT id FROM items WHERE code = 'cauliflower_seed'),
    (SELECT id FROM items WHERE code = 'cauliflower'),
    2,
    1320
),
(
    'garlic',
    'tỏi',
    (SELECT id FROM items WHERE code = 'garlic_seed'),
    (SELECT id FROM items WHERE code = 'garlic'),
    2,
    1500
),
(
    'kale',
    'cải xoăn',
    (SELECT id FROM items WHERE code = 'kale_seed'),
    (SELECT id FROM items WHERE code = 'kale'),
    2,
    1560
),
(
    'rhubarb',
    'đại hoàng',
    (SELECT id FROM items WHERE code = 'rhubarb_seed'),
    (SELECT id FROM items WHERE code = 'rhubarb'),
    2,
    1800
),
(
    'tomato',
    'cà chua',
    (SELECT id FROM items WHERE code = 'tomato_seed'),
    (SELECT id FROM items WHERE code = 'tomato'),
    2,
    1920
),
(
    'melon',
    'dưa lưới',
    (SELECT id FROM items WHERE code = 'melon_seed'),
    (SELECT id FROM items WHERE code = 'melon'),
    2,
    2160
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    seed_item_id = VALUES(seed_item_id),
    crop_item_id = VALUES(crop_item_id),
    harvest_quantity_per_plot = VALUES(harvest_quantity_per_plot),
    total_growth_seconds = VALUES(total_growth_seconds);

INSERT INTO crop_growth_stages (
    crop_id,
    stage_no,
    stage_start_seconds,
    image_key,
    render_scale,
    render_offset_y
) VALUES
((SELECT id FROM crops WHERE code = 'wheat'), 1, 0, 'crop_wheat_stage_1', 6, 0),
((SELECT id FROM crops WHERE code = 'wheat'), 2, 60, 'crop_wheat_stage_2', 5, -10),
((SELECT id FROM crops WHERE code = 'wheat'), 3, 200, 'crop_wheat_stage_3', 5, -15),
((SELECT id FROM crops WHERE code = 'wheat'), 4, 300, 'crop_wheat_stage_4', 5, -30),

((SELECT id FROM crops WHERE code = 'corn'), 1, 0, 'crop_corn_stage_1', 6, 0),
((SELECT id FROM crops WHERE code = 'corn'), 2, 200, 'crop_corn_stage_2', 6, -10),
((SELECT id FROM crops WHERE code = 'corn'), 3, 400, 'crop_corn_stage_3', 6, -40),
((SELECT id FROM crops WHERE code = 'corn'), 4, 600, 'crop_corn_stage_4', 6, -60),

((SELECT id FROM crops WHERE code = 'potato'), 1, 0, 'crop_potato_stage_1', 6, 0),
((SELECT id FROM crops WHERE code = 'potato'), 2, 300, 'crop_potato_stage_2', 6, -5),
((SELECT id FROM crops WHERE code = 'potato'), 3, 500, 'crop_potato_stage_3', 6, -20),
((SELECT id FROM crops WHERE code = 'potato'), 4, 720, 'crop_potato_stage_4', 6, -30),

((SELECT id FROM crops WHERE code = 'parsnip'), 1, 0, 'crop_parsnip_stage_1', 6, 0),
((SELECT id FROM crops WHERE code = 'parsnip'), 2, 400, 'crop_parsnip_stage_2', 6, -5),
((SELECT id FROM crops WHERE code = 'parsnip'), 3, 600, 'crop_parsnip_stage_3', 6, -20),
((SELECT id FROM crops WHERE code = 'parsnip'), 4, 840, 'crop_parsnip_stage_4', 6, -20),

((SELECT id FROM crops WHERE code = 'green_bean'), 1, 0, 'crop_green_bean_stage_1', 6, -45),
((SELECT id FROM crops WHERE code = 'green_bean'), 2, 450, 'crop_green_bean_stage_2', 6, -45),
((SELECT id FROM crops WHERE code = 'green_bean'), 3, 650, 'crop_green_bean_stage_3', 6, -45),
((SELECT id FROM crops WHERE code = 'green_bean'), 4, 960, 'crop_green_bean_stage_4', 6, -50),

((SELECT id FROM crops WHERE code = 'hops'), 1, 0, 'crop_hops_stage_1', 4, -35),
((SELECT id FROM crops WHERE code = 'hops'), 2, 420, 'crop_hops_stage_2', 4, -35),
((SELECT id FROM crops WHERE code = 'hops'), 3, 820, 'crop_hops_stage_3', 4, -35),
((SELECT id FROM crops WHERE code = 'hops'), 4, 1200, 'crop_hops_stage_4', 4, -35),

((SELECT id FROM crops WHERE code = 'cauliflower'), 1, 0, 'crop_cauliflower_stage_1', 6, 0),
((SELECT id FROM crops WHERE code = 'cauliflower'), 2, 400, 'crop_cauliflower_stage_2', 6, -20),
((SELECT id FROM crops WHERE code = 'cauliflower'), 3, 900, 'crop_cauliflower_stage_3', 6, 0),
((SELECT id FROM crops WHERE code = 'cauliflower'), 4, 1320, 'crop_cauliflower_stage_4', 6, 0),

((SELECT id FROM crops WHERE code = 'garlic'), 1, 0, 'crop_garlic_stage_1', 6, 0),
((SELECT id FROM crops WHERE code = 'garlic'), 2, 500, 'crop_garlic_stage_2', 6, -10),
((SELECT id FROM crops WHERE code = 'garlic'), 3, 1100, 'crop_garlic_stage_3', 6, -25),
((SELECT id FROM crops WHERE code = 'garlic'), 4, 1500, 'crop_garlic_stage_4', 6, -35),

((SELECT id FROM crops WHERE code = 'kale'), 1, 0, 'crop_kale_stage_1', 6, 0),
((SELECT id FROM crops WHERE code = 'kale'), 2, 500, 'crop_kale_stage_2', 6, -20),
((SELECT id FROM crops WHERE code = 'kale'), 3, 1000, 'crop_kale_stage_3', 6, -20),
((SELECT id FROM crops WHERE code = 'kale'), 4, 1560, 'crop_kale_stage_4', 6, -20),

((SELECT id FROM crops WHERE code = 'rhubarb'), 1, 0, 'crop_rhubarb_stage_1', 6, 0),
((SELECT id FROM crops WHERE code = 'rhubarb'), 2, 600, 'crop_rhubarb_stage_2', 6, 0),
((SELECT id FROM crops WHERE code = 'rhubarb'), 3, 1200, 'crop_rhubarb_stage_3', 6, -20),
((SELECT id FROM crops WHERE code = 'rhubarb'), 4, 1800, 'crop_rhubarb_stage_4', 6, -35),

((SELECT id FROM crops WHERE code = 'tomato'), 1, 0, 'crop_tomato_stage_1', 6, 0),
((SELECT id FROM crops WHERE code = 'tomato'), 2, 800, 'crop_tomato_stage_2', 6, -10),
((SELECT id FROM crops WHERE code = 'tomato'), 3, 1400, 'crop_tomato_stage_3', 6, -35),
((SELECT id FROM crops WHERE code = 'tomato'), 4, 1920, 'crop_tomato_stage_4', 6, -40),

((SELECT id FROM crops WHERE code = 'melon'), 1, 0, 'crop_melon_stage_1', 6, 0),
((SELECT id FROM crops WHERE code = 'melon'), 2, 720, 'crop_melon_stage_2', 6, 0),
((SELECT id FROM crops WHERE code = 'melon'), 3, 1440, 'crop_melon_stage_3', 6, -10),
((SELECT id FROM crops WHERE code = 'melon'), 4, 2160, 'crop_melon_stage_4', 5, -10)
ON DUPLICATE KEY UPDATE
    stage_start_seconds = VALUES(stage_start_seconds),
    image_key = VALUES(image_key),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y);

INSERT INTO shop_items (
    item_id,
    buy_price,
    required_farm_level,
    is_visible,
    is_active,
    sort_order
) VALUES
((SELECT id FROM items WHERE code = 'wheat_seed'), 1, 1, 1, 1, 1),
((SELECT id FROM items WHERE code = 'corn_seed'), 3, 1, 1, 1, 2),
((SELECT id FROM items WHERE code = 'potato_seed'), 4, 1, 1, 1, 3),
((SELECT id FROM items WHERE code = 'parsnip_seed'), 6, 1, 1, 1, 4),
((SELECT id FROM items WHERE code = 'green_bean_seed'), 8, 1, 1, 1, 5),
((SELECT id FROM items WHERE code = 'hops_seed'), 10, 1, 1, 1, 6),
((SELECT id FROM items WHERE code = 'cauliflower_seed'), 13, 2, 1, 1, 7),
((SELECT id FROM items WHERE code = 'garlic_seed'), 15, 2, 1, 1, 8),
((SELECT id FROM items WHERE code = 'kale_seed'), 17, 2, 1, 1, 9),
((SELECT id FROM items WHERE code = 'rhubarb_seed'), 20, 2, 1, 1, 10),
((SELECT id FROM items WHERE code = 'tomato_seed'), 25, 2, 1, 1, 11),
((SELECT id FROM items WHERE code = 'melon_seed'), 30, 2, 1, 1, 12)
ON DUPLICATE KEY UPDATE
    buy_price = VALUES(buy_price),
    required_farm_level = VALUES(required_farm_level),
    is_visible = VALUES(is_visible),
    is_active = VALUES(is_active),
    sort_order = VALUES(sort_order);

COMMIT;

START TRANSACTION;

INSERT INTO farm (
    user_id,
    farm_level,
    farm_exp,
    base_image_key,
    is_train_event
)
SELECT
    m.user_id,
    1,
    0,
    'base',
    0
FROM member m
WHERE m.leave_at IS NULL
  AND m.is_bot = 0
  AND NOT EXISTS (
      SELECT 1
      FROM farm f
      WHERE f.user_id = m.user_id
  );

INSERT INTO farm_crop_area (
    farm_id,
    unlocked_plot_count,
    status
)
SELECT
    f.id,
    1,
    'idle'
FROM farm f
WHERE NOT EXISTS (
    SELECT 1
    FROM farm_crop_area fca
    WHERE fca.farm_id = f.id
);

INSERT INTO farm_chicken_coop (
    farm_id,
    chicken_count,
    render_scale
)
SELECT
    f.id,
    0,
    1.0
FROM farm f
WHERE NOT EXISTS (
    SELECT 1
    FROM farm_chicken_coop fcc
    WHERE fcc.farm_id = f.id
);

INSERT INTO farm_cow_shed (
    farm_id,
    cow_count,
    render_scale
)
SELECT
    f.id,
    0,
    1.0
FROM farm f
WHERE NOT EXISTS (
    SELECT 1
    FROM farm_cow_shed fcs
    WHERE fcs.farm_id = f.id
);

INSERT INTO farm_fish_pond (
    farm_id
)
SELECT
    f.id
FROM farm f
WHERE NOT EXISTS (
    SELECT 1
    FROM farm_fish_pond ffp
    WHERE ffp.farm_id = f.id
);

COMMIT;

# update 1
INSERT INTO items (
    code,
    name,
    type_code,
    icon_image_key,
    description,
    render_scale,
    render_offset_y,
    sell_price,
    is_sellable,
    is_usable,
    is_active
) VALUES (
    'bug',
    'con sâu',
    'animal',
    'item_bug',
    'sâu bệnh bắt từ cây trồng',
    1.0,
    0,
    5,
    1,
    1,
    1
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    type_code = VALUES(type_code),
    icon_image_key = VALUES(icon_image_key),
    description = VALUES(description),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y),
    sell_price = VALUES(sell_price),
    is_sellable = VALUES(is_sellable),
    is_usable = VALUES(is_usable),
    is_active = VALUES(is_active);

# update 2
INSERT INTO items (
    code,
    name,
    type_code,
    icon_image_key,
    description,
    render_scale,
    render_offset_y,
    sell_price,
    is_sellable,
    is_usable,
    is_active
) VALUES
(
    'chicken',
    'con gà',
    'animal',
    'item_chicken',
    NULL,
    1.0,
    0,
    0,
    0,
    0,
    1
),
(
    'cow',
    'con bò',
    'animal',
    'item_cow',
    NULL,
    1.0,
    0,
    0,
    0,
    0,
    1
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    type_code = VALUES(type_code),
    icon_image_key = VALUES(icon_image_key),
    description = VALUES(description),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y),
    sell_price = VALUES(sell_price),
    is_sellable = VALUES(is_sellable),
    is_usable = VALUES(is_usable),
    is_active = VALUES(is_active);

INSERT INTO shop_items (
    item_id,
    buy_price,
    required_farm_level,
    is_visible,
    is_active,
    sort_order
)
SELECT
    i.id,
    6,
    1,
    1,
    1,
    14
FROM items i
WHERE i.code = 'bug'
ON DUPLICATE KEY UPDATE
    buy_price = VALUES(buy_price),
    required_farm_level = VALUES(required_farm_level),
    is_visible = VALUES(is_visible),
    is_active = VALUES(is_active),
    sort_order = VALUES(sort_order);

INSERT INTO shop_items (
    item_id,
    buy_price,
    required_farm_level,
    is_visible,
    is_active,
    sort_order
)
SELECT
    i.id,
    50,
    1,
    1,
    1,
    15
FROM items i
WHERE i.code = 'chicken'
ON DUPLICATE KEY UPDATE
    buy_price = VALUES(buy_price),
    required_farm_level = VALUES(required_farm_level),
    is_visible = VALUES(is_visible),
    is_active = VALUES(is_active),
    sort_order = VALUES(sort_order);

INSERT INTO shop_items (
    item_id,
    buy_price,
    required_farm_level,
    is_visible,
    is_active,
    sort_order
)
SELECT
    i.id,
    100,
    1,
    1,
    1,
    16
FROM items i
WHERE i.code = 'cow'
ON DUPLICATE KEY UPDATE
    buy_price = VALUES(buy_price),
    required_farm_level = VALUES(required_farm_level),
    is_visible = VALUES(is_visible),
    is_active = VALUES(is_active),
    sort_order = VALUES(sort_order);

# update 3
INSERT INTO items (
    code,
    name,
    type_code,
    icon_image_key,
    description,
    render_scale,
    render_offset_y,
    sell_price,
    is_sellable,
    is_usable,
    is_active
) VALUES
(
    'egg',
    'trứng gà',
    'animal_product',
    'item_egg',
    NULL,
    1.0,
    0,
    5,
    1,
    1,
    1
),
(
    'milk',
    'sữa bò',
    'animal_product',
    'item_milk',
    NULL,
    1.0,
    0,
    10,
    1,
    1,
    1
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    type_code = VALUES(type_code),
    icon_image_key = VALUES(icon_image_key),
    description = VALUES(description),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y),
    sell_price = VALUES(sell_price),
    is_sellable = VALUES(is_sellable),
    is_usable = VALUES(is_usable),
    is_active = VALUES(is_active);

# update 4
INSERT INTO items (
    code,
    name,
    type_code,
    icon_image_key,
    description,
    render_scale,
    render_offset_y,
    sell_price,
    is_sellable,
    is_usable,
    is_active
) VALUES
(
    'seaweed',
    'rong biển',
    'seafood',
    'item_seaweed',
    NULL,
    1.0,
    0,
    5,
    1,
    1,
    1
),
(
    'snail',
    'ốc sên',
    'seafood',
    'item_snail',
    NULL,
    1.0,
    0,
    7,
    1,
    1,
    1
),
(
    'shrimp',
    'tôm',
    'seafood',
    'item_shrimp',
    NULL,
    1.0,
    0,
    9,
    1,
    1,
    1
),
(
    'crab',
    'cua',
    'seafood',
    'item_crab',
    NULL,
    1.0,
    0,
    11,
    1,
    1,
    1
),
(
    'mussel',
    'con trai',
    'seafood',
    'item_mussel',
    NULL,
    1.0,
    0,
    12,
    1,
    1,
    1
),
(
    'halibut',
    'cá chim',
    'seafood',
    'item_halibut',
    NULL,
    1.0,
    0,
    14,
    1,
    1,
    1
),
(
    'chub',
    'cá bống',
    'seafood',
    'item_chub',
    NULL,
    1.0,
    0,
    8,
    1,
    1,
    1
),
(
    'tilapia',
    'cá rô phi',
    'seafood',
    'item_tilapia',
    NULL,
    1.0,
    0,
    13,
    1,
    1,
    1
),
(
    'sturgeon',
    'cá tầm',
    'seafood',
    'item_sturgeon',
    NULL,
    1.0,
    0,
    16,
    1,
    1,
    1
),
(
    'sea_cucumber',
    'hải sâm',
    'seafood',
    'item_sea_cucumber',
    NULL,
    1.0,
    0,
    18,
    1,
    1,
    1
),
(
    'squid',
    'con mực',
    'seafood',
    'item_squid',
    NULL,
    1.0,
    0,
    20,
    1,
    1,
    1
),
(
    'red_snapper',
    'cá chỉ vàng đỏ',
    'seafood',
    'item_red_snapper',
    NULL,
    1.0,
    0,
    22,
    1,
    1,
    1
),
(
    'octopus',
    'bạch tuộc',
    'seafood',
    'item_octopus',
    NULL,
    1.0,
    0,
    28,
    1,
    1,
    1
),
(
    'eel',
    'con lươn',
    'seafood',
    'item_eel',
    NULL,
    1.0,
    0,
    27,
    1,
    1,
    1
),
(
    'herring',
    'cá trích',
    'seafood',
    'item_herring',
    NULL,
    1.0,
    0,
    30,
    1,
    1,
    1
),
(
    'catfish',
    'cá trê',
    'seafood',
    'item_catfish',
    NULL,
    1.0,
    0,
    32,
    1,
    1,
    1
),
(
    'carp',
    'cá chép',
    'seafood',
    'item_carp',
    NULL,
    1.0,
    0,
    33,
    1,
    1,
    1
),
(
    'perch',
    'cá rô',
    'seafood',
    'item_perch',
    NULL,
    1.0,
    0,
    35,
    1,
    1,
    1
),
(
    'walleye',
    'cá vược',
    'seafood',
    'item_walleye',
    NULL,
    1.0,
    0,
    37,
    1,
    1,
    1
),
(
    'salmon',
    'cá hồi',
    'seafood',
    'item_salmon',
    NULL,
    1.0,
    0,
    40,
    1,
    1,
    1
),
(
    'bream',
    'cá mè',
    'seafood',
    'item_bream',
    NULL,
    1.0,
    0,
    42,
    1,
    1,
    1
),
(
    'sardine',
    'cá mòi',
    'seafood',
    'item_sardine',
    NULL,
    1.0,
    0,
    26,
    1,
    1,
    1
),
(
    'tuna',
    'cá ngừ',
    'seafood',
    'item_tuna',
    NULL,
    1.0,
    0,
    45,
    1,
    1,
    1
),
(
    'anchovy',
    'cá cơm',
    'seafood',
    'item_anchovy',
    NULL,
    1.0,
    0,
    41,
    1,
    1,
    1
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    type_code = VALUES(type_code),
    icon_image_key = VALUES(icon_image_key),
    description = VALUES(description),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y),
    sell_price = VALUES(sell_price),
    is_sellable = VALUES(is_sellable),
    is_usable = VALUES(is_usable),
    is_active = VALUES(is_active);

INSERT INTO items (
    code,
    name,
    type_code,
    icon_image_key,
    description,
    render_scale,
    render_offset_y,
    sell_price,
    is_sellable,
    is_usable,
    is_active
) VALUES
(
    'lobster',
    'tôm hùm',
    'seafood',
    'item_lobster',
    NULL,
    1.0,
    0,
    50,
    1,
    1,
    1
),
(
    'pufferfish',
    'cá nóc gai',
    'seafood',
    'item_pufferfish',
    NULL,
    1.0,
    0,
    45,
    1,
    1,
    1
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    type_code = VALUES(type_code),
    icon_image_key = VALUES(icon_image_key),
    description = VALUES(description),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y),
    sell_price = VALUES(sell_price),
    is_sellable = VALUES(is_sellable),
    is_usable = VALUES(is_usable),
    is_active = VALUES(is_active);

# thêm mía và hướng dương
INSERT INTO items (
    code,
    name,
    type_code,
    icon_image_key,
    description,
    render_scale,
    render_offset_y,
    sell_price,
    is_sellable,
    is_usable,
    is_active
) VALUES
(
    'sunflower_seed',
    'hạt hướng dương',
    'seed',
    'item_sunflower_seed',
    NULL,
    1.0,
    0,
    0,
    0,
    1,
    1
),
(
    'sunflower',
    'hướng dương',
    'crop',
    'item_sunflower',
    NULL,
    1.0,
    0,
    8,
    1,
    1,
    1
),
(
    'sugarcane_seed',
    'mía giống',
    'seed',
    'item_sugarcane_seed',
    NULL,
    1.0,
    0,
    0,
    0,
    1,
    1
),
(
    'sugarcane',
    'mía',
    'crop',
    'item_sugarcane',
    NULL,
    1.0,
    0,
    35,
    1,
    1,
    1
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    type_code = VALUES(type_code),
    icon_image_key = VALUES(icon_image_key),
    description = VALUES(description),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y),
    sell_price = VALUES(sell_price),
    is_sellable = VALUES(is_sellable),
    is_usable = VALUES(is_usable),
    is_active = VALUES(is_active);


INSERT INTO crops (
    code,
    name,
    seed_item_id,
    crop_item_id,
    harvest_quantity_per_plot,
    total_growth_seconds
)
SELECT
    'sunflower',
    'hướng dương',
    seedItem.id,
    cropItem.id,
    2,
    420
FROM items seedItem
JOIN items cropItem ON cropItem.code = 'sunflower'
WHERE seedItem.code = 'sunflower_seed'
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    seed_item_id = VALUES(seed_item_id),
    crop_item_id = VALUES(crop_item_id),
    harvest_quantity_per_plot = VALUES(harvest_quantity_per_plot),
    total_growth_seconds = VALUES(total_growth_seconds);


INSERT INTO crops (
    code,
    name,
    seed_item_id,
    crop_item_id,
    harvest_quantity_per_plot,
    total_growth_seconds
)
SELECT
    'sugarcane',
    'mía',
    seedItem.id,
    cropItem.id,
    2,
    900
FROM items seedItem
JOIN items cropItem ON cropItem.code = 'sugarcane'
WHERE seedItem.code = 'sugarcane_seed'
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    seed_item_id = VALUES(seed_item_id),
    crop_item_id = VALUES(crop_item_id),
    harvest_quantity_per_plot = VALUES(harvest_quantity_per_plot),
    total_growth_seconds = VALUES(total_growth_seconds);


INSERT INTO crop_growth_stages (
    crop_id,
    stage_no,
    stage_start_seconds,
    image_key,
    render_scale,
    render_offset_y
)
SELECT
    c.id,
    stageData.stage_no,
    stageData.stage_start_seconds,
    stageData.image_key,
    stageData.render_scale,
    stageData.render_offset_y
FROM crops c
JOIN (
    SELECT 1 AS stage_no, 0 AS stage_start_seconds, 'crop_sunflower_stage_1' AS image_key, 5 AS render_scale, 0 AS render_offset_y
    UNION ALL
    SELECT 2, 100, 'crop_sunflower_stage_2', 5, -20
    UNION ALL
    SELECT 3, 250, 'crop_sunflower_stage_3', 5, -40
    UNION ALL
    SELECT 4, 420, 'crop_sunflower_stage_4', 5, -40
) stageData
WHERE c.code = 'sunflower'
ON DUPLICATE KEY UPDATE
    stage_start_seconds = VALUES(stage_start_seconds),
    image_key = VALUES(image_key),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y);


INSERT INTO crop_growth_stages (
    crop_id,
    stage_no,
    stage_start_seconds,
    image_key,
    render_scale,
    render_offset_y
)
SELECT
    c.id,
    stageData.stage_no,
    stageData.stage_start_seconds,
    stageData.image_key,
    stageData.render_scale,
    stageData.render_offset_y
FROM crops c
JOIN (
    SELECT 1 AS stage_no, 0 AS stage_start_seconds, 'crop_sugarcane_stage_1' AS image_key, 5 AS render_scale, 0 AS render_offset_y
    UNION ALL
    SELECT 2, 300, 'crop_sugarcane_stage_2', 5, 0
    UNION ALL
    SELECT 3, 600, 'crop_sugarcane_stage_3', 5, -20
    UNION ALL
    SELECT 4, 900, 'crop_sugarcane_stage_4', 5, -40
) stageData
WHERE c.code = 'sugarcane'
ON DUPLICATE KEY UPDATE
    stage_start_seconds = VALUES(stage_start_seconds),
    image_key = VALUES(image_key),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y);


INSERT INTO shop_items (
    item_id,
    buy_price,
    required_farm_level,
    is_visible,
    is_active,
    sort_order
)
SELECT
    i.id,
    2,
    1,
    1,
    1,
    1
FROM items i
WHERE i.code = 'sunflower_seed'
ON DUPLICATE KEY UPDATE
    buy_price = VALUES(buy_price),
    required_farm_level = VALUES(required_farm_level),
    is_visible = VALUES(is_visible),
    is_active = VALUES(is_active),
    sort_order = VALUES(sort_order);


INSERT INTO shop_items (
    item_id,
    buy_price,
    required_farm_level,
    is_visible,
    is_active,
    sort_order
)
SELECT
    i.id,
    7,
    1,
    1,
    1,
    1
FROM items i
WHERE i.code = 'sugarcane_seed'
ON DUPLICATE KEY UPDATE
    buy_price = VALUES(buy_price),
    required_farm_level = VALUES(required_farm_level),
    is_visible = VALUES(is_visible),
    is_active = VALUES(is_active),
    sort_order = VALUES(sort_order);



# update food
    INSERT INTO items (
    code,
    name,
    type_code,
    icon_image_key,
    description,
    render_scale,
    render_offset_y,
    sell_price,
    is_sellable,
    is_usable,
    is_active
) VALUES
('cheese', 'phô mai', 'food', 'item_cheese', NULL, 1.0, 0, 15, 1, 1, 1),
('wheat_flour', 'bột mì', 'food', 'item_wheat_flour', NULL, 1.0, 0, 10, 1, 1, 1),
('oil', 'dầu ăn', 'food', 'item_oil', NULL, 1.0, 0, 15, 1, 1, 1),
('sugar', 'đường', 'food', 'item_sugar', NULL, 1.0, 0, 45, 1, 1, 1),
('fried_egg', 'trứng chiên', 'food', 'item_fried_egg', NULL, 1.0, 0, 15, 1, 1, 1),
('omelet', 'trứng ốp la', 'food', 'item_omelet', NULL, 1.0, 0, 25, 1, 1, 1),
('salad', 'salad', 'food', 'item_salad', NULL, 1.0, 0, 200, 1, 1, 1),
('cheese_cauliflower', 'súp lơ trộn phô mai', 'food', 'item_cheese_cauliflower', NULL, 1.0, 0, 100, 1, 1, 1),
('parsnip_soup', 'súp củ cải vàng', 'food', 'item_parsnip_soup', NULL, 1.0, 0, 120, 1, 1, 1),
('fried_calamari', 'mực chiên ròn', 'food', 'item_fried_calamari', NULL, 1.0, 0, 70, 1, 1, 1),
('pizza', 'pizza', 'food', 'item_pizza', NULL, 1.0, 0, 300, 1, 1, 1),
('bean_hotpot', 'đậu xanh hầm', 'food', 'item_bean_hotpot', NULL, 1.0, 0, 200, 1, 1, 1),
('carp_surprise', 'cá chép hấp', 'food', 'item_carp_surprise', NULL, 1.0, 0, 110, 1, 1, 1),
('hashbrowns', 'khoai tây chiên', 'food', 'item_hashbrowns', NULL, 1.0, 0, 125, 1, 1, 1),
('pancakes', 'pancakes', 'food', 'item_pancakes', NULL, 1.0, 0, 195, 1, 1, 1),
('salmon_dinner', 'cá hồi kiểu nhật', 'food', 'item_salmon_dinner', NULL, 1.0, 0, 235, 1, 1, 1),
('bread', 'bánh mì', 'food', 'item_bread', NULL, 1.0, 0, 52, 1, 1, 1),
('pink_cake', 'bánh kem hồng', 'food', 'item_pink_cake', NULL, 1.0, 0, 300, 1, 1, 1),
('rhubarb_pie', 'bánh đại hoàng', 'food', 'item_rhubarb_pie', NULL, 1.0, 0, 220, 1, 1, 1),
('cookie', 'bánh quy', 'food', 'item_cookie', NULL, 1.0, 0, 99, 1, 1, 1),
('spaghetti', 'spaghetti', 'food', 'item_spaghetti', NULL, 1.0, 0, 236, 1, 1, 1),
('fried_eel', 'lươn chiên tỏi', 'food', 'item_fried_eel', NULL, 1.0, 0, 147, 1, 1, 1),
('sashimi', 'sashimi', 'food', 'item_sashimi', NULL, 1.0, 0, 120, 1, 1, 1),
('maki_roll', 'cơm cuộn', 'food', 'item_maki_roll', NULL, 1.0, 0, 98, 1, 1, 1),
('ice_cream', 'kem', 'food', 'item_ice_cream', NULL, 1.0, 0, 56, 1, 1, 1),
('crab_cakes', 'bánh cua', 'food', 'item_crab_cakes', NULL, 1.0, 0, 43, 1, 1, 1),
('beer', 'bia', 'food', 'item_beer', NULL, 1.0, 0, 75, 1, 1, 1)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    type_code = VALUES(type_code),
    icon_image_key = VALUES(icon_image_key),
    description = VALUES(description),
    render_scale = VALUES(render_scale),
    render_offset_y = VALUES(render_offset_y),
    sell_price = VALUES(sell_price),
    is_sellable = VALUES(is_sellable),
    is_usable = VALUES(is_usable),
    is_active = VALUES(is_active);


INSERT INTO food_recipes (
    result_item_id,
    result_quantity,
    cooking_seconds,
    required_farm_level,
    is_active
)
SELECT
    resultItem.id,
    recipeData.result_quantity,
    recipeData.cooking_seconds,
    recipeData.required_farm_level,
    recipeData.is_active
FROM (
    SELECT 'cheese' AS result_item_code, 1 AS result_quantity, 180 AS cooking_seconds, 1 AS required_farm_level, 1 AS is_active
    UNION ALL SELECT 'wheat_flour', 1, 120, 1, 1
    UNION ALL SELECT 'oil', 1, 160, 1, 1
    UNION ALL SELECT 'sugar', 1, 240, 1, 1
    UNION ALL SELECT 'fried_egg', 1, 120, 1, 1
    UNION ALL SELECT 'omelet', 1, 180, 1, 1
    UNION ALL SELECT 'salad', 1, 160, 2, 1
    UNION ALL SELECT 'cheese_cauliflower', 1, 600, 2, 1
    UNION ALL SELECT 'parsnip_soup', 1, 780, 1, 1
    UNION ALL SELECT 'fried_calamari', 1, 1200, 1, 1
    UNION ALL SELECT 'pizza', 1, 1800, 2, 1
    UNION ALL SELECT 'bean_hotpot', 1, 1500, 1, 1
    UNION ALL SELECT 'carp_surprise', 1, 1440, 1, 1
    UNION ALL SELECT 'hashbrowns', 1, 1920, 1, 1
    UNION ALL SELECT 'pancakes', 1, 2160, 1, 1
    UNION ALL SELECT 'salmon_dinner', 1, 2040, 2, 1
    UNION ALL SELECT 'bread', 1, 240, 1, 1
    UNION ALL SELECT 'pink_cake', 1, 2400, 2, 1
    UNION ALL SELECT 'rhubarb_pie', 1, 2520, 2, 1
    UNION ALL SELECT 'cookie', 1, 420, 1, 1
    UNION ALL SELECT 'spaghetti', 1, 2700, 2, 1
    UNION ALL SELECT 'fried_eel', 1, 2160, 2, 1
    UNION ALL SELECT 'sashimi', 1, 840, 1, 1
    UNION ALL SELECT 'maki_roll', 1, 120, 1, 1
    UNION ALL SELECT 'ice_cream', 1, 180, 1, 1
    UNION ALL SELECT 'crab_cakes', 1, 540, 1, 1
    UNION ALL SELECT 'beer', 1, 420, 1, 1
) recipeData
JOIN items resultItem ON resultItem.code = recipeData.result_item_code
ON DUPLICATE KEY UPDATE
    result_quantity = VALUES(result_quantity),
    cooking_seconds = VALUES(cooking_seconds),
    required_farm_level = VALUES(required_farm_level),
    is_active = VALUES(is_active);


INSERT INTO food_recipe_ingredients (
    recipe_id,
    item_id,
    quantity
)
SELECT
    recipe.id,
    ingredientItem.id,
    ingredientData.quantity
FROM (
    SELECT 'cheese' AS result_item_code, 'milk' AS ingredient_item_code, 1 AS quantity
    UNION ALL SELECT 'wheat_flour', 'wheat', 2
    UNION ALL SELECT 'oil', 'sunflower', 1
    UNION ALL SELECT 'sugar', 'sugarcane', 1
    UNION ALL SELECT 'fried_egg', 'egg', 1
    UNION ALL SELECT 'omelet', 'egg', 1
    UNION ALL SELECT 'omelet', 'milk', 1
    UNION ALL SELECT 'salad', 'tomato', 1
    UNION ALL SELECT 'salad', 'cauliflower', 1
    UNION ALL SELECT 'salad', 'green_bean', 1
    UNION ALL SELECT 'cheese_cauliflower', 'cauliflower', 1
    UNION ALL SELECT 'cheese_cauliflower', 'cheese', 1
    UNION ALL SELECT 'parsnip_soup', 'parsnip', 2
    UNION ALL SELECT 'parsnip_soup', 'milk', 2
    UNION ALL SELECT 'fried_calamari', 'squid', 1
    UNION ALL SELECT 'fried_calamari', 'wheat_flour', 1
    UNION ALL SELECT 'fried_calamari', 'oil', 1
    UNION ALL SELECT 'pizza', 'tomato', 2
    UNION ALL SELECT 'pizza', 'wheat_flour', 2
    UNION ALL SELECT 'pizza', 'cheese', 2
    UNION ALL SELECT 'bean_hotpot', 'green_bean', 4
    UNION ALL SELECT 'carp_surprise', 'carp', 2
    UNION ALL SELECT 'hashbrowns', 'oil', 1
    UNION ALL SELECT 'hashbrowns', 'potato', 4
    UNION ALL SELECT 'pancakes', 'milk', 1
    UNION ALL SELECT 'pancakes', 'wheat_flour', 4
    UNION ALL SELECT 'pancakes', 'egg', 2
    UNION ALL SELECT 'salmon_dinner', 'salmon', 1
    UNION ALL SELECT 'salmon_dinner', 'kale', 4
    UNION ALL SELECT 'bread', 'wheat_flour', 4
    UNION ALL SELECT 'pink_cake', 'melon', 1
    UNION ALL SELECT 'pink_cake', 'wheat_flour', 1
    UNION ALL SELECT 'pink_cake', 'sugar', 1
    UNION ALL SELECT 'pink_cake', 'egg', 2
    UNION ALL SELECT 'rhubarb_pie', 'rhubarb', 2
    UNION ALL SELECT 'rhubarb_pie', 'wheat_flour', 1
    UNION ALL SELECT 'rhubarb_pie', 'sugar', 1
    UNION ALL SELECT 'cookie', 'wheat_flour', 2
    UNION ALL SELECT 'cookie', 'sugar', 1
    UNION ALL SELECT 'cookie', 'egg', 1
    UNION ALL SELECT 'spaghetti', 'tomato', 2
    UNION ALL SELECT 'spaghetti', 'wheat_flour', 2
    UNION ALL SELECT 'fried_eel', 'eel', 1
    UNION ALL SELECT 'fried_eel', 'garlic', 1
    UNION ALL SELECT 'fried_eel', 'oil', 1
    UNION ALL SELECT 'sashimi', 'salmon', 2
    UNION ALL SELECT 'maki_roll', 'tuna', 1
    UNION ALL SELECT 'maki_roll', 'seaweed', 1
    UNION ALL SELECT 'maki_roll', 'wheat', 2
    UNION ALL SELECT 'ice_cream', 'milk', 1
    UNION ALL SELECT 'ice_cream', 'sugar', 1
    UNION ALL SELECT 'crab_cakes', 'crab', 1
    UNION ALL SELECT 'crab_cakes', 'wheat_flour', 1
    UNION ALL SELECT 'crab_cakes', 'oil', 1
    UNION ALL SELECT 'beer', 'wheat', 2
    UNION ALL SELECT 'beer', 'hops', 1
) ingredientData
JOIN items resultItem ON resultItem.code = ingredientData.result_item_code
JOIN food_recipes recipe ON recipe.result_item_id = resultItem.id
JOIN items ingredientItem ON ingredientItem.code = ingredientData.ingredient_item_code
ON DUPLICATE KEY UPDATE
    quantity = VALUES(quantity);