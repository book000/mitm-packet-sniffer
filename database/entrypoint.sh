#!/bin/ash
# shellcheck shell=dash

# 引数を取得 (export or import)
MODE=$1

# Export the database
export_db() {
  # Remove the old schema file
  rm -f "/schema/*.sql"

  # Export the database to a file
  mysqldef -h "$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" --export > "/schema/$DB_NAME.sql"
}

# Import the database
import_db() {
  # Get the schema file
  SCHEMA_FILE="/schema/$DB_NAME.sql"

  # Check if the schema file exists
  if [ ! -f "$SCHEMA_FILE" ]; then
    echo "Schema file not found"
    exit 1
  fi

  # Import the database from a file
  if [ "$1" = "dry-run" ]; then
    mysqldef -h "$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" --dry-run < "$SCHEMA_FILE"
  else
    mysqldef -h "$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$SCHEMA_FILE"
  fi
}

if [ "$MODE" = "export" ]; then
  # Export the database
  export_db
elif [ "$MODE" = "import" ]; then
  # Import the database
  import_db
elif [ "$MODE" = "import-dry-run" ]; then
  # Import the database (dry-run)
  import_db dry-run
else
  # Invalid mode
  echo "Invalid mode: $MODE"
  exit 1
fi