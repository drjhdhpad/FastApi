from sqlalchemy import Engine, inspect


def _columns(engine: Engine, table: str) -> set[str]:
    return {column["name"] for column in inspect(engine).get_columns(table)}


def _add_column(engine: Engine, table: str, name: str, definition: str) -> None:
    if name not in _columns(engine, table):
        with engine.begin() as connection:
            connection.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


def _migrate_users(engine: Engine) -> None:
    columns = _columns(engine, "users")
    if "age" in columns:
        phone_expr = "phone" if "phone" in columns else "NULL"
        balance_expr = "balance" if "balance" in columns else "0"
        connection = engine.raw_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=OFF")
            cursor.execute(
                "CREATE TABLE users_new (id INTEGER NOT NULL PRIMARY KEY, "
                "name VARCHAR(100) NOT NULL, email VARCHAR(255) NOT NULL UNIQUE, "
                "phone VARCHAR(30), balance INTEGER NOT NULL DEFAULT 0)"
            )
            cursor.execute(
                "INSERT INTO users_new (id, name, email, phone, balance) "
                f"SELECT id, name, email, {phone_expr}, {balance_expr} FROM users"
            )
            cursor.execute("DROP TABLE users")
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")
            connection.commit()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    _add_column(engine, "users", "phone", "VARCHAR(30)")
    _add_column(engine, "users", "balance", "INTEGER NOT NULL DEFAULT 0")
    _add_column(engine, "users", "birth_date", "DATETIME")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE users SET birth_date = CURRENT_TIMESTAMP WHERE birth_date IS NULL"
        )


def run_migrations(engine: Engine) -> None:
    """Apply small additive migrations for databases created by earlier app versions."""
    _migrate_users(engine)
    _add_column(engine, "advistiments", "address_id", "INTEGER REFERENCES address(id)")
    _add_column(engine, "advistiments", "isActive", "BOOLEAN NOT NULL DEFAULT 1")
    _add_column(engine, "advistiments", "created_at", "DATETIME")
    _add_column(engine, "advistiments", "view_count", "INTEGER NOT NULL DEFAULT 0")
    _add_column(engine, "advistiments", "is_favorite", "BOOLEAN NOT NULL DEFAULT 0")
    _add_column(engine, "advistiments", "is_adult", "BOOLEAN NOT NULL DEFAULT 0")
    if "date" in _columns(engine, "advistiments"):
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "UPDATE advistiments SET created_at = date WHERE created_at IS NULL"
            )
            # The ORM writes created_at; the legacy NOT NULL column would reject inserts.
            connection.exec_driver_sql("ALTER TABLE advistiments DROP COLUMN date")

    existing_stats = _columns(engine, "stats")
    stats_columns = {
        "ad_id": "INTEGER REFERENCES advistiments(id) ON DELETE CASCADE",
        "event_type": "VARCHAR(20)",
        "count": "INTEGER NOT NULL DEFAULT 0",
        "date": "DATETIME",
    }
    for name, definition in stats_columns.items():
        if name not in existing_stats:
            _add_column(engine, "stats", name, definition)

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE stats SET event_type = 'просмотр' "
            "WHERE event_type IS NULL AND ad_id IS NOT NULL"
        )
        connection.exec_driver_sql(
            "UPDATE stats SET date = CURRENT_TIMESTAMP WHERE date IS NULL AND ad_id IS NOT NULL"
        )
