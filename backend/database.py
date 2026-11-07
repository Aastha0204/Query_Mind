import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL

# Load environment variables
load_dotenv()

# Read database credentials
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME")

# Check required settings
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    raise ValueError("Database credentials are missing in .env")

# Create database connection URL
connection_url = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

# Create database engine
engine = create_engine(connection_url)

# Test database connection
if __name__ == "__main__":
    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT DATABASE();")
            )

            print("Database connected successfully!")
            print("Connected database:", result.scalar())

    except Exception as error:
        print("Database connection failed!")
        print(error)

    finally:
        engine.dispose()