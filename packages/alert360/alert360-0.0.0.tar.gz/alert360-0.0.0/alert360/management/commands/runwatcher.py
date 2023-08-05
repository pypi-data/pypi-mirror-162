from django.core.management.base import BaseCommand, CommandError
from alert360.models import StateWatcher
import logging


logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Run all state watchers and perform any '\
        'pending actions if triggered'

    def add_arguments(self, parser):
        parser.add_argument(
            '-l',
            '--log',
            type=int,
            help='Logging level. (0-5, NOTSET-CRITICAL) default is 3'
        )

    def handle(self, *args, **options):
        log = options['log']
        if isinstance(log, int):
            log = log * 10
            logging.info("Setting log level to {0}".format(log))
            logging.getLogger('root').setLevel(log)
        logging.info("Starting StateWatcher")
        try:
            StateWatcher.start()
        except KeyboardInterrupt:
            logging.warning('Terminating StateWatcher')
