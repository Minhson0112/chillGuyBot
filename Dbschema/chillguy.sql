USE chill_station;
CREATE TABLE `tournament_master` (
    `id_tournament` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `tournament_name` VARCHAR(255) NOT NULL,
    `game_name` VARCHAR(255) NOT NULL,
    `total_prize` BIGINT NOT NULL,
    `is_available` BOOLEAN NOT NULL COMMENT 'is available tournament?'
);

CREATE TABLE `partner` (
    `guild_id` BIGINT UNSIGNED NOT NULL,
    `partner_at` DATE NOT NULL,
    PRIMARY KEY (`guild_id`)
);

CREATE TABLE `member` (
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT 'id discord bot',
    `global_name` VARCHAR(255) NULL COMMENT 'global name in discord',
    `username` VARCHAR(255) NOT NULL COMMENT 'username in discord',
    `nick` VARCHAR(255) NULL COMMENT 'username in chill station',
    `date_of_birth` DATE NULL COMMENT 'date of birth',
    `joined_at` DATETIME NOT NULL COMMENT 'join chill station at',
    `leave_at` DATETIME NULL COMMENT 'leave chill station at',
    `is_bot` BOOLEAN NOT NULL COMMENT 'is bot?',
    PRIMARY KEY (`user_id`)
);

CREATE TABLE `chat` (
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT 'id discord',
    `total_chat_count` BIGINT NOT NULL DEFAULT 0 COMMENT 'total chat in Chill Station',
    `level_chat_count` BIGINT NOT NULL DEFAULT 0 COMMENT 'total chat in Chill Station level channel',
    PRIMARY KEY (`user_id`),
    CONSTRAINT `chat_user_id_foreign`
        FOREIGN KEY (`user_id`) REFERENCES `member` (`user_id`)
);

CREATE TABLE `tournament_entry` (
    `id_tournament` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `registered_at` DATETIME NOT NULL,
    `status` INT NOT NULL DEFAULT 0 COMMENT '0: signing, 1: entry confirm, 2: eliminated',
    PRIMARY KEY (`id_tournament`, `user_id`),
    CONSTRAINT `tournament_entry_id_tournament_foreign`
        FOREIGN KEY (`id_tournament`) REFERENCES `tournament_master` (`id_tournament`),
    CONSTRAINT `tournament_entry_user_id_foreign`
        FOREIGN KEY (`user_id`) REFERENCES `member` (`user_id`)
);

# update schema lần 1

ALTER TABLE `member`
ADD COLUMN `join_count` INT UNSIGNED NOT NULL DEFAULT 1 COMMENT 'number of times the member has joined the server',
ADD COLUMN `warning_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'number of warnings for rule violations';

CREATE TABLE `member_moderation_history` (
    `id_member_moderation_history` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `action_by_user_id` BIGINT UNSIGNED NOT NULL COMMENT 'member id who performed the moderation action',
    `target_user_id` BIGINT UNSIGNED NOT NULL COMMENT 'member id who received the moderation action',
    `action_type` TINYINT UNSIGNED NOT NULL COMMENT '1: mute, 2: kick, 3: ban',
    `reason` VARCHAR(500) NULL COMMENT 'reason for moderation action',
    `duration_minutes` INT UNSIGNED NULL COMMENT 'duration in minutes for temporary moderation actions',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    PRIMARY KEY (`id_member_moderation_history`),
    CONSTRAINT `member_moderation_history_action_by_user_id_foreign`
        FOREIGN KEY (`action_by_user_id`) REFERENCES `member` (`user_id`),
    CONSTRAINT `member_moderation_history_target_user_id_foreign`
        FOREIGN KEY (`target_user_id`) REFERENCES `member` (`user_id`)
);

# update schema lần 2

CREATE TABLE `auto_responder` (
    `id_auto_responder` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT 'member who created this auto responder',
    `msg_key` VARCHAR(100) NOT NULL COMMENT 'trigger key',
    `is_global` BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'whether other members can use this key',
    `msg_link` VARCHAR(500) NOT NULL COMMENT 'discord message link used as template',
    `deleted_at` DATETIME NULL COMMENT 'soft delete timestamp',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',
    PRIMARY KEY (`id_auto_responder`),
    UNIQUE KEY `uq_auto_responder_msg_key` (`msg_key`),
    CONSTRAINT `auto_responder_user_id_foreign`
        FOREIGN KEY (`user_id`) REFERENCES `member` (`user_id`)
);

# update lần 3
ALTER TABLE partner
    DROP PRIMARY KEY,
    ADD COLUMN id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT FIRST,
    ADD COLUMN guild_name VARCHAR(255) NOT NULL AFTER guild_id,
    ADD COLUMN representative_user_id BIGINT UNSIGNED NOT NULL AFTER guild_name,
    ADD COLUMN partnered_by_user_id BIGINT UNSIGNED NOT NULL AFTER representative_user_id,
    ADD PRIMARY KEY (id),
    ADD UNIQUE KEY uq_partner_guild_id (guild_id),
    ADD CONSTRAINT fk_partner_representative_user
        FOREIGN KEY (representative_user_id) REFERENCES member(user_id),
    ADD CONSTRAINT fk_partner_partnered_by_user
        FOREIGN KEY (partnered_by_user_id) REFERENCES member(user_id);

ALTER TABLE `member`
ADD COLUMN `is_partner` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'is partner guild member?';

# update lần 4
CREATE TABLE `word` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `key_word` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_word_key_word` (`key_word`)
);

CREATE TABLE `word_guess_history` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `word_id` BIGINT UNSIGNED NOT NULL,
    `guessed_by_user_id` BIGINT UNSIGNED NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_word_guess_history_word_id`
        FOREIGN KEY (`word_id`) REFERENCES `word` (`id`),
    CONSTRAINT `fk_word_guess_history_guessed_by_user_id`
        FOREIGN KEY (`guessed_by_user_id`) REFERENCES `member` (`user_id`)
);

ALTER TABLE `member`
ADD COLUMN `correct_word_guess_count` INT NOT NULL DEFAULT 0 COMMENT 'number of times the member guessed the full word correctly';

# upate 5
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE `word_guess_history`;
TRUNCATE TABLE `word`;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `word_guess_input` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `guess_word` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_word_guess_input_guess_word` (`guess_word`)
);

# update 6

ALTER TABLE auto_responder
ADD COLUMN is_exact_match TINYINT(1) NOT NULL DEFAULT 1
AFTER is_global;

# update 7

CREATE TABLE owo_donate_history (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    sender_user_id BIGINT UNSIGNED NOT NULL,
    receiver_user_id BIGINT UNSIGNED NOT NULL,
    cowoncy_amount BIGINT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_owo_donate_history_sender
        FOREIGN KEY (sender_user_id) REFERENCES member(user_id),
    CONSTRAINT fk_owo_donate_history_receiver
        FOREIGN KEY (receiver_user_id) REFERENCES member(user_id)
);

INSERT INTO owo_donate_history (
    sender_user_id,
    receiver_user_id,
    cowoncy_amount,
    created_at
) VALUES
    (374116043075092481, 1350862103593877614, 500000, '2026-02-24 00:00:00'),
    (157058721170587648, 1350862103593877614, 5000000, '2026-02-24 00:00:00'),
    (1110688776126218272, 1350862103593877614, 100, '2026-02-24 00:00:00'),
    (157058721170587648, 1350862103593877614, 5000000, '2026-02-24 00:00:00'),
    (699607009888305264, 1350862103593877614, 1000000, '2026-03-06 00:00:00'),
    (374116043075092481, 1350862103593877614, 1000000, '2026-03-07 00:00:00'),
    (1110688776126218272, 1350862103593877614, 2000000, '2026-03-14 00:00:00'),
    (1300024791075393596, 1350862103593877614, 1000000, '2026-03-18 00:00:00');

# update 8
CREATE TABLE music_event (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    event_name VARCHAR(255) NOT NULL,
    role_id BIGINT UNSIGNED NOT NULL,
    is_available TINYINT(1) NOT NULL DEFAULT 1,
    participant_count INT UNSIGNED NOT NULL DEFAULT 0,
    expired_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE music_event_entry (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    music_event_id BIGINT UNSIGNED NOT NULL,
    song_name VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_music_event_entry_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id),
    CONSTRAINT fk_music_event_entry_music_event_id
        FOREIGN KEY (music_event_id) REFERENCES music_event(id)
);

# update 9 
ALTER TABLE member
ADD COLUMN chill_coin INT NOT NULL DEFAULT 0 COMMENT 'server private currency';

#update 10 (farm)
CREATE TABLE farm (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm id',
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'owner discord user id',
    farm_level INT NOT NULL DEFAULT 1 COMMENT 'farm level',
    farm_exp INT NOT NULL DEFAULT 0 COMMENT 'farm experience',
    base_image_key VARCHAR(255) DEFAULT "base" COMMENT 'base image key for farm rendering',
    is_train_event TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'whether train event is active in farm',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',
    PRIMARY KEY (id),
    UNIQUE KEY uq_farm_user_id (user_id),
    CONSTRAINT fk_farm_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm table';

CREATE TABLE items (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'item id',
    code VARCHAR(100) NOT NULL COMMENT 'unique item code',
    name VARCHAR(255) NOT NULL COMMENT 'item name',
    type_code VARCHAR(50) NOT NULL COMMENT 'item type code',
    icon_image_key VARCHAR(255) NOT NULL COMMENT 'icon image key',
    description VARCHAR(500) DEFAULT NULL COMMENT 'item description',

    render_scale FLOAT NOT NULL DEFAULT 1.0 COMMENT 'scale when rendering in game',
    render_offset_y INT NOT NULL DEFAULT 0 COMMENT 'vertical offset when rendering',

    sell_price INT NOT NULL DEFAULT 0 COMMENT 'sell price',
    is_sellable TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'can sell',
    is_usable TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'can use',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'is active',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_items_code (code),
    KEY idx_items_type_code (type_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='master table for all game items';

CREATE TABLE crops (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'crop id',
    code VARCHAR(100) NOT NULL COMMENT 'unique crop code',
    name VARCHAR(255) NOT NULL COMMENT 'crop name',
    seed_item_id BIGINT NOT NULL COMMENT 'seed item id',
    crop_item_id BIGINT NOT NULL COMMENT 'harvest item id',
    harvest_quantity_per_plot INT NOT NULL DEFAULT 1 COMMENT 'harvest quantity per plot',
    total_growth_seconds INT NOT NULL COMMENT 'total growth time in seconds',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',
    PRIMARY KEY (id),
    UNIQUE KEY uq_crops_code (code),
    UNIQUE KEY uq_crops_seed_item_id (seed_item_id),
    UNIQUE KEY uq_crops_crop_item_id (crop_item_id),
    CONSTRAINT fk_crops_seed_item_id
        FOREIGN KEY (seed_item_id) REFERENCES items(id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_crops_crop_item_id
        FOREIGN KEY (crop_item_id) REFERENCES items(id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='master table for crops';

CREATE TABLE crop_growth_stages (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'crop growth stage id',
    crop_id BIGINT NOT NULL COMMENT 'crop id',
    stage_no INT NOT NULL COMMENT 'growth stage number',
    stage_start_seconds INT NOT NULL COMMENT 'elapsed seconds from planted time to reach this stage',
    image_key VARCHAR(255) NOT NULL COMMENT 'image key for this crop stage',
    render_scale FLOAT NOT NULL DEFAULT 1.0 COMMENT 'render scale for this stage image',
    render_offset_y INT NOT NULL DEFAULT 0 COMMENT 'vertical offset when rendering this stage image',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',
    PRIMARY KEY (id),
    UNIQUE KEY uq_crop_growth_stage_crop_id_stage_no (crop_id, stage_no),
    CONSTRAINT fk_crop_growth_stages_crop_id
        FOREIGN KEY (crop_id) REFERENCES crops(id)
        ON DELETE CASCADE,
    CONSTRAINT chk_crop_growth_stages_stage_no
        CHECK (stage_no IN (1, 2, 3, 4))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='growth stages for crops';

CREATE TABLE farm_crop_area (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm crop area id',
    farm_id BIGINT NOT NULL COMMENT 'farm id',
    unlocked_plot_count INT NOT NULL DEFAULT 1 COMMENT 'number of unlocked plots',
    crop_id BIGINT DEFAULT NULL COMMENT 'current planted crop id',
    planted_at DATETIME DEFAULT NULL COMMENT 'planted at',
    harvestable_at DATETIME DEFAULT NULL COMMENT 'harvestable at',

    last_watered_at DATETIME DEFAULT NULL COMMENT 'last watered at',
    last_pest_removed_at DATETIME DEFAULT NULL COMMENT 'last pest removed at',

    is_dry TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'whether crop area is dry',
    is_pest_infected TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'whether crop area has pest infection',

    dryness_started_at DATETIME DEFAULT NULL COMMENT 'when dryness started',
    pest_started_at DATETIME DEFAULT NULL COMMENT 'when pest infection started',

    total_dry_seconds INT NOT NULL DEFAULT 0 COMMENT 'total dry duration in seconds',
    total_pest_seconds INT NOT NULL DEFAULT 0 COMMENT 'total pest duration in seconds',

    status VARCHAR(50) NOT NULL DEFAULT 'idle' COMMENT 'crop area status',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_farm_crop_area_farm_id (farm_id),
    KEY idx_farm_crop_area_crop_id (crop_id),

    CONSTRAINT fk_farm_crop_area_farm_id
        FOREIGN KEY (farm_id) REFERENCES farm(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_crop_area_crop_id
        FOREIGN KEY (crop_id) REFERENCES crops(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='runtime state of crop area in farm';

CREATE TABLE shop_items (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'shop item id',
    item_id BIGINT NOT NULL COMMENT 'item id',
    buy_price INT NOT NULL DEFAULT 0 COMMENT 'shop buy price',
    required_farm_level INT NOT NULL DEFAULT 1 COMMENT 'required farm level to buy item',
    is_visible TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'whether item is visible in shop',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'whether item can be bought in shop',
    sort_order INT NOT NULL DEFAULT 0 COMMENT 'shop display order',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_shop_items_item_id (item_id),
    KEY idx_shop_items_required_farm_level (required_farm_level),
    KEY idx_shop_items_sort_order (sort_order),

    CONSTRAINT fk_shop_items_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='shop items';

CREATE TABLE user_inventory (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'user inventory id',
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',
    item_id BIGINT NOT NULL COMMENT 'item id',
    quantity BIGINT NOT NULL DEFAULT 0 COMMENT 'item quantity',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_user_inventory_user_id_item_id (user_id, item_id),
    KEY idx_user_inventory_user_id (user_id),
    KEY idx_user_inventory_item_id (item_id),

    CONSTRAINT fk_user_inventory_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_user_inventory_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='user inventory';

CREATE TABLE farm_chicken_coop (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm chicken coop id',
    farm_id BIGINT NOT NULL COMMENT 'farm id',
    chicken_count INT NOT NULL DEFAULT 0 COMMENT 'number of chickens, max 2',

    chicken_1_image_key VARCHAR(255) DEFAULT NULL COMMENT 'image key for chicken 1',
    chicken_2_image_key VARCHAR(255) DEFAULT NULL COMMENT 'image key for chicken 2',

    chicken_1_x INT DEFAULT NULL COMMENT 'x position of chicken 1',
    chicken_1_y INT DEFAULT NULL COMMENT 'y position of chicken 1',
    chicken_2_x INT DEFAULT NULL COMMENT 'x position of chicken 2',
    chicken_2_y INT DEFAULT NULL COMMENT 'y position of chicken 2',

    render_scale FLOAT NOT NULL DEFAULT 1.0 COMMENT 'render scale for chickens',

    last_fed_at DATETIME DEFAULT NULL COMMENT 'last fed at',
    last_collected_egg_at DATETIME DEFAULT NULL COMMENT 'last collected egg at',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_farm_chicken_coop_farm_id (farm_id),

    CONSTRAINT fk_farm_chicken_coop_farm_id
        FOREIGN KEY (farm_id) REFERENCES farm(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_farm_chicken_coop_chicken_count
        CHECK (chicken_count BETWEEN 0 AND 2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm chicken coop';

CREATE TABLE farm_cow_shed (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm cow shed id',
    farm_id BIGINT NOT NULL COMMENT 'farm id',
    cow_count INT NOT NULL DEFAULT 0 COMMENT 'number of cows, max 1',

    cow_image_key VARCHAR(255) DEFAULT NULL COMMENT 'image key for cow',

    cow_x INT DEFAULT NULL COMMENT 'x position of cow',
    cow_y INT DEFAULT NULL COMMENT 'y position of cow',

    render_scale FLOAT NOT NULL DEFAULT 1.0 COMMENT 'render scale for cow',

    last_fed_at DATETIME DEFAULT NULL COMMENT 'last fed at',
    last_collected_milk_at DATETIME DEFAULT NULL COMMENT 'last collected milk at',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_farm_cow_shed_farm_id (farm_id),

    CONSTRAINT fk_farm_cow_shed_farm_id
        FOREIGN KEY (farm_id) REFERENCES farm(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_farm_cow_shed_cow_count
        CHECK (cow_count BETWEEN 0 AND 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm cow shed';

CREATE TABLE farm_fish_pond (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm fish pond id',
    farm_id BIGINT NOT NULL COMMENT 'farm id',
    last_fished_at DATETIME DEFAULT NULL COMMENT 'last fished at',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_farm_fish_pond_farm_id (farm_id),

    CONSTRAINT fk_farm_fish_pond_farm_id
        FOREIGN KEY (farm_id) REFERENCES farm(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm fish pond';

CREATE TABLE chill_coin_transactions (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'transaction id',

    from_user_id BIGINT UNSIGNED NOT NULL COMMENT 'sender user id',
    to_user_id BIGINT UNSIGNED NOT NULL COMMENT 'receiver user id',

    amount BIGINT NOT NULL COMMENT 'amount of chill coin transferred',

    transaction_type VARCHAR(50) NOT NULL DEFAULT 'transfer' COMMENT 'transaction type',
    note VARCHAR(255) DEFAULT NULL COMMENT 'optional note',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'transaction time',

    PRIMARY KEY (id),

    KEY idx_transactions_from_user_id (from_user_id),
    KEY idx_transactions_to_user_id (to_user_id),
    KEY idx_transactions_created_at (created_at),

    CONSTRAINT fk_transactions_from_user
        FOREIGN KEY (from_user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_transactions_to_user
        FOREIGN KEY (to_user_id) REFERENCES member(user_id)
        ON DELETE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='chill coin transaction history';

# update cau ca

CREATE TABLE fishing_history (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'fishing history id',

    user_id BIGINT NOT NULL COMMENT 'discord user id',
    item_id BIGINT NOT NULL COMMENT 'caught seafood item id',

    weight_kg DECIMAL(5,2) NOT NULL COMMENT 'caught seafood weight in kg',

    caught_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'caught at',

    PRIMARY KEY (id),

    KEY idx_fishing_history_user_id (user_id),
    KEY idx_fishing_history_item_id (item_id),
    KEY idx_fishing_history_caught_at (caught_at),
    KEY idx_fishing_history_weight_kg (weight_kg),

    CONSTRAINT fk_fishing_history_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_fishing_history_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_fishing_history_weight_kg
        CHECK (weight_kg >= 1.00 AND weight_kg <= 100.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='fishing catch history';


#next update

CREATE TABLE farm_market_listings (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'market listing id',

    seller_user_id BIGINT UNSIGNED NOT NULL COMMENT 'seller discord user id',
    buyer_user_id BIGINT UNSIGNED DEFAULT NULL COMMENT 'buyer discord user id',

    item_id BIGINT NOT NULL COMMENT 'listed item id',
    quantity BIGINT NOT NULL DEFAULT 1 COMMENT 'listed item quantity',

    price INT NOT NULL COMMENT 'selling price after 10 percent bonus',

    is_sold TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'whether item has been sold',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    sold_at DATETIME DEFAULT NULL COMMENT 'sold at',

    PRIMARY KEY (id),

    KEY idx_farm_market_listings_seller_user_id (seller_user_id),
    KEY idx_farm_market_listings_buyer_user_id (buyer_user_id),
    KEY idx_farm_market_listings_item_id (item_id),
    KEY idx_farm_market_listings_is_sold_created_at (is_sold, created_at),

    CONSTRAINT fk_farm_market_listings_seller_user_id
        FOREIGN KEY (seller_user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_market_listings_buyer_user_id
        FOREIGN KEY (buyer_user_id) REFERENCES member(user_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_farm_market_listings_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_farm_market_listings_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_farm_market_listings_price
        CHECK (price > 0),

    CONSTRAINT chk_farm_market_listings_sold_state
        CHECK (
            (is_sold = 0 AND sold_at IS NULL)
            OR
            (is_sold = 1 AND sold_at IS NOT NULL)
        )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm player market listings';

#new update 
CREATE TABLE food_recipes (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'food recipe id',

    result_item_id BIGINT NOT NULL COMMENT 'crafted food item id',
    result_quantity INT NOT NULL DEFAULT 1 COMMENT 'crafted food quantity',

    cooking_seconds INT NOT NULL COMMENT 'cooking duration in seconds',
    required_farm_level INT NOT NULL DEFAULT 1 COMMENT 'required farm level to cook',

    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'whether recipe is active',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_food_recipes_result_item_id (result_item_id),

    KEY idx_food_recipes_required_farm_level (required_farm_level),
    KEY idx_food_recipes_is_active (is_active),

    CONSTRAINT fk_food_recipes_result_item_id
        FOREIGN KEY (result_item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_food_recipes_result_quantity
        CHECK (result_quantity > 0),

    CONSTRAINT chk_food_recipes_cooking_seconds
        CHECK (cooking_seconds > 0),

    CONSTRAINT chk_food_recipes_required_farm_level
        CHECK (required_farm_level >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='food crafting recipes';

CREATE TABLE food_recipe_ingredients (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'food recipe ingredient id',

    recipe_id BIGINT NOT NULL COMMENT 'food recipe id',
    item_id BIGINT NOT NULL COMMENT 'ingredient item id',
    quantity INT NOT NULL COMMENT 'required ingredient quantity',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_food_recipe_ingredients_recipe_item (recipe_id, item_id),

    KEY idx_food_recipe_ingredients_recipe_id (recipe_id),
    KEY idx_food_recipe_ingredients_item_id (item_id),

    CONSTRAINT fk_food_recipe_ingredients_recipe_id
        FOREIGN KEY (recipe_id) REFERENCES food_recipes(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_food_recipe_ingredients_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_food_recipe_ingredients_quantity
        CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ingredients required for food recipes';

CREATE TABLE farm_kitchen (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm kitchen id',

    farm_id BIGINT NOT NULL COMMENT 'farm id',

    current_recipe_id BIGINT DEFAULT NULL COMMENT 'current cooking recipe id',
    cooking_quantity INT NOT NULL DEFAULT 0 COMMENT 'cooking quantity',

    started_at DATETIME DEFAULT NULL COMMENT 'cooking started at',
    finished_at DATETIME DEFAULT NULL COMMENT 'cooking finished at',
    total_cooking_seconds INT NOT NULL DEFAULT 0 COMMENT 'total cooking duration in seconds',

    status VARCHAR(50) NOT NULL DEFAULT 'idle' COMMENT 'kitchen status',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_farm_kitchen_farm_id (farm_id),

    KEY idx_farm_kitchen_current_recipe_id (current_recipe_id),
    KEY idx_farm_kitchen_status (status),

    CONSTRAINT fk_farm_kitchen_farm_id
        FOREIGN KEY (farm_id) REFERENCES farm(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_kitchen_current_recipe_id
        FOREIGN KEY (current_recipe_id) REFERENCES food_recipes(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_farm_kitchen_cooking_quantity
        CHECK (cooking_quantity >= 0),

    CONSTRAINT chk_farm_kitchen_total_cooking_seconds
        CHECK (total_cooking_seconds >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm kitchen cooking state';

INSERT INTO farm_kitchen (
    farm_id,
    status
)
SELECT
    f.id,
    'idle'
FROM farm f
WHERE NOT EXISTS (
    SELECT 1
    FROM farm_kitchen fk
    WHERE fk.farm_id = f.id
);

# update event tàu

CREATE TABLE farm_train_events (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm train event id',

    required_item_id BIGINT NOT NULL COMMENT 'requested item id',
    required_quantity BIGINT NOT NULL COMMENT 'requested item quantity',

    reward_chill_coin BIGINT NOT NULL DEFAULT 0 COMMENT 'reward chill coin',
    reward_exp INT NOT NULL DEFAULT 0 COMMENT 'reward farm exp',

    is_completed TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'whether train event is completed',

    created_by_user_id BIGINT UNSIGNED DEFAULT NULL COMMENT 'admin user id who created event',
    completed_by_farm_id BIGINT DEFAULT NULL COMMENT 'farm id that completed event',
    completed_by_user_id BIGINT UNSIGNED DEFAULT NULL COMMENT 'user id that completed event',

    completed_at DATETIME DEFAULT NULL COMMENT 'completed at',
    closed_at DATETIME DEFAULT NULL COMMENT 'closed at',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    KEY idx_farm_train_events_required_item_id (required_item_id),
    KEY idx_farm_train_events_is_completed (is_completed),
    KEY idx_farm_train_events_created_at (created_at),
    KEY idx_farm_train_events_completed_at (completed_at),

    CONSTRAINT fk_farm_train_events_required_item_id
        FOREIGN KEY (required_item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_farm_train_events_created_by_user_id
        FOREIGN KEY (created_by_user_id) REFERENCES member(user_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_farm_train_events_completed_by_farm_id
        FOREIGN KEY (completed_by_farm_id) REFERENCES farm(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_farm_train_events_completed_by_user_id
        FOREIGN KEY (completed_by_user_id) REFERENCES member(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_farm_train_events_required_quantity
        CHECK (required_quantity > 0),

    CONSTRAINT chk_farm_train_events_reward_chill_coin
        CHECK (reward_chill_coin >= 0),

    CONSTRAINT chk_farm_train_events_reward_exp
        CHECK (reward_exp >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm train events';


CREATE TABLE farm_train_event_histories (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm train event history id',

    train_event_id BIGINT NOT NULL COMMENT 'farm train event id',
    farm_id BIGINT NOT NULL COMMENT 'farm id that loaded item',
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id that loaded item',

    delivered_item_id BIGINT NOT NULL COMMENT 'delivered item id',
    delivered_quantity BIGINT NOT NULL COMMENT 'delivered item quantity',

    reward_chill_coin BIGINT NOT NULL DEFAULT 0 COMMENT 'reward chill coin snapshot',
    reward_exp INT NOT NULL DEFAULT 0 COMMENT 'reward farm exp snapshot',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),

    KEY idx_farm_train_event_histories_train_event_id (train_event_id),
    KEY idx_farm_train_event_histories_farm_id (farm_id),
    KEY idx_farm_train_event_histories_user_id (user_id),
    KEY idx_farm_train_event_histories_created_at (created_at),
    KEY idx_farm_train_event_histories_reward_chill_coin (reward_chill_coin),
    KEY idx_farm_train_event_histories_reward_exp (reward_exp),

    CONSTRAINT fk_farm_train_event_histories_train_event_id
        FOREIGN KEY (train_event_id) REFERENCES farm_train_events(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_train_event_histories_farm_id
        FOREIGN KEY (farm_id) REFERENCES farm(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_train_event_histories_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_train_event_histories_delivered_item_id
        FOREIGN KEY (delivered_item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_farm_train_event_histories_delivered_quantity
        CHECK (delivered_quantity > 0),

    CONSTRAINT chk_farm_train_event_histories_reward_chill_coin
        CHECK (reward_chill_coin >= 0),

    CONSTRAINT chk_farm_train_event_histories_reward_exp
        CHECK (reward_exp >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm train event completion histories';

# member activ update
CREATE TABLE member_daily_activity (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'member daily activity id',

    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',

    activity_date DATE NOT NULL COMMENT 'activity date',

    total_chat_count BIGINT NOT NULL DEFAULT 0 COMMENT 'total chat count in this day',

    level_chat_count BIGINT NOT NULL DEFAULT 0 COMMENT 'level chat count in this day',

    voice_seconds BIGINT NOT NULL DEFAULT 0 COMMENT 'total voice connected seconds in this day',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_member_daily_activity_user_date (user_id, activity_date),

    KEY idx_member_daily_activity_activity_date (activity_date),

    KEY idx_member_daily_activity_user_id (user_id),

    CONSTRAINT fk_member_daily_activity_user_id
        FOREIGN KEY (user_id)
        REFERENCES member (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='daily member activity statistics';

# thêm để kiểm soát member
ALTER TABLE member
    ADD COLUMN is_staff TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'is staff member?' AFTER chill_coin,
    ADD COLUMN is_mod TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'is moderator member?' AFTER is_staff,
    ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'is admin member?' AFTER is_mod,
    ADD COLUMN can_create_auto_res TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'can create auto responder?' AFTER is_admin;

# lệnh daily
CREATE TABLE daily_checkin_rewards (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'daily checkin reward id',

    streak_day INT NOT NULL COMMENT 'streak day from 1 to 7',

    reward_chill_coin BIGINT NOT NULL DEFAULT 0 COMMENT 'reward chill coin',

    reward_item_id BIGINT DEFAULT NULL COMMENT 'reward item id',
    reward_item_quantity BIGINT NOT NULL DEFAULT 0 COMMENT 'reward item quantity',

    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'whether reward is active',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_daily_checkin_rewards_streak_day (streak_day),

    KEY idx_daily_checkin_rewards_reward_item_id (reward_item_id),
    KEY idx_daily_checkin_rewards_is_active (is_active),

    CONSTRAINT fk_daily_checkin_rewards_reward_item_id
        FOREIGN KEY (reward_item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_daily_checkin_rewards_streak_day
        CHECK (streak_day >= 1 AND streak_day <= 7),

    CONSTRAINT chk_daily_checkin_rewards_reward_chill_coin
        CHECK (reward_chill_coin >= 0),

    CONSTRAINT chk_daily_checkin_rewards_reward_item_quantity
        CHECK (reward_item_quantity >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='daily checkin reward master';

CREATE TABLE daily_checkin_histories (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'daily checkin history id',

    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',

    checkin_date DATE NOT NULL COMMENT 'checkin date',

    streak_day INT NOT NULL COMMENT 'streak day when checked in',

    reward_chill_coin BIGINT NOT NULL DEFAULT 0 COMMENT 'received chill coin snapshot',

    reward_item_id BIGINT DEFAULT NULL COMMENT 'received item id snapshot',
    reward_item_quantity BIGINT NOT NULL DEFAULT 0 COMMENT 'received item quantity snapshot',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_daily_checkin_histories_user_date (user_id, checkin_date),

    KEY idx_daily_checkin_histories_user_id (user_id),
    KEY idx_daily_checkin_histories_checkin_date (checkin_date),
    KEY idx_daily_checkin_histories_streak_day (streak_day),
    KEY idx_daily_checkin_histories_reward_item_id (reward_item_id),

    CONSTRAINT fk_daily_checkin_histories_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_daily_checkin_histories_reward_item_id
        FOREIGN KEY (reward_item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_daily_checkin_histories_streak_day
        CHECK (streak_day >= 1 AND streak_day <= 7),

    CONSTRAINT chk_daily_checkin_histories_reward_chill_coin
        CHECK (reward_chill_coin >= 0),

    CONSTRAINT chk_daily_checkin_histories_reward_item_quantity
        CHECK (reward_item_quantity >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='daily checkin histories';

# daily task
CREATE TABLE daily_task_masters (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'daily task master id',

    task_code VARCHAR(100) NOT NULL COMMENT 'unique task code',
    task_name VARCHAR(255) NOT NULL COMMENT 'task display name',
    description VARCHAR(500) DEFAULT NULL COMMENT 'task description',

    task_type VARCHAR(50) NOT NULL COMMENT 'task type: chat_message, voice_time, plant_crop, sell_market_item, fishing, cooking, train_delivery',

    target_item_id BIGINT DEFAULT NULL COMMENT 'target item id if task requires an item',
    target_crop_id BIGINT DEFAULT NULL COMMENT 'target crop id if task requires a crop',
    target_channel_id BIGINT DEFAULT NULL COMMENT 'discord channel id if task targets a channel',

    required_value BIGINT NOT NULL DEFAULT 1 COMMENT 'required progress value, message count, seconds, item count, etc',

    reward_chill_coin BIGINT NOT NULL DEFAULT 0 COMMENT 'reward chill coin',
    reward_exp INT NOT NULL DEFAULT 0 COMMENT 'reward farm exp',

    min_farm_level INT NOT NULL DEFAULT 1 COMMENT 'minimum farm level to receive this task',
    weight INT NOT NULL DEFAULT 100 COMMENT 'random weight',

    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'whether task is active',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_daily_task_masters_task_code (task_code),

    KEY idx_daily_task_masters_task_type (task_type),
    KEY idx_daily_task_masters_target_item_id (target_item_id),
    KEY idx_daily_task_masters_target_crop_id (target_crop_id),
    KEY idx_daily_task_masters_target_channel_id (target_channel_id),
    KEY idx_daily_task_masters_min_farm_level (min_farm_level),
    KEY idx_daily_task_masters_is_active (is_active),

    CONSTRAINT fk_daily_task_masters_target_item_id
        FOREIGN KEY (target_item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_daily_task_masters_target_crop_id
        FOREIGN KEY (target_crop_id) REFERENCES crops(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_daily_task_masters_required_value
        CHECK (required_value > 0),

    CONSTRAINT chk_daily_task_masters_reward_chill_coin
        CHECK (reward_chill_coin >= 0),

    CONSTRAINT chk_daily_task_masters_reward_exp
        CHECK (reward_exp >= 0),

    CONSTRAINT chk_daily_task_masters_min_farm_level
        CHECK (min_farm_level >= 1),

    CONSTRAINT chk_daily_task_masters_weight
        CHECK (weight > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='daily task master';


CREATE TABLE user_daily_tasks (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'user daily task id',

    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',
    task_date DATE NOT NULL COMMENT 'daily task date',

    slot_no INT NOT NULL COMMENT 'task slot from 1 to 5',

    task_master_id BIGINT NOT NULL COMMENT 'daily task master id',

    task_code VARCHAR(100) NOT NULL COMMENT 'snapshot task code',
    task_name VARCHAR(255) NOT NULL COMMENT 'snapshot task name',
    description VARCHAR(500) DEFAULT NULL COMMENT 'snapshot task description',

    task_type VARCHAR(50) NOT NULL COMMENT 'snapshot task type',

    target_item_id BIGINT DEFAULT NULL COMMENT 'snapshot target item id',
    target_crop_id BIGINT DEFAULT NULL COMMENT 'snapshot target crop id',
    target_channel_id BIGINT DEFAULT NULL COMMENT 'snapshot target channel id',

    required_value BIGINT NOT NULL COMMENT 'required progress value',
    progress_value BIGINT NOT NULL DEFAULT 0 COMMENT 'current progress value',

    reward_chill_coin BIGINT NOT NULL DEFAULT 0 COMMENT 'reward chill coin snapshot',
    reward_exp INT NOT NULL DEFAULT 0 COMMENT 'reward farm exp snapshot',

    status VARCHAR(50) NOT NULL DEFAULT 'in_progress' COMMENT 'task status: in_progress, completed',

    completed_at DATETIME DEFAULT NULL COMMENT 'completed at',
    reward_received_at DATETIME DEFAULT NULL COMMENT 'reward received at',
    notified_at DATETIME DEFAULT NULL COMMENT 'completion notification sent at',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_user_daily_tasks_user_date_slot (user_id, task_date, slot_no),
    UNIQUE KEY uq_user_daily_tasks_user_date_master (user_id, task_date, task_master_id),

    KEY idx_user_daily_tasks_user_id (user_id),
    KEY idx_user_daily_tasks_task_date (task_date),
    KEY idx_user_daily_tasks_task_master_id (task_master_id),
    KEY idx_user_daily_tasks_task_type (task_type),
    KEY idx_user_daily_tasks_status (status),
    KEY idx_user_daily_tasks_target_item_id (target_item_id),
    KEY idx_user_daily_tasks_target_crop_id (target_crop_id),
    KEY idx_user_daily_tasks_target_channel_id (target_channel_id),

    CONSTRAINT fk_user_daily_tasks_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_user_daily_tasks_task_master_id
        FOREIGN KEY (task_master_id) REFERENCES daily_task_masters(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_user_daily_tasks_target_item_id
        FOREIGN KEY (target_item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_user_daily_tasks_target_crop_id
        FOREIGN KEY (target_crop_id) REFERENCES crops(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_user_daily_tasks_slot_no
        CHECK (slot_no >= 1 AND slot_no <= 5),

    CONSTRAINT chk_user_daily_tasks_required_value
        CHECK (required_value > 0),

    CONSTRAINT chk_user_daily_tasks_progress_value
        CHECK (progress_value >= 0),

    CONSTRAINT chk_user_daily_tasks_reward_chill_coin
        CHECK (reward_chill_coin >= 0),

    CONSTRAINT chk_user_daily_tasks_reward_exp
        CHECK (reward_exp >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='user daily tasks';

# gift code

CREATE TABLE giftcodes (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'giftcode id',

    code VARCHAR(100) NOT NULL COMMENT 'giftcode code',
    reward_chill_coin BIGINT NOT NULL DEFAULT 0 COMMENT 'reward chill coin',

    expired_at DATE NOT NULL COMMENT 'giftcode expiration date',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_giftcodes_code (code),
    KEY idx_giftcodes_expired_at (expired_at),

    CONSTRAINT chk_giftcodes_reward_chill_coin
        CHECK (reward_chill_coin >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='giftcode master';

CREATE TABLE giftcode_claim_histories (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'giftcode claim history id',

    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',
    giftcode_id BIGINT NOT NULL COMMENT 'giftcode id',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_giftcode_claim_histories_user_giftcode (user_id, giftcode_id),

    KEY idx_giftcode_claim_histories_user_id (user_id),
    KEY idx_giftcode_claim_histories_giftcode_id (giftcode_id),

    CONSTRAINT fk_giftcode_claim_histories_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_giftcode_claim_histories_giftcode_id
        FOREIGN KEY (giftcode_id) REFERENCES giftcodes(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='giftcode claim history';

CREATE TABLE giftcode_rewards (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'giftcode reward id',

    giftcode_id BIGINT NOT NULL COMMENT 'giftcode id',
    item_id BIGINT NOT NULL COMMENT 'reward item id',
    quantity BIGINT NOT NULL COMMENT 'reward item quantity',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_giftcode_rewards_giftcode_item (giftcode_id, item_id),

    KEY idx_giftcode_rewards_giftcode_id (giftcode_id),
    KEY idx_giftcode_rewards_item_id (item_id),

    CONSTRAINT fk_giftcode_rewards_giftcode_id
        FOREIGN KEY (giftcode_id) REFERENCES giftcodes(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_giftcode_rewards_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_giftcode_rewards_quantity
        CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='giftcode item rewards';

# doi tien
CREATE TABLE owo_exchange_coin_histories (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'owo exchange coin history id',

    message_id BIGINT NOT NULL COMMENT 'owo bot message id',
    channel_id BIGINT NOT NULL COMMENT 'discord channel id',

    sender_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id who sent cowoncy',
    receiver_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id who received cowoncy',

    cowoncy_amount BIGINT NOT NULL COMMENT 'transferred cowoncy amount',

    transferred_at DATETIME NOT NULL COMMENT 'transferred datetime in GMT+7',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_owo_exchange_coin_histories_message_id (message_id),

    KEY idx_owo_exchange_coin_histories_channel_id (channel_id),
    KEY idx_owo_exchange_coin_histories_sender_user_id (sender_user_id),
    KEY idx_owo_exchange_coin_histories_receiver_user_id (receiver_user_id),
    KEY idx_owo_exchange_coin_histories_transferred_at (transferred_at),

    CONSTRAINT fk_owo_exchange_coin_histories_sender_user_id
        FOREIGN KEY (sender_user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_owo_exchange_coin_histories_receiver_user_id
        FOREIGN KEY (receiver_user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_owo_exchange_coin_histories_cowoncy_amount
        CHECK (cowoncy_amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='owo exchange coin histories';


CREATE TABLE role_shop (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    role_id BIGINT NOT NULL,

    price_cowoncy BIGINT NULL,
    price_chill_coin BIGINT NULL,

    valid_days INT NOT NULL DEFAULT 30,

    is_active TINYINT(1) NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uq_role_shop_role (role_id)
);

CREATE TABLE member_role_purchase (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT UNSIGNED NOT NULL,
    role_shop_id BIGINT NOT NULL,

    status VARCHAR(50) NOT NULL,

    payment_type VARCHAR(50) NULL,
    payment_amount BIGINT NULL,

    registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at DATETIME NULL,
    expired_at DATETIME NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_member_role_purchase_user
        FOREIGN KEY (user_id)
        REFERENCES member(user_id),

    CONSTRAINT fk_member_role_purchase_role_shop
        FOREIGN KEY (role_shop_id)
        REFERENCES role_shop(id),

    UNIQUE KEY uq_member_role_purchase_user_role (user_id, role_shop_id)
);


# dụng cụ

CREATE TABLE tool_templates (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'tool template id',

    item_id BIGINT NOT NULL COMMENT 'tool item id',

    tool_type VARCHAR(50) NOT NULL COMMENT 'tool type: watering_can, fishing_rod, sickle, milk_pail',
    tool_level INT NOT NULL DEFAULT 1 COMMENT 'tool level',

    max_durability INT NOT NULL COMMENT 'maximum durability',
    durability_cost_per_use INT NOT NULL DEFAULT 1 COMMENT 'durability cost per use',

    crop_growth_reduction_seconds INT NOT NULL DEFAULT 0 COMMENT 'crop growth time reduction seconds',
    fishing_cooldown_reduction_seconds INT NOT NULL DEFAULT 0 COMMENT 'fishing cooldown reduction seconds',
    fishing_success_rate DECIMAL(3,2) NOT NULL DEFAULT 0.00 COMMENT 'fishing success rate: 0 or 0.10 to 0.90',
    harvest_bonus_percent INT NOT NULL DEFAULT 0 COMMENT 'harvest bonus percent',
    milk_bonus_quantity INT NOT NULL DEFAULT 0 COMMENT 'milk bonus quantity per harvest',

    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'whether tool template is active',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_tool_templates_item_id (item_id),
    KEY idx_tool_templates_tool_type (tool_type),
    KEY idx_tool_templates_tool_level (tool_level),
    KEY idx_tool_templates_is_active (is_active),

    CONSTRAINT fk_tool_templates_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_tool_templates_tool_level
        CHECK (tool_level >= 1),

    CONSTRAINT chk_tool_templates_max_durability
        CHECK (max_durability > 0),

    CONSTRAINT chk_tool_templates_durability_cost_per_use
        CHECK (durability_cost_per_use > 0),

    CONSTRAINT chk_tool_templates_crop_growth_reduction_seconds
        CHECK (crop_growth_reduction_seconds >= 0),

    CONSTRAINT chk_tool_templates_fishing_cooldown_reduction_seconds
        CHECK (fishing_cooldown_reduction_seconds >= 0),

    CONSTRAINT chk_tool_templates_fishing_success_rate
        CHECK (fishing_success_rate = 0.00 OR fishing_success_rate BETWEEN 0.10 AND 0.90),

    CONSTRAINT chk_tool_templates_harvest_bonus_percent
        CHECK (harvest_bonus_percent >= 0),

    CONSTRAINT chk_tool_templates_milk_bonus_quantity
        CHECK (milk_bonus_quantity >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='tool template master';

CREATE TABLE user_tools (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'user tool id',

    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',
    item_id BIGINT NOT NULL COMMENT 'tool item id',
    tool_template_id BIGINT NOT NULL COMMENT 'tool template id',

    current_durability INT NOT NULL COMMENT 'current durability',

    status VARCHAR(50) NOT NULL DEFAULT 'available' COMMENT 'tool status: available, equipped, broken',

    acquired_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'acquired at',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    KEY idx_user_tools_user_id (user_id),
    KEY idx_user_tools_item_id (item_id),
    KEY idx_user_tools_tool_template_id (tool_template_id),
    KEY idx_user_tools_status (status),

    CONSTRAINT fk_user_tools_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_user_tools_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_user_tools_tool_template_id
        FOREIGN KEY (tool_template_id) REFERENCES tool_templates(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_user_tools_current_durability
        CHECK (current_durability >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='owned tools of user';


CREATE TABLE farm_tool_equipment (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm tool equipment id',

    farm_id BIGINT NOT NULL COMMENT 'farm id',
    tool_type VARCHAR(50) NOT NULL COMMENT 'tool type: watering_can, sickle, fishing_rod',
    user_tool_id BIGINT NOT NULL COMMENT 'equipped user tool id',

    equipped_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'equipped at',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_farm_tool_equipment_farm_type (farm_id, tool_type),
    UNIQUE KEY uq_farm_tool_equipment_user_tool_id (user_tool_id),

    KEY idx_farm_tool_equipment_farm_id (farm_id),
    KEY idx_farm_tool_equipment_tool_type (tool_type),

    CONSTRAINT fk_farm_tool_equipment_farm_id
        FOREIGN KEY (farm_id) REFERENCES farm(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_tool_equipment_user_tool_id
        FOREIGN KEY (user_tool_id) REFERENCES user_tools(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='equipped tools of farm';


# doi chill coin sang cowoncy
CREATE TABLE chill_coin_exchange_cowoncy_histories (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'chill coin exchange cowoncy history id',

    sender_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id who sent cowoncy',
    receiver_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id who received cowoncy',

    chill_coin_amount BIGINT NOT NULL COMMENT 'exchanged chill coin amount',
    cowoncy_amount BIGINT NOT NULL COMMENT 'received cowoncy amount',

    transferred_at DATETIME NOT NULL COMMENT 'transferred datetime in GMT+7',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),

    KEY idx_chill_coin_exchange_cowoncy_histories_sender_user_id (sender_user_id),
    KEY idx_chill_coin_exchange_cowoncy_histories_receiver_user_id (receiver_user_id),
    KEY idx_chill_coin_exchange_cowoncy_histories_transferred_at (transferred_at),

    CONSTRAINT fk_chill_coin_exchange_cowoncy_histories_sender_user_id
        FOREIGN KEY (sender_user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_chill_coin_exchange_cowoncy_histories_receiver_user_id
        FOREIGN KEY (receiver_user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_chill_coin_exchange_cowoncy_histories_chill_coin_amount
        CHECK (chill_coin_amount > 0),

    CONSTRAINT chk_chill_coin_exchange_cowoncy_histories_cowoncy_amount
        CHECK (cowoncy_amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='chill coin to cowoncy exchange histories';


# add member notification permission
ALTER TABLE member
    ADD COLUMN is_allow_notifications TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'is allowed to receive notifications';


# giveaway
CREATE TABLE giveaway (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'giveaway id',

    type VARCHAR(50) NOT NULL COMMENT 'giveaway type: chill_coin, cowoncy, vnd, custom',
    title VARCHAR(255) DEFAULT NULL COMMENT 'giveaway title',
    winner_count INT NOT NULL DEFAULT 1 COMMENT 'number of winners',
    reward_chill_coin BIGINT DEFAULT NULL COMMENT 'reward chill coin amount',
    reward_cowoncy BIGINT DEFAULT NULL COMMENT 'reward cowoncy amount',
    reward_vnd BIGINT DEFAULT NULL COMMENT 'reward vnd amount',
    reward_text TEXT DEFAULT NULL COMMENT 'custom reward description',

    status VARCHAR(50) NOT NULL DEFAULT 'active' COMMENT 'giveaway status: active, cancelled, ended',

    duration_seconds BIGINT NOT NULL COMMENT 'giveaway duration in seconds',
    draw_at DATETIME NOT NULL COMMENT 'scheduled draw datetime',
    ended_at DATETIME DEFAULT NULL COMMENT 'ended at',
    cancelled_at DATETIME DEFAULT NULL COMMENT 'cancelled at',

    channel_id BIGINT NOT NULL COMMENT 'discord channel id',
    message_id BIGINT DEFAULT NULL COMMENT 'discord giveaway message id',
    created_by_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id who created giveaway',
    cancelled_by_user_id BIGINT UNSIGNED DEFAULT NULL COMMENT 'discord user id who cancelled giveaway',
    limit_role_id BIGINT DEFAULT NULL COMMENT 'required discord role id to join giveaway',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    KEY idx_giveaway_status_draw_at (status, draw_at),
    KEY idx_giveaway_type (type),
    KEY idx_giveaway_channel_id (channel_id),
    KEY idx_giveaway_message_id (message_id),
    KEY idx_giveaway_created_by_user_id (created_by_user_id),
    KEY idx_giveaway_cancelled_by_user_id (cancelled_by_user_id),
    KEY idx_giveaway_limit_role_id (limit_role_id),

    CONSTRAINT fk_giveaway_created_by_user_id
        FOREIGN KEY (created_by_user_id) REFERENCES member(user_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_giveaway_cancelled_by_user_id
        FOREIGN KEY (cancelled_by_user_id) REFERENCES member(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_giveaway_winner_count
        CHECK (winner_count > 0),

    CONSTRAINT chk_giveaway_duration_seconds
        CHECK (duration_seconds > 0),

    CONSTRAINT chk_giveaway_type
        CHECK (type IN ('chill_coin', 'cowoncy', 'vnd', 'custom')),

    CONSTRAINT chk_giveaway_reward_by_type
        CHECK (
            (type = 'chill_coin' AND reward_chill_coin IS NOT NULL AND reward_chill_coin > 0)
            OR (type = 'cowoncy' AND reward_cowoncy IS NOT NULL AND reward_cowoncy > 0)
            OR (type = 'vnd' AND reward_vnd IS NOT NULL AND reward_vnd > 0)
            OR (type = 'custom' AND reward_text IS NOT NULL)
        )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='giveaway master';


CREATE TABLE giveaway_participants (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'giveaway participant id',

    giveaway_id BIGINT NOT NULL COMMENT 'giveaway id',
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',

    status VARCHAR(50) NOT NULL DEFAULT 'active' COMMENT 'participant status: active, removed, invalid',
    invalid_reason VARCHAR(255) DEFAULT NULL COMMENT 'invalid reason: missing_role, left_server, bot_user, manual_remove, etc',

    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'joined at',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_giveaway_participants_giveaway_user (giveaway_id, user_id),

    KEY idx_giveaway_participants_giveaway_id (giveaway_id),
    KEY idx_giveaway_participants_user_id (user_id),
    KEY idx_giveaway_participants_status (status),
    KEY idx_giveaway_participants_giveaway_status (giveaway_id, status),

    CONSTRAINT fk_giveaway_participants_giveaway_id
        FOREIGN KEY (giveaway_id) REFERENCES giveaway(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_giveaway_participants_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='giveaway participants';


CREATE TABLE giveaway_winners (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'giveaway winner id',

    giveaway_id BIGINT NOT NULL COMMENT 'giveaway id',
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',

    draw_round INT NOT NULL DEFAULT 1 COMMENT 'draw or reroll round',
    slot_number INT NOT NULL COMMENT 'winner slot number',
    current_slot_number INT DEFAULT NULL COMMENT 'current active winner slot number, null for rerolled winners',

    status VARCHAR(50) NOT NULL DEFAULT 'selected' COMMENT 'winner status: selected, claimed, disqualified, rerolled',
    disqualified_reason VARCHAR(255) DEFAULT NULL COMMENT 'disqualified reason: missing_role, left_server, no_response, manual_reroll, etc',

    rerolled_from_winner_id BIGINT DEFAULT NULL COMMENT 'previous winner id if this row is from reroll',

    selected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'selected at',
    claimed_at DATETIME DEFAULT NULL COMMENT 'claimed at',
    disqualified_at DATETIME DEFAULT NULL COMMENT 'disqualified at',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_giveaway_winners_giveaway_user (giveaway_id, user_id),
    UNIQUE KEY uq_giveaway_winners_current_slot (giveaway_id, current_slot_number),

    KEY idx_giveaway_winners_giveaway_id (giveaway_id),
    KEY idx_giveaway_winners_user_id (user_id),
    KEY idx_giveaway_winners_status (status),
    KEY idx_giveaway_winners_giveaway_status (giveaway_id, status),
    KEY idx_giveaway_winners_rerolled_from_winner_id (rerolled_from_winner_id),

    CONSTRAINT fk_giveaway_winners_giveaway_id
        FOREIGN KEY (giveaway_id) REFERENCES giveaway(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_giveaway_winners_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_giveaway_winners_rerolled_from_winner_id
        FOREIGN KEY (rerolled_from_winner_id) REFERENCES giveaway_winners(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_giveaway_winners_draw_round
        CHECK (draw_round > 0),

    CONSTRAINT chk_giveaway_winners_slot_number
        CHECK (slot_number > 0),

    CONSTRAINT chk_giveaway_winners_current_slot_number
        CHECK (current_slot_number IS NULL OR current_slot_number > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='giveaway winners';
