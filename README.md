# kafka02 — réplication PostgreSQL → PostgreSQL avec Debezium et Kafka

## Objectif

### Architecture - niveau 1 (contexte)

```mermaid
C4Context
  title Plateforme de détection de fraude - Niveau 1 (contexte)

  Person(op, "Opérateur (Fab)", "Lance et arrête le flux, règle batch_size et fraud_percent")
  System(plat, "Plateforme de détection de fraude", "Ingère des transactions en temps réel, les note (prédiction factice), les stocke en OLTP et les réplique en OLAP")
  System_Ext(s3, "Pool de transactions S3", "feed.csv hébergé sur AWS S3 (91 324 lignes)")

  Rel(op, plat, "Pilote le flux", "feedctl.sh, settings.json")
  Rel(plat, s3, "Lit le fichier en flux", "HTTPS")
```

### Architecture - niveau 2 (conteneurs)

```mermaid
C4Container
  title Plateforme de détection de fraude - Niveau 2 (conteneurs)

  Person(op, "Opérateur (Fab)", "")
  System_Ext(s3, "Pool S3", "feed.csv")

  System_Boundary(plat, "Plateforme de détection de fraude (docker compose, project-network)") {
    Container(prod, "producer-tnx", "Python, httpx", "Lit feed.csv par lots, injecte la fraude synthétique, envoie à l'API")
    Container(api, "api-gateway", "FastAPI, uvicorn", "Seul écrivain du topic : POST /ingest, répond 202 ou 503")
    ContainerQueue(kafka, "kafka-broker", "Kafka KRaft, 1 nœud", "Topic 02_stripe.incoming-tnx + topics Debezium")
    Container(cons, "consumer-tnx", "Python, kafka-python-ng", "Groupe group-predict, score factice, écrit dans l'OLTP, N réplicas")
    ContainerDb(src, "db-src (OLTP)", "PostgreSQL 18", "Schémas payments et frauds, wal_level=logical")
    Container(conn, "kafka-connect", "Debezium source + ClickHouse sink v1.7.0", "Réplication CDC de l'OLTP vers l'OLAP")
    ContainerDb(tgt, "db-target (OLAP)", "ClickHouse", "Tables brutes ReplacingMergeTree")
  }

  Rel(op, prod, "start / halt", "feedctl.sh, settings.json")
  Rel(prod, s3, "Lit feed.csv", "HTTPS")
  Rel(prod, api, "POST /ingest", "HTTP, JSON")
  Rel(api, kafka, "Publie", "Kafka, acks=all")
  Rel(kafka, cons, "Livre les messages", "Kafka, commit manuel")
  Rel(cons, src, "INSERT transactions ou rejects", "SQL, psycopg")
  Rel(src, conn, "Changements (WAL)", "Réplication logique")
  Rel(conn, kafka, "Publie et relit les topics CDC", "Kafka")
  Rel(conn, tgt, "Insère les lignes", "HTTP 8123")

  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```


Tous les services sont sur un même réseau Docker, nommé `<$PROJECT_NAME>`).

|

## Ordre de création et dépendances

`
```

« healthy » signifie que le test de santé (`healthcheck`) du service est passé. `init` termine à l'état `Exited (0)` : c'est normal.

Scripts d'initialisation des bases, exécutés une seule fois à la création d'une base vide, dans l'ordre alphabétique :

- `./db-src/` : `01_role.sh` (rôle `debezium`), `02_schemas.sql` (schéma et tables), `03_permissions.sh` (droits), `04_publications.sh` (publication)
- `./db-target/` : création des tables cibles (`01_create_table_customers.sql`)

## Options figées pour l'instant

Les variables sont dans `.env`, sauf mention contraire.

### Kafka (cluster, nœud, ports)



### Topics


### Connect et connecteur



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


### Accès depuis l'hôte (127.0.0.1 uniquement)



### Persistance

# Commandes

- relance du projet et reconstruction  des bases + conteneurs
docker compose up -d --build

- Arrêt des conteneurs + suppression + suppression des volumes nommés
docker compose down -v --remove-orphans
