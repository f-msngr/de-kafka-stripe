## Visualiser les topics -> `/kafka/bin/kafka-topics.sh`
    /kafka/bin/kafka-topics.sh --bootstrap-server kafka-broker:29092 --list
    02_stripe-connect_configs
    02_stripe-connect_offsets
    02_stripe-connect_statuses
    02_stripe.frauds.rejects
    02_stripe.ingest.incoming-tnx
    02_stripe.payments.activities
    02_stripe.payments.addresses
    02_stripe.payments.analysts
    02_stripe.payments.cities
    02_stripe.payments.currencies
    02_stripe.payments.customers
    02_stripe.payments.jobs
    02_stripe.payments.merchants
    02_stripe.payments.states
    02_stripe.payments.transactions
    __consumer_offsets

## Détail d'un topic (partitions, replica) -> `/kafka/bin/kafka-topics.sh`
    
    /kafka/bin/kafka-topics.sh --bootstrap-server kafka-broker:29092 --describe --topic 02_stripe.incoming-tnx
    Topic: 02_stripe.incoming-tnx	TopicId: uhvcCLRRQqWlQ2wMp5Or6g	PartitionCount: 1	ReplicationFactor: 1	Configs: min.insync.replicas=1,segment.bytes=536870912,retention.ms=86400000,retention.bytes=1073741824
	Topic: 02_stripe.incoming-tnx	Partition: 0	Leader: 1	Replicas: 1	Isr: 1	Elr: 	LastKnownElr:

## Lire les messages -> `/kafka/bin/kafka-console-consumer.sh`

    /kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka-broker:29092 --topic 02_stripe.incoming-tnx --from-beginning --max-messages 10
    The consumer rebalance protocol (KIP-848) is production-ready! Set group.protocol=consumer to try it out. See https://kafka.apache.org/documentation/#consumer_rebalance_protocol
    {"n": 1, "ts": "2026-10-10T16:24:46.269407+00:00"}
    {"n": 2, "ts": "2026-10-10T16:24:46.269946+00:00"}
    {"n": 3, "ts": "2026-10-10T16:24:46.269975+00:00"}
    {"n": 4, "ts": "2026-10-10T16:24:46.269993+00:00"}
    {"n": 5, "ts": "2026-10-10T16:24:46.270006+00:00"}
    {"n": 6, "ts": "2026-10-10T16:25:00.008054+00:00"}
    {"n": 7, "ts": "2026-10-10T16:25:00.008251+00:00"}
    {"n": 8, "ts": "2026-10-10T16:25:00.008294+00:00"}
    {"n": 9, "ts": "2026-10-10T16:25:00.008324+00:00"}
    {"n": 10, "ts": "2026-10-10T16:25:00.008353+00:00"}
    Processed a total of 10 messages

## Nombre de messages -> `/kafka/bin/kafka-get-offsets.sh`

    /kafka/bin/kafka-get-offsets.sh --bootstrap-server kafka-broker:29092 --topic 02_stripe.incoming-tnx
    02_stripe.incoming-tnx:0:10

## Offset atteint pour un groupe sur un topic -> `/kafka/bin/kafka-consumer-groups.sh`

    /kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka-broker:29092 --describe --group group-predict

    GROUP           TOPIC                  PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID                                             HOST            CLIENT-ID
    group-predict   02_stripe.incoming-tnx 0          -               30107           -               kafka-python-2.2.3-314d7bb6-80a1-4cbf-a850-07dab6e697aa /172.22.0.7     kafka-python-2.2.3
