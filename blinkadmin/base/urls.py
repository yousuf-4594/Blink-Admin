from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name='home-page'),

    # Core URLs
    path('login/', views.loginPage, name='login-page'),
    path('logout/', views.logoutUser, name='logout'),
    path('orders/', views.ordersPage, name='orders-page'),
    path('customers/', views.customersPage, name='customers-page'),
    path('restaurants/', views.restaurantsPage, name='restaurants-page'),
    path('fooditems/', views.foodItemsPage, name='fooditems-page'),
    path('analytics/', views.analyticsPage, name='analytics-page'),

    path('restaurants/add-new-restaurant/', views.newRestaurantPage,
         name='new-restaurant-page'),
    path('restaurants/delete-restaurant/<str:id>/', views.deleteRestaurantPage,
         name='delete-restaurant-page'),
    path('restaurants/edit-restaurant/<str:id>/', views.editRestaurantPage,
         name='edit-restaurant-page'),

    path('customers/add-new-customer/', views.newCustomerPage, name='new-customer-page'),
    path('customers/delete-customer/<str:id>/', views.deleteCustomerPage, name='delete-customer-page'),
    path('customers/edit-customer/<str:id>/', views.editCustomerPage, name='edit-customer-page'),

    path('fooditems/add-new-food/', views.newFoodPage, name='new-food-page'),
    path('fooditems/delete-food/<str:id>', views.deleteFoodPage, name='delete-food-page'),
    

    path('fetch_views/', views.fetchViews, name='fetch-views'),

]
