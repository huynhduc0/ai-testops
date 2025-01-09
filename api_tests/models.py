from django.contrib.auth.models import User
from django.db import models

class TestExecution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    execute_info = models.TextField()
    report_pass_fail = models.BooleanField()
    log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    base_url = models.CharField(max_length=255, null=True, blank=True)  # Add this line

    def __str__(self):
        return f"TestExecution by {self.user.username} at {self.created_at}"

class TestCase(models.Model):
    test_execution = models.ForeignKey(TestExecution, on_delete=models.CASCADE, related_name='test_cases')
    url = models.CharField(max_length=255, null=True, blank=True)
    method = models.CharField(max_length=10, default="GET")
    body = models.TextField(null=True, blank=True)
    parameters = models.TextField(null=True, blank=True)
    content = models.TextField()
    result = models.CharField(max_length=255, null=True, blank=True)
    error_details = models.TextField(null=True, blank=True)
    request_response = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TestCase for {self.test_execution} at {self.created_at}"

class TestResult(models.Model):
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='test_results')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50)
    log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TestResult {self.id} - {self.status}"

class BaseUrl(models.Model):
    url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"BaseUrl {self.url}"