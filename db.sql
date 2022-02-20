CREATE TABLE `student` (
	`id` VARCHAR(20) NOT NULL,
	`name` VARCHAR(30) NOT NULL,
	`password` VARCHAR(255) NOT NULL,
	`bio` VARCHAR(255) NOT NULL,
	`dob` VARCHAR(20) NOT NULL,
	`school_id` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `school` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(100) NOT NULL,
	`state` VARCHAR(100) NOT NULL,
	`city` VARCHAR(100) NOT NULL,
	`country` VARCHAR(100) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `admin` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`email` VARCHAR(255) NOT NULL,
	`password` VARCHAR(255) NOT NULL,
	`school_id` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `club` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(50) NOT NULL,
	`description` VARCHAR(255) NOT NULL,
	`school_id` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `club_post` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`title` VARCHAR(255) NOT NULL,
	`content` VARCHAR(255) NOT NULL,
	`club_id` INT NOT NULL,
	`student_id` VARCHAR(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `billboard_post` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`title` VARCHAR(255) NOT NULL,
	`content` VARCHAR(255) NOT NULL,
	`school_id` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `product` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(30) NOT NULL,
	`description` VARCHAR(255) NOT NULL,
	`price` VARCHAR(10) NOT NULL,
	`school_id` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `order` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`product_id` INT NOT NULL,
	`seller_id` VARCHAR(255) NOT NULL,
	`buyer_id` VARCHAR(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `event` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(50) NOT NULL,
	`description` VARCHAR(255) NOT NULL,
	`date_time` DATETIME NOT NULL,
	`location` VARCHAR(50) NOT NULL,
	`school_id` INT NOT NULL,
	`student_id` VARCHAR(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `advertisement` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`title` VARCHAR(255) NOT NULL,
	`img_url` VARCHAR(255) NOT NULL,
	`admin_id` INT NOT NULL,
	`school_id` INT NOT NULL,
	PRIMARY KEY (`id`)
);

ALTER TABLE `student` ADD CONSTRAINT `student_fk0` FOREIGN KEY (`school_id`) REFERENCES `school`(`id`);

ALTER TABLE `admin` ADD CONSTRAINT `admin_fk0` FOREIGN KEY (`school_id`) REFERENCES `school`(`id`);

ALTER TABLE `club` ADD CONSTRAINT `club_fk0` FOREIGN KEY (`school_id`) REFERENCES `school`(`id`);

ALTER TABLE `club_post` ADD CONSTRAINT `club_post_fk0` FOREIGN KEY (`club_id`) REFERENCES `club`(`id`);

ALTER TABLE `club_post` ADD CONSTRAINT `club_post_fk1` FOREIGN KEY (`student_id`) REFERENCES `student`(`id`);

ALTER TABLE `billboard_post` ADD CONSTRAINT `billboard_post_fk0` FOREIGN KEY (`school_id`) REFERENCES `school`(`id`);

ALTER TABLE `product` ADD CONSTRAINT `product_fk0` FOREIGN KEY (`school_id`) REFERENCES `school`(`id`);

ALTER TABLE `order` ADD CONSTRAINT `order_fk0` FOREIGN KEY (`product_id`) REFERENCES `product`(`id`);

ALTER TABLE `order` ADD CONSTRAINT `order_fk1` FOREIGN KEY (`seller_id`) REFERENCES `student`(`id`);

ALTER TABLE `order` ADD CONSTRAINT `order_fk2` FOREIGN KEY (`buyer_id`) REFERENCES `student`(`id`);

ALTER TABLE `event` ADD CONSTRAINT `event_fk0` FOREIGN KEY (`school_id`) REFERENCES `school`(`id`);

ALTER TABLE `event` ADD CONSTRAINT `event_fk1` FOREIGN KEY (`student_id`) REFERENCES `student`(`id`);

ALTER TABLE `advertisement` ADD CONSTRAINT `advertisement_fk0` FOREIGN KEY (`admin_id`) REFERENCES `admin`(`id`);

ALTER TABLE `advertisement` ADD CONSTRAINT `advertisement_fk1` FOREIGN KEY (`school_id`) REFERENCES `school`(`id`);