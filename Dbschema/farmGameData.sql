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