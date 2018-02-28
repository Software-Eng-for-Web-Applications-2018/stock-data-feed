## Database Schema

## SQL Server
- **Source:** MySQL
- **Verison:** 5.6
- **Server Version:** 5.7.21-0
- **OS:** Ubuntu .16.04.1

## Table List

| Tables_in_df       |
|--------------------|
| stock_price_day    |
| stock_price_minute |

## Table Descriptions

### stock_price_minute

| Field  | Type       | Null | Key | Default | Extra |
|--------|------------|------|-----|---------|-------|
| dateid | datetime   | NO   | PRI | NULL    |       |
| sym    | varchar(5) | NO   | PRI | NULL    |       |
| volume | double     | YES  |     | NULL    |       |
| close  | double     | YES  |     | NULL    |       |
| high   | double     | YES  |     | NULL    |       |
| open   | double     | YES  |     | NULL    |       |
| low    | double     | YES  |     | NULL    |       |

### stock_price_day

| Field  | Type       | Null | Key | Default | Extra |
|--------|------------|------|-----|---------|-------|
| dateid | date       | NO   | PRI | NULL    |       |
| sym    | varchar(5) | NO   | PRI | NULL    |       |
| volume | double     | YES  |     | NULL    |       |
| close  | double     | YES  |     | NULL    |       |
| high   | double     | YES  |     | NULL    |       |
| open   | double     | YES  |     | NULL    |       |
| low    | double     | YES  |     | NULL    |       |

### Schema Creation
```
CREATE DATABASE df;
USE df;
CREATE TABLE `stock_price_minute` (
  `dateid` datetime NOT NULL,
  `sym` varchar(5) NOT NULL,
  `volume` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `open` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  PRIMARY KEY (`dateid`,`sym`),
  KEY `stock_price_minute_dateid_idx` (`dateid`),
  KEY `stock_price_minute_sym_idx` (`sym`)
);
CREATE TABLE `stock_price_day` (
  `dateid` date NOT NULL,
  `sym` varchar(5) NOT NULL,
  `volume` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `open` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  PRIMARY KEY (`dateid`,`sym`),
  KEY `stock_price_day_dateid_idx` (`dateid`),
  KEY `stock_price_day_sym_idx` (`sym`)
);
```
