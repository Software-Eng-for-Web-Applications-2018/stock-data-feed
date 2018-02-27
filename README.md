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
CREATE TABLE `stock_price_day` (
  `dateid` date NOT NULL,
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

### Running
Collects AABA, AAPL, AMD, AMZN, C, INTC, MSFT, GOOGL, WFC, and VZ every minute

- `python alpha_feed.py`

```
Initalizing data collection threads
  daemon_1 scheduling AABA, AAPL collection every 60 seconds
  daemon_2 scheduling AMD, AMZN collection every 60 seconds
  daemon_3 scheduling C, INTC collection every 60 seconds
  daemon_4 scheduling MSFT, GOOGL collection every 60 seconds
  daemon_5 scheduling WFC, VZ collection every 60 seconds
##### Data Collection #####
  Inserting new data for MSFT, GOOGL
  Inserting new data for C, INTC
  Inserting new data for AMD, AMZN
  Inserting new data for AABA, AAPL
  Inserting new data for WFC, VZ
```

Collects AABA, AAPL, AMD, AMZN, C, INTC, MSFT, GOOGL, WFC, and VZ and prints to
terminal head

- `python alpha_feed.py -t`

## AlphaFeed API
Instantiate the AlphaVantage data feed object.

`data_feed = AlphaFeed()`

Set the symbols you want to collect.

`data_feed.symbols = ('AAPL', 'AMD', 'DIS')`

If you want change the table you want to UPSERT data set the minute_table parameter.

`data_feed.minute_table = 'test_table'`

Run "upsert_minute" method to collect the latest minute data to
  "minute_table".

`data_feed.upsert_minute()`
