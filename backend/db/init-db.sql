-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`User` (
  `IdUser` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(25) NOT NULL COMMENT 'Сторого Кирилица',
  `LastName` VARCHAR(50) NOT NULL COMMENT 'Строго Кирилица',
  `SecondName` VARCHAR(25) NULL COMMENT 'Строго Кирилица',
  `Email` VARCHAR(50) NOT NULL COMMENT 'Обязан содержать @',
  `UserName` VARCHAR(20) NOT NULL COMMENT 'без спецсимволов',
  `Password` VARCHAR(15) NOT NULL COMMENT 'от 8 символов, с 1 заглавной буквой, 1 цифрой, без спецсимволов',
  `Rating` DOUBLE NOT NULL DEFAULT 0,
  `CreatedAt` DATETIME NOT NULL,
  `Enabled` TINYINT NOT NULL DEFAULT 1 COMMENT '0 при бане',
  `Avatar` BLOB NULL COMMENT 'Фото пользователя',
  `IsStaff` TINYINT NOT NULL DEFAULT 0 COMMENT '1 - admin, 0 - user',
  PRIMARY KEY (`IdUser`),
  UNIQUE INDEX `idUser_UNIQUE` (`IdUser` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Autor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Autor` (
  `IdAutor` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(20) NULL COMMENT 'Кирилица или латиница',
  `LastName` VARCHAR(50) NOT NULL COMMENT 'Кирилица или латиница',
  UNIQUE INDEX `idAutor_UNIQUE` (`IdAutor` ASC) VISIBLE,
  PRIMARY KEY (`IdAutor`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`BookLiterary`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`BookLiterary` (
  `IdBookLiterary` INT NOT NULL AUTO_INCREMENT,
  `IdAutor` INT NOT NULL,
  `BookName` VARCHAR(50) NOT NULL,
  `Note` VARCHAR(50) NULL,
  `ISBN` VARCHAR(17) NULL,
  `YearPublishing` DATE NOT NULL COMMENT '4 цифры года',
  PRIMARY KEY (`IdBookLiterary`),
  UNIQUE INDEX `IdBookLiterary_UNIQUE` (`IdBookLiterary` ASC) VISIBLE,
  INDEX `fk_BookLiterary_Autor1_idx` (`IdAutor` ASC) VISIBLE,
  CONSTRAINT `fk_BookLiterary_Autor1`
    FOREIGN KEY (`IdAutor`)
    REFERENCES `mydb`.`Autor` (`IdAutor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Status`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Status` (
  `IdStatus` INT NOT NULL COMMENT '1x - статус обмена, 2x - статус обращения',
  `Name` VARCHAR(100) NULL COMMENT 'Описание статуса',
  PRIMARY KEY (`IdStatus`),
  UNIQUE INDEX `idStatus_UNIQUE` (`IdStatus` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`OfferList`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`OfferList` (
  `IdOfferList` INT NOT NULL AUTO_INCREMENT,
  `IdBookLiterary` INT NOT NULL,
  `IdUser` INT NOT NULL,
  `CreateAt` DATETIME NOT NULL,
  `UpdateAt` DATETIME NOT NULL COMMENT 'При создании равен CreatedAt',
  `IdStatus` INT NOT NULL,
  PRIMARY KEY (`IdOfferList`),
  UNIQUE INDEX `idOfferList_UNIQUE` (`IdOfferList` ASC) VISIBLE,
  INDEX `fk_OfferList_User_idx` (`IdUser` ASC) VISIBLE,
  INDEX `fk_OfferList_BookLiterary1_idx` (`IdBookLiterary` ASC) VISIBLE,
  INDEX `fk_OfferList_Status1_idx` (`IdStatus` ASC) VISIBLE,
  CONSTRAINT `fk_OfferList_User`
    FOREIGN KEY (`IdUser`)
    REFERENCES `mydb`.`User` (`IdUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_OfferList_BookLiterary1`
    FOREIGN KEY (`IdBookLiterary`)
    REFERENCES `mydb`.`BookLiterary` (`IdBookLiterary`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_OfferList_Status1`
    FOREIGN KEY (`IdStatus`)
    REFERENCES `mydb`.`Status` (`IdStatus`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`UserAddress`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`UserAddress` (
  `idUserAddress` INT NOT NULL AUTO_INCREMENT,
  `IdUser` INT NOT NULL,
  `AddrIndex` VARCHAR(6) NOT NULL COMMENT '6 цифр',
  `AddrCity` VARCHAR(15) NOT NULL COMMENT 'Кирилица',
  `AddrStreet` VARCHAR(25) NOT NULL COMMENT 'Кирилица, цифры, тире',
  `AddrHouse` VARCHAR(5) NOT NULL,
  `AddrStructure` VARCHAR(10) NULL COMMENT 'Число или буквы',
  `AddrApart` VARCHAR(3) NULL,
  PRIMARY KEY (`idUserAddress`),
  UNIQUE INDEX `idUserAddress_UNIQUE` (`idUserAddress` ASC) VISIBLE,
  INDEX `fk_UserAddress_User1_idx` (`IdUser` ASC) VISIBLE,
  CONSTRAINT `fk_UserAddress_User1`
    FOREIGN KEY (`IdUser`)
    REFERENCES `mydb`.`User` (`IdUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`WishList`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`WishList` (
  `IdWishList` INT NOT NULL AUTO_INCREMENT,
  `IdUser` INT NOT NULL,
  `CreatedAt` DATETIME NOT NULL,
  `UpdateAt` DATETIME NOT NULL COMMENT 'При создании равен CreatedAt',
  `IdStatus` INT NOT NULL,
  `IdUserAddress` INT NOT NULL,
  PRIMARY KEY (`IdWishList`),
  UNIQUE INDEX `IdWishList_UNIQUE` (`IdWishList` ASC) VISIBLE,
  INDEX `fk_WishList_User1_idx` (`IdUser` ASC) VISIBLE,
  INDEX `fk_WishList_Status1_idx` (`IdStatus` ASC) VISIBLE,
  INDEX `fk_WishList_UserAddress1_idx` (`IdUserAddress` ASC) VISIBLE,
  CONSTRAINT `fk_WishList_User1`
    FOREIGN KEY (`IdUser`)
    REFERENCES `mydb`.`User` (`IdUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_WishList_Status1`
    FOREIGN KEY (`IdStatus`)
    REFERENCES `mydb`.`Status` (`IdStatus`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_WishList_UserAddress1`
    FOREIGN KEY (`IdUserAddress`)
    REFERENCES `mydb`.`UserAddress` (`idUserAddress`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`UserMsg`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`UserMsg` (
  `IdUserMsg` INT NOT NULL AUTO_INCREMENT,
  `IdUser` INT NOT NULL,
  `CreateAt` DATETIME NOT NULL,
  `Text` VARCHAR(250) NOT NULL COMMENT 'Кирилица, кавычки, знаки препинания',
  `Notes` VARCHAR(150) NULL COMMENT 'Заполняет admin\nКирилица, кавычки, знаки препинания',
  `IdStatus` INT NOT NULL,
  `Type` TINYINT NOT NULL COMMENT '1 - входящее, 0 - исходящее',
  PRIMARY KEY (`IdUserMsg`),
  UNIQUE INDEX `IdUserMsg_UNIQUE` (`IdUserMsg` ASC) VISIBLE,
  INDEX `fk_UserMsg_User1_idx` (`IdUser` ASC) VISIBLE,
  INDEX `fk_UserMsg_Status1_idx` (`IdStatus` ASC) VISIBLE,
  CONSTRAINT `fk_UserMsg_User1`
    FOREIGN KEY (`IdUser`)
    REFERENCES `mydb`.`User` (`IdUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_UserMsg_Status1`
    FOREIGN KEY (`IdStatus`)
    REFERENCES `mydb`.`Status` (`IdStatus`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`ExchangeList`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`ExchangeList` (
  `IdExchangeList` INT NOT NULL AUTO_INCREMENT,
  `IdOfferList1` INT NOT NULL,
  `IdWishList1` INT NOT NULL,
  `IdOfferList2` INT NOT NULL,
  `IdWishList2` INT NOT NULL,
  `CreateAt` DATETIME NOT NULL COMMENT 'Обновляется при изменении статуса\nОтсчёт периодов:\n- 2 дня для подтверждения обмена вторым участником\n- 7 дней для подтверждения отправки книги обоими участниками',
  `IsBoth` TINYINT NOT NULL DEFAULT 0 COMMENT '0 - обмен не подтверждён\n1 - обмен подтверждён',
  PRIMARY KEY (`IdExchangeList`),
  UNIQUE INDEX `IdExchangeList_UNIQUE` (`IdExchangeList` ASC) VISIBLE,
  INDEX `fk_ExchangeList_OfferList1_idx` (`IdOfferList1` ASC) VISIBLE,
  INDEX `fk_ExchangeList_WishList1_idx` (`IdWishList1` ASC) VISIBLE,
  INDEX `fk_ExchangeList_OfferList2_idx` (`IdOfferList2` ASC) VISIBLE,
  INDEX `fk_ExchangeList_WishList2_idx` (`IdWishList2` ASC) VISIBLE,
  CONSTRAINT `fk_ExchangeList_OfferList1`
    FOREIGN KEY (`IdOfferList1`)
    REFERENCES `mydb`.`OfferList` (`IdOfferList`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ExchangeList_WishList1`
    FOREIGN KEY (`IdWishList1`)
    REFERENCES `mydb`.`WishList` (`IdWishList`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ExchangeList_OfferList2`
    FOREIGN KEY (`IdOfferList2`)
    REFERENCES `mydb`.`OfferList` (`IdOfferList`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ExchangeList_WishList2`
    FOREIGN KEY (`IdWishList2`)
    REFERENCES `mydb`.`WishList` (`IdWishList`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`UserExchangeList`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`UserExchangeList` (
  `IdUserExchangeList` INT NOT NULL AUTO_INCREMENT,
  `IdOfferList` INT NOT NULL,
  `TrackNumber` VARCHAR(14) NULL COMMENT 'Код с \"Почты России\", возможно тире',
  `Receiving` TINYINT NOT NULL COMMENT '0 - книга не получена\n1 - книга получена',
  PRIMARY KEY (`IdUserExchangeList`),
  UNIQUE INDEX `IdUserExchangeList_UNIQUE` (`IdUserExchangeList` ASC) VISIBLE,
  INDEX `fk_UserExchangeList_OfferList1_idx` (`IdOfferList` ASC) VISIBLE,
  CONSTRAINT `fk_UserExchangeList_OfferList1`
    FOREIGN KEY (`IdOfferList`)
    REFERENCES `mydb`.`OfferList` (`IdOfferList`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`UserList`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`UserList` (
  `IdUserList` INT NOT NULL AUTO_INCREMENT,
  `IdOfferList` INT NULL COMMENT 'null если IdWishList не null',
  `IdWishList` INT NULL COMMENT 'null если IdOfferList не null',
  PRIMARY KEY (`IdUserList`),
  UNIQUE INDEX `IdUserList_UNIQUE` (`IdUserList` ASC) VISIBLE,
  INDEX `fk_UserList_OfferList1_idx` (`IdOfferList` ASC) VISIBLE,
  INDEX `fk_UserList_WishList1_idx` (`IdWishList` ASC) VISIBLE,
  CONSTRAINT `fk_UserList_OfferList1`
    FOREIGN KEY (`IdOfferList`)
    REFERENCES `mydb`.`OfferList` (`IdOfferList`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_UserList_WishList1`
    FOREIGN KEY (`IdWishList`)
    REFERENCES `mydb`.`WishList` (`IdWishList`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`BookResponse`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`BookResponse` (
  `IdBookLiterary` INT NOT NULL,
  `IdUser` INT NOT NULL,
  `CreateAt` DATETIME NOT NULL,
  `Response` VARCHAR(500) NOT NULL COMMENT 'Кирилица, возможны кавычки и знаки препинания',
  `Note` VARCHAR(50) NULL,
  PRIMARY KEY (`IdBookLiterary`, `IdUser`),
  INDEX `fk_BookLiterary_has_User_User1_idx` (`IdUser` ASC) VISIBLE,
  INDEX `fk_BookLiterary_has_User_BookLiterary1_idx` (`IdBookLiterary` ASC) VISIBLE,
  CONSTRAINT `fk_BookLiterary_has_User_BookLiterary1`
    FOREIGN KEY (`IdBookLiterary`)
    REFERENCES `mydb`.`BookLiterary` (`IdBookLiterary`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_BookLiterary_has_User_User1`
    FOREIGN KEY (`IdUser`)
    REFERENCES `mydb`.`User` (`IdUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Category`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Category` (
  `IdCategory` INT NOT NULL AUTO_INCREMENT,
  `Value` VARCHAR(25) NOT NULL COMMENT 'Кирилица',
  `MultySelect` TINYINT NOT NULL DEFAULT 0 COMMENT '0 - выбор одного из\n1 - выбор одного или несколько из',
  PRIMARY KEY (`IdCategory`),
  UNIQUE INDEX `idCategory_UNIQUE` (`IdCategory` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`ValueCategory`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`ValueCategory` (
  `IdValueCategory` INT NOT NULL AUTO_INCREMENT,
  `Value` VARCHAR(25) NOT NULL COMMENT 'Кирилица',
  `IdCategory` INT NOT NULL,
  PRIMARY KEY (`IdValueCategory`),
  UNIQUE INDEX `idCategoryValue_UNIQUE` (`IdValueCategory` ASC) VISIBLE,
  INDEX `fk_ValueCategory_Category1_idx` (`IdCategory` ASC) VISIBLE,
  CONSTRAINT `fk_ValueCategory_Category1`
    FOREIGN KEY (`IdCategory`)
    REFERENCES `mydb`.`Category` (`IdCategory`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`UserValueCategory`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`UserValueCategory` (
  `IdUserList` INT NOT NULL,
  `IdValueCategory` INT NOT NULL,
  PRIMARY KEY (`IdUserList`, `IdValueCategory`),
  INDEX `fk_UserList_has_CategoryValue_CategoryValue1_idx` (`IdValueCategory` ASC) VISIBLE,
  INDEX `fk_UserList_has_CategoryValue_UserList1_idx` (`IdUserList` ASC) VISIBLE,
  CONSTRAINT `fk_UserList_has_CategoryValue_UserList1`
    FOREIGN KEY (`IdUserList`)
    REFERENCES `mydb`.`UserList` (`IdUserList`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_UserList_has_CategoryValue_CategoryValue1`
    FOREIGN KEY (`IdValueCategory`)
    REFERENCES `mydb`.`ValueCategory` (`IdValueCategory`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Session`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Session` (
  `IdSession` INT NOT NULL AUTO_INCREMENT,
  `SessionToken` VARCHAR(36) NOT NULL,
  `UserId` INT NOT NULL,
  `CreatedAt` DATETIME NOT NULL,
  `ExpiresAt` DATETIME NOT NULL,
  PRIMARY KEY (`IdSession`),
  UNIQUE INDEX `SessionToken_UNIQUE` (`SessionToken` ASC) VISIBLE,
  INDEX `fk_Session_User1_idx` (`UserId` ASC) VISIBLE,
  CONSTRAINT `fk_Session_User1`
    FOREIGN KEY (`UserId`)
    REFERENCES `mydb`.`User` (`IdUser`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
