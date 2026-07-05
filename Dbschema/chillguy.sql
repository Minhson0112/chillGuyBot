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

    price INT NOT NULL COMMENT 'total base selling price',

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
    fishing_catch_quantity INT NOT NULL DEFAULT 1 COMMENT 'number of fish caught per successful fishing attempt',
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

    CONSTRAINT chk_tool_templates_fishing_catch_quantity
        CHECK (fishing_catch_quantity > 0),

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

# update partner notification message tracking
ALTER TABLE partner
    ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'active' AFTER partner_at,
    ADD COLUMN message_id BIGINT DEFAULT NULL AFTER status;


# anonymous matching
CREATE TABLE anonymous_match_queue (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'anonymous match queue id',

    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',
    status VARCHAR(50) NOT NULL DEFAULT 'waiting' COMMENT 'queue status: waiting, matched, cancelled',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    matched_at DATETIME DEFAULT NULL COMMENT 'matched at',

    PRIMARY KEY (id),

    KEY idx_anonymous_match_queue_user_status (user_id, status),
    KEY idx_anonymous_match_queue_status_created_at (status, created_at),

    CONSTRAINT fk_anonymous_match_queue_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_anonymous_match_queue_status
        CHECK (status IN ('waiting', 'matched', 'cancelled'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='anonymous match queue';


CREATE TABLE anonymous_match_sessions (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'anonymous match session id',

    user_a_id BIGINT UNSIGNED NOT NULL COMMENT 'first discord user id',
    user_b_id BIGINT UNSIGNED NOT NULL COMMENT 'second discord user id',

    user_a_alias VARCHAR(32) NOT NULL COMMENT 'first user anonymous alias',
    user_b_alias VARCHAR(32) NOT NULL COMMENT 'second user anonymous alias',

    status VARCHAR(50) NOT NULL DEFAULT 'active' COMMENT 'session status: active, ending_requested, ended',

    end_requested_by_a TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'first user requested ending',
    end_requested_by_b TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'second user requested ending',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    ended_at DATETIME DEFAULT NULL COMMENT 'ended at',

    PRIMARY KEY (id),

    KEY idx_anonymous_match_sessions_user_a_status (user_a_id, status),
    KEY idx_anonymous_match_sessions_user_b_status (user_b_id, status),
    KEY idx_anonymous_match_sessions_status (status),

    CONSTRAINT fk_anonymous_match_sessions_user_a_id
        FOREIGN KEY (user_a_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_anonymous_match_sessions_user_b_id
        FOREIGN KEY (user_b_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_anonymous_match_sessions_status
        CHECK (status IN ('active', 'ending_requested', 'ended')),

    CONSTRAINT chk_anonymous_match_sessions_different_users
        CHECK (user_a_id <> user_b_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='anonymous match sessions';


# daily fortune
CREATE TABLE member_daily_fortune (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'member daily fortune id',

    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',
    fortune_date DATE NOT NULL COMMENT 'fortune date',

    love_rate TINYINT UNSIGNED NOT NULL COMMENT 'love fortune rate from 0 to 100',
    luck_rate TINYINT UNSIGNED NOT NULL COMMENT 'luck fortune rate from 0 to 100',
    career_rate TINYINT UNSIGNED NOT NULL COMMENT 'career or study fortune rate from 0 to 100',

    description TEXT NOT NULL COMMENT 'AI generated fortune description',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    UNIQUE KEY uq_member_daily_fortune_user_date (user_id, fortune_date),

    KEY idx_member_daily_fortune_user_id (user_id),
    KEY idx_member_daily_fortune_fortune_date (fortune_date),

    CONSTRAINT fk_member_daily_fortune_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_member_daily_fortune_love_rate
        CHECK (love_rate <= 100),

    CONSTRAINT chk_member_daily_fortune_luck_rate
        CHECK (luck_rate <= 100),

    CONSTRAINT chk_member_daily_fortune_career_rate
        CHECK (career_rate <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='daily member fortune';

CREATE TABLE server_invites (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'server invite id',

    invite_code VARCHAR(32) NOT NULL COMMENT 'discord invite code',
    invite_url VARCHAR(255) NOT NULL COMMENT 'discord invite url',

    channel_id BIGINT UNSIGNED DEFAULT NULL COMMENT 'discord channel id',
    inviter_user_id BIGINT UNSIGNED DEFAULT NULL COMMENT 'discord user id who created invite',

    uses BIGINT NOT NULL DEFAULT 0 COMMENT 'current invite uses from discord',
    max_uses BIGINT NOT NULL DEFAULT 0 COMMENT 'max uses, 0 means unlimited',
    max_age BIGINT NOT NULL DEFAULT 0 COMMENT 'max age seconds, 0 means never expire',
    temporary BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'temporary membership invite',

    status VARCHAR(50) NOT NULL DEFAULT 'active' COMMENT 'invite status: active, expired, deleted, unknown',

    discord_created_at DATETIME DEFAULT NULL COMMENT 'invite created at from discord',
    expired_at DATETIME DEFAULT NULL COMMENT 'calculated invite expired at',
    deleted_at DATETIME DEFAULT NULL COMMENT 'invite deleted at',
    last_fetched_at DATETIME DEFAULT NULL COMMENT 'last fetched from discord',
    UNIQUE KEY uq_server_invites_invite_code (invite_code),

    KEY idx_server_invites_inviter_user_id (inviter_user_id),
    KEY idx_server_invites_status (status),
    KEY idx_server_invites_last_fetched_at (last_fetched_at),

    CONSTRAINT fk_server_invites_inviter_user_id
        FOREIGN KEY (inviter_user_id) REFERENCES member(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT chk_server_invites_status
        CHECK (status IN ('active', 'expired', 'deleted', 'unknown'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='discord server invites';


# add invite link to partner
ALTER TABLE partner
    ADD COLUMN invite_link VARCHAR(255) DEFAULT NULL COMMENT 'partner server invite link' AFTER guild_name;


# lotto event
CREATE TABLE lotto_event (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'lotto event id',

    name VARCHAR(255) NOT NULL COMMENT 'lotto event name',
    ticket_price_cowoncy BIGINT NOT NULL COMMENT 'ticket price in cowoncy',

    buy_deadline DATETIME NOT NULL COMMENT 'deadline to buy tickets',
    draw_at DATETIME DEFAULT NULL COMMENT 'draw time',

    status VARCHAR(50) NOT NULL DEFAULT 'open' COMMENT 'event status: open, closed, drawn, cancelled',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'is active event',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    KEY idx_lotto_event_status_deadline (status, buy_deadline),
    KEY idx_lotto_event_is_active (is_active),

    CONSTRAINT chk_lotto_event_ticket_price_cowoncy
        CHECK (ticket_price_cowoncy > 0),

    CONSTRAINT chk_lotto_event_status
        CHECK (status IN ('open', 'closed', 'drawn', 'cancelled'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='lotto events';


CREATE TABLE lotto_ticket_purchase (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'lotto ticket purchase id',

    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',
    lotto_event_id BIGINT NOT NULL COMMENT 'lotto event id',

    ticket_quantity INT NOT NULL COMMENT 'ticket quantity',

    status VARCHAR(50) NOT NULL COMMENT 'purchase status: pending_payment, paid, cancelled, expired',

    payment_type VARCHAR(50) DEFAULT NULL COMMENT 'payment type',
    payment_amount BIGINT DEFAULT NULL COMMENT 'payment amount',

    registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'registered at',
    paid_at DATETIME DEFAULT NULL COMMENT 'paid at',
    expired_at DATETIME DEFAULT NULL COMMENT 'expired at',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    KEY idx_lotto_ticket_purchase_user_status (user_id, status),
    KEY idx_lotto_ticket_purchase_event_status (lotto_event_id, status),

    CONSTRAINT fk_lotto_ticket_purchase_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_lotto_ticket_purchase_event_id
        FOREIGN KEY (lotto_event_id) REFERENCES lotto_event(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_lotto_ticket_purchase_quantity
        CHECK (ticket_quantity > 0),

    CONSTRAINT chk_lotto_ticket_purchase_payment_amount
        CHECK (payment_amount IS NULL OR payment_amount > 0),

    CONSTRAINT chk_lotto_ticket_purchase_status
        CHECK (status IN ('pending_payment', 'paid', 'cancelled', 'expired'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='lotto ticket purchases';


CREATE TABLE lotto_ticket (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'lotto ticket id',

    lotto_event_id BIGINT NOT NULL COMMENT 'lotto event id',
    lotto_ticket_purchase_id BIGINT NOT NULL COMMENT 'lotto ticket purchase id',
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',

    number_1 INT NOT NULL COMMENT 'first lotto number',
    number_2 INT NOT NULL COMMENT 'second lotto number',
    number_3 INT NOT NULL COMMENT 'third lotto number',
    number_4 INT NOT NULL COMMENT 'fourth lotto number',
    number_5 INT NOT NULL COMMENT 'fifth lotto number',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),

    KEY idx_lotto_ticket_event_user (lotto_event_id, user_id),
    KEY idx_lotto_ticket_purchase (lotto_ticket_purchase_id),

    CONSTRAINT fk_lotto_ticket_event_id
        FOREIGN KEY (lotto_event_id) REFERENCES lotto_event(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_lotto_ticket_purchase_id
        FOREIGN KEY (lotto_ticket_purchase_id) REFERENCES lotto_ticket_purchase(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_lotto_ticket_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_lotto_ticket_number_1
        CHECK (number_1 BETWEEN 1 AND 99),

    CONSTRAINT chk_lotto_ticket_number_2
        CHECK (number_2 BETWEEN 1 AND 99),

    CONSTRAINT chk_lotto_ticket_number_3
        CHECK (number_3 BETWEEN 1 AND 99),

    CONSTRAINT chk_lotto_ticket_number_4
        CHECK (number_4 BETWEEN 1 AND 99),

    CONSTRAINT chk_lotto_ticket_number_5
        CHECK (number_5 BETWEEN 1 AND 99)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='lotto tickets';

CREATE TABLE member_payment_transaction (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'member payment transaction id',

    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',

    payment_target_type VARCHAR(50) NOT NULL COMMENT 'payment target type: role_shop, lotto_ticket',
    payment_target_id BIGINT NOT NULL COMMENT 'target purchase record id',

    status VARCHAR(50) NOT NULL COMMENT 'payment status: pending_payment, paid, cancelled, expired',

    required_cowoncy_amount BIGINT DEFAULT NULL COMMENT 'required cowoncy amount',
    required_chill_coin_amount BIGINT DEFAULT NULL COMMENT 'required chill coin amount',

    paid_payment_type VARCHAR(50) DEFAULT NULL COMMENT 'actual paid payment type',
    paid_amount BIGINT DEFAULT NULL COMMENT 'actual paid amount',

    registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'registered at',
    paid_at DATETIME DEFAULT NULL COMMENT 'paid at',
    cancelled_at DATETIME DEFAULT NULL COMMENT 'cancelled at',
    expired_at DATETIME DEFAULT NULL COMMENT 'expired at',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    KEY idx_member_payment_user_status (user_id, status),
    KEY idx_member_payment_target (payment_target_type, payment_target_id),
    KEY idx_member_payment_status_created_at (status, created_at),

    CONSTRAINT fk_member_payment_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_member_payment_status
        CHECK (status IN ('pending_payment', 'paid', 'cancelled', 'expired')),

    CONSTRAINT chk_member_payment_target_type
        CHECK (payment_target_type IN ('role_shop', 'lotto_ticket')),

    CONSTRAINT chk_member_payment_required_cowoncy_amount
        CHECK (required_cowoncy_amount IS NULL OR required_cowoncy_amount > 0),

    CONSTRAINT chk_member_payment_required_chill_coin_amount
        CHECK (required_chill_coin_amount IS NULL OR required_chill_coin_amount > 0),

    CONSTRAINT chk_member_payment_required_amount
        CHECK (required_cowoncy_amount IS NOT NULL OR required_chill_coin_amount IS NOT NULL),

    CONSTRAINT chk_member_payment_paid_amount
        CHECK (paid_amount IS NULL OR paid_amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='member payment transactions';

# update merge game play history
CREATE TABLE merge_game_play_history (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'merge game play history id',

    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',

    score INT UNSIGNED NOT NULL COMMENT 'game score',
    sun_time BIGINT UNSIGNED DEFAULT NULL COMMENT 'milliseconds until creating sun',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),

    KEY idx_merge_game_play_user_created_at (user_id, created_at),
    KEY idx_merge_game_play_score (score),

    CONSTRAINT fk_merge_game_play_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_merge_game_play_score
        CHECK (score >= 0),

    CONSTRAINT chk_merge_game_play_sun_time
        CHECK (sun_time IS NULL OR sun_time >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='merge game play histories';

# booster custom roles
CREATE TABLE booster_custom_role (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'booster custom role id',

    granted_by_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id who granted the role',
    target_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id who received the role',
    role_id BIGINT UNSIGNED NOT NULL COMMENT 'discord custom role id',

    status VARCHAR(50) NOT NULL DEFAULT 'active' COMMENT 'custom role status: active, removed',
    removed_by_user_id BIGINT UNSIGNED DEFAULT NULL COMMENT 'discord user id who removed the role',
    removed_reason VARCHAR(255) DEFAULT NULL COMMENT 'removed reason: boost_removed, manual_remove, role_deleted, etc',
    removed_at DATETIME DEFAULT NULL COMMENT 'removed at',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),

    KEY idx_booster_custom_role_target_status (target_user_id, status),
    KEY idx_booster_custom_role_role_id (role_id),
    KEY idx_booster_custom_role_granted_by_user_id (granted_by_user_id),
    KEY idx_booster_custom_role_removed_by_user_id (removed_by_user_id),

    CONSTRAINT fk_booster_custom_role_granted_by_user_id
        FOREIGN KEY (granted_by_user_id) REFERENCES member(user_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_booster_custom_role_target_user_id
        FOREIGN KEY (target_user_id) REFERENCES member(user_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_booster_custom_role_removed_by_user_id
        FOREIGN KEY (removed_by_user_id) REFERENCES member(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_booster_custom_role_status
        CHECK (status IN ('active', 'removed')),

    CONSTRAINT chk_booster_custom_role_removed_state
        CHECK (
            (status = 'active' AND removed_at IS NULL)
            OR (status = 'removed' AND removed_at IS NOT NULL)
        )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='booster custom roles';

# update giveaway subscription reward types
ALTER TABLE giveaway
    DROP CHECK chk_giveaway_type,
    DROP CHECK chk_giveaway_reward_by_type,
    ADD CONSTRAINT chk_giveaway_type
        CHECK (
            type IN (
                'chill_coin',
                'cowoncy',
                'vnd',
                'discord_nitro',
                'netflix',
                'spotify',
                'custom'
            )
        ),
    ADD CONSTRAINT chk_giveaway_reward_by_type
        CHECK (
            (type = 'chill_coin' AND reward_chill_coin IS NOT NULL AND reward_chill_coin > 0)
            OR (type = 'cowoncy' AND reward_cowoncy IS NOT NULL AND reward_cowoncy > 0)
            OR (type = 'vnd' AND reward_vnd IS NOT NULL AND reward_vnd > 0)
            OR (
                type IN ('discord_nitro', 'netflix', 'spotify')
                AND reward_text IS NOT NULL
                AND TRIM(reward_text) <> ''
            )
            OR (type = 'custom' AND reward_text IS NOT NULL)
        );

# add fishing ready notification tracking
ALTER TABLE farm_fish_pond
    ADD COLUMN is_fishing_ready_notified TINYINT(1) NOT NULL DEFAULT 0
        COMMENT 'whether fishing ready notification was sent'
        AFTER last_fished_at;

# store fixed fishing cooldown completion time
ALTER TABLE farm_fish_pond
    ADD COLUMN next_fishable_at DATETIME DEFAULT NULL
        COMMENT 'next fishable at'
        AFTER last_fished_at;

UPDATE farm_fish_pond
SET next_fishable_at = DATE_ADD(last_fished_at, INTERVAL 5 MINUTE)
WHERE last_fished_at IS NOT NULL;

# add egg and milk ready notification tracking
ALTER TABLE farm_chicken_coop
    ADD COLUMN is_egg_ready_notified TINYINT(1) NOT NULL DEFAULT 0
        COMMENT 'whether egg ready notification was sent'
        AFTER last_collected_egg_at;

ALTER TABLE farm_cow_shed
    ADD COLUMN is_milk_ready_notified TINYINT(1) NOT NULL DEFAULT 0
        COMMENT 'whether milk ready notification was sent'
        AFTER last_collected_milk_at;

# add animal hungry notification tracking
ALTER TABLE farm_chicken_coop
    ADD COLUMN is_hungry_notified TINYINT(1) NOT NULL DEFAULT 0
        COMMENT 'whether hungry notification was sent'
        AFTER is_egg_ready_notified;

ALTER TABLE farm_cow_shed
    ADD COLUMN is_hungry_notified TINYINT(1) NOT NULL DEFAULT 0
        COMMENT 'whether hungry notification was sent'
        AFTER is_milk_ready_notified;

# add farm theft tracking
ALTER TABLE farm
    ADD COLUMN last_robbed_at DATETIME DEFAULT NULL
        COMMENT 'last time the farm was robbed',
    ADD COLUMN robbed_count INT NOT NULL DEFAULT 0
        COMMENT 'number of times the farm was robbed',
    ADD CONSTRAINT chk_farm_robbed_count
        CHECK (robbed_count >= 0);

# add farm theft history
CREATE TABLE farm_theft_histories (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm theft history id',
    thief_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id of the thief',
    victim_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id of the victim',
    item_id BIGINT NOT NULL COMMENT 'stolen item id',
    stolen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'stolen at',

    PRIMARY KEY (id),

    KEY idx_farm_theft_histories_thief_stolen_at (thief_user_id, stolen_at),
    KEY idx_farm_theft_histories_victim_user_id (victim_user_id),
    KEY idx_farm_theft_histories_item_id (item_id),
    KEY idx_farm_theft_histories_stolen_at (stolen_at),

    CONSTRAINT fk_farm_theft_histories_thief_user_id
        FOREIGN KEY (thief_user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_theft_histories_victim_user_id
        FOREIGN KEY (victim_user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_theft_histories_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm theft history';

# add farm base skin master
CREATE TABLE base_skin_master (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'base skin id',
    code VARCHAR(100) NOT NULL COMMENT 'unique base skin code',
    name VARCHAR(255) NOT NULL COMMENT 'base skin name',
    base_image_key VARCHAR(255) NOT NULL COMMENT 'farm base image key',
    description VARCHAR(500) DEFAULT NULL COMMENT 'base skin description',
    buy_price INT NOT NULL DEFAULT 0 COMMENT 'buy price in chill coin',
    required_farm_level INT NOT NULL DEFAULT 1 COMMENT 'required farm level',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'is active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_base_skin_master_code (code),
    UNIQUE KEY uq_base_skin_master_image_key (base_image_key),
    KEY idx_base_skin_master_active_level (is_active, required_farm_level),

    CONSTRAINT chk_base_skin_master_buy_price
        CHECK (buy_price >= 0),
    CONSTRAINT chk_base_skin_master_required_farm_level
        CHECK (required_farm_level >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm base skin master';

# add base skin inventory for each member
CREATE TABLE member_base_skin_inventory (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'member base skin inventory id',
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',
    base_skin_id BIGINT NOT NULL COMMENT 'base skin id',
    is_using TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'is currently in use',
    acquired_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'acquired at',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_member_base_skin_inventory_user_skin (user_id, base_skin_id),
    KEY idx_member_base_skin_inventory_user_id (user_id),
    KEY idx_member_base_skin_inventory_base_skin_id (base_skin_id),

    CONSTRAINT fk_member_base_skin_inventory_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_member_base_skin_inventory_base_skin_id
        FOREIGN KEY (base_skin_id) REFERENCES base_skin_master(id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='base skins owned by members';

INSERT INTO base_skin_master (
    code,
    name,
    base_image_key,
    description,
    buy_price,
    required_farm_level,
    is_active
)
VALUES (
    'base',
    'Mặc định',
    'base',
    'Base farm mặc định',
    0,
    1,
    1
), (
    'sakura',
    'sakura',
    'sakura',
    NULL,
    40000,
    2,
    1
), (
    'snow',
    'snow',
    'snow',
    NULL,
    30000,
    2,
    1
), (
    'christmas',
    'christmas',
    'christmas',
    NULL,
    200000,
    3,
    0
), (
    'halloween',
    'halloween',
    'halloween',
    NULL,
    300000,
    3,
    0
), (
    'newYear',
    'newYear',
    'newYear',
    NULL,
    150000,
    3,
    0
), (
    'cyberpunk',
    'cyberpunk',
    'cyberpunk',
    NULL,
    80000,
    4,
    1
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    base_image_key = VALUES(base_image_key),
    description = VALUES(description),
    buy_price = VALUES(buy_price),
    required_farm_level = VALUES(required_farm_level),
    is_active = VALUES(is_active);

INSERT INTO member_base_skin_inventory (
    user_id,
    base_skin_id,
    is_using
)
SELECT
    farm.user_id,
    baseSkin.id,
    1
FROM farm
JOIN base_skin_master baseSkin
    ON baseSkin.code = 'base'
ON DUPLICATE KEY UPDATE
    is_using = VALUES(is_using);

# add farm harvest history
CREATE TABLE farm_harvest_histories (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm harvest history id',
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id of the farm owner',
    item_id BIGINT NOT NULL COMMENT 'harvested crop item id',
    quantity INT NOT NULL COMMENT 'harvested quantity including tool bonus',
    is_perfect_harvest TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'whether no crops were lost to pests, dryness, or theft',
    harvested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'harvested at',

    PRIMARY KEY (id),

    KEY idx_farm_harvest_histories_user_harvested_at (user_id, harvested_at),
    KEY idx_farm_harvest_histories_item_id (item_id),
    KEY idx_farm_harvest_histories_perfect_harvested_at (is_perfect_harvest, harvested_at),

    CONSTRAINT fk_farm_harvest_histories_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_harvest_histories_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_farm_harvest_histories_quantity
        CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm harvest history';

# add farm cooking history
CREATE TABLE farm_cooking_histories (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'farm cooking history id',
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',
    item_id BIGINT NOT NULL COMMENT 'received food item id',
    quantity INT NOT NULL COMMENT 'received quantity',
    received_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'received at',

    PRIMARY KEY (id),

    KEY idx_farm_cooking_histories_user_received_at (user_id, received_at),
    KEY idx_farm_cooking_histories_item_id (item_id),

    CONSTRAINT fk_farm_cooking_histories_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_farm_cooking_histories_item_id
        FOREIGN KEY (item_id) REFERENCES items(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_farm_cooking_histories_quantity
        CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='farm cooking history';

# add server item and couple system
CREATE TABLE server_item_master (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'server item id',
    name VARCHAR(255) NOT NULL COMMENT 'server item name',
    type VARCHAR(50) NOT NULL COMMENT 'server item type',
    price_cowoncy BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'item price in cowoncy',
    price_chill_coin BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'item price in chill coin',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'whether item is active',
    icon_image_key VARCHAR(255) NOT NULL COMMENT 'icon image key',
    intimacy_points INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'intimacy points granted by item',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),
    KEY idx_server_item_master_type_active (type, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='master table for server items';

CREATE TABLE server_user_inventory (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'server user inventory id',
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id',
    item_id BIGINT NOT NULL COMMENT 'server item id',
    quantity BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'item quantity',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_server_user_inventory_user_item (user_id, item_id),
    KEY idx_server_user_inventory_item_id (item_id),

    CONSTRAINT fk_server_user_inventory_user_id
        FOREIGN KEY (user_id) REFERENCES member(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_server_user_inventory_item_id
        FOREIGN KEY (item_id) REFERENCES server_item_master(id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='server item inventory for members';

CREATE TABLE server_item_gift_histories (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'server item gift history id',
    giver_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id of gift giver',
    receiver_user_id BIGINT UNSIGNED NOT NULL COMMENT 'discord user id of gift receiver',
    item_id BIGINT NOT NULL COMMENT 'gifted server item id',
    quantity BIGINT UNSIGNED NOT NULL COMMENT 'gifted item quantity',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',

    PRIMARY KEY (id),
    KEY idx_server_item_gift_histories_giver_created_at (giver_user_id, created_at),
    KEY idx_server_item_gift_histories_receiver_created_at (receiver_user_id, created_at),
    KEY idx_server_item_gift_histories_item_id (item_id),

    CONSTRAINT fk_server_item_gift_histories_giver_user_id
        FOREIGN KEY (giver_user_id) REFERENCES member(user_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_server_item_gift_histories_receiver_user_id
        FOREIGN KEY (receiver_user_id) REFERENCES member(user_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_server_item_gift_histories_item_id
        FOREIGN KEY (item_id) REFERENCES server_item_master(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_server_item_gift_histories_distinct_users
        CHECK (giver_user_id <> receiver_user_id),

    CONSTRAINT chk_server_item_gift_histories_quantity
        CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='server item gift history';

CREATE TABLE couple (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'couple id',
    user_1_id BIGINT UNSIGNED NOT NULL COMMENT 'first discord user id',
    user_2_id BIGINT UNSIGNED NOT NULL COMMENT 'second discord user id',
    intimacy_points BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'couple intimacy points',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    divorcing_at DATETIME DEFAULT NULL COMMENT 'divorcing at',
    couple_role_id BIGINT UNSIGNED DEFAULT NULL COMMENT 'discord couple role id',

    PRIMARY KEY (id),
    UNIQUE KEY uq_couple_users (user_1_id, user_2_id),
    KEY idx_couple_user_2_id (user_2_id),
    KEY idx_couple_divorcing_at (divorcing_at),

    CONSTRAINT fk_couple_user_1_id
        FOREIGN KEY (user_1_id) REFERENCES member(user_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_couple_user_2_id
        FOREIGN KEY (user_2_id) REFERENCES member(user_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_couple_distinct_users
        CHECK (user_1_id <> user_2_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='server couple relationships';

CREATE TABLE couple_daily_voice_activity (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'couple daily voice activity id',
    couple_id BIGINT NOT NULL COMMENT 'couple id',
    activity_date DATE NOT NULL COMMENT 'activity date in GMT+7',
    voice_seconds BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'seconds both users were in the same voice channel',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',

    PRIMARY KEY (id),
    UNIQUE KEY uq_couple_daily_voice_activity_couple_date (couple_id, activity_date),
    KEY idx_couple_daily_voice_activity_date_voice (activity_date, voice_seconds),

    CONSTRAINT fk_couple_daily_voice_activity_couple_id
        FOREIGN KEY (couple_id) REFERENCES couple(id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='daily time couples spent together in voice';
