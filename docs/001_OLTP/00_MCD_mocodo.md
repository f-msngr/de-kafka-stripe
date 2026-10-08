JOBS: job_id, job
WORK, 0N JOBS, 11 CUSTOMERS
CUSTOMERS: customer_id, first_name, last_name, gender, dob
LOCATE, 1N ADDRESSES, 11 CUSTOMERS
ADDRESSES: address_id, street, lat, long

MERCHANTS: merchant_id, merchant
SELL, 11 TRANSACTIONS, 0N MERCHANTS: merch_lat, merch_long
BUY, 0N CUSTOMERS, 11 TRANSACTIONS: cc_num, ip_geoloc, device_type
ANALYSTS: analyst_id, role
SETTLE, 0N CITIES, 11 ADDRESSES

REJECTS: reject_id, first_name, last_name, dob, merchant, transdate_transtime, cc_num, ip_geoloc, device_type, amount_presentation, currency_id_presentation, fraud_score, model_version
PRESENT, 0N CURRENCIES, 11 TRANSACTIONS
TRANSACTIONS: transactions_id, trans_num, transdate_transtime, status, amount_presentation, amt, fraud_score, model_version, review_status, refunded_at
REVIEW, 01 TRANSACTIONS, 0N ANALYSTS: is_fraud, verdict_at
CITIES: city_id, city, zip, city_pop

:
CURRENCIES: currency_id, currency
RECEIVE, 0N CURRENCIES, 11 TRANSACTIONS: currency_rate
GATHER, 0N ACTIVITIES, 11 TRANSACTIONS
MANAGE, 0N STATES, 11 CITIES

:
:
:
ACTIVITIES: activity_id, category
STATES: state_id, state
