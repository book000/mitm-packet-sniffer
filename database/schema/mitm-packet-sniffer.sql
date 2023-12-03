CREATE TABLE `ignore_hosts` (
  `address` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_seen_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `next_check_phase` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `responses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `host` varchar(255) NOT NULL,
  `port` int NOT NULL,
  `method` varchar(10) NOT NULL,
  `scheme` text NOT NULL,
  `authority` text NOT NULL,
  `path` text NOT NULL,
  `path_hash` varchar(255) NOT NULL,
  `query` longtext NOT NULL,
  `request_content` longtext NULL,
  `request_content_type` varchar(10) NOT NULL,
  `http_version` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `request_headers` longtext NOT NULL,
  `status_code` int NOT NULL,
  `response_headers` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `response_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `response_content_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_host_port_method_pathhash_statuscode_contenttype` (`host`,`port`,`method`,`path_hash`,`status_code`,`response_content_type`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1636 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
