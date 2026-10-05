#1791165605

-- Shared crafting commission board (korangar GDD F31, decision D7). The board
-- only records requests: items and zeny move by ordinary player trade, never
-- through this table. Names are copied at post/assign time for display.
CREATE TABLE IF NOT EXISTS `korangar_commission` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `requester_char_id` INT UNSIGNED NOT NULL,
  `requester_name` VARCHAR(30) NOT NULL,
  `item_name` VARCHAR(50) NOT NULL,
  `fee` INT UNSIGNED NOT NULL DEFAULT 0,
  `crafter_char_id` INT UNSIGNED NOT NULL DEFAULT 0,
  `crafter_name` VARCHAR(30) NOT NULL DEFAULT '',
  `status` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `korangar_commission_status` (`status`),
  KEY `korangar_commission_requester` (`requester_char_id`, `status`)
) ENGINE=InnoDB;

INSERT IGNORE INTO `sql_updates` (`timestamp`) VALUES (1791165605);
