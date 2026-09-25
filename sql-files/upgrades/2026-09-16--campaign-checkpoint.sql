-- Durable Seal Cascade party checkpoint state (QW-054).
-- This is deliberately separate from per-character quest and story variables.
CREATE TABLE IF NOT EXISTS `dm_campaign_checkpoint` (
  `campaign_id` VARCHAR(32) NOT NULL,
  `schema_version` SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  `party_id` INT UNSIGNED NOT NULL,
  `arc_id` SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  `step` INT UNSIGNED NOT NULL DEFAULT 0,
  `carrier_char_id` INT UNSIGNED NOT NULL DEFAULT 0,
  `last_actor_char_id` INT UNSIGNED NOT NULL DEFAULT 0,
  `last_transition_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`campaign_id`, `party_id`),
  KEY `dm_campaign_checkpoint_party` (`party_id`),
  KEY `dm_campaign_checkpoint_arc` (`arc_id`)
) ENGINE=InnoDB;

-- Append-only audit trail for forward transitions and explicit recovery.
CREATE TABLE IF NOT EXISTS `dm_campaign_checkpoint_log` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `campaign_id` VARCHAR(32) NOT NULL,
  `party_id` INT UNSIGNED NOT NULL,
  `step` INT UNSIGNED NOT NULL,
  `actor_char_id` INT UNSIGNED NOT NULL DEFAULT 0,
  `event` VARCHAR(32) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `dm_campaign_checkpoint_log_lookup` (`campaign_id`, `party_id`, `id`)
) ENGINE=InnoDB;

-- Stable campaign membership survives a party leave/rejoin and records which
-- character ids are eligible for the current checkpoint.
CREATE TABLE IF NOT EXISTS `dm_campaign_checkpoint_member` (
  `campaign_id` VARCHAR(32) NOT NULL,
  `char_id` INT UNSIGNED NOT NULL,
  `party_id` INT UNSIGNED NOT NULL,
  `eligible` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `last_seen_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`campaign_id`, `char_id`),
  KEY `dm_campaign_checkpoint_member_party` (`campaign_id`, `party_id`)
) ENGINE=InnoDB;

INSERT IGNORE INTO `sql_updates` (`timestamp`) VALUES (20260916);
