## Structure du rep

    kafka-connect/
    ├── Dockerfile                  # étape 1 : contrôle des plugins ; étape 2 : image finale
    ├── configs/<nom>.json          # un fichier = un connector (config à plat, variables ${env:NOM})
    ├── plugins/<un_dossier_par_plugin>/*.jar   # jars copiés dans /kafka/connect/ de l'image
    └── scripts/
        ├── check-plugins.sh        # exécuté au BUILD (étape 1 du Dockerfile)
        ├── check-connectors.sh     # copié dans l'image : healthcheck (l'API REST répond)
        └── init.sh                 # monté dans le service `init` : charge configs/*.json

## Version du plugin

La version à jour au moment de la création du projet est la 1.7.0
Visible ici https://github.com/ClickHouse/clickhouse-kafka-connect/releases

- Télécharger la version à jour en .zip,
- Décompresser le .jar dans plugins/clickhouse-kafka-connect

## Path des plugins

L'image Debezium va chercher plugins dans des sous-dossiers de /kafka/connect/
Les plugins doivent donc être dans des sous-dossiers de plugins/ sur le host
pour être montés comme prévu dans le Dockerfile

## Contrôles, dans l'ordre

| Quand | Où | Ce qui est contrôlé |
|---|---|---|
| Build | Dockerfile, étape 1 (`check-plugins.sh`) | Chaque `plugins/<dossier>/` contient des jars lisibles qui déclarent une classe Connect. Sinon : pas d'image. |
| Démarrage | Healthcheck du compose (`/kafka/check-connectors.sh`) | L'API REST répond (`/connectors`). |
| Chargement | `init.sh` (`PUT /connectors/<nom>/config`) | Connect valide la config ; erreur HTTP 400 si non conforme, l'init échoue. |
| Après chargement | `init.sh` (`GET /connectors/<nom>/status`) | État affiché dans les logs : `RUNNING` attendu pour le connector et ses tasks. |

Le healthcheck n'exige pas de connector enregistré : l'init attend que Connect soit `healthy` avant de les charger.

## Commandes utiles

```sh
# Reconstruire (le compose ne reconstruit pas tout seul une image existante)
docker compose build --no-cache --pull --progress=plain kafka-connect
docker compose up -d

# Erreurs du build, étape 1 (--no-cache : sinon une étape déjà en cache n'affiche rien)
docker compose build --no-cache --progress=plain kafka-connect 2>&1 | tee /tmp/build.log
grep -n -B2 -A6 'ERREUR\|ÉCHEC' /tmp/build.log

# Connectors et état, depuis l'hôte (HOST_CONNECT_PORT = port publié du compose)
curl -s http://localhost:${HOST_CONNECT_PORT}/connectors
curl -s http://localhost:${HOST_CONNECT_PORT}/connector-plugins | grep -o 'ClickHouseSinkConnector'
```