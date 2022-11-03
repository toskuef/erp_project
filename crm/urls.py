from django.urls import path

from crm import views

app_name = 'crm'

urlpatterns = [
    path('customer/form_communication/', views.get_form_communication,
         name='get_form_communication'),
    path('customer/<int:pk>/', views.CustomerDetail.as_view(),
         name='crm_customer_detail'),
    path('customer/<int:pk>/edit/', views.customer_edit,
         name='crm_customer_edit'),
    path('customer/<int:pk>/address/edit/', views.address_edit,
         name='crm_address_edit'),
    path('customer-filter/', views.customer_list_filter, name='customer-filter'),
    path('order/<int:pk>/', views.OrderDetail.as_view(),
         name='crm_order_detail'),
    path('orders/product/<int:pk>/', views.ProductDetail.as_view(), name='crm_product_detail'),
    path('tasks/start/<int:pk>/<int:cust_pk>/<slug:object>/', views.start_task,
         name='start_task'),
    path('tasks/done/<int:cust_pk>/<int:pk>/<slug:object>/', views.done_task,
         name='done_task'),
    path('vk/', views.vk),
    path('lead/', views.LeadList.as_view(), name='crm_lead'),
    path('search/', views.Search.as_view(), name='search'),
    path('add-file/<int:pk>/<slug:object>/', views.add_file, name='add_file'),
    path('', views.CustomerList.as_view(), name='crm_customers'),

]
