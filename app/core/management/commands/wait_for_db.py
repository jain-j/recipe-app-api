"""
Django management command wait_for_db
"""
import time

from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

class Command(BaseCommand):

    def handle(self, *args, **options):
        """This will be executed when wait_for_db command will be hit"""
        self.stdout.write('Waiting for database...')

        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except(Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting for 1 second')
                time.sleep(1)
        
        self.stdout.write('Database Available!')