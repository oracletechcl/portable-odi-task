-- Run with Spark SQL after substituting input_path, output_path, and tax_rate.
CREATE OR REPLACE TEMP VIEW customers
USING csv
OPTIONS (
  path '${input_path}',
  header 'true',
  inferSchema 'true'
);

CREATE OR REPLACE TEMP VIEW active_customers AS
SELECT
  customer_id,
  UPPER(TRIM(customer_name)) AS customer_name,
  status,
  country,
  CAST(amount AS DOUBLE) AS amount,
  ROUND(amount * (1 + ${tax_rate}), 2) AS amount_tax
FROM customers
WHERE status = 'ACTIVE';

INSERT OVERWRITE DIRECTORY '${output_path}'
USING csv
OPTIONS (header 'true')
SELECT * FROM active_customers;
