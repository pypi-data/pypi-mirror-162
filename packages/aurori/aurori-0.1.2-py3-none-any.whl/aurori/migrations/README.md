Generic single-database configuration.

To create a new revision in `versions`:

`alembic revision -m "name" --autogenerate --rev-id REV_ID`

Upgrade to a new revision:

`alembic upgrade REV_ID`

Stamp to an actual version (may be needed before upgrade or create a new revision):

`alembic stamp --purge REV_ID`