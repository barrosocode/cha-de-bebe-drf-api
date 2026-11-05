# Imports
import uuid
from django.core.exceptions import ValidationError
from django.db import models

# Models

class Tag(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'tags'
        verbose_name_plural = 'tags'

    def save(self, *args, **kwargs):
        self.name = self.name.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Gift(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    link = models.URLField()
    limit = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, related_name='gifts')

    class Meta:
        db_table = 'gifts'
        verbose_name_plural = 'gifts'

    def clean(self):
        super().clean()

        if not self.pk:
            return

        purchased = self.giftselection_set.count()

        if self.limit < purchased:
            raise ValidationError({"limit": (
                        "O limite não pode ser menor que a quantidade "
                        f"de itens já comprados ({purchased})."
            )})

    def __str__(self):
        return self.name

class File(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    image = models.ImageField(upload_to='gifts/', blank=True, null=True)
    alt = models.CharField(max_length=255, blank=True)
    gift = models.ForeignKey(Gift, related_name='files', on_delete=models.CASCADE)

    class Meta:
        db_table = 'files'
        verbose_name_plural = 'files'

    def __str__(self):
        if self.image:
            return self.image.name
        return self.alt or str(self.uuid)

"""
uuid, name, description, link (url válido), limit (número inteiro positivo, não pode ser menor do que a quantidade de guests_gifts já cadastrados no sistema para aquele gift).

### files

#### fields

uuid, name (unique), alt

#### relationships

- belongsTo Gifts

"""
