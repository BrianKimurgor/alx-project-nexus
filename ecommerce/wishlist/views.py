from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Wishlist
from .serializers import WishlistSerializer, WishlistCreateSerializer
from cart.models import CartItem  # Import the Cart model from the cart app

class WishlistListView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return wishlist items for the authenticated user
        return Wishlist.objects.filter(user=self.request.user)

class WishlistCreateView(generics.CreateAPIView):
    serializer_class = WishlistCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically associate the wishlist item with the authenticated user
        serializer.save(user=self.request.user)

class WishlistDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only delete their own wishlist items
        return Wishlist.objects.filter(user=self.request.user)

class MoveToCartView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get the wishlist item for the authenticated user
        wishlist_item = Wishlist.objects.filter(user=request.user, id=kwargs['pk']).first()

        if wishlist_item:
            # Check if the product is already in the cart
            if not Cart.objects.filter(user=request.user, product=wishlist_item.product).exists():
                # Add the product to the cart
                Cart.objects.create(user=request.user, product=wishlist_item.product)
            
            # Remove the product from the wishlist
            wishlist_item.delete()
            return Response({'message': 'Product moved to cart'}, status=status.HTTP_200_OK)
        
        # If the wishlist item is not found, return an error
        return Response({'error': 'Wishlist item not found'}, status=status.HTTP_404_NOT_FOUND)