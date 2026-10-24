column00,trans_date_trans_time,cc_num,merchant,category,amt,first,last,gender,street,city,state,zip,lat,long,city_pop,job,dob,trans_num,unix_time,merch_lat,merch_longcolumn00,trans_date_trans_time,cc_num,merchant,category,amt,first,last,gender,street,city,state,zip,lat,long,city_pop,job,dob,trans_num,unix_time,merch_lat,merch_longcolumn00,trans_date_trans_time,cc_num,merchant,category,amt,first,last,gender,street,city,state,zip,lat,long,city_pop,job,dob,trans_num,unix_time,merch_lat,merch_long

**worker_incoming_tnx** (SUPPRESSION : column00,unix_time + AJOUT uuid)

uuid,trans_date_trans_time,cc_num,merchant,category,amt,first,last,gender,street,city,state,zip,lat,long,city_pop,job,dob,trans_num,unix_time,merch_lat,merch_longcolumn00,trans_date_trans_time,cc_num,merchant,category,amt,first,last,gender,street,city,state,zip,lat,long,city_pop,job,dob,trans_num,unix_time,merch_lat,merch_longcolumn00,trans_date_trans_time,cc_num,merchant,category,amt,first,last,gender,street,city,state,zip,lat,long,city_pop,job,dob,trans_num,merch_lat,merch_long

**worker_predict**

Upserts dans l’ordre : states → cities → addresses → jobs → customers → activities → merchants (chacun renvoie son identifiant)

si fraud_score >= FRAUD_THRESHOLD : 
    insertion dans frauds.rejects
sinon
    insertion dans payments.transactions


```mermaid
flowchart TD
    A[tnx - csv] --> |producer-tnx : Lit une ligne du CSV, retire column00 et unix_time, ajoute un uuid, l’envoie en POST /ingest - réponse 202 | B[tnx - json ]
    B --> |api-gateway : Met la transaction dans le topic Kafka TOPIC_INCOMING_TNX | C[ tnx - json ]
    C --> |consumer-tnx : Lit le topic, prédit fraud_score, ouvre une transaction SQL dans db-src | D[ références - BDD]
    D -->|Upsert| E[ payments.states ]
    D -->|Upsert| F[ payments.cities ]
    D -->|Upsert| G[ payments.addresses ]
    D -->|Upsert| H[ payments.jobs ]
    D -->|Upsert| I[ payments.customers ]
    D -->|Upsert| J[ payments.activities ]
    D -->|Upsert| K[ payments.merchants ]
    D --> L{ model_version, fraud_score, fraud_score** <= FRAUD_THRESHOLD }
    L -->|true : insert | M[ payments.transactions : is_fraud=false, status: successful/failed/refunded/reversed, review_status: init/cleared/pending/reviewed ]
    L -->|false : insert| N[ frauds.rejects]
    E -->| CDC Debezium + Sink Kafka| O[ raw.states ]
    F -->| CDC Debezium + Sink Kafka| P[ raw.cities ]
    G -->| CDC Debezium + Sink Kafka| Q[ raw.addresses ]
    H -->| CDC Debezium + Sink Kafka| R[ raw.jobs ]
    I -->| CDC Debezium + Sink Kafka| S[ raw.customers ]
    J -->| CDC Debezium + Sink Kafka| T[ raw.activities ]
    K -->| CDC Debezium + Sink Kafka| U[ raw.merchants ]
    M -->| CDC Debezium + Sink Kafka| V[ raw.payments ]
    N -->| CDC Debezium + Sink Kafka| W[ raw.rejects ]
```