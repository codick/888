from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserRegSerializer, LogIn, ProductSerializer, CartSerializer, OrderSerializer
from .models import User, Cart, Order, Product


class IsAuthenticatedandnotadmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_superuser)


@api_view(['POST'])
@permission_classes([AllowAny])
def SignUpViewDef(request):
    serializer = UserRegSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "data": {
                "user_token": Token.objects.create(user=user).key
            }
        }, status=status.HTTP_201_CREATED)
    return Response({
        "error":
            {
                'code': 422,
                'message': "Validation Errors",
                "errors": serializer.errors
            }
    }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['POST'])
@permission_classes([AllowAny])
def LoginViewDef(request):
    serializer = LogIn(data=request.data)
    if serializer.is_valid():
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except:
            return Response({
                "error": {
                    "code": 401,
                    "message": "Authentication failed"
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"data":{
            "user_token": token.key
        }}, status=status.HTTP_200_OK)
    else:
        return Response({
            "error":
                {
                    "code": 402,
                    "message": "Validation Error",
                    "errors": serializer.errors
                }
        })


class LogOut(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.auth_token.delete()
        return Response({
            "data":
                {
                    "message": "logout"
                }
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def ProductsViewDef(request):
    queryset = Product.objects.all()
    serializer = ProductSerializer(queryset, many=True)
    return Response({
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def ProductAddViewDef(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        return Response({
            "data": {
                "id": data['id'],
                "message": "Product added"
            }
        }, status=status.HTTP_201_CREATED)
    return Response({
        "error":
            {
                "code": 402,
                "message": "Validation Error",
                "errors": serializer.errors
            }
    })


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def ProductPatchDeleteDef(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except:
        return Response({
            "error":
                {
                    "code": 404,
                    "message": "Not Found",

                }
        }, status=status.HTTP_404_NOT_FOUND)
    if request.method == "PATCH":
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "body":
                    serializer.data
            })
        else:
            return Response({
                "error": {
                    "code": 422,
                    "message": "Нарушение правил валидации",
                    "errors": serializer.errors
                }
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    elif request.method == 'DELETE':
        product.delete()
        return Response({
            "body": {
                "message":
                    "Product removed"
            }
        }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticatedandnotadmin])
def CartViewDef(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    data = serializer.data
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticatedandnotadmin])
def AddandRemoveToCartDef(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except:
        return Response({
            "error":
                {
                    "code": 404,
                    "message": "Not Found",

                }
        }, status=status.HTTP_404_NOT_FOUND)
    if request.method == "POST":
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.products.add(product)
        return Response({"body": {
            "message": "Product add to cart"
        }
        }, status=status.HTTP_201_CREATED)
    elif request.method == "DELETE":
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.products.remove(product)
        return Response({"body": {
            "message": "Item removed from cart"
        }
        }, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedandnotadmin])
def GetCreateOrderView(request):
    if request.method == "GET":
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        cart, _ = Cart.objects.get_or_create(user=request.user)
        order = Order.objects.create(user=request.user)
        total = 0
        for product in cart.products.all():
            total += product.price
            order.products.add(product)
        order.order_price = total
        order.save()
        cart.delete()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)