from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from subprocess import run
import os


class Command(BaseCommand):
    help = 'Command to dump postgres database efficiently without consuming excessive memory/swap'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            default='c',
            choices=['c', 'p', 't', 'd'],
            help='Dump format: c (custom compressed, default), p (plain sql), t (tar), d (directory)',
        )

    def handle(self, *args, **options):
        dt = datetime.now()
        dts = dt.strftime("%Y%m%d%H%M")
        db_settings = settings.DATABASES['default']
        db_user = db_settings.get('USER', '')
        db_host = db_settings.get('HOST', 'localhost')
        db_port = str(db_settings.get('PORT', '5432'))
        db_name = db_settings.get('NAME', '')
        db_password = db_settings.get('PASSWORD', '')
        dump_format = options.get('format', 'c')
        
        ext = 'dump' if dump_format == 'c' else 'sql'
        filename = f"{db_name}-{dts}.{ext}"

        env = os.environ.copy()
        if db_password:
            env["PGPASSWORD"] = db_password

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
        run(cmd, env=env, check=True)
        self.stdout.write(self.style.SUCCESS(f"Successfully dumped database to '{filename}'"))


