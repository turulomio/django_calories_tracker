"""
Django management command to export PostgreSQL database dumps.

This module provides a management command (`dumppostgres`) that executes `pg_dump`
directly against the configured default database. Dumping via `pg_dump` allows
efficient, stream-based backups with low memory/swap consumption compared to
Django's native `dumpdata` command for large datasets.

Database Restoration Instructions (Custom Format `c`)
------------------------------------------------------
To restore a backup file generated in custom format (`.dump`), use `pg_restore`:

```bash
# Basic restore:
pg_restore -U <db_user> -h <db_host> -p <db_port> -d <db_name> <filename>.dump

# Clean/drop existing objects before recreating them:
pg_restore -U <db_user> -h <db_host> -p <db_port> -d <db_name> --clean --if-exists <filename>.dump

# Parallel restore with multiple jobs (faster for large databases):
pg_restore -U <db_user> -h <db_host> -p <db_port> -d <db_name> -j 4 <filename>.dump

# If password is required:
PGPASSWORD="<password>" pg_restore -U <db_user> -h <db_host> -p <db_port> -d <db_name> <filename>.dump
```
"""

from datetime import datetime
import os
from subprocess import run

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    """
    Management command to dump the PostgreSQL database using `pg_dump`.

    Reads connection parameters (HOST, PORT, USER, NAME, PASSWORD) from Django's
    configured `default` database in `settings.DATABASES` and generates a timestamped
    backup file.

    See module docstring for instructions on restoring the generated backup files
    using `pg_restore` or `psql`.
    """

    help = 'Command to dump postgres database efficiently without consuming excessive memory/swap'

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Define command line arguments for the management command.

        Parameters
        ----------
        parser : CommandParser
            The argument parser instance to configure.
        """
        parser.add_argument(
            '--format',
            default='c',
            choices=['c', 'p', 't', 'd'],
            help='Dump format: c (custom compressed, default), p (plain sql), t (tar), d (directory)',
        )

    def handle(self, *args, **options) -> None:
        """
        Execute the PostgreSQL dump command.

        Reads the active database settings, constructs the target filename based on
        timestamp and format, sets up the authentication environment, and triggers
        the external `pg_dump` utility.

        Parameters
        ----------
        *args
            Positional arguments passed to the command.
        **options
            Named options passed to the command, including `format`.

        Raises
        ------
        subprocess.CalledProcessError
            If `pg_dump` command fails during execution.
        """
        # Generate timestamp for uniquely naming the dump file
        dt = datetime.now()
        dts = dt.strftime("%Y%m%d%H%M")

        # Retrieve default database connection credentials from Django settings
        db_settings = settings.DATABASES['default']
        db_user = db_settings.get('USER', '')
        db_host = db_settings.get('HOST', 'localhost')
        db_port = str(db_settings.get('PORT', '5432'))
        db_name = db_settings.get('NAME', '')
        db_password = db_settings.get('PASSWORD', '')
        dump_format = options.get('format', 'c')

        # Determine file extension based on selected dump format
        ext = 'dump' if dump_format == 'c' else 'sql'
        filename = f"{db_name}-{dts}.{ext}"

        # Setup environment variables to pass database password securely to pg_dump
        env = os.environ.copy()
        if db_password:
            env["PGPASSWORD"] = db_password

        # Construct pg_dump command arguments
        cmd = [
            "pg_dump",
            "-U", db_user,
            "-h", db_host,
            "--port", db_port,
            "-F", dump_format,
            "-f", filename,
            db_name,
        ]

        self.stdout.write(f"Dumping database '{db_name}' to '{filename}' with format '{dump_format}'...")

        # Run pg_dump synchronously; raises CalledProcessError if returncode != 0
        run(cmd, env=env, check=True)
        self.stdout.write(self.style.SUCCESS(f"Successfully dumped database to '{filename}'"))



