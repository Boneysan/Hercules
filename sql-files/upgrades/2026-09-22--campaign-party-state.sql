-- Party-wide quest progress and story flags. A character who logs in alone
-- can restore these without another party member being online.
CREATE TABLE IF NOT EXISTS `dm_campaign_party_state` (
  `campaign_id` VARCHAR(32) NOT NULL,
  `party_id` INT UNSIGNED NOT NULL,
  `kind` VARCHAR(8) NOT NULL,
  `name` VARCHAR(64) NOT NULL,
  `value` INT NOT NULL DEFAULT 0,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`campaign_id`, `party_id`, `kind`, `name`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `dm_campaign_pending_grant` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `campaign_id` VARCHAR(32) NOT NULL,
  `party_id` INT UNSIGNED NOT NULL,
  `char_id` INT UNSIGNED NOT NULL,
  `kind` VARCHAR(8) NOT NULL,
  `amount` INT NOT NULL,
  `amount2` INT NOT NULL DEFAULT 0,
  `claimed` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `dm_campaign_pending_grant_char` (`char_id`, `claimed`)
) ENGINE=InnoDB;

INSERT IGNORE INTO `sql_updates` (`timestamp`) VALUES (20260922);
