
import os

from dotenv import load_dotenv
from groq import Groq

from schema import get_database_schema, format_schema_for_llm


# Load environment variables from .env
load_dotenv()

# Read Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Please add it to your .env file."
    )

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Model used for SQL generation
MODEL_NAME = "openai/gpt-oss-120b"


def generate_sql(user_question):
    """
    Convert a natural language question into a MySQL query.
    """

    if not user_question or not user_question.strip():
        raise ValueError("Please enter a valid question.")

    # Get database schema
    database_schema = get_database_schema()

    # Convert schema into readable text
    formatted_schema = format_schema_for_llm(database_schema)

    # Instructions for the AI model
    system_prompt = f"""
    You are an expert MySQL query generator.

    Your task is to convert the user's natural language
    question into a valid MySQL SELECT query.

    DATABASE SCHEMA:
    {formatted_schema}

    RULES:
    1. Generate only MySQL-compatible SQL.
    2. Generate only SELECT queries.
    3. Never generate INSERT, UPDATE, DELETE, DROP,
       ALTER, CREATE or TRUNCATE statements.
    4. Use only tables and columns present in the schema.
    5. Use JOIN when data from multiple related tables is needed.
    6. Do not invent table names or column names.
    7. Return only the SQL query.
    8. Do not include Markdown code fences or explanations.
    """

    try:

        # Send question and instructions to Groq
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_question
                }
            ],
            temperature=0
        )

        # Extract generated SQL
        generated_sql = response.choices[0].message.content

        if not generated_sql:
            raise ValueError("The AI model returned an empty response.")

        return generated_sql.strip()

    except Exception as error:
        raise RuntimeError(
            f"SQL generation failed: {error}"
        ) from error


if __name__ == "__main__":

    question = "Show the names of all students"

    try:
        sql_query = generate_sql(question)

        print("\nUser Question:")
        print(question)

        print("\nGenerated SQL:")
        print(sql_query)

    except Exception as error:
        print("Error:", error)
