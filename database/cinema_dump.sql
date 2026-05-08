-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: cinema_db
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `booking`
--

DROP TABLE IF EXISTS `booking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking` (
  `booking_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `deal_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `total_amount` decimal(10,2) NOT NULL,
  `booking_code` int DEFAULT NULL,
  `screening_id` int DEFAULT NULL,
  PRIMARY KEY (`booking_id`),
  UNIQUE KEY `booking_code` (`booking_code`),
  KEY `deal_id` (`deal_id`),
  KEY `idx_booking_user_created_at` (`user_id`,`created_at`),
  KEY `fk_booking_screening_snap` (`screening_id`),
  CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `customer` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `booking_ibfk_2` FOREIGN KEY (`deal_id`) REFERENCES `deal` (`deal_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_booking_screening_snap` FOREIGN KEY (`screening_id`) REFERENCES `screening` (`screening_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking`
--

LOCK TABLES `booking` WRITE;
/*!40000 ALTER TABLE `booking` DISABLE KEYS */;
INSERT INTO `booking` VALUES (1,1,NULL,'2026-05-06 15:54:36',44.50,100001,NULL),(2,2,1,'2026-05-06 15:54:36',15.30,100002,NULL),(3,3,NULL,'2026-05-06 15:54:36',18.00,100003,NULL),(4,9,NULL,'2026-05-06 17:15:24',55.00,100004,NULL),(5,9,NULL,'2026-05-06 17:31:09',56.50,100005,NULL),(6,9,NULL,'2026-05-06 23:58:39',187.50,100006,NULL),(7,9,NULL,'2026-05-07 00:30:14',88.00,100007,NULL),(8,9,NULL,'2026-05-07 13:00:31',42.50,100008,NULL),(9,9,NULL,'2026-05-07 14:19:54',22.50,100009,NULL),(10,9,NULL,'2026-05-07 15:53:19',27.00,100010,NULL),(11,9,NULL,'2026-05-07 17:57:03',20.50,100011,11),(12,9,NULL,'2026-05-07 19:13:01',81.70,100012,11),(13,9,NULL,'2026-05-07 19:15:36',62.50,100013,12),(14,9,NULL,'2026-05-08 00:27:27',32.50,100014,18),(15,9,NULL,'2026-05-08 00:29:26',2.50,100015,18),(16,10,NULL,'2026-05-08 00:56:35',30.00,100016,18),(17,10,NULL,'2026-05-08 00:58:22',93.50,100017,14),(18,9,NULL,'2026-05-08 01:09:29',17.50,100018,18);
/*!40000 ALTER TABLE `booking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking_consumable`
--

DROP TABLE IF EXISTS `booking_consumable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking_consumable` (
  `booking_id` int NOT NULL,
  `consumable_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`booking_id`,`consumable_id`),
  KEY `consumable_id` (`consumable_id`),
  CONSTRAINT `booking_consumable_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`booking_id`) ON DELETE CASCADE,
  CONSTRAINT `booking_consumable_ibfk_2` FOREIGN KEY (`consumable_id`) REFERENCES `consumable` (`consumable_id`) ON DELETE CASCADE,
  CONSTRAINT `booking_consumable_chk_1` CHECK ((`quantity` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking_consumable`
--

LOCK TABLES `booking_consumable` WRITE;
/*!40000 ALTER TABLE `booking_consumable` DISABLE KEYS */;
INSERT INTO `booking_consumable` VALUES (1,1,1),(4,1,1),(4,5,1),(6,1,1),(6,2,1),(6,3,1),(6,4,1),(6,5,1),(7,3,9),(10,3,1),(17,2,1),(17,3,1),(17,5,2);
/*!40000 ALTER TABLE `booking_consumable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consumable`
--

DROP TABLE IF EXISTS `consumable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consumable` (
  `consumable_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `stock_quantity` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`consumable_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consumable`
--

LOCK TABLES `consumable` WRITE;
/*!40000 ALTER TABLE `consumable` DISABLE KEYS */;
INSERT INTO `consumable` VALUES (1,'Large Popcorn',8.00,498),(2,'Large Soda',6.00,498),(3,'Candy Box',4.50,98),(4,'Hot Dog',9.00,249),(5,'Chocolate',4.00,196);
/*!40000 ALTER TABLE `consumable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `user_id` int NOT NULL,
  `birth_date` date DEFAULT NULL,
  `loyalty_points` int DEFAULT '0',
  `membership_tier` varchar(50) DEFAULT 'Standard',
  PRIMARY KEY (`user_id`),
  CONSTRAINT `customer_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES (1,'1990-05-14',1500,'VIP'),(2,'1985-10-22',200,'Standard'),(3,'2001-01-08',50,'Standard'),(9,'2002-12-11',0,'Standard'),(10,NULL,0,'Standard');
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_favorite_movie`
--

DROP TABLE IF EXISTS `customer_favorite_movie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_favorite_movie` (
  `user_id` int NOT NULL,
  `movie_id` int NOT NULL,
  PRIMARY KEY (`user_id`,`movie_id`),
  KEY `movie_id` (`movie_id`),
  CONSTRAINT `customer_favorite_movie_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `customer` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `customer_favorite_movie_ibfk_2` FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_favorite_movie`
--

LOCK TABLES `customer_favorite_movie` WRITE;
/*!40000 ALTER TABLE `customer_favorite_movie` DISABLE KEYS */;
INSERT INTO `customer_favorite_movie` VALUES (1,1),(2,2),(1,3),(9,4),(9,6);
/*!40000 ALTER TABLE `customer_favorite_movie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deal`
--

DROP TABLE IF EXISTS `deal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deal` (
  `deal_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `discount_percent` decimal(5,2) NOT NULL,
  `valid_until` date DEFAULT NULL,
  PRIMARY KEY (`deal_id`),
  CONSTRAINT `deal_chk_1` CHECK ((`discount_percent` between 0 and 100))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deal`
--

LOCK TABLES `deal` WRITE;
/*!40000 ALTER TABLE `deal` DISABLE KEYS */;
INSERT INTO `deal` VALUES (1,'Student Discount',15.00,'2026-12-31'),(2,'VIP Member Special',25.00,'2026-12-31');
/*!40000 ALTER TABLE `deal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employee`
--

DROP TABLE IF EXISTS `employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee` (
  `user_id` int NOT NULL,
  `role` varchar(100) NOT NULL,
  `salary` decimal(10,2) DEFAULT NULL,
  `account_status` varchar(50) DEFAULT 'Active',
  `auth_level` int DEFAULT '1',
  `work_shift` varchar(100) DEFAULT NULL,
  `theater_id` int DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  KEY `theater_id` (`theater_id`),
  CONSTRAINT `employee_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `employee_ibfk_2` FOREIGN KEY (`theater_id`) REFERENCES `theater` (`theater_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee`
--

LOCK TABLES `employee` WRITE;
/*!40000 ALTER TABLE `employee` DISABLE KEYS */;
INSERT INTO `employee` VALUES (4,'System Admin',8500.00,'Active',3,'All',NULL),(5,'Ticket Counter',3500.00,'Active',1,'Morning',1),(6,'Usher',3000.00,'Active',1,'Evening',2),(7,'General Manager',9000.00,'Active',3,'All',NULL),(8,'Cashier',5000.00,'Active',1,'Evening',1),(10,'Cashier',7500.00,'Active',1,'All',1);
/*!40000 ALTER TABLE `employee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `format`
--

DROP TABLE IF EXISTS `format`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `format` (
  `format_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`format_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `format`
--

LOCK TABLES `format` WRITE;
/*!40000 ALTER TABLE `format` DISABLE KEYS */;
INSERT INTO `format` VALUES (1,'2D'),(2,'3D'),(3,'IMAX');
/*!40000 ALTER TABLE `format` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genre`
--

DROP TABLE IF EXISTS `genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genre` (
  `genre_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`genre_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genre`
--

LOCK TABLES `genre` WRITE;
/*!40000 ALTER TABLE `genre` DISABLE KEYS */;
INSERT INTO `genre` VALUES (2,'Action'),(10,'Adventure'),(9,'Animation'),(4,'Comedy'),(3,'Drama'),(6,'Fantasy'),(5,'Horror'),(7,'Romance'),(1,'Sci-Fi'),(8,'Thriller');
/*!40000 ALTER TABLE `genre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movie`
--

DROP TABLE IF EXISTS `movie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movie` (
  `movie_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `director` varchar(255) DEFAULT NULL,
  `duration_mins` int NOT NULL,
  `rating_age` varchar(10) DEFAULT NULL,
  `release_date` date DEFAULT NULL,
  `summary` text,
  `poster_url` varchar(500) DEFAULT NULL,
  `visibility_status` enum('now_showing','coming_soon','catalog_only') NOT NULL DEFAULT 'catalog_only',
  PRIMARY KEY (`movie_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movie`
--

LOCK TABLES `movie` WRITE;
/*!40000 ALTER TABLE `movie` DISABLE KEYS */;
INSERT INTO `movie` VALUES (1,'Dune: Part Two','Denis Villeneuve',166,'13','2024-03-01','Paul Atreides unites with the Fremen while on a warpath of revenge against the conspirators who destroyed his family. Facing a choice between the love of his life and the fate of the universe, he endeavors to prevent a terrible future.','/static/uploads/posters/Dune_Part_Two_poster_1778149423.jpeg','now_showing'),(2,'Avatar 3','James Cameron',197,'13','2025-12-19','Jake and Neytiri\'s family grapples with grief, encountering a new, aggressive Na\'vi tribe, the Ash People, who are led by the fiery Varang, as the conflict on Pandora escalates and a new moral focus emerges.','/static/uploads/posters/Avatar_ates_ve_kul_film_posteri_1778147863.jpg','now_showing'),(3,'Interstellar','Christopher Nolan',169,'13','2014-11-07','In a dystopian future where Earth has become near-uninhabitable, a team of astronauts embark on a mission to find a new home for humanity.','/static/uploads/posters/Interstellar_film_poster_1778149328.jpg','now_showing'),(4,'Se7en','David Fincher',127,'17','1995-12-11','Two detectives try to track down a serial killer who chooses his victims based on the Seven Deadly Sins.','/static/uploads/posters/se7en_1778149543.jpg','now_showing'),(6,'Prisoners','Dennis Villeneuve',153,'17','2013-12-27','A desperate father takes the law into his own hands after police fail to find two kidnapped girls.','/static/uploads/posters/Prisoners_1778142436.jpg','now_showing'),(7,'The Odyssey','Christopher Nolan',160,'13','2026-07-17','After the Trojan War, Odysseus faces a dangerous voyage back to Ithaca, meeting creatures like the Cyclops Polyphemus, Sirens, and Circe along the way.','/static/uploads/posters/Odyssey_filmi_afis_1778149891.jpg','coming_soon'),(8,'Spider-Man: Brand New Day','Destin Daniel Cretton',150,'13','2026-07-31','A forgotten Peter Parker lives alone as a full-time Spider-Man until mounting pressure triggers a dangerous change and a powerful new enemy emerges.','/static/uploads/posters/smbnd_online_1400x2100_reflection_03_1778150338.jpg','coming_soon');
/*!40000 ALTER TABLE `movie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movie_cast`
--

DROP TABLE IF EXISTS `movie_cast`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movie_cast` (
  `movie_id` int NOT NULL,
  `cast_name` varchar(255) NOT NULL,
  PRIMARY KEY (`movie_id`,`cast_name`),
  CONSTRAINT `movie_cast_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movie_cast`
--

LOCK TABLES `movie_cast` WRITE;
/*!40000 ALTER TABLE `movie_cast` DISABLE KEYS */;
INSERT INTO `movie_cast` VALUES (1,'Timothee Chalamet'),(1,'Zendaya'),(2,'Sam Worthington'),(2,'Zoe Saldana'),(3,'Anne Hathaway'),(3,'Matthew McConaughey'),(6,'Hugh Jackman'),(6,'Jake Gyllenhaal'),(7,'Anne Hathaway'),(7,'Matt Damon'),(7,'Robert Pattinson'),(7,'Tom Holland'),(7,'Zendaya'),(8,'Sadie Sink'),(8,'Tom Hollland'),(8,'Zendaya');
/*!40000 ALTER TABLE `movie_cast` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movie_format`
--

DROP TABLE IF EXISTS `movie_format`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movie_format` (
  `movie_id` int NOT NULL,
  `format_id` int NOT NULL,
  PRIMARY KEY (`movie_id`,`format_id`),
  KEY `format_id` (`format_id`),
  CONSTRAINT `movie_format_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`) ON DELETE CASCADE,
  CONSTRAINT `movie_format_ibfk_2` FOREIGN KEY (`format_id`) REFERENCES `format` (`format_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movie_format`
--

LOCK TABLES `movie_format` WRITE;
/*!40000 ALTER TABLE `movie_format` DISABLE KEYS */;
INSERT INTO `movie_format` VALUES (1,1),(4,1),(6,1),(7,1),(2,2),(3,2),(8,2),(1,3),(2,3),(3,3),(7,3),(8,3);
/*!40000 ALTER TABLE `movie_format` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movie_genre`
--

DROP TABLE IF EXISTS `movie_genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movie_genre` (
  `movie_id` int NOT NULL,
  `genre_id` int NOT NULL,
  PRIMARY KEY (`movie_id`,`genre_id`),
  KEY `genre_id` (`genre_id`),
  CONSTRAINT `movie_genre_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`) ON DELETE CASCADE,
  CONSTRAINT `movie_genre_ibfk_2` FOREIGN KEY (`genre_id`) REFERENCES `genre` (`genre_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movie_genre`
--

LOCK TABLES `movie_genre` WRITE;
/*!40000 ALTER TABLE `movie_genre` DISABLE KEYS */;
INSERT INTO `movie_genre` VALUES (1,1),(3,1),(8,1),(2,2),(7,2),(4,3),(6,3),(2,6),(7,6),(4,8),(1,10),(2,10),(3,10),(8,10);
/*!40000 ALTER TABLE `movie_genre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movie_run`
--

DROP TABLE IF EXISTS `movie_run`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movie_run` (
  `run_id` int NOT NULL AUTO_INCREMENT,
  `movie_id` int NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  PRIMARY KEY (`run_id`),
  KEY `movie_id` (`movie_id`),
  CONSTRAINT `movie_run_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`) ON DELETE CASCADE,
  CONSTRAINT `chk_movie_run_dates` CHECK ((`end_date` >= `start_date`))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movie_run`
--

LOCK TABLES `movie_run` WRITE;
/*!40000 ALTER TABLE `movie_run` DISABLE KEYS */;
INSERT INTO `movie_run` VALUES (1,1,'2024-03-01','2026-12-31'),(2,2,'2026-05-08','2027-05-01'),(3,3,'2014-11-07','2026-05-09'),(4,4,'2026-05-06','2026-05-08'),(5,8,'2026-05-08','2026-05-08'),(6,6,'2026-05-07','2026-05-08');
/*!40000 ALTER TABLE `movie_run` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int NOT NULL,
  `method` varchar(50) NOT NULL DEFAULT 'Credit Card',
  `status` varchar(50) DEFAULT 'Completed',
  PRIMARY KEY (`payment_id`),
  UNIQUE KEY `booking_id` (`booking_id`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`booking_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (1,1,'Credit Card','Refunded'),(2,2,'Cash','Refunded'),(3,3,'Credit Card','Refunded'),(4,4,'Credit Card','Refunded'),(5,5,'Credit Card','Refunded'),(6,6,'Credit Card','Paid'),(7,7,'Credit Card','Refunded'),(8,8,'Credit Card','Refunded'),(9,9,'Credit Card','Refunded'),(10,10,'Credit Card','Refunded'),(11,11,'Credit Card','Paid'),(12,12,'Credit Card','Paid'),(13,13,'Credit Card','Paid'),(14,14,'Credit Card','Paid'),(15,15,'Credit Card','Refunded'),(16,16,'POS Cash','Completed'),(17,17,'POS Mobile','Completed'),(18,18,'Credit Card','Paid');
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `review`
--

DROP TABLE IF EXISTS `review`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `review` (
  `review_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `movie_id` int NOT NULL,
  `rating` int DEFAULT NULL,
  `comment` text,
  PRIMARY KEY (`review_id`),
  KEY `user_id` (`user_id`),
  KEY `movie_id` (`movie_id`),
  CONSTRAINT `review_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `customer` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `review_ibfk_2` FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`) ON DELETE CASCADE,
  CONSTRAINT `review_chk_1` CHECK (((`rating` >= 1) and (`rating` <= 5)))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `review`
--

LOCK TABLES `review` WRITE;
/*!40000 ALTER TABLE `review` DISABLE KEYS */;
INSERT INTO `review` VALUES (1,1,1,5,'Visually stunning!'),(2,2,1,4,'A bit long, but great.'),(3,1,3,5,'Nolan is a genius.');
/*!40000 ALTER TABLE `review` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `saloon`
--

DROP TABLE IF EXISTS `saloon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `saloon` (
  `theater_id` int NOT NULL,
  `number` int NOT NULL,
  `capacity` int NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `rows` int NOT NULL DEFAULT '0',
  `cols` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`theater_id`,`number`),
  CONSTRAINT `saloon_ibfk_1` FOREIGN KEY (`theater_id`) REFERENCES `theater` (`theater_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `saloon`
--

LOCK TABLES `saloon` WRITE;
/*!40000 ALTER TABLE `saloon` DISABLE KEYS */;
INSERT INTO `saloon` VALUES (1,3,80,'Standard',1,8,10),(2,2,40,'Standard',1,4,10),(2,3,150,'IMAX',1,10,15);
/*!40000 ALTER TABLE `saloon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `screening`
--

DROP TABLE IF EXISTS `screening`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `screening` (
  `screening_id` int NOT NULL AUTO_INCREMENT,
  `movie_id` int NOT NULL,
  `theater_id` int NOT NULL,
  `saloon_number` int NOT NULL,
  `start_time` datetime NOT NULL,
  `base_price` decimal(10,2) NOT NULL,
  `is_subtitled` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`screening_id`),
  KEY `idx_screening_id_theater_saloon` (`screening_id`,`theater_id`,`saloon_number`),
  KEY `idx_screening_theater_saloon_start_time` (`theater_id`,`saloon_number`,`start_time`),
  KEY `idx_screening_movie_start_time` (`movie_id`,`start_time`),
  CONSTRAINT `screening_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`) ON DELETE CASCADE,
  CONSTRAINT `screening_ibfk_2` FOREIGN KEY (`theater_id`, `saloon_number`) REFERENCES `saloon` (`theater_id`, `number`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `screening`
--

LOCK TABLES `screening` WRITE;
/*!40000 ALTER TABLE `screening` DISABLE KEYS */;
INSERT INTO `screening` VALUES (11,3,2,3,'2026-05-09 21:00:00',18.00,1),(12,6,1,3,'2026-05-07 19:16:00',15.00,0),(13,6,2,2,'2026-05-08 12:00:00',12.00,0),(14,4,1,3,'2026-05-08 15:00:00',15.00,0),(15,2,2,3,'2026-05-08 17:00:00',18.00,0),(16,1,2,3,'2026-05-08 12:00:00',18.00,1),(17,6,1,3,'2026-05-08 18:00:00',15.00,0),(18,3,1,3,'2026-05-08 12:00:00',15.00,1);
/*!40000 ALTER TABLE `screening` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seat`
--

DROP TABLE IF EXISTS `seat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seat` (
  `theater_id` int NOT NULL,
  `saloon_number` int NOT NULL,
  `row_letter` varchar(1) NOT NULL,
  `number` int NOT NULL,
  `type` varchar(50) DEFAULT 'Standard',
  PRIMARY KEY (`theater_id`,`saloon_number`,`row_letter`,`number`),
  CONSTRAINT `seat_ibfk_1` FOREIGN KEY (`theater_id`, `saloon_number`) REFERENCES `saloon` (`theater_id`, `number`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seat`
--

LOCK TABLES `seat` WRITE;
/*!40000 ALTER TABLE `seat` DISABLE KEYS */;
INSERT INTO `seat` VALUES (1,3,'A',1,'Standard'),(1,3,'A',2,'Standard'),(1,3,'A',3,'Standard'),(1,3,'A',4,'Standard'),(1,3,'A',5,'Standard'),(1,3,'A',6,'Standard'),(1,3,'A',7,'Standard'),(1,3,'A',8,'Standard'),(1,3,'A',9,'Standard'),(1,3,'A',10,'Standard'),(1,3,'B',1,'Standard'),(1,3,'B',2,'Standard'),(1,3,'B',3,'Standard'),(1,3,'B',4,'Standard'),(1,3,'B',5,'Standard'),(1,3,'B',6,'Standard'),(1,3,'B',7,'Standard'),(1,3,'B',8,'Standard'),(1,3,'B',9,'Standard'),(1,3,'B',10,'Standard'),(1,3,'C',1,'Standard'),(1,3,'C',2,'Standard'),(1,3,'C',3,'Standard'),(1,3,'C',4,'Standard'),(1,3,'C',5,'Standard'),(1,3,'C',6,'Standard'),(1,3,'C',7,'Standard'),(1,3,'C',8,'Standard'),(1,3,'C',9,'Standard'),(1,3,'C',10,'Standard'),(1,3,'D',1,'Standard'),(1,3,'D',2,'Standard'),(1,3,'D',3,'Standard'),(1,3,'D',4,'Standard'),(1,3,'D',5,'Standard'),(1,3,'D',6,'Standard'),(1,3,'D',7,'Standard'),(1,3,'D',8,'Standard'),(1,3,'D',9,'Standard'),(1,3,'D',10,'Standard'),(1,3,'E',1,'Standard'),(1,3,'E',2,'Standard'),(1,3,'E',3,'Standard'),(1,3,'E',4,'Standard'),(1,3,'E',5,'Standard'),(1,3,'E',6,'Standard'),(1,3,'E',7,'Standard'),(1,3,'E',8,'Standard'),(1,3,'E',9,'Standard'),(1,3,'E',10,'Standard'),(1,3,'F',1,'Standard'),(1,3,'F',2,'Standard'),(1,3,'F',3,'Standard'),(1,3,'F',4,'Standard'),(1,3,'F',5,'Standard'),(1,3,'F',6,'Standard'),(1,3,'F',7,'Standard'),(1,3,'F',8,'Standard'),(1,3,'F',9,'Standard'),(1,3,'F',10,'Standard'),(1,3,'G',1,'Standard'),(1,3,'G',2,'Standard'),(1,3,'G',3,'Standard'),(1,3,'G',4,'Standard'),(1,3,'G',5,'Standard'),(1,3,'G',6,'Standard'),(1,3,'G',7,'Standard'),(1,3,'G',8,'Standard'),(1,3,'G',9,'Standard'),(1,3,'G',10,'Standard'),(1,3,'H',1,'Standard'),(1,3,'H',2,'Standard'),(1,3,'H',3,'Standard'),(1,3,'H',4,'Standard'),(1,3,'H',5,'Standard'),(1,3,'H',6,'Standard'),(1,3,'H',7,'Standard'),(1,3,'H',8,'Standard'),(1,3,'H',9,'Standard'),(1,3,'H',10,'Standard'),(2,2,'A',1,'Standard'),(2,2,'A',2,'Standard'),(2,2,'A',3,'Standard'),(2,2,'A',4,'Standard'),(2,2,'A',5,'Standard'),(2,2,'A',6,'Standard'),(2,2,'A',7,'Standard'),(2,2,'A',8,'Standard'),(2,2,'A',9,'Standard'),(2,2,'A',10,'Standard'),(2,2,'B',1,'Standard'),(2,2,'B',2,'Standard'),(2,2,'B',3,'Standard'),(2,2,'B',4,'Standard'),(2,2,'B',5,'Standard'),(2,2,'B',6,'Standard'),(2,2,'B',7,'Standard'),(2,2,'B',8,'Standard'),(2,2,'B',9,'Standard'),(2,2,'B',10,'Standard'),(2,2,'C',1,'Standard'),(2,2,'C',2,'Standard'),(2,2,'C',3,'Standard'),(2,2,'C',4,'Standard'),(2,2,'C',5,'Standard'),(2,2,'C',6,'Standard'),(2,2,'C',7,'Standard'),(2,2,'C',8,'Standard'),(2,2,'C',9,'Standard'),(2,2,'C',10,'Standard'),(2,2,'D',1,'Standard'),(2,2,'D',2,'Standard'),(2,2,'D',3,'Standard'),(2,2,'D',4,'Standard'),(2,2,'D',5,'Standard'),(2,2,'D',6,'Standard'),(2,2,'D',7,'Standard'),(2,2,'D',8,'Standard'),(2,2,'D',9,'Standard'),(2,2,'D',10,'Standard'),(2,3,'A',1,'Standard'),(2,3,'A',2,'Standard'),(2,3,'A',3,'Standard'),(2,3,'A',4,'Standard'),(2,3,'A',5,'Standard'),(2,3,'A',6,'Standard'),(2,3,'A',7,'Standard'),(2,3,'A',8,'Standard'),(2,3,'A',9,'Standard'),(2,3,'A',10,'Standard'),(2,3,'A',11,'Standard'),(2,3,'A',12,'Standard'),(2,3,'A',13,'Standard'),(2,3,'A',14,'Standard'),(2,3,'A',15,'Standard'),(2,3,'B',1,'Standard'),(2,3,'B',2,'Standard'),(2,3,'B',3,'Standard'),(2,3,'B',4,'Standard'),(2,3,'B',5,'Standard'),(2,3,'B',6,'Standard'),(2,3,'B',7,'Standard'),(2,3,'B',8,'Standard'),(2,3,'B',9,'Standard'),(2,3,'B',10,'Standard'),(2,3,'B',11,'Standard'),(2,3,'B',12,'Standard'),(2,3,'B',13,'Standard'),(2,3,'B',14,'Standard'),(2,3,'B',15,'Standard'),(2,3,'C',1,'Standard'),(2,3,'C',2,'Standard'),(2,3,'C',3,'Standard'),(2,3,'C',4,'Standard'),(2,3,'C',5,'Standard'),(2,3,'C',6,'Standard'),(2,3,'C',7,'Standard'),(2,3,'C',8,'Standard'),(2,3,'C',9,'Standard'),(2,3,'C',10,'Standard'),(2,3,'C',11,'Standard'),(2,3,'C',12,'Standard'),(2,3,'C',13,'Standard'),(2,3,'C',14,'Standard'),(2,3,'C',15,'Standard'),(2,3,'D',1,'Standard'),(2,3,'D',2,'Standard'),(2,3,'D',3,'Standard'),(2,3,'D',4,'Standard'),(2,3,'D',5,'Standard'),(2,3,'D',6,'Standard'),(2,3,'D',7,'Standard'),(2,3,'D',8,'Standard'),(2,3,'D',9,'Standard'),(2,3,'D',10,'Standard'),(2,3,'D',11,'Standard'),(2,3,'D',12,'Standard'),(2,3,'D',13,'Standard'),(2,3,'D',14,'Standard'),(2,3,'D',15,'Standard'),(2,3,'E',1,'Standard'),(2,3,'E',2,'Standard'),(2,3,'E',3,'Standard'),(2,3,'E',4,'Standard'),(2,3,'E',5,'Standard'),(2,3,'E',6,'Standard'),(2,3,'E',7,'Standard'),(2,3,'E',8,'Standard'),(2,3,'E',9,'Standard'),(2,3,'E',10,'Standard'),(2,3,'E',11,'Standard'),(2,3,'E',12,'Standard'),(2,3,'E',13,'Standard'),(2,3,'E',14,'Standard'),(2,3,'E',15,'Standard'),(2,3,'F',1,'Standard'),(2,3,'F',2,'Standard'),(2,3,'F',3,'Standard'),(2,3,'F',4,'Standard'),(2,3,'F',5,'Standard'),(2,3,'F',6,'Standard'),(2,3,'F',7,'Standard'),(2,3,'F',8,'Standard'),(2,3,'F',9,'Standard'),(2,3,'F',10,'Standard'),(2,3,'F',11,'Standard'),(2,3,'F',12,'Standard'),(2,3,'F',13,'Standard'),(2,3,'F',14,'Standard'),(2,3,'F',15,'Standard'),(2,3,'G',1,'Standard'),(2,3,'G',2,'Standard'),(2,3,'G',3,'Standard'),(2,3,'G',4,'Standard'),(2,3,'G',5,'Standard'),(2,3,'G',6,'Standard'),(2,3,'G',7,'Standard'),(2,3,'G',8,'Standard'),(2,3,'G',9,'Standard'),(2,3,'G',10,'Standard'),(2,3,'G',11,'Standard'),(2,3,'G',12,'Standard'),(2,3,'G',13,'Standard'),(2,3,'G',14,'Standard'),(2,3,'G',15,'Standard'),(2,3,'H',1,'Standard'),(2,3,'H',2,'Standard'),(2,3,'H',3,'Standard'),(2,3,'H',4,'Standard'),(2,3,'H',5,'Standard'),(2,3,'H',6,'Standard'),(2,3,'H',7,'Standard'),(2,3,'H',8,'Standard'),(2,3,'H',9,'Standard'),(2,3,'H',10,'Standard'),(2,3,'H',11,'Standard'),(2,3,'H',12,'Standard'),(2,3,'H',13,'Standard'),(2,3,'H',14,'Standard'),(2,3,'H',15,'Standard'),(2,3,'I',1,'Standard'),(2,3,'I',2,'Standard'),(2,3,'I',3,'Standard'),(2,3,'I',4,'Standard'),(2,3,'I',5,'Standard'),(2,3,'I',6,'Standard'),(2,3,'I',7,'Standard'),(2,3,'I',8,'Standard'),(2,3,'I',9,'Standard'),(2,3,'I',10,'Standard'),(2,3,'I',11,'Standard'),(2,3,'I',12,'Standard'),(2,3,'I',13,'Standard'),(2,3,'I',14,'Standard'),(2,3,'I',15,'Standard'),(2,3,'J',1,'Standard'),(2,3,'J',2,'Standard'),(2,3,'J',3,'Standard'),(2,3,'J',4,'Standard'),(2,3,'J',5,'Standard'),(2,3,'J',6,'Standard'),(2,3,'J',7,'Standard'),(2,3,'J',8,'Standard'),(2,3,'J',9,'Standard'),(2,3,'J',10,'Standard'),(2,3,'J',11,'Standard'),(2,3,'J',12,'Standard'),(2,3,'J',13,'Standard'),(2,3,'J',14,'Standard'),(2,3,'J',15,'Standard');
/*!40000 ALTER TABLE `seat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `theater`
--

DROP TABLE IF EXISTS `theater`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `theater` (
  `theater_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `address` text,
  PRIMARY KEY (`theater_id`),
  UNIQUE KEY `phone_number` (`phone_number`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `theater`
--

LOCK TABLES `theater` WRITE;
/*!40000 ALTER TABLE `theater` DISABLE KEYS */;
INSERT INTO `theater` VALUES (1,'Mavibahçe','555-1111','Mavibahçe AVM, İzmir'),(2,'Hilltown','555-2222','Hilltown AVM, İzmir');
/*!40000 ALTER TABLE `theater` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket` (
  `ticket_id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int NOT NULL,
  `screening_id` int NOT NULL,
  `theater_id` int NOT NULL,
  `saloon_number` int NOT NULL,
  `row_letter` varchar(1) NOT NULL,
  `seat_number` int NOT NULL,
  `ticket_type` varchar(50) DEFAULT 'Standard',
  `scanned_at` datetime DEFAULT NULL,
  `ticket_code` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ticket_id`),
  UNIQUE KEY `screening_id` (`screening_id`,`theater_id`,`saloon_number`,`row_letter`,`seat_number`),
  UNIQUE KEY `ticket_code` (`ticket_code`),
  KEY `theater_id` (`theater_id`,`saloon_number`,`row_letter`,`seat_number`),
  KEY `idx_ticket_booking_id` (`booking_id`),
  CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`booking_id`) ON DELETE CASCADE,
  CONSTRAINT `ticket_ibfk_2` FOREIGN KEY (`screening_id`) REFERENCES `screening` (`screening_id`) ON DELETE CASCADE,
  CONSTRAINT `ticket_ibfk_3` FOREIGN KEY (`theater_id`, `saloon_number`, `row_letter`, `seat_number`) REFERENCES `seat` (`theater_id`, `saloon_number`, `row_letter`, `number`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket`
--

LOCK TABLES `ticket` WRITE;
/*!40000 ALTER TABLE `ticket` DISABLE KEYS */;
INSERT INTO `ticket` VALUES (25,11,11,2,3,'G',8,'Standard',NULL,'100011G8'),(26,12,11,2,3,'C',7,'Standard',NULL,'100012C7'),(27,12,11,2,3,'E',10,'Standard',NULL,'100012E10'),(28,12,11,2,3,'E',13,'Standard',NULL,'100012E13'),(29,12,11,2,3,'G',3,'Standard',NULL,'100012G3'),(30,12,11,2,3,'I',7,'Standard',NULL,'100012I7'),(31,12,11,2,3,'I',12,'Standard',NULL,'100012I12'),(32,13,12,1,3,'D',2,'Standard',NULL,'100013D2'),(33,13,12,1,3,'E',2,'Standard',NULL,'100013E2'),(34,13,12,1,3,'E',3,'Standard',NULL,'100013E3'),(35,13,12,1,3,'E',4,'Standard',NULL,'100013E4'),(36,14,18,1,3,'H',6,'Standard','2026-05-08 02:17:02','100014H6'),(37,14,18,1,3,'H',7,'Standard','2026-05-08 02:17:02','100014H7'),(40,16,18,1,3,'G',4,'Standard',NULL,'100016G4'),(41,16,18,1,3,'G',5,'Standard',NULL,'100016G5'),(42,17,14,1,3,'A',1,'Standard',NULL,'100017A1'),(43,17,14,1,3,'A',2,'Standard',NULL,'100017A2'),(44,17,14,1,3,'A',3,'Standard',NULL,'100017A3'),(45,17,14,1,3,'A',4,'Standard',NULL,'100017A4'),(46,17,14,1,3,'A',5,'Standard',NULL,'100017A5'),(48,18,18,1,3,'G',7,'Standard','2026-05-08 02:16:37','100018G7');
/*!40000 ALTER TABLE `ticket` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `phone_number` (`phone_number`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Alice','Smith','555-0001','alice@email.com','hashed1','2026-05-06 15:54:36'),(2,'Bob','Jones','555-0002','bob@email.com','hashed2','2026-05-06 15:54:36'),(3,'Charlie','Brown','555-0003','charlie@email.com','hashed3','2026-05-06 15:54:36'),(4,'Diana','Prince','555-0004','diana.admin@cinema.com','hashed4','2026-05-06 15:54:36'),(5,'Evan','Wright','555-0005','evan.staff@cinema.com','hashed5','2026-05-06 15:54:36'),(6,'Fiona','Gallagher','555-0006','fiona.new@cinema.com','hashed6','2026-05-06 15:54:36'),(7,'Nolan','Grayson','555-0007','admin@cinema.com','scrypt:32768:8:1$dM5c2ebqE3KvuxQN$9ded3e63555b9abc46c40b05226e5626a31862996db7e5bd64549bec8dfa989553f7483ca2f36d052597b4768b0c166e78d010ecee6d704171962a3fa4ef8285','2026-05-06 15:54:36'),(8,'Samantha Eve','Willkins','05315691596','eve@gmail.com','scrypt:32768:8:1$kDuNxwJsRiuQNOKM$c31844155018e6c17eb63333f3191b2cb3a78fcc70c42ea72c3874b2dd88f0aac64c5b676fbd32b2a6e9800b835ec54e2f5be05ea4a2f20d867ee31206d55b34','2026-05-06 16:13:04'),(9,'Reis','Yıldız','05315691497','reisyildiz02@gmail.com','scrypt:32768:8:1$boTZwftEqwByl0Vd$9e468aeb0b75dd6dbf6d945e2b8a54b02710dc0280592f264231877848ee727ca146c7734f73b60ba9bf66a6e7c9d12659626bb777bfeccde63f539694350585','2026-05-06 17:14:30'),(10,'Olçar','Dikilitaş','05456094138','olcardklts@gmail.com','scrypt:32768:8:1$nY8ZKZD2Wza5CdDj$839b69a30f67b3df01d4c00fc28c6ca350c1e4d93fb099610f93287b1737ffac4c5f531731e34dc1f0e794fc28d83d5681541cd400fc52e12fea743c00277c93','2026-05-07 22:38:57');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-08  8:38:01
