"""SQL tools the agent can call to inspect and query the NYC taxi database."""

import duckdb

from tools.sql.setup import DB_FILE

MAX_ROWS = 50


class SQLTools:
    """Read-only access to the `trips` table in the DuckDB taxi database."""

    def __init__(self, db_path: str = str(DB_FILE)):
        self.con = duckdb.connect(db_path, read_only=True)

    def get_schema(self) -> str:
        """Get the schema of the `trips` table.

        Returns:
            One line per column in the form `column_name: column_type`.
        """
        rows = self.con.execute("DESCRIBE trips").fetchall()
        return "\n".join(f"{name}: {col_type}" for name, col_type, *_ in rows)

    def run_sql(self, query: str) -> str:
        """Run a SQL query against the taxi database.

        Args:
            query: The SQL query to execute (DuckDB dialect).

        Returns:
            Column headers followed by up to 50 data rows, separated by ` | `.
            On failure, an error message the caller can use to fix the query.
        """
        try:
            cursor = self.con.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchmany(MAX_ROWS)
        except duckdb.Error as e:
            return f"SQL error: {e}"

        lines = [" | ".join(columns)]
        lines.extend(" | ".join(str(value) for value in row) for row in rows)
        return "\n".join(lines)
