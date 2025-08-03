from rest_framework import serializers
from .models import Customer

class RegisterCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'monthly_income', 'phone_number', 'approved_limit']
        read_only_fields = ['customer_id', 'approved_limit']
