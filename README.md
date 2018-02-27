# Stock Data Feed
Data pull from AlphaVantage to SQL db for minute intervals.

## Installation
- Runs with Python2.7 but it won't be difficult to change to Python3 in the
  future

### Database
```
CREATE DATABASE <name>;
CREATE TABLE `stock_price_minute` (
  `dateid` datetime NOT NULL,
  `sym` varchar(5) NOT NULL,
  `volume` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `open` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  PRIMARY KEY (`dateid`,`sym`)
);
```

### Pip

#### Linux
`apt-get install pip`

#### Windows
- I recommend using Anaconda for Python 2.7 or Cygwin
- Anaconda will have pip already installed
- Cygwin select "pip2.7" binary to install along with "python2.7"

## Configuration
- Change the name of "example_config.py" to config.py"
- Set AlphaVantage API Token value
- Set MYSQL_DB_URI string
  * <http://flask-sqlalchemy.pocoo.org/2.3/config/>

### Python Libraries
- `pip install -r requirements.txt`

## Basic Usage
Instantiate the AlphaVantage data feed object.

`data_feed = AlphaFeed()`

Set the symbols you want to collect.

`data_feed.symbols = ('AAPL', 'AMD', 'DIS')`

If you want change the table you want to UPSERT data set the minute_table parameter.

`data_feed.minute_table = 'test_table`

Run "upsert_minute" method to collect the latest minute data to
  "minute_table".

`data_feed.upsert_minute()`

### Test Run
Collects AAPL and AMD recent stock prices per minute.

- `python alpha_feed.py`
