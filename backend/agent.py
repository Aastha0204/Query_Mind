
from sqlalchemy import text

from database import engine
from sql_generator import generate_sql
from sql_validator import validate_sql


# Maximum number of records returned to the application
MAX_ROWS = 100


def run_agent(user_question):
    """
    Complete Natural Language to SQL workflow:

    1. Receive user's English question.
    2. Generate SQL using Groq.
    3. Validate SQL using SQLGlot.
    4. Execute SQL on MySQL.
    5. Return actual database results.
    """

    response = {
        "success": False,
        "question": user_question,
        "generated_sql": None,
        "validated_sql": None,
        "columns": [],
        "rows": [],
        "row_count": 0,
        "truncated": False,
        "error": None
    }

    try:
        # Step 1: Validate user input
        if not user_question or not user_question.strip():
            raise ValueError("Please enter a question.")

        # Step 2: Generate SQL using Groq
        generated_sql = generate_sql(user_question)

        response["generated_sql"] = generated_sql

        # Step 3: Validate generated SQL
        validated_sql = validate_sql(generated_sql)

        response["validated_sql"] = validated_sql

        # Step 4: Execute validated SQL on MySQL
        with engine.connect() as connection:

            result = connection.execute(
                text(validated_sql)
            )

            # Get column names
            response["columns"] = list(result.keys())

            # Fetch at most MAX_ROWS + 1 records
            records = result.mappings().fetchmany(MAX_ROWS + 1)

            # Check whether more records exist
            if len(records) > MAX_ROWS:
                response["truncated"] = True
                records = records[:MAX_ROWS]

            # Convert database rows into dictionaries
            response["rows"] = [
                dict(record) for record in records
            ]

            response["row_count"] = len(response["rows"])

        response["success"] = True

    except Exception as error:

        response["error"] = str(error)

    return response


if __name__ == "__main__":

    print("\n================================")
    print("NATURAL LANGUAGE TO SQL AGENT")
    print("================================")

    question = input("\nEnter your question: ")

    result = run_agent(question)

    print("\n========== GENERATED SQL ==========")
    print(result["generated_sql"])

    print("\n========== VALIDATED SQL ==========")
    print(result["validated_sql"])

    if result["success"]:

        print("\n========== QUERY EXECUTION ==========")
        print("Status: SUCCESS")

        print("\nColumns:")
        print(result["columns"])

        print("\nActual Database Results:")

        for row in result["rows"]:
            print(row)

        print("\nTotal rows returned:", result["row_count"])

        if result["truncated"]:
            print(f"Only the first {MAX_ROWS} rows are displayed.")

    else:

        print("\n========== QUERY FAILED ==========")
        print("Status: FAILED")
        print("Reason:", result["error"])
