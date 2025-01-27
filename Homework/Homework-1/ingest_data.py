#!/usr/bin/env python
# coding: utf-8

import os
import argparse

from time import time

import pandas as pd
from sqlalchemy import create_engine


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    database = params.database
    table = params.table
    url = params.url

    csv_name = 'output.csv'

    # Download CSV
    os.system(f'wget {url} -O {csv_name}')


    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
    engine.connect()

    # /home/dmadmin/Downloads/yellow_tripdata_2021-01.csv
    df_iter = pd.read_csv(f'{csv_name}', iterator=True, chunksize=100000, compression='gzip')

    df = next(df_iter)

#    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
#    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)


    df.head(n=0).to_sql(name=table, con=engine, if_exists='replace')

    df.to_sql(name=table, con=engine, if_exists='append')

    while True:
        t_start = time()
        
        df = next(df_iter)

#        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
#        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

        df.to_sql(name=table, con=engine, if_exists='append')

        t_end = time()

        print('inserted another chunk..., took %.3f seconds: ' % (t_end - t_start))

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    # user, password, host, port, database name, table name, url of csv
    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host name for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--database', help='postgres database')
    parser.add_argument('--table', help='postgres table name')
    parser.add_argument('--url', help='url of csv data file')

    args = parser.parse_args()

    main(args)
