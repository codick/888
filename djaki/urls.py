from . import views
from django.urls import path

urlpatterns = [
    path('login', views.LoginViewDef),
    path('signup', views.SignUpViewDef),
    path('products', views.ProductsViewDef),
    path('cart/<int:pk>', views.AddandRemoveToCartDef),
    path('cart', views.CartViewDef),
    path('order', views.GetCreateOrderView),
    path('logout', views.LogOut.as_view()),
    path('product', views.ProductAddViewDef),
    path('product/<int:pk>', views.ProductPatchDeleteDef)
]