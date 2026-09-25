#1790300137

-- Account-persistent, server-authoritative player Guide discoveries.
-- Story quest state is deliberately stored elsewhere, per character.
CREATE TABLE IF NOT EXISTS `korangar_account_discovery` (
	`account_id` INT UNSIGNED NOT NULL,
	`mob_id` SMALLINT UNSIGNED NOT NULL,
	`milestone` TINYINT UNSIGNED NOT NULL DEFAULT 1,
	`discovered_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`account_id`, `mob_id`),
	KEY `korangar_account_discovery_mob` (`mob_id`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `korangar_account_map_discovery` (
	`account_id` INT UNSIGNED NOT NULL,
	`map_name` VARCHAR(24) NOT NULL,
	`discovered_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`account_id`, `map_name`),
	KEY `korangar_account_map_discovery_map` (`map_name`)
) ENGINE=InnoDB;

INSERT IGNORE INTO `sql_updates` (`timestamp`) VALUES (1790300137);
