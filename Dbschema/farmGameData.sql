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

#data daily
INSERT INTO daily_checkin_rewards (
    streak_day,
    reward_chill_coin,
    reward_item_id,
    reward_item_quantity,
    is_active
)
SELECT
    reward_data.streak_day,
    reward_data.reward_chill_coin,
    items.id,
    reward_data.reward_item_quantity,
    1
FROM (
    SELECT 1 AS streak_day, 10 AS reward_chill_coin, 'bug' AS reward_item_code, 3 AS reward_item_quantity
    UNION ALL
    SELECT 2, 20, 'cheese', 2
    UNION ALL
    SELECT 3, 30, 'wheat_flour', 4
    UNION ALL
    SELECT 4, 40, 'oil', 3
    UNION ALL
    SELECT 5, 50, 'sugar', 3
    UNION ALL
    SELECT 6, 60, 'salmon', 1
    UNION ALL
    SELECT 7, 70, 'ice_cream', 1
) reward_data
INNER JOIN items
    ON items.code = reward_data.reward_item_code
ON DUPLICATE KEY UPDATE
    reward_chill_coin = VALUES(reward_chill_coin),
    reward_item_id = VALUES(reward_item_id),
    reward_item_quantity = VALUES(reward_item_quantity),
    is_active = VALUES(is_active);

# data daily task
INSERT INTO daily_task_masters (
    task_code,
    task_name,
    description,
    task_type,
    target_item_id,
    target_crop_id,
    target_channel_id,
    required_value,
    reward_chill_coin,
    reward_exp,
    min_farm_level,
    weight,
    is_active
)
SELECT
    task_data.task_code,
    task_data.task_name,
    task_data.description,
    task_data.task_type,
    items.id AS target_item_id,
    crops.id AS target_crop_id,
    task_data.target_channel_id,
    task_data.required_value,
    task_data.reward_chill_coin,
    task_data.reward_exp,
    task_data.min_farm_level,
    task_data.weight,
    task_data.is_active
FROM (
    SELECT
        'chat_general_20' AS task_code,
        'trò chuyện 20 tin nhắn' AS task_name,
        'gửi 20 tin nhắn trong kênh chat chung' AS description,
        'chat_message' AS task_type,
        NULL AS target_item_code,
        NULL AS target_crop_code,
        1356994232857923827 AS target_channel_id,
        20 AS required_value,
        30 AS reward_chill_coin,
        10 AS reward_exp,
        1 AS min_farm_level,
        90 AS weight,
        1 AS is_active

    UNION ALL
    SELECT 'voice_any_5_minutes', 'vào voice 5 phút', 'kết nối voice bất kỳ trong tổng cộng 5 phút', 'voice_time', NULL, NULL, NULL, 300, 35, 10, 1, 60, 1

    UNION ALL
    SELECT 'plant_sunflower_4', 'trồng 4 hướng dương', 'trồng 4 cây hướng dương trong farm', 'plant_crop', NULL, 'sunflower', NULL, 4, 35, 12, 1, 70, 1

    UNION ALL
    SELECT 'plant_sugarcane_4', 'trồng 4 mía', 'trồng 4 cây mía trong farm', 'plant_crop', NULL, 'sugarcane', NULL, 4, 35, 12, 1, 70, 1

    UNION ALL
    SELECT 'plant_wheat_4', 'trồng 4 lúa mì', 'trồng 4 cây lúa mì trong farm', 'plant_crop', NULL, 'wheat', NULL, 4, 25, 12, 1, 60, 1

    UNION ALL
    SELECT 'plant_green_bean_4', 'trồng 4 đậu xanh', 'trồng 4 cây đậu xanh trong farm', 'plant_crop', NULL, 'green_bean', NULL, 4, 35, 13, 1, 50, 1

    UNION ALL
    SELECT 'sell_market_any_1', 'đăng bán 1 món ở shop riêng', 'đăng bán 1 món bất kỳ lên shop cá nhân', 'sell_market_item', NULL, NULL, NULL, 1, 45, 14, 1, 80, 1

    UNION ALL
    SELECT 'fishing_3', 'câu cá 3 lần', 'câu cá tổng cộng 3 lần', 'fishing', NULL, NULL, NULL, 3, 25, 10, 1, 80, 1

    UNION ALL
    SELECT 'cooking_cheese_2', 'nấu 2 phô mai', 'bắt đầu nấu 2 phô mai', 'cooking', 'cheese', NULL, NULL, 2, 45, 15, 1, 60, 1

    UNION ALL
    SELECT 'cooking_oil_2', 'nấu 2 dầu ăn', 'bắt đầu nấu 2 dầu ăn', 'cooking', 'oil', NULL, NULL, 2, 45, 15, 1, 60, 1

    UNION ALL
    SELECT 'cooking_wheat_flour_4', 'nấu 4 bột mì', 'bắt đầu nấu 4 bột mì', 'cooking', 'wheat_flour', NULL, NULL, 4, 45, 15, 1, 60, 1

    UNION ALL
    SELECT 'cooking_sugar_2', 'nấu 2 đường', 'bắt đầu nấu 2 đường', 'cooking', 'sugar', NULL, NULL, 2, 45, 15, 1, 60, 1

    UNION ALL
    SELECT 'train_delivery_1', 'hoàn thành 1 đơn tàu hỏa', 'chất hàng lên tàu hỏa thành công 1 lần', 'train_delivery', NULL, NULL, NULL, 1, 50, 20, 1, 50, 1

    UNION ALL
    SELECT 'pest_remove_1', 'bắt sâu 1 lần', 'bắt sâu cho cây trồng 1 lần', 'pest_remove', NULL, NULL, NULL, 1, 15, 6, 1, 60, 1

    UNION ALL
    SELECT 'buy_market_any_1', 'mua 1 món từ shop người chơi', 'mua 1 món bất kỳ từ shop cá nhân của người chơi khác', 'buy_market_item', NULL, NULL, NULL, 1, 30, 20, 1, 60, 1

    UNION ALL
    SELECT 'egg_collect_1', 'lấy trứng 1 lần', 'lấy trứng từ chuồng gà 1 lần', 'egg_collect', 'egg', NULL, NULL, 1, 40, 4, 1, 70, 1

    UNION ALL
    SELECT 'milk_collect_1', 'vắt sữa 1 lần', 'vắt sữa từ chuồng bò 1 lần', 'milk_collect', 'milk', NULL, NULL, 1, 45, 4, 1, 70, 1
) task_data
LEFT JOIN items
    ON items.code = task_data.target_item_code
LEFT JOIN crops
    ON crops.code = task_data.target_crop_code
WHERE (
    task_data.target_item_code IS NULL
    OR items.id IS NOT NULL
)
AND (
    task_data.target_crop_code IS NULL
    OR crops.id IS NOT NULL
)
ON DUPLICATE KEY UPDATE
    task_name = VALUES(task_name),
    description = VALUES(description),
    task_type = VALUES(task_type),
    target_item_id = VALUES(target_item_id),
    target_crop_id = VALUES(target_crop_id),
    target_channel_id = VALUES(target_channel_id),
    required_value = VALUES(required_value),
    reward_chill_coin = VALUES(reward_chill_coin),
    reward_exp = VALUES(reward_exp),
    min_farm_level = VALUES(min_farm_level),
    weight = VALUES(weight),
    is_active = VALUES(is_active);

#gift 
START TRANSACTION;

INSERT INTO giftcodes (
    code,
    reward_chill_coin,
    expired_at
)
VALUES (
    'chillstation',
    50,
    '2099-12-31'
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
VALUES (
    @giftcode_id,
    1,
    10
)
ON DUPLICATE KEY UPDATE
    quantity = VALUES(quantity);

COMMIT;


# big udate thêm cây
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
)
VALUES
    ('hot_pepper_seed', 'hạt giống ớt', 'seed', 'item_hot_pepper_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('hot_pepper', 'ớt', 'crop', 'item_hot_pepper', '', 1.0, 0, 100, 1, 1, 1),

    ('red_cabbage_seed', 'hạt bắp cải đỏ', 'seed', 'item_red_cabbage_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('red_cabbage', 'bắp cải đỏ', 'crop', 'item_red_cabbage', '', 1.0, 0, 115, 1, 1, 1),

    ('yam_seed', 'khoai lang giống', 'seed', 'item_yam_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('yam', 'khoai lang', 'crop', 'item_yam', '', 1.0, 0, 125, 1, 1, 1),

    ('cranberry_seed', 'hạt nam việt quất', 'seed', 'item_cranberry_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('cranberry', 'nam việt quất', 'crop', 'item_cranberry', '', 1.0, 0, 142, 1, 1, 1),

    ('pumpkin_seed', 'hạt bí ngô', 'seed', 'item_pumpkin_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('pumpkin', 'bí ngô', 'crop', 'item_pumpkin', '', 1.0, 0, 163, 1, 1, 1),

    ('artichoke_seed', 'hạt atisô', 'seed', 'item_artichoke_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('artichoke', 'atisô', 'crop', 'item_artichoke', '', 1.0, 0, 175, 1, 1, 1),

    ('blueberry_seed', 'hạt việt quất', 'seed', 'item_blueberry_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('blueberry', 'việt quất', 'crop', 'item_blueberry', '', 1.0, 0, 189, 1, 1, 1),

    ('strawberry_seed', 'hạt dâu tây', 'seed', 'item_strawberry_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('strawberry', 'dâu tây', 'crop', 'item_strawberry', '', 1.0, 0, 196, 1, 1, 1),

    ('eggplant_seed', 'hạt cà tím', 'seed', 'item_eggplant_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('eggplant', 'cà tím', 'crop', 'item_eggplant', '', 1.0, 0, 227, 1, 1, 1),

    ('grape_seed', 'hạt nho', 'seed', 'item_grape_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('grape', 'nho', 'crop', 'item_grape', '', 1.0, 0, 241, 1, 1, 1),

    ('bok_choy_seed', 'hạt cải thìa', 'seed', 'item_bok_choy_seed', '', 1.0, 0, 0, 0, 1, 1),
    ('bok_choy', 'rau cải thìa', 'crop', 'item_bok_choy', '', 1.0, 0, 253, 1, 1, 1)
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
    src.code,
    src.name,
    seed_item.id,
    crop_item.id,
    src.harvest_quantity_per_plot,
    src.total_growth_seconds
FROM (
    SELECT 'hot_pepper' AS code, 'ớt' AS name, 'hot_pepper_seed' AS seed_item_code, 'hot_pepper' AS crop_item_code, 2 AS harvest_quantity_per_plot, 2400 AS total_growth_seconds
    UNION ALL SELECT 'red_cabbage', 'bắp cải đỏ', 'red_cabbage_seed', 'red_cabbage', 2, 2700
    UNION ALL SELECT 'yam', 'khoai lang', 'yam_seed', 'yam', 2, 3300
    UNION ALL SELECT 'cranberry', 'nam việt quất', 'cranberry_seed', 'cranberry', 2, 3720
    UNION ALL SELECT 'pumpkin', 'bí ngô', 'pumpkin_seed', 'pumpkin', 2, 4380
    UNION ALL SELECT 'artichoke', 'atisô', 'artichoke_seed', 'artichoke', 2, 5160
    UNION ALL SELECT 'blueberry', 'việt quất', 'blueberry_seed', 'blueberry', 2, 5400
    UNION ALL SELECT 'strawberry', 'dâu tây', 'strawberry_seed', 'strawberry', 2, 5760
    UNION ALL SELECT 'eggplant', 'cà tím', 'eggplant_seed', 'eggplant', 2, 6720
    UNION ALL SELECT 'grape', 'nho', 'grape_seed', 'grape', 2, 7440
    UNION ALL SELECT 'bok_choy', 'rau cải thìa', 'bok_choy_seed', 'bok_choy', 2, 7800
) src
JOIN items seed_item ON seed_item.code = src.seed_item_code
JOIN items crop_item ON crop_item.code = src.crop_item_code
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
    crops.id,
    src.stage_no,
    src.stage_start_seconds,
    src.image_key,
    src.render_scale,
    src.render_offset_y
FROM (
    SELECT 'hot_pepper' AS crop_code, 1 AS stage_no, 0 AS stage_start_seconds, 'crop_hot_pepper_stage_1' AS image_key, 5 AS render_scale, 0 AS render_offset_y
    UNION ALL SELECT 'hot_pepper', 2, 800, 'crop_hot_pepper_stage_2', 5, -10
    UNION ALL SELECT 'hot_pepper', 3, 1600, 'crop_hot_pepper_stage_3', 5, -20
    UNION ALL SELECT 'hot_pepper', 4, 2400, 'crop_hot_pepper_stage_4', 5, -25

    UNION ALL SELECT 'red_cabbage', 1, 0, 'crop_red_cabbage_stage_1', 5, 0
    UNION ALL SELECT 'red_cabbage', 2, 900, 'crop_red_cabbage_stage_2', 5, 0
    UNION ALL SELECT 'red_cabbage', 3, 1800, 'crop_red_cabbage_stage_3', 5, 0
    UNION ALL SELECT 'red_cabbage', 4, 2700, 'crop_red_cabbage_stage_4', 5, 0

    UNION ALL SELECT 'yam', 1, 0, 'crop_yam_stage_1', 5, 0
    UNION ALL SELECT 'yam', 2, 1100, 'crop_yam_stage_2', 5, -10
    UNION ALL SELECT 'yam', 3, 2200, 'crop_yam_stage_3', 5, -15
    UNION ALL SELECT 'yam', 4, 3300, 'crop_yam_stage_4', 5, 0

    UNION ALL SELECT 'cranberry', 1, 0, 'crop_cranberry_stage_1', 5, 0
    UNION ALL SELECT 'cranberry', 2, 1240, 'crop_cranberry_stage_2', 5, 0
    UNION ALL SELECT 'cranberry', 3, 2480, 'crop_cranberry_stage_3', 5, -20
    UNION ALL SELECT 'cranberry', 4, 3720, 'crop_cranberry_stage_4', 5, -20

    UNION ALL SELECT 'pumpkin', 1, 0, 'crop_pumpkin_stage_1', 5, 0
    UNION ALL SELECT 'pumpkin', 2, 1460, 'crop_pumpkin_stage_2', 5, -10
    UNION ALL SELECT 'pumpkin', 3, 2920, 'crop_pumpkin_stage_3', 5, -10
    UNION ALL SELECT 'pumpkin', 4, 4380, 'crop_pumpkin_stage_4', 5, -10

    UNION ALL SELECT 'artichoke', 1, 0, 'crop_artichoke_stage_1', 5, 0
    UNION ALL SELECT 'artichoke', 2, 1720, 'crop_artichoke_stage_2', 5, -10
    UNION ALL SELECT 'artichoke', 3, 3440, 'crop_artichoke_stage_3', 5, -20
    UNION ALL SELECT 'artichoke', 4, 5160, 'crop_artichoke_stage_4', 5, -20

    UNION ALL SELECT 'blueberry', 1, 0, 'crop_blueberry_stage_1', 5, 0
    UNION ALL SELECT 'blueberry', 2, 1800, 'crop_blueberry_stage_2', 5, -10
    UNION ALL SELECT 'blueberry', 3, 3600, 'crop_blueberry_stage_3', 5, -25
    UNION ALL SELECT 'blueberry', 4, 5400, 'crop_blueberry_stage_4', 5, -30

    UNION ALL SELECT 'strawberry', 1, 0, 'crop_strawberry_stage_1', 5, 0
    UNION ALL SELECT 'strawberry', 2, 1920, 'crop_strawberry_stage_2', 5, 0
    UNION ALL SELECT 'strawberry', 3, 3840, 'crop_strawberry_stage_3', 5, 0
    UNION ALL SELECT 'strawberry', 4, 5760, 'crop_strawberry_stage_4', 5, -10

    UNION ALL SELECT 'eggplant', 1, 0, 'crop_eggplant_stage_1', 5, 0
    UNION ALL SELECT 'eggplant', 2, 2240, 'crop_eggplant_stage_2', 5, -10
    UNION ALL SELECT 'eggplant', 3, 4480, 'crop_eggplant_stage_3', 5, -25
    UNION ALL SELECT 'eggplant', 4, 6720, 'crop_eggplant_stage_4', 5, -25

    UNION ALL SELECT 'grape', 1, 0, 'crop_grape_stage_1', 5, -50
    UNION ALL SELECT 'grape', 2, 2480, 'crop_grape_stage_2', 5, -50
    UNION ALL SELECT 'grape', 3, 4960, 'crop_grape_stage_3', 5, -50
    UNION ALL SELECT 'grape', 4, 7440, 'crop_grape_stage_4', 5, -50

    UNION ALL SELECT 'bok_choy', 1, 0, 'crop_bok_choy_stage_1', 5, 0
    UNION ALL SELECT 'bok_choy', 2, 2600, 'crop_bok_choy_stage_2', 5, -5
    UNION ALL SELECT 'bok_choy', 3, 5200, 'crop_bok_choy_stage_3', 5, -5
    UNION ALL SELECT 'bok_choy', 4, 7800, 'crop_bok_choy_stage_4', 5, -10
) src
JOIN crops ON crops.code = src.crop_code
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
    items.id,
    src.buy_price,
    src.required_farm_level,
    src.is_visible,
    src.is_active,
    src.sort_order
FROM (
    SELECT 'hot_pepper_seed' AS item_code, 40 AS buy_price, 3 AS required_farm_level, 1 AS is_visible, 1 AS is_active, 19 AS sort_order
    UNION ALL SELECT 'red_cabbage_seed', 50, 3, 1, 1, 20
    UNION ALL SELECT 'yam_seed', 65, 3, 1, 1, 21
    UNION ALL SELECT 'cranberry_seed', 74, 3, 1, 1, 22
    UNION ALL SELECT 'pumpkin_seed', 91, 3, 1, 1, 23
    UNION ALL SELECT 'artichoke_seed', 101, 3, 1, 1, 24
    UNION ALL SELECT 'blueberry_seed', 113, 4, 1, 1, 25
    UNION ALL SELECT 'strawberry_seed', 121, 4, 1, 1, 26
    UNION ALL SELECT 'eggplant_seed', 148, 4, 1, 1, 27
    UNION ALL SELECT 'grape_seed', 159, 4, 1, 1, 28
    UNION ALL SELECT 'bok_choy_seed', 164, 4, 1, 1, 29
) src
JOIN items ON items.code = src.item_code
ON DUPLICATE KEY UPDATE
    buy_price = VALUES(buy_price),
    required_farm_level = VALUES(required_farm_level),
    is_visible = VALUES(is_visible),
    is_active = VALUES(is_active),
    sort_order = VALUES(sort_order);

COMMIT;


# thêm đồ ăn
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
)
VALUES
    ('tortilla', 'bánh tráng ngô', 'food', 'item_tortilla', '', 1.0, 0, 21, 1, 1, 1),
    ('vinegar', 'giấm', 'food', 'item_vinegar', '', 1.0, 0, 18, 1, 1, 1),
    ('mayonnaise', 'sốt mayonnaise', 'food', 'item_mayonnaise', '', 1.0, 0, 28, 1, 1, 1),
    ('baked_fish', 'cá nướng tỏi', 'food', 'item_baked_fish', '', 1.0, 0, 216, 1, 1, 1),
    ('strawberry_lover_pie', 'bánh kem dâu', 'food', 'item_strawberry_lover_pie', '', 1.0, 0, 621, 1, 1, 1),
    ('fish_taco', 'bánh cá', 'food', 'item_fish_taco', '', 1.0, 0, 421, 1, 1, 1),
    ('escargot', 'sên sào tỏi', 'food', 'item_escargot', '', 1.0, 0, 181, 1, 1, 1),
    ('lobster_bisque', 'súp tôm hùm', 'food', 'item_lobster_bisque', '', 1.0, 0, 130, 1, 1, 1),
    ('cranberry_candy', 'nước ép việt quất', 'food', 'item_cranberry_candy', '', 1.0, 0, 180, 1, 1, 1),
    ('blackberry_cobbler', 'bánh nhân nho', 'food', 'item_blackberry_cobbler', '', 1.0, 0, 600, 1, 1, 1),
    ('fruit_salad', 'salad hoa quả', 'food', 'item_fruit_salad', '', 1.0, 0, 636, 1, 1, 1),
    ('pumpkin_pie', 'bánh bí ngô', 'food', 'item_pumpkin_pie', '', 1.0, 0, 211, 1, 1, 1),
    ('artichoke_dip', 'atisô chấm sữa', 'food', 'item_artichoke_dip', '', 1.0, 0, 236, 1, 1, 1),
    ('cranberry_sauce', 'mứt việt quất', 'food', 'item_cranberry_sauce', '', 1.0, 0, 270, 1, 1, 1),
    ('fish_burger', 'burger cá', 'food', 'item_fish_burger', '', 1.0, 0, 661, 1, 1, 1),
    ('stuffing', 'món trộn', 'food', 'item_stuffing', '', 1.0, 0, 226, 1, 1, 1),
    ('super_meal', 'rau chộn', 'food', 'item_super_meal', '', 1.0, 0, 700, 1, 1, 1),
    ('pumpkin_soup', 'súp bí ngô', 'food', 'item_pumpkin_soup', '', 1.0, 0, 206, 1, 1, 1),
    ('autumn_bounty', 'đặc sản mùa thu', 'food', 'item_autumn_bounty', '', 1.0, 0, 300, 1, 1, 1),
    ('blueberry_tart', 'bánh tart', 'food', 'item_blueberry_tart', '', 1.0, 0, 320, 1, 1, 1),
    ('spicy_octopus', 'bạch tuộc sốt cay', 'food', 'item_spicy_octopus', '', 1.0, 0, 203, 1, 1, 1),
    ('tom_yum_soup', 'súp tomyum', 'food', 'item_tom_yum_soup', '', 1.0, 0, 180, 1, 1, 1),
    ('pepper_poppers', 'phô mai cay', 'food', 'item_pepper_poppers', '', 1.0, 0, 136, 1, 1, 1),
    ('treat', 'kẹo mút', 'food', 'item_treat', '', 1.0, 0, 312, 1, 1, 1)
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
    result_item.id,
    src.result_quantity,
    src.cooking_seconds,
    src.required_farm_level,
    src.is_active
FROM (
    SELECT 'tortilla' AS result_item_code, 1 AS result_quantity, 240 AS cooking_seconds, 1 AS required_farm_level, 1 AS is_active
    UNION ALL SELECT 'vinegar', 1, 180, 1, 1
    UNION ALL SELECT 'mayonnaise', 1, 200, 1, 1
    UNION ALL SELECT 'baked_fish', 1, 1260, 2, 1
    UNION ALL SELECT 'strawberry_lover_pie', 1, 1380, 4, 1
    UNION ALL SELECT 'fish_taco', 1, 420, 3, 1
    UNION ALL SELECT 'escargot', 1, 1007, 2, 1
    UNION ALL SELECT 'lobster_bisque', 1, 1320, 1, 1
    UNION ALL SELECT 'cranberry_candy', 1, 360, 3, 1
    UNION ALL SELECT 'blackberry_cobbler', 1, 480, 4, 1
    UNION ALL SELECT 'fruit_salad', 1, 540, 4, 1
    UNION ALL SELECT 'pumpkin_pie', 1, 600, 3, 1
    UNION ALL SELECT 'artichoke_dip', 1, 660, 3, 1
    UNION ALL SELECT 'cranberry_sauce', 1, 330, 3, 1
    UNION ALL SELECT 'fish_burger', 1, 3000, 4, 1
    UNION ALL SELECT 'stuffing', 1, 230, 3, 1
    UNION ALL SELECT 'super_meal', 1, 720, 4, 1
    UNION ALL SELECT 'pumpkin_soup', 1, 780, 3, 1
    UNION ALL SELECT 'autumn_bounty', 1, 240, 3, 1
    UNION ALL SELECT 'blueberry_tart', 1, 1500, 4, 1
    UNION ALL SELECT 'spicy_octopus', 1, 840, 3, 1
    UNION ALL SELECT 'tom_yum_soup', 1, 1620, 3, 1
    UNION ALL SELECT 'pepper_poppers', 1, 960, 3, 1
    UNION ALL SELECT 'treat', 1, 960, 4, 1
) src
JOIN items result_item ON result_item.code = src.result_item_code
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
    food_recipes.id,
    ingredient_item.id,
    src.quantity
FROM (
    SELECT 'tortilla' AS result_item_code, 'corn' AS ingredient_item_code, 1 AS quantity

    UNION ALL SELECT 'vinegar', 'wheat', 2

    UNION ALL SELECT 'mayonnaise', 'egg', 2

    UNION ALL SELECT 'baked_fish', 'tilapia', 1
    UNION ALL SELECT 'baked_fish', 'garlic', 1

    UNION ALL SELECT 'strawberry_lover_pie', 'pink_cake', 1
    UNION ALL SELECT 'strawberry_lover_pie', 'strawberry', 1

    UNION ALL SELECT 'fish_taco', 'red_cabbage', 1
    UNION ALL SELECT 'fish_taco', 'tortilla', 1
    UNION ALL SELECT 'fish_taco', 'chub', 1
    UNION ALL SELECT 'fish_taco', 'mayonnaise', 1

    UNION ALL SELECT 'escargot', 'garlic', 1
    UNION ALL SELECT 'escargot', 'snail', 1

    UNION ALL SELECT 'lobster_bisque', 'lobster', 1
    UNION ALL SELECT 'lobster_bisque', 'milk', 2

    UNION ALL SELECT 'cranberry_candy', 'cranberry', 1
    UNION ALL SELECT 'cranberry_candy', 'sugar', 1

    UNION ALL SELECT 'blackberry_cobbler', 'grape', 2
    UNION ALL SELECT 'blackberry_cobbler', 'sugar', 1
    UNION ALL SELECT 'blackberry_cobbler', 'wheat_flour', 1

    UNION ALL SELECT 'fruit_salad', 'grape', 1
    UNION ALL SELECT 'fruit_salad', 'blueberry', 1
    UNION ALL SELECT 'fruit_salad', 'melon', 1

    UNION ALL SELECT 'pumpkin_pie', 'pumpkin', 1
    UNION ALL SELECT 'pumpkin_pie', 'wheat_flour', 1
    UNION ALL SELECT 'pumpkin_pie', 'sugar', 1

    UNION ALL SELECT 'artichoke_dip', 'artichoke', 1
    UNION ALL SELECT 'artichoke_dip', 'milk', 1

    UNION ALL SELECT 'cranberry_sauce', 'cranberry', 1
    UNION ALL SELECT 'cranberry_sauce', 'sugar', 2

    UNION ALL SELECT 'fish_burger', 'bread', 1
    UNION ALL SELECT 'fish_burger', 'eggplant', 1
    UNION ALL SELECT 'fish_burger', 'anchovy', 1

    UNION ALL SELECT 'stuffing', 'bread', 1
    UNION ALL SELECT 'stuffing', 'cranberry', 1

    UNION ALL SELECT 'super_meal', 'bok_choy', 1
    UNION ALL SELECT 'super_meal', 'cranberry', 1
    UNION ALL SELECT 'super_meal', 'artichoke', 1

    UNION ALL SELECT 'pumpkin_soup', 'pumpkin', 1
    UNION ALL SELECT 'pumpkin_soup', 'milk', 1

    UNION ALL SELECT 'autumn_bounty', 'pumpkin', 1
    UNION ALL SELECT 'autumn_bounty', 'yam', 1

    UNION ALL SELECT 'blueberry_tart', 'blueberry', 1
    UNION ALL SELECT 'blueberry_tart', 'wheat_flour', 1
    UNION ALL SELECT 'blueberry_tart', 'sugar', 1
    UNION ALL SELECT 'blueberry_tart', 'egg', 1

    UNION ALL SELECT 'spicy_octopus', 'octopus', 1
    UNION ALL SELECT 'spicy_octopus', 'hot_pepper', 1

    UNION ALL SELECT 'tom_yum_soup', 'shrimp', 1
    UNION ALL SELECT 'tom_yum_soup', 'hot_pepper', 1

    UNION ALL SELECT 'pepper_poppers', 'cheese', 1
    UNION ALL SELECT 'pepper_poppers', 'hot_pepper', 1

    UNION ALL SELECT 'treat', 'sugar', 1
    UNION ALL SELECT 'treat', 'strawberry', 1
    UNION ALL SELECT 'treat', 'milk', 1
) src
JOIN items result_item ON result_item.code = src.result_item_code
JOIN food_recipes ON food_recipes.result_item_id = result_item.id
JOIN items ingredient_item ON ingredient_item.code = src.ingredient_item_code
ON DUPLICATE KEY UPDATE
    quantity = VALUES(quantity);

COMMIT;