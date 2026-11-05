import uuid
import random
import string

from django.db import models


class Invite(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=6, unique=True, editable=False)

    class Meta:
        db_table = "invites"
        verbose_name_plural = "invites"

    def save(self, *args, **kwargs):
        # Gera o código apenas se ainda não existir
        if not self.code:
            self.code = self._generate_code()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_code():
        """Gera um código único de 6 caracteres alfanuméricos"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=6))
            # Garante unicidade (caso colida, tenta de novo)
            if not Invite.objects.filter(code=code).exists():
                return code

    def __str__(self):
        return f"{self.name} ({self.code})"
