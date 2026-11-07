
from sqlalchemy import inspect
from database import engine


def get_database_schema():
    """
    Extract complete database schema information
    including tables, columns, primary keys and foreign keys.
    """

    inspector = inspect(engine)

    schema = {}

    # Get all table names
    tables = inspector.get_table_names()

    for table in tables:

        # Get all columns of the current table
        columns = inspector.get_columns(table)

        # Get primary key information
        primary_key_info = inspector.get_pk_constraint(table)
        primary_keys = primary_key_info.get("constrained_columns", [])

        # Get foreign key information
        foreign_keys = inspector.get_foreign_keys(table)

        foreign_key_map = {}

        for fk in foreign_keys:

            source_columns = fk.get("constrained_columns", [])
            target_columns = fk.get("referred_columns", [])
            target_table = fk.get("referred_table")

            for source_column, target_column in zip(
                source_columns, target_columns
            ):
                foreign_key_map[source_column] = {
                    "references_table": target_table,
                    "references_column": target_column
                }

        column_details = []

        for column in columns:

            column_name = column["name"]

            column_details.append({
                "column_name": column_name,
                "data_type": str(column["type"]),
                "nullable": column["nullable"],
                "primary_key": column_name in primary_keys,
                "foreign_key": foreign_key_map.get(column_name)
            })

        schema[table] = column_details

    return schema


def format_schema_for_llm(schema):
    """
    Convert schema information into readable text
    that can be provided to the AI model.
    """

    formatted_schema = []

    for table, columns in schema.items():

        formatted_schema.append(f"Table: {table}")

        for column in columns:

            details = (
                f"  - {column['column_name']} "
                f"({column['data_type']})"
            )

            if column["primary_key"]:
                details += " PRIMARY KEY"

            if column["foreign_key"]:
                fk = column["foreign_key"]

                details += (
                    f" FOREIGN KEY REFERENCES "
                    f"{fk['references_table']}"
                    f"({fk['references_column']})"
                )

            if column["nullable"]:
                details += " NULL"
            else:
                details += " NOT NULL"

            formatted_schema.append(details)

        formatted_schema.append("")

    return "\n".join(formatted_schema)


if __name__ == "__main__":

    try:
        database_schema = get_database_schema()

        print("\n========== DATABASE SCHEMA ==========\n")

        print(format_schema_for_llm(database_schema))

        print("\n========== SCHEMA EXTRACTION SUCCESSFUL ==========\n")

    except Exception as error:
        print("Schema extraction failed!")
        print("Error:", error)
