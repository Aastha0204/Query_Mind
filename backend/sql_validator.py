
import sqlglot
from sqlglot import exp


def validate_sql(sql_query):
    """
    Validate generated SQL before database execution.

    Allows only a single SELECT statement.
    Rejects INSERT, UPDATE, DELETE, DROP and other
    statements that can modify database data or structure.
    """

    # Check empty query
    if not sql_query or not sql_query.strip():
        raise ValueError("SQL query cannot be empty.")

    try:
        # Parse SQL using MySQL syntax
        parsed_queries = sqlglot.parse(
            sql_query,
            read="mysql"
        )

        # Reject empty or multiple statements
        if len(parsed_queries) != 1 or parsed_queries[0] is None:
            raise ValueError(
                "Only one SQL statement is allowed."
            )

        parsed_query = parsed_queries[0]

        # Allow only SELECT statements
        if not isinstance(parsed_query, exp.Select):
            raise ValueError(
                "Only SELECT queries are allowed."
            )

        # Block SELECT INTO, which can write query output
        if parsed_query.find(exp.Into):
            raise ValueError(
                "SELECT INTO statements are not allowed."
            )

        # Convert query into normalized MySQL SQL
        validated_query = parsed_query.sql(
            dialect="mysql"
        )

        return validated_query

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(
            f"Invalid SQL syntax: {error}"
        ) from error


if __name__ == "__main__":

    test_queries = [
        "SELECT first_name, last_name FROM students;",
        "DELETE FROM students;",
        "DROP TABLE students;",
        "UPDATE students SET first_name = 'Aastha';",
        "SELECT * FROM students; SELECT * FROM courses;"
    ]

    for query in test_queries:

        print("\nOriginal Query:")
        print(query)

        try:
            result = validate_sql(query)

            print("Status: ALLOWED")
            print("Validated SQL:", result)

        except ValueError as error:

            print("Status: BLOCKED")
            print("Reason:", error)
