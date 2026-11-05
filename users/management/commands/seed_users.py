# Imports
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Cria usuários padrão para o sistema (papai e mamae)'

    def handle(self, *args, **kwargs):
        # Papai
        if not User.objects.filter(username='papai').exists():
            User.objects.create_user(
                username='papai',
                password='paissword24022027',
                first_name='Gabriel Barroso Faustino Gomes',
            )
            self.stdout.write(self.style.SUCCESS('Usuário papai criado com sucesso'))
        else:
            self.stdout.write(self.style.WARNING('Usuário papai já existe'))
        # Mamae
        if not User.objects.filter(username='mamae').exists():
            User.objects.create_user(
                username='mamae',
                password='mamaessword24022027',
                first_name='Beatriz de Oliveira Figueiredo Gomes',
            )
            self.stdout.write(self.style.SUCCESS('Usuário mamae criado com sucesso'))
        else:
            self.stdout.write(self.style.WARNING('Usuário mamae já existe'))
