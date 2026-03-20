from django.urls import path
from . import views

urlpatterns = [
    path('map/', views.map_view, name='map_view'),
    path('api/location/', views.get_cart_location, name='get_cart_location'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('api/update-location/', views.update_location_api, name='update_location_api'),
    path('list/', views.vendor_list, name='vendor_list'),
    path('menu/<int:cart_id>/', views.menu_view, name='menu_view'),
    path('order/<int:item_id>/', views.order_item, name='order_item'),
    path('register/', views.vendor_register, name='vendor_register'),
    path('manage-menu/', views.manage_menu, name='manage_menu'),
    path('settings/', views.cart_settings, name='cart_settings'),
    path('schedule/', views.manage_schedule, name='manage_schedule'),
    path('schedule/delete/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('start-party/<int:cart_id>/', views.start_party, name='start_party'),
    path('party/join/<uuid:lobby_code>/', views.join_party, name='join_party'),
    path('party/menu/<uuid:lobby_code>/', views.party_menu, name='party_menu'),
    path('party/add/<uuid:lobby_code>/<int:item_id>/', views.add_to_party, name='add_to_party'),
    path('party/remove/<uuid:lobby_code>/<int:item_id>/', views.remove_from_party, name='remove_from_party'),
    path('pay-bill/<str:lobby_code>/', views.pay_bill, name='pay_bill'),
    path('menu/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),
    path('menu/edit/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),
    path('cart/delete/', views.delete_cart, name='delete_cart'),
    path('pay-individual/<int:cart_id>/', views.pay_individual_bill, name='pay_individual_bill'),
    ]