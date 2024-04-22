from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView
urlpatterns = [

    #    path('auth/',include('rest_framework.urls', namespace = 'rest_framework')),
        #  path('create/', UserListCreateAPIView.as_view(),name="User-List-Create"),
        #  path('', UserListView.as_view(), name="User"),
         path('create/', UserCreateView.as_view(), name="User-Create"),
        # path('', UserListCreateAPIView.as_view(), name='usuario-list-create'),
        #  path('<str:pk>/', UserRetrieveUpdateDestroyAPIView.as_view(), name='usuario-retrieve-update-destroy'),

]