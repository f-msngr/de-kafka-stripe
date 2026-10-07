-- Valeurs posées à l'import : ADR 0002 §2.1 (analyste 0, init, verdict à la date de la transaction, score et version vides) et §2.2 (USD, taux 1)
INSERT INTO payments.transactions (
  trans_num, transdate_transtime, cc_num, amount_presentation, amt, currency_rate,
  currency_id_presentation, currency_id_received, status, review_status,
  analyst_id, is_fraud, verdict_at, merch_lat, merch_long,
  customer_id, merchant_id, activity_id)
SELECT
  s.trans_num, s.trans_date_trans_time::timestamptz, s.cc_num, s.amt::numeric(20,4), s.amt::numeric(20,4), 1,
  'USD', 'USD', 'successful', 'init',
  0, s.is_fraud::boolean, s.trans_date_trans_time::timestamptz, s.merch_lat::numeric(9,6), s.merch_long::numeric(9,6),
  cu.customer_id, m.merchant_id, a.activity_id
FROM import_csv s
JOIN payments.customers  cu ON cu.first_name = s."first" AND cu.last_name = s."last" AND cu.dob = s.dob::date
JOIN payments.merchants  m  ON m.merchant = s.merchant
JOIN payments.activities a  ON a.category = s.category
ON CONFLICT (trans_num) DO NOTHING;