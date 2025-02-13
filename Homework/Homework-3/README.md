# Homework 3
## Adding 2024 January - June Yellow Taxi Data
### Get files into Google Storage
Modified and used load_yellow_taxi_data.py to load the six parquet files into a Google Storage Bucket.
### Create External BigQuery Table
Referenced the dataset and bucket to create the external table.
```sql
CREATE OR REPLACE EXTERNAL TABLE `yellow_taxi.rides-202401-202406-external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://dez2025_hw3/yellow_tripdata_2024-0*.parquet']
);
```
### Create Materialized/Regular BigQuery Table
Referenced the external table to create the 'regular' table.
```sql
CREATE OR REPLACE TABLE `yellow_taxi.rides-202401-202406-regular`
AS SELECT * FROM `yellow_taxi.rides-202401-202406-external`;
```
## Question 1
### What is count of records for the 2024 Yellow Taxi Data?
```sql
SELECT COUNT(1) FROM `yellow_taxi.rides-202401-202406-regular`;

-- 20,332,093
```

## Question 2
### Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables. What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?
#### External Table
```SQL
SELECT DISTINCT(PULocationID) FROM `yellow_taxi.rides-202401-202406-external`;

-- This query will process 0 B when run.
```
#### Materialized Table
```sql
SELECT DISTINCT(PULocationID) FROM `yellow_taxi.rides-202401-202406-regular`;

-- This query will process 155.12 MB when run.
```

## Question 3
### Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table. Why are the estimated number of Bytes different?
```sql
SELECT PULocationID FROM `yellow_taxi.rides-202401-202406-regular`;

-- This query will process 155.12 MB when run.

SELECT PULocationID, DOLocationID FROM `yellow_taxi.rides-202401-202406-regular`;

-- This query will process 310.24 MB when run.
```
```
BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.
```
## Question 4
### How many records have a fare_amount of 0?
```sql
SELECT COUNT(1) FROM `yellow_taxi.rides-202401-202406-regular` WHERE fare_amount < 0.01 AND fare_amount > -0.01;

SELECT COUNT(1) FROM `yellow_taxi.rides-202401-202406-regular` WHERE fare_amount = 0.00;

-- fare_amount is a float
-- Both queries yield 8,333
```
## Question 5
### What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)?
Partition should be used on a time-unit column such as **tpep_dropoff_datetime**. Cluster is good for ordering queries such as **VendorID**.

`Partition by tpep_dropoff_datetime and Cluster on VendorID`
```sql
CREATE OR REPLACE TABLE `yellow_taxi.rides-202401-202406-partclust`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS (
  SELECT * FROM `yellow_taxi.rides-202401-202406-external`
);
```
## Question 6
### Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 (inclusive). Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values? 
```sql
SELECT DISTINCT(VendorID) FROM `yellow_taxi.rides-202401-202406-regular` WHERE tpep_dropoff_datetime >= TIMESTAMP('2024-03-01') AND tpep_dropoff_datetime <= TIMESTAMP('2024-03-15');

-- Bytes Processed = 310.24 MB

SELECT DISTINCT(VendorID) FROM `yellow_taxi.rides-202401-202406-partclust` WHERE tpep_dropoff_datetime >= TIMESTAMP('2024-03-01') AND tpep_dropoff_datetime <= TIMESTAMP('2024-03-15');

-- Bytes Processed = 26.84 MB
```
`310.24 MB for non-partitioned table and 26.84 MB for the partitioned table`
## Question 7
### Where is the data stored in the External Table you created?
It is stored in the actual cloud storage, i.e `GCP Bucket`

## Question 8
### It is best practice in Big Query to always cluster your data?
`FALSE` - it depends on the table structure/datatypes and how the table will be queried.

## Question 9
### Write a SELECT count(*) query FROM the materialized table you created. How many bytes does it estimate will be read? Why?
```sql
SELECT COUNT(*) FROM `yellow_taxi.rides-202401-202406-regular`;

-- 0 B
```
Without conditions, no actual data is being queried or returned, it's just a count of the rows.