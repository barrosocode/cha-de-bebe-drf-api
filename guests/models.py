import uuid

from django.db import models


class Guest(models.Model):
    AGE_CHOICES = [
        ('adult', 'Adult'),
        ('kid', 'Kid'),
    ]

    CATEGORY_CHOICES = [
        ('family', 'Family'),
        ('friend', 'Friend'),
        ('church', 'Church'),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    age = models.CharField(max_length=10, choices=AGE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    invite = models.ForeignKey(
        'invites.Invite',
        on_delete=models.CASCADE,
        related_name='guests'
    )
    gifts = models.ManyToManyField(
        'gifts.Gift',
        through='GiftSelection',
        related_name='guests'
    )

    class Meta:
        db_table = "guests"
        verbose_name_plural = "guests"

    def confirm_presence(self):
        """Confirma a presença do convidado"""
        self.confirmed = True
        self.save()

    def __str__(self):
        status = "✓" if self.confirmed else "✗"
        return f"{self.name} ({self.category}) {status}"


class GiftSelection(models.Model):
    """
    Tabela intermediária para o relacionamento Guest ↔ Gift.
    Guarda metadata sobre quando o presente foi escolhido e a mensagem deixada.
    """
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    gift = models.ForeignKey('gifts.Gift', on_delete=models.CASCADE)
    message = models.TextField(blank=True, default='')  # ← NOVO CAMPO
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gift_selections"

    def __str__(self):
        has_msg = " 💬" if self.message else ""
        return f"{self.guest.name} → {self.gift.name}{has_msg}"
