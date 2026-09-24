-- Typed, idempotent replay for DM campaign quest/flag state (GDD S10).
CREATE TABLE IF NOT EXISTS `dm_campaign_party_event` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `campaign_id` VARCHAR(32) NOT NULL,
  `party_id` INT UNSIGNED NOT NULL,
  `kind` VARCHAR(16) NOT NULL,
  `name` VARCHAR(64) NOT NULL,
  `value` INT NOT NULL DEFAULT 0,
  `actor_char_id` INT UNSIGNED NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `dm_campaign_party_event_replay` (`campaign_id`, `party_id`, `id`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `dm_campaign_party_cursor` (
  `campaign_id` VARCHAR(32) NOT NULL,
  `char_id` INT UNSIGNED NOT NULL,
  `party_id` INT UNSIGNED NOT NULL,
  `last_event_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`campaign_id`, `char_id`),
  KEY `dm_campaign_party_cursor_party` (`campaign_id`, `party_id`)
) ENGINE=InnoDB;

INSERT IGNORE INTO `sql_updates` (`timestamp`) VALUES (20260924);
