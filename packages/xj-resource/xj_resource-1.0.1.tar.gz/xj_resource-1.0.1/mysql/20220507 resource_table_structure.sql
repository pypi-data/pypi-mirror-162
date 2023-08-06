/*
 Navicat Premium Data Transfer

 Source Server         : 北京1号 abmin GT0v7175
 Source Server Type    : MySQL
 Source Server Version : 80018
 Source Host           : bj.muztak.cn:63306
 Source Schema         : pay_muztak_cn

 Target Server Type    : MySQL
 Target Server Version : 80018
 File Encoding         : 65001

 Date: 07/05/2022 00:25:40
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for resource_image
-- ----------------------------
DROP TABLE IF EXISTS `resource_image`;
CREATE TABLE `resource_image`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `filename` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `format` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `thumb` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `snapshot` json NULL,
  `md5` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `resource_image_user_id_f56dcdb4_fk_user_base_info_id`(`user_id`) USING BTREE,
  INDEX `resource_image_url_9995db84`(`url`) USING BTREE,
  CONSTRAINT `resource_image_user_id_f56dcdb4_fk_user_base_info_id` FOREIGN KEY (`user_id`) REFERENCES `user_base_info` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 258 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for resource_image_map
-- ----------------------------
DROP TABLE IF EXISTS `resource_image_map`;
CREATE TABLE `resource_image_map`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `source_id` bigint(20) NULL DEFAULT NULL,
  `source_table` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `price` decimal(32, 8) NULL DEFAULT NULL,
  `image_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `resource_image_map_image_id_cd0bd534_fk_resource_image_id`(`image_id`) USING BTREE,
  INDEX `resource_image_map_price_e7845028`(`price`) USING BTREE,
  CONSTRAINT `resource_image_map_image_id_cd0bd534_fk_resource_image_id` FOREIGN KEY (`image_id`) REFERENCES `resource_image` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
