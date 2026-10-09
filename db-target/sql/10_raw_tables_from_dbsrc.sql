-- __source_lsn : Numéro de position dans le WAL au moment où le changement a eu lieu. UInt64 = entier positif sur 64 bits
-- Ajouté par le sink à partir de source.lsn
-- LSN = Log Sequence Number, un compteur qui ne fait qu’augmenter : un changement plus récent a toujours un LSN plus grand
-- Pas de Nullable(...) ici car state_id et state sont NOT NULL dans la source
-- ENGINE = ReplacingMergeTree(__source_lsn)
-- Le moteur (ENGINE) décide comment ClickHouse stocke et gère les lignes.
-- MergeTree : famille de moteurs qui écrit les données par paquets (« parts ») puis les fusionne régulièrement en arrière-plan.
-- Replacing : lors d’une fusion, si plusieurs lignes ont la même clé (voir ORDER BY), il n’en garde qu’une.
-- (__source_lsn) entre parenthèses : c’est la colonne de version. Parmi les lignes de même clé, il garde celle dont le __source_lsn est le plus grand, donc la plus récente. Sans parenthèses, il garderait la dernière insérée
-- un UPDATE dans PostgreSQL arrive dans Kafka comme une nouvelle ligne pour la même clé. ClickHouse n’écrase rien tout de suite : il garde les deux, puis la fusion supprime l’ancienne
-- Entre-temps, un SELECT simple peut renvoyer les deux versions. SELECT … FROM states FINAL force le dédoublonnage à la lecture
-- ORDER BY state_id : C’est la clé de tri : ClickHouse range physiquement les lignes dans cet ordre
-- Pour ReplacingMergeTree, c’est aussi la clé qui définit « ce qui est la même ligne » : deux lignes avec le même state_id sont des versions d’une même ligne
CREATE TABLE IF NOT EXISTS states (
  state_id Int32, state String, __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY state_id;

---------------------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cities (
  city_id Int32, city String, zip String, city_pop Nullable(Int32), state_id Int32, __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY city_id;

CREATE TABLE IF NOT EXISTS addresses (
  address_id Int64, street String, lat String, `long` String, city_id Int32, __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY address_id;

CREATE TABLE IF NOT EXISTS jobs (
  job_id Int32, job String, __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY job_id;

-- Format Date dans Postgresq devient Date32 dans Clickhouse car Debezium convertit les dates en nombre de jours depuis 1970
-- et une date antérieure devient un nombre négatif
CREATE TABLE IF NOT EXISTS customers (
  customer_id Int64, first_name String, last_name String, gender String, dob Date32,
  job_id Int32, address_id Int64, __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY customer_id;

CREATE TABLE IF NOT EXISTS activities (
  activity_id Int32, category String, __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY activity_id;

CREATE TABLE IF NOT EXISTS merchants (
  merchant_id Int64, merchant String, __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY merchant_id;

CREATE TABLE IF NOT EXISTS transactions (
  transaction_id Int64, trans_num Nullable(String), transdate_transtime String,
  cc_num String, ip_geoloc Nullable(String), device_type Nullable(String),
  amount_presentation String, amt String, currency_rate String,
  currency_id_presentation String, currency_id_received String,
  fraud_score Nullable(String), model_version Nullable(String),
  status String, review_status String, refunded_at Nullable(String),
  analyst_id Nullable(Int32), is_fraud Nullable(Bool), verdict_at Nullable(String),
  merch_lat String, merch_long Nullable(String),
  customer_id Int64, merchant_id Int64, activity_id Int32, __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY transaction_id;

CREATE TABLE IF NOT EXISTS currencies (
  currency_id String, currency Nullable(String), __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY currency_id;

CREATE TABLE IF NOT EXISTS analysts (
  analyst_id Int32, role Nullable(String), __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY analyst_id;

CREATE TABLE IF NOT EXISTS rejects (
  reject_id Int64, customer_id Int64, first_name String, last_name String, dob Date32,
  merchant_id Int64, merchant String, transdate_transtime String, cc_num String,
  ip_geoloc Nullable(String), device_type Nullable(String),
  amount_presentation String, currency_id_presentation String,
  fraud_score String, model_version String, __source_lsn UInt64
) ENGINE = ReplacingMergeTree(__source_lsn) ORDER BY reject_id;