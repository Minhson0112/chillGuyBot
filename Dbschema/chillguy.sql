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