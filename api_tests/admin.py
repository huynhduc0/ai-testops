# api_tests/admin.py
from django.contrib import admin
from .models import TestExecution, TestCase, TestResult

@admin.register(TestExecution)
class TestExecutionAdmin(admin.ModelAdmin):
    list_display = ('user', 'execute_info', 'report_pass_fail', 'created_at', 'updated_at')
    search_fields = ('user__username', 'execute_info', 'log')
    list_filter = ('report_pass_fail', 'created_at', 'updated_at')

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('test_execution', 'url', 'method', 'result', 'created_at', 'updated_at')
    search_fields = ('test_execution__execute_info', 'url', 'method', 'result')
    list_filter = ('created_at', 'updated_at')

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TestResult._meta.fields]
    search_fields = ('owner__username', 'status')
    list_filter = ('created_at',)