from django.shortcuts import render, redirect
from django.http import HttpResponse
from .extraction import parse_swagger_from_url
from .test_generator import generate_test_cases, run_test_cases, generate_report
from .models import TestExecution, TestCase
from .generators.gemini import GeminiLLM
from .generators.llm_offline import OfflineLLM

def parse_and_test(request):
    swagger_url = request.GET.get('url')
    swagger_data = parse_swagger_from_url(swagger_url)
    llm = GeminiLLM("AIzaSyDey1NPVwZjxaj0F4k286NT4ra0hZNRFRo")  # Use OfflineLLM by default
    test_cases = generate_test_cases(llm, swagger_data)
    
    test_execution = TestExecution.objects.create(
        user=request.user,
        execute_info=f"Tested Swagger from {swagger_url}",
        report_pass_fail=False,
        log=""
    )
    
    for test_case in test_cases:
        TestCase.objects.create(
            test_execution=test_execution,
            url=test_case['url'],
            method=test_case['method'],
            body=test_case['body'],
            parameters=test_case['parameters'],
            content=test_case['content']
        )
    
    return render(request, 'api_tests/test_form.html', {'test_cases': test_execution.test_cases.all()})

def execute_test_case(request, test_case_id):
    test_case = TestCase.objects.get(id=test_case_id)
    result = run_test_cases([test_case.content])[0]
    report = generate_report([result])
    
    test_case.result = result[1]
    test_case.error_details = result[1] if "Failed" in result[1] else None
    test_case.request_response = None  # You can add logic to capture request/response if needed
    test_case.save()
    
    return HttpResponse(report, content_type="text/plain")

def execute_tests(request, execution_id):
    test_execution = TestExecution.objects.get(id=execution_id)
    test_cases = test_execution.test_cases.all()
    results = run_test_cases([tc.content for tc in test_cases])
    report = generate_report(results)
    
    test_execution.report_pass_fail = all(r[1] == "Passed" for r in results)
    test_execution.log = report
    test_execution.save()
    
    for test_case, result in zip(test_cases, results):
        error_details = result[1] if "Failed" in result[1] else None
        request_response = None  # You can add logic to capture request/response if needed
        
        test_case.result = result[1]
        test_case.error_details = error_details
        test_case.request_response = request_response
        test_case.save()
    
    return HttpResponse(report, content_type="text/plain")

def test_api_view(request):
    if request.method == 'POST':
        swagger_url = request.POST.get('swagger_url')
        swagger_data = parse_swagger_from_url(swagger_url)
        llm = GeminiLLM(api_key="your-gemini-api-key")
        test_cases = generate_test_cases(llm, swagger_data)
        results = run_test_cases(test_cases)
        report = generate_report(results)
        return render(request, 'api_tests/test_form.html', {'report': report})
    return render(request, 'api_tests/test_form.html')
