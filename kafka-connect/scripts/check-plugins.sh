#!/bin/sh
# Contrôle statique des plugins Kafka Connect (exécuté au build, voir Dockerfile).
# Règle : <DOSSIER_PLUGINS>/<un_dossier_par_plugin>/*.jar ; chaque plugin doit déclarer au moins une classe Connect.
# Usage : check-plugins.sh <DOSSIER_PLUGINS>
set -u
DIR="${1:?usage: check-plugins.sh <DOSSIER_PLUGINS>}"
ERREURS=0
ERR() { echo "ERREUR : $*" >&2; ERREURS=$((ERREURS + 1)); }

# Un jar posé à la racine n'est pas dans un sous-dossier de plugin : à ranger
# cf. README.md
for J in "$DIR"/*.jar; do
  [ -e "$J" ] && ERR "jar à la racine de $DIR (à ranger dans un sous-dossier) : $(basename "$J")"
done

NB=0
for P in "$DIR"/*/; do
  [ -d "$P" ] || continue
  NB=$((NB + 1)); NOM=$(basename "$P"); NBJAR=0; DECL=0
  echo "plugin : $NOM"
  for J in "$P"*.jar; do
    [ -e "$J" ] || continue
    NBJAR=$((NBJAR + 1))
    if ! unzip -tq "$J" >/dev/null 2>&1; then ERR "$NOM : jar illisible ou corrompu : $(basename "$J")"; continue; fi
    # Kafka Connect découvre les plugins par les fichiers META-INF/services/org.apache.kafka.connect.*
    for SVC in $(unzip -Z1 "$J" 'META-INF/services/org.apache.kafka.connect.*' 2>/dev/null); do
      TYPE=${SVC##*.}
      for CLASSE in $(unzip -p "$J" "$SVC" | sed -e 's/#.*//' -e 's/[[:space:]]//g' -e '/^$/d'); do
        echo "  $TYPE : $CLASSE"; DECL=$((DECL + 1))
      done
    done
  done
  [ "$NBJAR" -eq 0 ] && ERR "$NOM : aucun .jar dans ce dossier"
  [ "$NBJAR" -gt 0 ] && [ "$DECL" -eq 0 ] && ERR "$NOM : aucune classe Kafka Connect déclarée (pas un plugin, ou mauvais jar)"
done
[ "$NB" -eq 0 ] && ERR "aucun sous-dossier de plugin dans $DIR"

if [ "$ERREURS" -gt 0 ]; then echo "ÉCHEC : $ERREURS erreur(s)" >&2; exit 1; fi
echo "OK : $NB plugin(s) valide(s)"