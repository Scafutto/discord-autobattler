CREATE TABLE `users` (
  `id` varchar(255) NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `characters` (
  `id` int NOT NULL AUTO_INCREMENT,
  `class` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `level` int DEFAULT '1',
  `experience` int DEFAULT '0',
  `vitality` int DEFAULT NULL,
  `power` int DEFAULT NULL,
  `defense` int DEFAULT NULL,
  `critical` int DEFAULT NULL,
  `speed` int DEFAULT NULL,
  `taunt` int DEFAULT NULL,
  `accuracy` int DEFAULT NULL,
  `dodge` int DEFAULT NULL,
  `skill1` varchar(255) DEFAULT NULL,
  `skill2` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `USERS_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `USERS_id` (`USERS_id`),
  CONSTRAINT `characters_ibfk_1` FOREIGN KEY (`USERS_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `deleted_characters` (
  `id` int NOT NULL,
  `class` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `level` int DEFAULT NULL,
  `experience` int DEFAULT NULL,
  `vitality` int DEFAULT NULL,
  `power` int DEFAULT NULL,
  `defense` int DEFAULT NULL,
  `critical` int DEFAULT NULL,
  `speed` int DEFAULT NULL,
  `taunt` int DEFAULT NULL,
  `accuracy` int DEFAULT NULL,
  `dodge` int DEFAULT NULL,
  `skill1` varchar(255) DEFAULT NULL,
  `skill2` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `USERS_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `achievements` (
  `USERS_id` varchar(255) DEFAULT NULL,
  `achievement_name` varchar(255) DEFAULT NULL,
  `achievement_value` tinyint(1) DEFAULT NULL,
  KEY `USERS_id` (`USERS_id`),
  CONSTRAINT `achievements_ibfk_1` FOREIGN KEY (`USERS_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `completed_quests` (
  `USERS_id` varchar(255) DEFAULT NULL,
  `act` int DEFAULT NULL,
  `quest` varchar(255) DEFAULT NULL,
  KEY `USERS_id` (`USERS_id`),
  CONSTRAINT `completed_quests_ibfk_1` FOREIGN KEY (`USERS_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `team` (
  `id` int NOT NULL AUTO_INCREMENT,
  `USERS_id` varchar(255) DEFAULT NULL,
  `CHARACTERS_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `USERS_id` (`USERS_id`),
  KEY `CHARACTERS_id` (`CHARACTERS_id`),
  CONSTRAINT `team_ibfk_1` FOREIGN KEY (`USERS_id`) REFERENCES `users` (`id`),
  CONSTRAINT `team_ibfk_2` FOREIGN KEY (`CHARACTERS_id`) REFERENCES `characters` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE unlocked_characters (
    USERS_id VARCHAR(255),
    character_class VARCHAR(255),
    FOREIGN KEY (USERS_id) REFERENCES users(id)
);
