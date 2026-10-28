// OLAP analytique (ClickHouse via dbt).
// ==========================================
// Fichier non DBML standard - référence pour OLAP créé par des transformations DBT
// ==========================================
// Mois = premier jour du mois (type date). Dates en UTC.

Table dim_customers {            // à plat : client + métier + adresse + ville + état
  customer_id Int64 [pk]
  first_name  String
  last_name   String
  gender      String
  dob         Date32
  job         String
  street      String
  lat         Decimal(9,6)
  long        Decimal(9,6)
  city        String
  zip         String
  city_pop    Nullable(Int32)
  state       String
}

Table dim_merchants {
  merchant_id Int64 [pk]
  merchant    String
}

Table dim_analysts {
  analyst_id Int32 [pk]            // 0 = import initial
  role       Nullable(String)
}

Table fct_transactions {         // une ligne = une transaction
  transaction_id      Int64 [pk]
  trans_num           String
  customer_id         Int64
  merchant_id         Int64
  transdate_transtime DateTime64(6,'UTC')
  transaction_date    Date
  transaction_month   Date
  amt                 Decimal(20,4)
  status              String
  review_status       String
}

Table fct_predictions {          // une ligne = une prédiction du modèle ; exclut les lignes init
  trans_num           String [pk]
  outcome             String    // rejected | cleared | pending | reviewed
  transdate_transtime DateTime64(6,'UTC')
  prediction_date     Date
  prediction_month    Date
  amt                 Decimal(20,4)
  fraud_score         Decimal(6,4)
  model_version       String
  is_fraud            Nullable(Bool)   // renseigné seulement si outcome = reviewed
}

Table fct_frauds {               // une ligne = une fraude, évitée ou subie
  trans_num           String [pk]
  origin              String    // rejected | reviewed | init
  merchant_id         Int64
  transdate_transtime DateTime64(6,'UTC')
  fraud_date          Date
  fraud_month         Date
  amt                 Decimal(20,4)
  merch_lat           Decimal(9,6)
  merch_long          Decimal(9,6)
  fraud_score         Nullable(Decimal(6,4))  // null pour init
}

Table fct_reviews {              // une ligne = un verdict d analyste
  transaction_id        Int64 [pk]
  trans_num             String
  analyst_id            Int32
  transdate_transtime   DateTime64(6,'UTC')
  transaction_date      Date
  transaction_month     Date
  verdict_at            DateTime64(6, 'UTC')    // verdict_at NOT NULL dans fct_reviews
  verdict_date          Date
  verdict_month         Date
  review_delay_s        Int64     // verdict_at - transdate_transtime, en secondes
  is_fraud              Bool
  amt                   decimal(20,4)
}
