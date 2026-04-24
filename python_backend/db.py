import os
from contextlib import contextmanager
from pathlib import Path

try:
    import pymysql
    from pymysql.cursors import DictCursor
except ImportError:  # pragma: no cover - handled at runtime for friendlier errors
    pymysql = None
    DictCursor = None


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
ENV_PATH = BASE_DIR / ".env"


def load_env_file(path=ENV_PATH):
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file()


class DatabaseUnavailable(RuntimeError):
    pass


def db_config(include_database=True):
    config = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": False,
    }
    if include_database:
        config["database"] = os.getenv("MYSQL_DATABASE", "profitai")
    return config


@contextmanager
def connection(include_database=True):
    if pymysql is None:
        raise DatabaseUnavailable("Missing dependency: install PyMySQL from python_backend/requirements.txt")

    conn = pymysql.connect(**db_config(include_database=include_database))
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_one(sql, params=None):
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()


def fetch_all(sql, params=None):
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()


def execute(sql, params=None):
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.lastrowid


def execute_many(sql, items):
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, items)
            return cursor.rowcount


def healthcheck():
    try:
        row = fetch_one("SELECT 1 AS ok")
        return bool(row and row.get("ok") == 1), None
    except Exception as exc:
        return False, str(exc)
