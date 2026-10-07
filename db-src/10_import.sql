-- L'entrypoint Docker (qui ignore les sous-dossiers) lance un run.sql
-- dont le path est relatif au fichier appelant (ici init/10_import.sql)
-- et qui gère l'ensemble des imports de données (csv, json, sql, etc.)
-- le tout dans une séquence transactionnelle (BEGIN/COMMIT).
-- On peut pas simplement lancer les imports successifs de façon transactionnelle avec des fichiers .sql
-- dans ce répertoire monté dans /docker-entrypoint-initdb.d/
-- car psql lance les fichiers, chacun dans une session séparée donc transaction séparée
-- et ne gère pas les transactions entre eux.
\ir import/run.sql
