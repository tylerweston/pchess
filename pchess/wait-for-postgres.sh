#!/bin/bash
# wait-for-postgres.sh

# this is unused and will be removed
set -e

host="$1"
shift

until psql -h "$host" -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exit 0