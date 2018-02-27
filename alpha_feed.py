from alpha_vantage.timeseries import TimeSeries
from config import (ALPHA_VANTAGE_API_KEY, MYSQL_DB_URI)
from sqlalchemy import create_engine
import pandas as pd


class AlphaFeed(object):

    symbols = ('AAPL', 'AMD')
    '''Symbols to collect data for.'''

    minute_table = 'stock_price_minute'
    '''SQL table containing price per minute.'''

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
	    __conditions__=','.join(conditions))
	self.engine.execute(query)

    def upsert_minute(self):
        '''Collects minute data for symbols and UPSERTS to minute_table.'''
        dfs = []
        for symbol in self.symbols:
            # Collect data for symbol from AlphaAdvantage
            df, _ = self.ts.get_intraday(
                symbol=symbol,
                interval='1min',
                outputsize='full'
            )
            # Set symbol field for table insert
            df['sym'] = symbol
            dfs.append(df)
        # UNION all DataFrames
        df_all = pd.concat(dfs)
        # Rename columns to follow SQL field naming convention
        df_all= df_all.rename(columns=self.col_rename)
        self.upsert_df(self.minute_table, df_all)


if __name__ == '__main__':
    data_feed = AlphaFeed()
    data_feed.symbols = ('AAPL', 'AMD')
    data_feed.upsert_minute()
