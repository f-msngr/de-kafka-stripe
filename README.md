# kafka02 — réplication PostgreSQL → PostgreSQL avec Debezium et Kafka

## ⚠️ .env est inclu mais sans effet car aucune clé privée
    - uniquement pour des raisons de sauvegarde
    - penser à modifier .gitignore après clonage de ce repo template

## Objectif

Squelette réutilisable de réplication en continu (CDC, *Change Data Capture* : copie des modifications d'une base au fil de l'eau) d'une base PostgreSQL source vers une base PostgreSQL cible, à adapter à des besoins précis.

Choix de dimensionnement actuels :

| Élément | Nombre | Précision |
|---|---|---|
| Connecteur Debezium | 1 | `./init/connectors/pg-connector-inventory.json` ; capture les tables `customers` et `orders` du schéma `inventory` ; occupe 1 des 5 slots de réplication autorisés sur `db-src` (un slot est une réservation côté PostgreSQL qui garde les changements en attente de lecture) |
| Service consumer | 1 | `consumer-trial`, rôle principal de monitoring ; code dans `./consumers/consumer-trial/` ; lit les 2 topics |
| Groupe de consommation | 1 | `Monitor` |
| Nœud Kafka | 1 | Broker et contrôleur dans le même conteneur (`kafka`) |

## Architecture logique

```
db-src ──► connect ──► kafka ──► consumer-trial ──► db-target
PostgreSQL  Debezium    topics    groupe "Monitor"   PostgreSQL
(source)    (lit le WAL)          (lit 2 topics)     (cible)

init ──► connect     (enregistre le connecteur par l'API REST, puis s'arrête)
```

Tous les services sont sur un même réseau Docker, nommé `<$PROJECT_NAME>`).

| Service | Image | Rôle |
|---|---|---|
| `db-src` | `postgres:18.4-bookworm` | Base source ; son journal des changements (WAL) est lu par Debezium |
| `kafka` | `quay.io/debezium/kafka:3.6` | Broker Kafka unique en mode KRaft (sans ZooKeeper) ; stocke les changements dans des topics |
| `connect` | `quay.io/debezium/connect:3.6` | Exécute le connecteur Debezium : lit le WAL de `db-src` et publie dans Kafka |
| `db-target` | `postgres:18.4-bookworm` | Base cible |
| `consumer-trial` | construite depuis `./consumers/consumer-trial/Dockerfile` | Lit les topics et écrit dans `db-target` |
| `init` | `curlimages/curl:latest` (version non épinglée) | Enregistre le connecteur dans `connect` (`./init/init.sh`, `./init/connectors/`), puis s'arrête |

## Ordre de création et dépendances

```
Étape 1 (en parallèle, aucune dépendance) : db-src, kafka, db-target
Étape 2 : connect          attend : kafka "healthy"
Étape 3 : init             attend : connect "healthy" ET db-src "healthy"
Étape 4 : consumer-trial   attend : kafka "healthy", db-target "healthy"
                                    ET la fin réussie de init (code de sortie 0)
```

« healthy » signifie que le test de santé (`healthcheck`) du service est passé. `init` termine à l'état `Exited (0)` : c'est normal.

Scripts d'initialisation des bases, exécutés une seule fois à la création d'une base vide, dans l'ordre alphabétique :

- `./db-src/` : `01_role.sh` (rôle `debezium`), `02_schemas.sql` (schéma et tables), `03_permissions.sh` (droits), `04_publications.sh` (publication)
- `./db-target/` : création des tables cibles (`01_create_table_customers.sql`)

## Options figées pour l'instant

Les variables sont dans `.env`, sauf mention contraire.

### Kafka (cluster, nœud, ports)

| Option | Valeur | Variable / fichier |
|---|---|---|
| Identifiant du cluster | `<$CLUSTER_ID>` (UUID généré) | `CLUSTER_ID` |
| Mode | KRaft (sans ZooKeeper), 1 nœud | n/a |
| Identifiant du nœud | `1` | `NODE_ID` |
| Rôle du nœud | `combined` (broker + contrôleur) | `NODE_ROLE` |
| Votants du quorum | `1@kafka:9093` | `KAFKA_CONTROLLER_QUORUM_VOTERS` (construit depuis `NODE_ID`, `SRVC_KAFKA`, `CTNR_KAFKA_INTERNAL_CONTROLLER_LISTENER_PORT`) |
| Port interne (conteneurs du réseau) | `29092` | `CTNR_KAFKA_INTERNAL_LISTENER_PORT` ; adresse des clients : `BOOTSTRAP_SERVERS` = `kafka:29092` |
| Port externe (depuis l'hôte) | `9092` dans le conteneur, publié sur `127.0.0.1:9092` | `CTNR_KAFKA_EXTERNAL_LISTENER_PORT`, `HOST_KAFKA_PORT` |
| Port du contrôleur | `9093` | `CTNR_KAFKA_INTERNAL_CONTROLLER_LISTENER_PORT` |

### Topics

| Option | Valeur | Variable / fichier |
|---|---|---|
| Nommage | `<préfixe>.<schéma>.<table>`, préfixe `<$PROJECT_NAME>` | `TOPIC_PREFIX_CONNECT` (= `PROJECT_NAME`) |
| Topics de données | `<$SRC_TABLES_CONNECT>` | déduits du préfixe, et de la liste des tables (format schéma.table dans connector.json) |
| Partitions | 1 par topic (valeur par défaut du broker, non fixée dans la configuration) : un seul consumer actif par groupe | n/a |
| Réplication | 1 (broker unique ; valeur par défaut, non fixée) | n/a |
| Création | Automatique, avec les valeurs par défaut du broker | n/a |
| Rétention (tous les topics) | 24 h, 1 Go par partition, contrôle toutes les 5 min, segments de 512 Mo | `docker-compose.yaml`, service `kafka` : `KAFKA_LOG_RETENTION_MS`, `KAFKA_LOG_RETENTION_BYTES`, `KAFKA_LOG_RETENTION_CHECK_INTERVAL_MS`, `KAFKA_LOG_SEGMENT_BYTES` (valeurs en dur) |

### Connect et connecteur

| Option | Valeur | Variable / fichier |
|---|---|---|
| Groupe des workers Connect | `kafka02-connect_group` | `GROUP_ID` |
| Topics internes de Connect | `kafka02-connect_configs`, `kafka02-connect_offsets`, `kafka02-connect_statuses` | `CONFIG_STORAGE_TOPIC`, `OFFSET_STORAGE_TOPIC`, `STATUS_STORAGE_TOPIC` |
| Lecture initiale | `snapshot.mode: always` : toutes les lignes sont relues à chaque démarrage du connecteur | `./init/connectors/pg-connector-inventory.json` |
| Plugin de décodage | `pgoutput` | même JSON |
| Suppressions | `tombstones.on.delete: false` (pas de message vide après un DELETE) | même JSON |
| Slot de réplication | `kafka02_inventory` | `DEBEZIUM_SLOT_TRIAL` |
| Publication | `debezium_pub`, couvre tout le schéma `inventory` | `DEBEZIUM_PUBLICATION`, `./db-src/04_publications.sh` |
| Tables capturées | `customers`, `orders` | `SRC_TABLES_CONNECT` |

### Bases de données

| Option | Valeur | Variable / fichier |
|---|---|---|
| Version PostgreSQL | 18.4 | image `postgres:18.4-bookworm` |
| Journal logique | `wal_level=logical` | `command:` du service `db-src` |
| Slots de réplication maximum | 5 | `max_replication_slots`, `command:` de `db-src` |
| WAL conservé au maximum par slot | 10 Go | `max_slot_wal_keep_size`, `command:` de `db-src` |
| Source : base et schéma | `postgres`, `inventory` | `DB_SRC_NAME`, `DB_SRC_SCHEMA` |
| Source : rôle de Debezium | `debezium` | `DEBEZIUM_USER` |
| Cible : base | `dbtarget` | `DB_TARGET_NAME` |

### Consumer

| Option | Valeur | Variable / fichier |
|---|---|---|
| Service | `consumer-trial` | `docker-compose.yaml`, `./consumers/consumer-trial/` |
| Groupe | `Monitor` | `KAFKA_GROUP_ID_MONITOR` |
| Topics lus | les 2 topics de données | `TOPIC_PREFIX`, `SRC_TABLES` (variables du service) |
| Début de lecture | `earliest` pour un groupe sans historique | `consumer_replicate.py` |
| Validation des lectures | manuelle (`enable_auto_commit=False`) | `consumer_replicate.py` |
| Bibliothèque Kafka | kafka-python 3.0.0 | `./consumers/consumer-trial/requirements.txt` |

### Accès depuis l'hôte (127.0.0.1 uniquement)

| Service | Port hôte | Variable |
|---|---|---|
| `db-src` | `5434` | `HOST_DB_SRC_PORT` |
| `db-target` | `5435` | `HOST_DB_TARGET_PORT` |
| `kafka` | `9092` | `HOST_KAFKA_PORT` |
| `connect` | `8083` | `HOST_CONNECT_PORT` |

### Persistance

Aucun volume nommé n'est déclaré : les données (bases, topics, offsets) ne sont pas conservées d'une recréation à l'autre, et les scripts d'initialisation sont rejoués sur chaque base neuve.