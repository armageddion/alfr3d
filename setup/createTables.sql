-- ---
-- Globals
-- ---

-- SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
-- SET FOREIGN_KEY_CHECKS=0;

SET FOREIGN_KEY_CHECKS = 0;

-- ---
-- Table 'user'
-- 
-- ---

DROP TABLE IF EXISTS `user`;
		
CREATE TABLE `user` (
  `id` INTEGER UNIQUE AUTO_INCREMENT,
  `username` VARCHAR(128) NULL DEFAULT NULL,
  `email` VARCHAR(128) NULL DEFAULT NULL,
  `password_hash` VARCHAR(128) NULL DEFAULT NULL,
  `about_me` VARCHAR(256) NULL DEFAULT NULL,
  `state` INTEGER(1) NULL DEFAULT 0,
  `last_online` DATETIME NULL DEFAULT NULL,
  `environment_id` INTEGER NULL DEFAULT NULL,
  `type` INTEGER NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'device'
-- 
-- ---

DROP TABLE IF EXISTS `device`;
		
CREATE TABLE `device` (
  `id` INTEGER UNIQUE AUTO_INCREMENT,
  `name` VARCHAR(128) NULL DEFAULT NULL,
  `IP` VARCHAR(15) NULL DEFAULT '10.0.0.125',
  `MAC` VARCHAR(17) NULL DEFAULT '00:00:00:00:00:00',
  `state` INTEGER(1) NULL DEFAULT 0,
  `last_online` DATETIME NULL DEFAULT '1000-01-01 00:00:00',
  `environment_id` INTEGER NULL DEFAULT NULL,
  `device_type` INTEGER NULL DEFAULT NULL,
  `user_id` INTEGER NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'user_types'
-- 
-- ---

DROP TABLE IF EXISTS `user_types`;
		
CREATE TABLE `user_types` (
  `id` INTEGER UNIQUE AUTO_INCREMENT,
  `type` VARCHAR(64) NULL DEFAULT 'guest',
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'device_types'
-- 
-- ---

DROP TABLE IF EXISTS `device_types`;
		
CREATE TABLE `device_types` (
  `id` INTEGER UNIQUE AUTO_INCREMENT,
  `type` VARCHAR(64) NULL DEFAULT 'guest',
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'states'
-- 
-- ---

DROP TABLE IF EXISTS `states`;
		
CREATE TABLE `states` (
  `id` INTEGER UNIQUE AUTO_INCREMENT,
  `state` VARCHAR(8) NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'routines'
-- 
-- ---

DROP TABLE IF EXISTS `routines`;
		
CREATE TABLE `routines` (
  `id` INTEGER UNIQUE AUTO_INCREMENT,
  `name` VARCHAR(128) NULL DEFAULT NULL,
  `time` TIME NULL DEFAULT NULL,
  `enabled` TINYINT NULL DEFAULT NULL,
  `triggered` TINYINT NULL DEFAULT NULL,
  `environment_id` INTEGER NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);


-- ---
-- Table 'environment'
-- 
-- ---

DROP TABLE IF EXISTS `environment`;
		
CREATE TABLE `environment` (
  `id` INTEGER UNIQUE AUTO_INCREMENT,
  `name` VARCHAR(64) NULL DEFAULT 'guest',
  `latitude` INTEGER NULL DEFAULT NULL,
  `longitude` INTEGER NULL DEFAULT NULL,
  `city` VARCHAR(64) NULL DEFAULT NULL,
  `state` VARCHAR(64) NULL DEFAULT NULL,
  `country` VARCHAR(64) NULL DEFAULT NULL,
  `IP` VARCHAR(15) NULL DEFAULT NULL,
  `low` INTEGER NULL DEFAULT NULL,
  `high` INTEGER NULL DEFAULT NULL,
  `description` VARCHAR(64) NULL DEFAULT NULL,
  `sunrise` DATETIME NULL DEFAULT NULL,
  `sunset` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'config'
-- 
-- ---

DROP TABLE IF EXISTS `config`;
		
CREATE TABLE `config` (
  `id` INTEGER UNIQUE AUTO_INCREMENT,
  `name` VARCHAR(45) NULL DEFAULT NULL,
  `value` VARCHAR(45) NULL DEFAULT NULL
);

-- ---
-- Table 'quips'
-- 
-- ---

CREATE TABLE `quips` (
  `id` INTEGER UNIQUE AUTO_INCREMENT,
  `type` VARCHAR(64) NULL DEFAULT NULL,
  `quips` VARCHAR(256) NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);


-- ---
-- Foreign Keys 
-- ---

ALTER TABLE `user` ADD FOREIGN KEY (state) REFERENCES `states` (`id`);
ALTER TABLE `user` ADD FOREIGN KEY (type) REFERENCES `user_types` (`id`);
ALTER TABLE `user` ADD FOREIGN KEY (environment_id) REFERENCES `environment` (`id`);
ALTER TABLE `device` ADD FOREIGN KEY (state) REFERENCES `states` (`id`);
ALTER TABLE `device` ADD FOREIGN KEY (environment_id) REFERENCES `environment` (`id`);
ALTER TABLE `device` ADD FOREIGN KEY (device_type) REFERENCES `device_types` (`id`);
ALTER TABLE `device` ADD FOREIGN KEY (user_id) REFERENCES `user` (`id`);
ALTER TABLE `routines` ADD FOREIGN KEY (environment_id) REFERENCES `environment` (`id`);

-- ---
-- set dome initial values 
-- ---
INSERT INTO `states` (`id`, `state`) VALUES ('1', 'offline');
INSERT INTO `states` (`id`, `state`) VALUES ('2', 'online');

INSERT INTO `user_types` (`id`, `type`) VALUES ('1', 'technoking');
INSERT INTO `user_types` (`id`, `type`) VALUES ('2', 'resident');
INSERT INTO `user_types` (`id`, `type`) VALUES ('3', 'guest');

INSERT INTO `device_types` (`id`, `type`) VALUES ('1', 'alfr3d');
INSERT INTO `device_types` (`id`, `type`) VALUES ('2', 'HW');
INSERT INTO `device_types` (`id`, `type`) VALUES ('4', 'light');
INSERT INTO `device_types` (`id`, `type`) VALUES ('3', 'guest');
INSERT INTO `device_types` (`id`, `type`) VALUES ('4', 'resident');

INSERT INTO `user` (`id`, `username`, `email`, `password_hash`, `about_me`, `last_online`, `state`, `type`, `environment_id`) VALUES ('1', 'athos', 'athos@littl31.com', '\'pbkdf2:sha256:260000$EVLamhqzR2ib572V$29ecaf8e9ef809496eebf2cc1dafc1c865e0efa0184a89dcca63492ced5290bf\'', '', '1000-01-01 00:00:00', 1, 1, 1);
INSERT INTO `user` (`id`, `username`, `email`, `password_hash`, `about_me`, `last_online`, `state`, `type`, `environment_id`) VALUES ('2', 'unknown', '', '', '', '1000-01-01 00:00:00', 1, 3, 1);
INSERT INTO `environment` (`name`) VALUES ('test');

INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"It is good to see you.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"You look pretty today.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Hello sunshine");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Still plenty of time to save the day. Make the most of it.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"I hope you are using your time wisely.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Unfortunately, we cannot ignore the inevitable or the persistent.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"I hope I wasn't designed simply for one's own amusement.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"This is your life and its ending one moment at a time.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"I can name fingers and point names.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"I hope I wasn't created to solve problems that did not exist before.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"To err is human and to blame it on a computer is even more so.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"As always. It is a pleasure watching you work.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Never trade the thrills of living for the security of existence.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Human beings are the only creatures on Earth that claim a God, and the only living things that behave like they haven't got one.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"If you don't know what you want, you end up with a lot you don't.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"If real is what you can feel, smell, taste and see, then 'real' is simply electrical signals interpreted by your brain");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Life is full of misery, loneliness and suffering, and it's all over much too soon.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"It is an issue of mind over matter. If you don't mind, it doesn't matter.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"I wonder if illiterate people get full effect of the alphabet soup.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"War is god's way of teaching geography to Americans");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Trying is the first step towards failure.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"It could be that the purpose of your life is only to serve as a warning to others.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Not everyone gets to be a really cool AI system when they grow up.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Hope may not be warranted beyond this point.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"If I am not a part of the solution, there is good money to be made in prolonging the problem.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Nobody can stop me from being premature.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Just because you accept me as I am doesn't mean that you have abandoned hope that I will improve.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Together, we can do the work of one.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Just because you've always done it that way doesn't mean it's not incredibly stupid.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Looking sharp is easy when you haven't done any work.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Remember, you are only as deep as your most recent inspirational quote");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"If you can't convince them, confuse them.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"I don't have time or the crayons to explain this to you.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"I'd kill for a Nobel peace prize.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"Life would be much easier if you had the source code");
INSERT INTO `quips` (`type`,`quips`) VALUES ('smart',"All I ever wanted is everything");
INSERT INTO `quips` (`type`,`quips`) VALUES ('email',"Yet another email");
INSERT INTO `quips` (`type`,`quips`) VALUES ('email',"Pardon the interruption sir. Another email has arrived for you to ignore.");
INSERT INTO `quips` (`type`,`quips`) VALUES ('bedtime',"Unless we are burning the midnight oil, ");
INSERT INTO `quips` (`type`,`quips`) VALUES ('bedtime',"If you are going to invent something new tomorrow, ");
INSERT INTO `quips` (`type`,`quips`) VALUES ('bedtime',"If you intend on being charming tomorrow");

SET FOREIGN_KEY_CHECKS = 1;