from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer, PaymentStatusSerializer
import uuid

class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Generate a unique transaction ID
        transaction_id = str(uuid.uuid4())
        serializer.save(transaction_id=transaction_id, status='PENDING')

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)