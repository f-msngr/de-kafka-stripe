# Commandes

- Relancer le serveur
  `docker compose up -d --force-recreate db-target`

- Voir l'état du service
  `docker compose ps db-target`                       # attendre « healthy

- Tester le client depuis l'hôte via un shell du conteneur :
  `docker compose exec db-target sh -c 'clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD" -q "SELECT 1"'`   # doit répondre : 1

- Se connecter au client dans le conteneur :
  `clickhouse-client --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD"`

- Afficher la config spécifique
  `SELECT name, value FROM system.server_settings WHERE name = 'PARAMETRE_SERVEUR'`

# Structure des fichiers de conf

## Dossier de configuration `FICHIER.xml` du server lu et fusionné au démarrage

monté dans `/etc/clickhouse-server/config.d/FICHIER.xml`

  <clickhouse>
    <PARAMETRE_SERVEUR>VALEUR</PARAMETRE_SERVEUR>
  </clickhouse>

## Dossier de configuration `FICHIER.xml` des permissions et droits des users lu et fusionné au démarrage

monté dans `/etc/clickhouse-server/users.d/FICHIER.xml`

  <clickhouse>
    <PARAMETRE_USERS>VALEUR</PARAMETRE_USERS>
  </clickhouse>