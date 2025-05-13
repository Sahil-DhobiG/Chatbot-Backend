# filepath: e:\DhobiG technical work - task\Chatbot\backend\chatbot_api\urls.py
from django.urls import path
from .views import ChatbotDataView
from .dynamic_data_view import DynamicDataView

urlpatterns = [
    path('chatbot-data/', ChatbotDataView.as_view(), name='chatbot-data'),
    path('dynamic-data/', DynamicDataView.as_view(), name='dynamic-data'),
]
