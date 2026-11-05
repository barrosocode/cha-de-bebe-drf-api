from rest_framework import serializers


class RecentReservationSerializer(serializers.Serializer):
    guest_name = serializers.CharField()
    gift_name = serializers.CharField()
    message = serializers.CharField(allow_blank=True)
    reserved_at = serializers.DateTimeField()


class DashboardSerializer(serializers.Serializer):
    total_invites = serializers.IntegerField()
    total_guests = serializers.IntegerField()
    confirmed_guests = serializers.IntegerField()
    confirmation_rate = serializers.FloatField()
    total_gifts = serializers.IntegerField()
    reserved_gifts = serializers.IntegerField()
    reservation_rate = serializers.FloatField()
    recent_reservations = RecentReservationSerializer(many=True)
