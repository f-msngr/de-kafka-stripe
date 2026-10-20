#/bin/sh
gnome-terminal -- bash -c 'echo "TOPIC 02_stripe.incoming-tnx" ; docker exec -it 02_stripe-kafka-broker /kafka/bin/kafka-topics.sh --bootstrap-server kafka-broker:29092 --describe --topic 02_stripe.incoming-tnx; echo "Offsets par groupe" ; docker exec -it 02_stripe-kafka-broker /kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka-broker:29092 --describe --group predict-group ; cd ./producer-tnx ; exec bash'
gnome-terminal --working-directory="$HOME/ld/02_stripe" -- bash -c 'docker compose logs -f consumer-tnx; exec bash'
gnome-terminal -- bash -c 'docker compose exec kafka-broker /kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka-broker:29092 --topic 02_stripe.incoming-tnx --from-beginning; exec bash'
gnome-terminal -- bash -c 'docker compose exec db-src psql -h localhost -p 5432 -U stripe ; exec bash'
gnome-terminal -- bash -c 'docker compose exec db-target clickhouse-client --user clickhouse-user --password clickhouse-pwd ; exec bash'
