CREATE DATABASE IF NOT EXISTS `imdb`;
CREATE TABLE `imdb`.`movies` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(250) NULL,
  `url` VARCHAR(250) NULL,
  `genre` VARCHAR(250) NULL,
  `year` VARCHAR(50) NULL,
  `country` VARCHAR(50) NULL,
  `gross` VARCHAR(50) NULL,
  `budget` VARCHAR(50) NULL,
  `path` VARCHAR(100) NULL ,
  `director_data` JSON NULL,
  `writer_data` JSON NULL,
  `producer_data` JSON NULL,
  `release_dates` JSON NULL,
  `production_data` JSON NULL,
  `distributors_data` JSON NULL,
  `awards` JSON NULL,
  PRIMARY KEY (`id`));
