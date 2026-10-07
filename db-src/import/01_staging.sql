-- Table de passage : le csv à importer (import.csv) tel quel,
-- tout en texte, dans l'ordre des 23 colonnes du fichier
CREATE TEMP TABLE import_csv (
  idx                 text,
  trans_date_trans_time text,
  cc_num              text,
  merchant            text,
  category            text,
  amt                 text,
  "first"             text,
  "last"              text,
  gender              text,
  street              text,
  city                text,
  state               text,
  zip                 text,
  lat                 text,
  "long"              text,
  city_pop            text,
  job                 text,
  dob                 text,
  trans_num           text,
  unix_time           text,
  merch_lat           text,
  merch_long          text,
  is_fraud            text
) ON COMMIT DROP;

\copy import_csv FROM '/docker-entrypoint-initdb.d/import/import.csv' WITH (FORMAT csv, HEADER true)