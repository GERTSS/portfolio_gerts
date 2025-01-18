#!/bin/sh
set -e

until pg_isready -h "db" -U "admin"; do
  echo "Waiting for database connection..."
  sleep 2
done

python - <<EOF
from main import app, db, create_tables, wait_for_db
with app.app_context():
  wait_for_db(db.engine)
  create_tables()
EOF

exec gunicorn --bind 0.0.0.0:8080 main:app