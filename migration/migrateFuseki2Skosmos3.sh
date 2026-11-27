#!/bin/sh

# Define default language (e.g.: en, de, fr, ...)
DEFAULT_LANGUAGE=en

############################################################################
# Don't touch the following lines
############################################################################
# Determine directory of the script
ACTUAL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$ACTUAL_DIR"

# Get environment variables of project
set -a
. $ACTUAL_DIR/../.env
set +a

# Define fuseki type (possible values: dev, live)
FUSEKI_TYPE="${1:-dev}"

# Determine name of the container (fuseki-dev|live)
FUSEKI_DEV_CONTAINER=evoks_${INSTANCE_NAME}_fuseki-${FUSEKI_TYPE}

# Determine name of the network of fuseki-dev\live container
FUSEKI_DEV_NETWORK=$(docker inspect ${FUSEKI_DEV_CONTAINER} \
  --format '{{range $name, $_ := .NetworkSettings.Networks}}{{$name}}{{end}}')

# Determine available vocabularies
VOCABS=$(
  docker exec $FUSEKI_DEV_CONTAINER bash -c '
    for f in /fuseki-base/configuration/*.ttl; do
      basename "$f" .ttl
    done | grep -v assembler
  '
)
echo Fuseki container: $FUSEKI_DEV_CONTAINER
echo Fuseki network: $FUSEKI_DEV_NETWORK
echo Vocabularies found: $VOCABS

# Check all vocabularies for terms without a linked language
for vocab in $VOCABS; do
  echo "========================================================================================="
  echo Check for terms in vocabulary \'${vocab}\'...
  echo "--------------------------------------------"
  COUNT=$(docker run --rm \
    --network "$FUSEKI_DEV_NETWORK" \
    -v ".:/data" \
    alpine:3.22 \
    sh -c "
      apk add --no-cache curl jq >/dev/null
      curl -s -X POST \
        -H 'Content-Type: application/sparql-query' \
        --data-binary @/data/count_pref-labels.rq \
        'http://fuseki-${FUSEKI_TYPE}:3030/${vocab}/query' | jq -r '.results.bindings[0].count.value // 0'")
  if [ "$COUNT" -gt 0 ]; then
    echo "    There are ${COUNT} term(s) without a linked language"
    echo "    Try to fix the vocabulary..."
    read -p "    Use the following language as default [${DEFAULT_LANGUAGE}, 'x'=SKIP]:" LANGUAGE
    # In case of no input use default language defined above
    LANGUAGE=${LANGUAGE:-$DEFAULT_LANGUAGE}
    # Check for valid language code (e.g. en, de, fr, ...)
    if [[ "${LANGUAGE}" =~ ^[a-z]{2}$ ]]; then
      echo "    Use ${LANGUAGE} as default language."
      # Prepare Query
      sed "s/__DEFAULT_LANGUAGE__/${LANGUAGE}/g" template_update_pref-labels.rq > update_pref-labels.rq

      # Run update inside a docker container with access to fuseki
      docker run --rm \
        --network "$FUSEKI_DEV_NETWORK" \
        -v ".:/data" \
        curlimages/curl   sh -c "
          curl -X POST -H 'Content-Type: application/sparql-update' \
            --data-binary @/data/update_pref-labels.rq \
            'http://fuseki-${FUSEKI_TYPE}:3030/${vocab}/update'"
      echo "   ... fixed!"
    else 
      echo "   ... skip vocabular!"
    fi
  else 
    echo "    Vocabulary already prepared for SKOSMOS 3!"
  fi
done
echo "========================================================================================="
echo Migration of EVOKS finished!

