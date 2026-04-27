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