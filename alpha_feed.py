from alpha_vantage.timeseries import TimeSeries
from config import (ALPHA_VANTAGE_API_KEY, MYSQL_DB_URI)
from sqlalchemy import create_engine
import pandas as pd
import sys
import time
import threading
lock = threading.Lock()


class AlphaFeed(object):

    symbols = ('AAPL', 'AMD')
    '''Tuple of stock symbols to collect data for.'''

    minute_table = 'stock_price_minute'
    '''SQL table containing price per minute.'''

    day_table = 'stock_price_day'
    '''SQL table containing price per day.'''

    col_rename = {
        'date': 'dateid',
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume'
    }
    '''Renames AlphaVantage returned fields to SQL friendly field names.'''

    def __init__(self):
        '''Starts database connection and instantiates AlphaVantage API.'''
        self.engine = create_engine(MYSQL_DB_URI)
        self.ts = TimeSeries(
            key=ALPHA_VANTAGE_API_KEY,
            output_format='pandas',
            indexing_type='integer'
        )

    def upsert_df(self, table, df):
        '''UPSERTS DataFrame to specified table.

        Args:
            table (str): SQL table name to UPSERT to.
            df (DataFrame): Pandas DataFrame containing new data entries.
        '''
        # Table columns
        cols = list(df.columns)
        entries = []
        # Values to insert
        for idx, row in df.iterrows():
            # Remove the "u" flag for unicode entries
            row_entries_str = map(str, row.tolist())
            entries.append(str(tuple(row_entries_str)))
            # Duplicate key update
            conditions = ['{0}=VALUES({0})'.format(col) for col in cols]
    
        # Alpha Advantage won't return malicous values
        base_query = '''
        INSERT INTO {__table__}
            ({__cols__})
        VALUES
            {__entries__}
        ON DUPLICATE KEY UPDATE
            {__conditions__};
        '''
        query = base_query.format(
            __table__=table,
            __cols__=','.join(cols),
            __entries__=','.join(entries),
            __conditions__=','.join(conditions)
        )
        self.engine.execute(query)

    def get_data(self, job_type='rt'):
        '''Collects stock price data for symbols and UPSERTS to SQL table.
        
        Args:
            job_type (str): Specify type of data collection.
                rt: Realtime data per minute
                hist: Historical daily data where available

        Returns:
            DataFrame: Pandas DataFrame with data pulled from AlphaVantage

        Raises: ValueError if improper job_type
        '''
        # Only set 1min interval for realtime data
        if job_type == 'rt':
            data_req = self.ts.get_intraday
            ts_kwargs = {'interval': '1min', 'outputsize': 'full'}
            upsert_table = self.minute_table
        elif job_type == 'hist':
            data_req = self.ts.get_daily
            ts_kwargs = {'outputsize': 'full'}
            upsert_table = self.day_table
        else:
            raise ValueError('Invalid job type {}'.format(job_type))

        dfs = []
        # Collect data for each symbol from AlphaAdvantage
        for symbol in self.symbols:
            ts_kwargs['symbol'] = symbol
            try:
                df, _ = data_req(**ts_kwargs)
            except ValueError as e:
                print('Invalid stock symbol {}: {}'.format(symbol, e))
                continue
            # Set symbol field for table insert
            df['sym'] = symbol
            dfs.append(df)
        # UNION all DataFrames
        df_all = pd.concat(dfs)
        # Rename columns to follow SQL field naming convention
        df_all= df_all.rename(columns=self.col_rename)
        return df_all


def rt_collection_deamon(symbols, period_dur=60):
    '''Runs AlphaFeed's realtime get_data method every period duration.
    Args:
        symbols (tuple): Stock symbols to collect
        period_dur (float): Time to wait between each request
    '''
    data_feed = AlphaFeed()
    syms_str = ', '.join(symbols)
    while True:
        df = data_feed.get_data('rt')
        with lock:
            print('  Inserting new data for {}'.format(syms_str))
            data_feed.upsert_df(data_feed.minute_table, df)
        time.sleep(period_dur)


def init_deamons(thread_tasks):
    '''Starts rt_collection_deamon for each provided thread_tasks.

    Args:
        thread_tasks (tuple): Contains arguments for rt_collection_deamon
            symbols (tuple): Stock symbols to collect
            period_dur (float): Time to wait between each request
    '''
    print('Initalizing data collection threads')
    threads = []
    msg_temp = '  {} scheduling {} collection every {} seconds'
    for idx, thread_task in enumerate(thread_tasks):
        syms, period = thread_task
        daemon_name = 'daemon_' + str(idx+1)
        print(msg_temp.format(daemon_name, ', '.join(syms), period))
        task = threading.Thread(
            target=rt_collection_deamon,
            name=daemon_name,
            args=(thread_task)
        )
        task.setDaemon(True)
        threads.append(task)
    # Start all threads
    print('##### Data Collection #####')
    [task.start() for task in threads]

    # Keep alive
    while True:
        pass


if __name__ == '__main__':
    if len(sys.argv) == 2:
        # Prints head of found data for testing purposes
        if sys.argv[1] == '-t':
            data_feed = AlphaFeed()
            data_feed.symbols = ('AABA', 'AAPL', 'AMD', 'AMZN', 'C', 'INTC',
                                 'MSFT', 'GOOGL', 'WFC', 'VZ')
            print('--- REALTIME ---')
            print(data_feed.get_data('rt').head())
            print('--- Historical ---')
            print(data_feed.get_data('hist').head())
        else:
            print('Unrecognized argument {}'.format(sys.argv[1]))
    else:
        thread_tasks = (
            (('AABA', 'AAPL'), 60),
            (('AMD', 'AMZN'), 60),
            (('C', 'INTC'), 60),
            (('MSFT', 'GOOGL'), 60),
            (('WFC', 'VZ'), 60)
        )
        thread_tasks = (thread_tasks)
        init_deamons(thread_tasks)
