from django.core.management.base import BaseCommand, CommandError
from ip_tracking.models import BlockedIP
import ipaddress


class Command(BaseCommand):
    help = 'Adds an IP address to the blacklist'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str,
                            help='The IP address to block')

    def handle(self, *args, **options):
        ip_to_block = options['ip_address']

        try:
            ipaddress.ip_address(ip_to_block)
        except ValueError:
            raise CommandError(f'"{ip_to_block}" is not a valid IP address.')

        blocked_ip, created = BlockedIP.objects.get_or_create(
            ip_address=ip_to_block)

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Successfully blocked IP address: {ip_to_block}'))
        else:
            self.stdout.write(self.style.WARNING(
                f'IP address {ip_to_block} is already blocked.'))
