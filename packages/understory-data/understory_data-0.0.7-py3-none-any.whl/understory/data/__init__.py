"""Data management in the understory."""

# TODO git repos, media, post history

import web

app = web.application(__name__, prefix="data", args={"table": r"\w+", "key": r"\w+"})


def get_tables():
    """Return a sorted list of tables in the SQLite database."""
    return sorted(web.tx.db.tables)


@app.control("")
class Data:
    """Data sources."""

    owner_only = ["get"]

    def get(self):
        """Return an index of data sources."""
        return app.view.index(get_tables())


@app.control("tables")
class SQLiteTables:
    """Interface to the SQLite database."""

    owner_only = ["get"]

    def get(self):
        """Return a list of tables."""
        return app.view.sqlite(get_tables())


@app.control("tables/{table}")
class SQLiteTable:
    """A table in the SQLite database."""

    owner_only = ["get"]

    def get(self, table):
        """Return a table's rows and columns."""
        return app.view.sqlite_table(table, web.tx.db.select(table))


@app.control(r"export")
class Export:
    """Export your data."""

    owner_only = ["get"]

    def get(self):
        """Return an exporter."""
        return "<button>Export</button>"


@app.control(r"export.bar")
class ExportArchive:
    """Export data in a modified Blog Archive Format."""

    owner_only = ["get"]

    def get(self):
        """Return a zip containing microformatted posts and media files."""
        web.header("Content-Type", "application/bar")
        return "{{return export archive in zip format}}"
