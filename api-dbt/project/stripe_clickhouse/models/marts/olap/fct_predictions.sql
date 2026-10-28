/*
union des transactions et des rejets des transactions+ rejets résultats d'une prédiction
avec dimensions date et mois intégrées
cast de fraud_score, model_version, is_fraud
filtre les transactions init qui n'ont pas été prédites
*/

SELECT
    trans_num,
    'rejected' AS outcome,                                    -- équivalent à review_status
    transdate_transtime,
    toDate(transdate_transtime) AS prediction_date,           -- nouvelle colonne = dimension intégrée au fait
    toStartOfMonth(transdate_transtime) AS prediction_month,  -- nouvelle colonne = dimension intégrée au fait
    amt,
    CAST(fraud_score AS Decimal(6,4)) AS fraud_score,
    CAST(model_version AS String) AS model_version,
    CAST(NULL AS Nullable(Bool)) AS is_fraud          -- crée une colonne nommée is_fraud, dont toutes les lignes valent NULL, pour aligner les colonnes avec UNION ALL
FROM {{ ref('stg_raw__rejects') }}

UNION ALL

SELECT
    trans_num,
    review_status AS outcome,                                   -- équivalent à review_status
    transdate_transtime,
    toDate(transdate_transtime) AS prediction_date,             -- nouvelle colonne = dimension intégrée au fait
    toStartOfMonth(transdate_transtime) AS prediction_month,    -- nouvelle colonne = dimension intégrée au fait
    amt,
    CAST(fraud_score AS Decimal(6,4)) AS fraud_score,
    CAST(model_version AS String) AS model_version,
    CAST(if(review_status = 'reviewed', is_fraud, NULL) AS Nullable(Bool)) AS is_fraud
FROM {{ ref('stg_raw__transactions') }}
WHERE review_status <> 'init'       -- filtre les init, non passés par une prédiction