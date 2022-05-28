from django.urls import path
from .views import (AssignAgentView, LeadDeleteView, LeadDetailView, 
LeadListView, LeadCreateView, LeadUpdateView, 
CategoryListView, CategoryDetailView, LeadCategoryUpdateView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView, FeedbackCreateView, FeedbackListView, FeedbackNotifyView, FeedbackDeleteView)

app_name = "leads"

urlpatterns = [
    path('', LeadListView.as_view(), name='lead-list'),
    path('<int:pk>/update/', LeadUpdateView.as_view(), name = 'lead-update'),
    path('<int:pk>/delete/', LeadDeleteView.as_view(),name = 'lead-delete'),
    path('<int:pk>/', LeadDetailView.as_view(), name = 'lead-detail'),
    path('<int:pk>/assign-agent/',AssignAgentView.as_view(), name = 'assign-agent'),
    path('<int:pk>/category/',LeadCategoryUpdateView.as_view(), name = 'lead-category-update'),
    path('create/',LeadCreateView.as_view(), name = 'lead-create'),
    path('complaints/', FeedbackListView.as_view(), name='complaints'),
    path('feedback/', FeedbackCreateView.as_view(), name='feedback'),
    path('feedback/<int:pk>/notify', FeedbackNotifyView.as_view(), name='feedback-notify'),
    path('feedback/<int:pk>/delete', FeedbackDeleteView.as_view(), name='feedback-delete'),
    path('categories/',CategoryListView.as_view(), name = 'category-list'),
    path('categories/<int:pk>/',CategoryDetailView.as_view(), name = 'category-detail'),
    path('create-category/',CategoryCreateView.as_view(), name = 'category-create'),
    path('categories/<int:pk>/update',CategoryUpdateView.as_view(), name = 'category-update'),
    path('categories/<int:pk>/delete',CategoryDeleteView.as_view(), name = 'category-delete'),   
]