## Nommage de project, stripe_olap, clickhouse
les noms sont en dur dans les fichiers de configuration .yml / répertoires / dockerfile

vérifier les occurences aver grep -rl avant toute modification de nom

## Lancer dbt pour test depuis le conteneur (/home/user/app$)
    dbt run --select <UN_DES_MODELES_DANS_REP_MODELS> --project-dir $DBT_PROJECT_DIR --target dev