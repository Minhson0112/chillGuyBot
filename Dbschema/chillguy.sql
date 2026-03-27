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
    `revealed_pattern` VARCHAR(255) NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_word_guess_history_word_id`
        FOREIGN KEY (`word_id`) REFERENCES `word` (`id`),
    CONSTRAINT `fk_word_guess_history_guessed_by_user_id`
        FOREIGN KEY (`guessed_by_user_id`) REFERENCES `member` (`user_id`)
);

ALTER TABLE `member`
ADD COLUMN `correct_word_guess_count` INT NOT NULL DEFAULT 0 COMMENT 'number of times the member guessed the full word correctly';