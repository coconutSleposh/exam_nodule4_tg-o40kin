import os

from dotenv import load_dotenv

load_dotenv()


class DbCreds:
    @classmethod
    def get_creds(cls):
        """Read PostgreSQL connection settings from the project .env file."""
        keys = {
            "host": "DB_HOST",
            "port": "DB_PORT",
            "dbname": "DB_NAME",
            "user": "DB_USER",
            "password": "DB_PASSWORD",
        }
        creds = {field: os.getenv(env_name) for field, env_name in keys.items()}
        missing = [keys[field] for field, value in creds.items() if not value]
        if missing:
            raise RuntimeError(
                "Missing database settings in .env: " + ", ".join(missing)
            )

        creds["port"] = int(creds["port"])
        return creds
