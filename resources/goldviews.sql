CREATE OR REPLACE VIEW :catalog.:schema.monthly_fx_report AS
SELECT 
    date_format(date, 'yyyy-MM') as month,
    currency,
    avg(exchange_rate) as avg_rate
FROM :catalog.:schema.exchange_rates_silver
GROUP BY 1, 2;