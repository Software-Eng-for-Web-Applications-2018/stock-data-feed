import sys
import time
import threading
from alpha_feed import AlphaFeed
lock = threading.Lock()


def rt_collection_deamon(symbols, period_dur=60):
    '''Runs AlphaFeed's realtime get_data method every period duration.
    Args:
        symbols (tuple): Stock symbols to collect
        period_dur (float): Time to wait between each request
            Default to 1 minute
    '''
    data_feed = AlphaFeed()
    data_feed.symbols = symbols
    syms_str = ', '.join(symbols)
    while True:
        df = data_feed.get_data('rt')
        with lock:
            print('  Inserting new data for {}'.format(syms_str))
            data_feed.upsert_df(data_feed.minute_table, df)
            print('    * SUCCESS!')
        time.sleep(period_dur)


def hist_collection_deamon(symbols, period_dur=3600):
    '''Runs AlphaFeed's historical get_data method every period duration.
    Args:                                                               
        symbols (tuple): Stock symbols to collect                       
        period_dur (float): Time to wait between each request           
            Default to 1 hour
    '''                                                                 
    data_feed = AlphaFeed()                                             
    data_feed.symbols = symbols                                         
    syms_str = ', '.join(symbols)                                       
    while True:                                                         
        df = data_feed.get_data('hist')                                 
        with lock:                                                      
            print('  Inserting new data for {}'.format(syms_str))       
            data_feed.upsert_df(data_feed.day_table, df)             
            print('    * SUCCESS!')                                     
        time.sleep(period_dur)                                          


def init_deamons(thread_tasks, target_task):
    '''Starts target_task for each provided thread_tasks.

    Args:
        thread_tasks (tuple): Contains arguments for target_task
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
            target=target_task,
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
    # Lazy argparse
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
        elif sys.argv[1] == '-H':
            thread_tasks = (                                 
                (('AABA', 'AAPL'), 21600),                   
                (('AMD', 'AMZN'), 21600),                    
                (('C', 'INTC'), 21600),                      
                (('MSFT', 'GOOGL'), 21600),                  
                (('GOOG', 'VZ'), 21600)                      
            )                                                
            thread_tasks = (thread_tasks)                    
            init_deamons(thread_tasks, hist_collection_deamon) 
        else:
            print('Unrecognized argument {}'.format(sys.argv[1]))
    else:
        thread_tasks = (
            (('AABA', 'AAPL'), 60),
            (('AMD', 'AMZN'), 60),
            (('C', 'INTC'), 60),
            (('MSFT', 'GOOGL'), 60),
            (('GOOG', 'VZ'), 60)
        )
        thread_tasks = (thread_tasks)
        init_deamons(thread_tasks, rt_collection_deamon)
