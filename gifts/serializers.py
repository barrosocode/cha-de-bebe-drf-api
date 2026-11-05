# Imports
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Gift, Tag, File

# Classes

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['uuid', 'name', 'description']
        read_only_fields = ['uuid']

class FileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ['uuid', 'image', 'image_url', 'alt', 'gift']

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class GiftSerializer(serializers.ModelSerializer):
    # Campo de entrada: aceita lista de strings (nomes de tags)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False,
        help_text="Lista de nomes de tags. Serão criadas automaticamente se não existirem."
    )

    # Campo de saída: retorna objetos Tag completos
    tags = TagSerializer(many=True, read_only=True)

    # Campo de saída: retorna files aninhados
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Gift
        fields = ['uuid', 'name', 'description', 'link', 'limit', 'tag_names', 'tags', 'files']

    def validate_limit(self, value):
        """Valida que o limit é maior que zero"""
        if value <= 0:
            raise serializers.ValidationError("O limite deve ser maior que zero")
        return value

    def create(self, validated_data):
        """Cria um gift e processa as tags automaticamente"""
        tag_names = validated_data.pop('tag_names', [])

        # Cria o gift
        gift = Gift.objects.create(**validated_data)

        # Processa cada tag: cria se não existir, depois adiciona ao gift
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name.strip().upper(),
                defaults={'description': ''}
            )
            gift.tags.add(tag)

        return gift

    def update(self, instance, validated_data):
        """Atualiza um gift e reprocessa as tags"""
        tag_names = validated_data.pop('tag_names', None)

        # Atualiza os campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Se tag_names foi enviado, reprocessa as tags
        if tag_names is not None:
            instance.tags.clear()  # Remove todas as tags atuais

            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name.strip().upper(),
                    defaults={'description': ''}
                )
                instance.tags.add(tag)

        return instance


class GiftPurchaseSerializer(serializers.Serializer):
    """Confirma a compra de um presente a partir do código do convite."""
    code = serializers.CharField(max_length=6)
    guest = serializers.UUIDField()
    message = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_code(self, value):
        code = value.strip().upper()
        if len(code) != 6:
            raise serializers.ValidationError('O código do convite deve ter 6 caracteres')
        return code


class GiftPurchaseGuestSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    name = serializers.CharField()


class GiftPurchaseResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    guest = GiftPurchaseGuestSerializer()
    gift_message = serializers.CharField()
    selected_at = serializers.DateTimeField()
