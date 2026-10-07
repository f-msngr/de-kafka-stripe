-- Contrôles : pour chaque table, nombre attendu (clés distinctes du CSV) = nombre trouvé dans la base. Un écart annule toute la transaction.
DO $$
DECLARE ecarts text;
BEGIN
  SELECT string_agg(label || ' : attendu ' || attendu || ', obtenu ' || obtenu, E'\n') INTO ecarts
  FROM (
    SELECT 'états' AS label,
      (SELECT count(DISTINCT state) FROM import_csv) AS attendu,
      (SELECT count(*) FROM payments.states WHERE state IN (SELECT state FROM import_csv)) AS obtenu
    UNION ALL SELECT 'villes',
      (SELECT count(DISTINCT (city, state, zip)) FROM import_csv),
      (SELECT count(*) FROM payments.cities c JOIN payments.states st USING (state_id)
        WHERE EXISTS (SELECT 1 FROM import_csv s WHERE s.city = c.city AND s.state = st.state AND s.zip = c.zip))
    UNION ALL SELECT 'adresses',
      (SELECT count(DISTINCT (street, lat::numeric(9,6), "long"::numeric(9,6), city, state, zip)) FROM import_csv),
      (SELECT count(*) FROM payments.addresses a
         JOIN payments.cities c ON c.city_id = a.city_id
         JOIN payments.states st ON st.state_id = c.state_id
        WHERE EXISTS (SELECT 1 FROM import_csv s
                       WHERE s.street = a.street AND s.lat::numeric(9,6) = a.lat AND s."long"::numeric(9,6) = a.long
                         AND s.city = c.city AND s.state = st.state AND s.zip = c.zip))
    UNION ALL SELECT 'métiers',
      (SELECT count(DISTINCT job) FROM import_csv),
      (SELECT count(*) FROM payments.jobs WHERE job IN (SELECT job FROM import_csv))
    UNION ALL SELECT 'clients',
      (SELECT count(DISTINCT ("first", "last", dob)) FROM import_csv),
      (SELECT count(*) FROM payments.customers c
        WHERE EXISTS (SELECT 1 FROM import_csv s WHERE s."first" = c.first_name AND s."last" = c.last_name AND s.dob::date = c.dob))
    UNION ALL SELECT 'catégories',
      (SELECT count(DISTINCT category) FROM import_csv),
      (SELECT count(*) FROM payments.activities WHERE category IN (SELECT category FROM import_csv))
    UNION ALL SELECT 'marchands',
      (SELECT count(DISTINCT merchant) FROM import_csv),
      (SELECT count(*) FROM payments.merchants WHERE merchant IN (SELECT merchant FROM import_csv))
    UNION ALL SELECT 'transactions',
      (SELECT count(*) FROM import_csv),
      (SELECT count(*) FROM payments.transactions WHERE trans_num IN (SELECT trans_num FROM import_csv))
    UNION ALL SELECT 'transactions frauduleuses',
      (SELECT count(*) FROM import_csv WHERE is_fraud::boolean),
      (SELECT count(*) FROM payments.transactions WHERE is_fraud AND trans_num IN (SELECT trans_num FROM import_csv))
  ) c
  WHERE attendu <> obtenu;

  IF ecarts IS NOT NULL THEN
    RAISE EXCEPTION E'Contrôles d''import en échec :\n%', ecarts;
  END IF;
END
$$;