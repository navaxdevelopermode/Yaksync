from django.urls import path
from . import views

app_name = 'animals'

urlpatterns = [
    path('', views.AnimalListView.as_view(), name='list'),
    path('analytics/', views.AnimalAnalyticsView.as_view(), name='analytics'),
    path('analytics/data/', views.AnimalAnalyticsDataView.as_view(), name='analytics_data'),
    path('create/', views.AnimalCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AnimalDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AnimalUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.AnimalDeleteView.as_view(), name='delete'),
]
