from django.urls import path
from .views import parse_and_test, test_api_view, execute_tests, execute_test_case, generate_test_case_content

urlpatterns = [
    path('', parse_and_test, name='parse_and_test'),
    path('test/', test_api_view, name='test_api'),
    path('api_test/', parse_and_test, name='parse_and_test'),
    path('execute_tests/<int:execution_id>/', execute_tests, name='execute_tests'),
    path('execute_test_case/<int:test_case_id>/', execute_test_case, name='execute_test_case'),
    path('generate_test_case_content/<int:test_case_id>/', generate_test_case_content, name='generate_test_case_content'),
]