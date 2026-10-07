ARG DEBEZIUM_VERSION

# Étape 1 : contrôle des plugins. Le build s'arrête ici si un plugin est invalide.
# Sortie visible dans les logs du build pas dans ceux du conteneur
FROM alpine:3 AS check-plugins
RUN apk add --no-cache unzip
COPY --chmod=755 ./scripts/check-plugins.sh /check-plugins.sh
COPY ./plugins/ /plugins/
RUN /check-plugins.sh /plugins


# Étape 2 : build de l'image finale
FROM quay.io/debezium/connect:${DEBEZIUM_VERSION}
# Installation du plugin Debezium pour Clickhouse (Nécessaire pour db-target)
# Utiliser la derière version
# https://github.com/ClickHouse/clickhouse-kafka-connect/releases
# cf. README.md

# Plugins Kafka Connect ajoutés à l'image Debezium : ClickHouse Kafka Connect Sink
# (jar téléchargé à la main, version et sha256 : voir README.md).
# Connect cherche les plugins dans /kafka/connect/<un_dossier_par_plugin>/ ;
# ce même découpage existe donc côté host dans plugins/.
# le COPY --from=check-plugins oblige Docker à exécuter l'étape 1
# jars copiés seulement si l'étape 1 a réussi
COPY --from=check-plugins --chown=kafka:kafka /plugins/ /kafka/connect/

# Tester les connectors
COPY --chown=kafka:kafka --chmod=755 ./scripts/check-connectors.sh /kafka/check-connectors.sh

# Pas de HEALTHCHECK ici
# Le contrôle des JSON de configs/ est une étape suivante (scripts/check-connectors.sh).

# Déjà l'utilisateur par défaut de l'image Debezium - écrit pour mémoire
USER kafka