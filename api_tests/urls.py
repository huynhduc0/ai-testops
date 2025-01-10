from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import save_test_case_content, parse_and_test, test_api_view, execute_tests, execute_test_case, generate_test_case_content, save_test_result, list_test_executions, test_execution_detail, test_case_detail_api, test_result_detail, update_base_url, update_test_summary

urlpatterns = [
    # Page Views
    path('', parse_and_test, name='parse_and_test'),
    path('test/', test_api_view, name='test_api'),
    path('test_executions/', list_test_executions, name='list_test_executions'),
    path('test_execution/<int:pk>/', test_execution_detail, name='test_execution_detail'),
    path('test_result/<int:test_result_id>/', test_result_detail, name='test_result_detail'),

    # API Views
    path('api/execute_tests/<int:execution_id>/', execute_tests, name='execute_tests'),
    path('api/execute_test_case/<int:test_case_id>/', execute_test_case, name='execute_test_case'),
    path('api/generate_test_case_content/<int:test_case_id>/', generate_test_case_content, name='generate_test_case_content'),
    path('api/save/<int:test_case_id>/', save_test_result, name='save_test_result'),
    path('api/testcase/save/<int:test_case_id>/', save_test_case_content, name='save_test_case_content'),
    path('api/test_case/<int:test_case_id>/', test_case_detail_api, name='test_case_detail_api'),
    path('update_base_url/', update_base_url, name='update_base_url'),
    path('api/update_test_summary/', update_test_summary, name='update_test_summary'),
]