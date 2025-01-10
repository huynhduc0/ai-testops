from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .extraction import parse_swagger_from_url, get_base_url
from .test_generator import request_run_test_case, generate_report, generate_test_case
from .models import TestExecution, TestCase, TestResult, BaseUrl
from .generators.gemini import GeminiLLM
from .generators.llm_offline import OfflineLLM
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.serializers.json import DjangoJSONEncoder

# Page Views
@login_required
def parse_and_test(request):
    if request.method == 'POST':
        try:
            swagger_url = request.POST.get('swagger_url')
            swagger_data = parse_swagger_from_url(swagger_url)
            base_url = get_base_url(swagger_data)
            print(base_url)
            test_execution, created = TestExecution.objects.get_or_create(
                user=request.user,
                execute_info=f"Tested Swagger from {swagger_url} with base URL {base_url}",
                defaults={'report_pass_fail': False, 'log': ""}
            )
            
            test_cases = []
            for path, methods in swagger_data['paths'].items():
                for method, details in methods.items():
                    test_case, created = TestCase.objects.get_or_create(
                        test_execution=test_execution,
                        url=path,
                        method=method.upper(),
                        defaults={'body': details.get('requestBody', {}), 'parameters': details.get('parameters', []), 'content': ""}
                    )
                    test_cases.append({
                        'id': test_case.id,
                        'url': test_case.url,
                        'method': test_case.method,
                        'body': test_case.body,
                        'parameters': test_case.parameters,
                        'content': test_case.content
                    })
            
            return JsonResponse({'execution_id': test_execution.id, 'test_cases': test_cases})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'api_tests/test_form.html')

@login_required
def test_api_view(request):
    return render(request, 'api_tests/test_form.html')

@login_required
def list_test_executions(request):
    test_executions = TestExecution.objects.all()
    return render(request, 'api_tests/list_test_executions.html', {'test_executions': test_executions})

@login_required
def test_execution_detail(request, pk):
    test_execution = TestExecution.objects.get(pk=pk)
    passed_count = test_execution.test_cases.filter(test_results__status='passed').count()
    failed_count = test_execution.test_cases.filter(test_results__status='failed').count()
    pending_count = test_execution.test_cases.filter(test_results__status='pending').count()
    unprocessed_count = test_execution.test_cases.filter(test_results__isnull=True).count()
    test_cases = list(test_execution.test_cases.values('id', 'url', 'method', 'body', 'parameters', 'content'))
    return render(request, 'api_tests/test_execution_detail.html', {
        'test_execution': test_execution,
        'base_url': test_execution.base_url,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'pending_count': pending_count,
        'unprocessed_count': unprocessed_count,
        'test_cases': json.dumps(test_cases, cls=DjangoJSONEncoder)
    })

@login_required
def test_result_detail(request, test_result_id):
    test_result = TestResult.objects.get(id=test_result_id)
    return render(request, 'api_tests/test_result_detail.html', {'test_result': test_result})

# API Views
@login_required
def generate_test_case_content(request, test_case_id):
    try:
        llm = GeminiLLM("AIzaSyDey1NPVwZjxaj0F4k286NT4ra0hZNRFRo")
        test_case = TestCase.objects.get(id=test_case_id)
        additional_prompt = request.GET.get('additional_prompt', '')
        base_url = test_case.test_execution.base_url
        test_case = generate_test_case(llm, test_case, base_url, additional_prompt)
        return JsonResponse({'content': test_case.content})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def execute_test_case(request, test_case_id):
    try:
        test_case = TestCase.objects.get(id=test_case_id)
        test_case.status = 'requested'
        test_case.save()
        
        request_run_test_case(test_case_id, test_case.content)
        
        return JsonResponse({'error_details': test_case.error_details, 'request_response': test_case.request_response})
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def execute_tests(request, execution_id):
    try:
        test_execution = TestExecution.objects.get(id=execution_id)
        test_cases = test_execution.test_cases.all()
        results = []
        llm = GeminiLLM("AIzaSyDey1NPVwZjxaj0F4k286NT4ra0hZNRFRo")

        for test_case in test_cases:
            try:
                # Generate test case content
                base_url = test_execution.base_url
                test_case = generate_test_case(llm, test_case, base_url)
                
                # Trigger test case execution
                request_run_test_case(test_case.id, test_case.content)
                test_case.status = 'executed'
                test_case.save()
                results.append({
                    'test_case': test_case.id,
                    'status': 'executed',
                    'summary': 'Test executed successfully',
                    'log': ''
                })
            except Exception as e:
                results.append({
                    'test_case': test_case.id,
                    'status': 'failed',
                    'summary': str(e),
                    'log': ''
                })

        report = generate_report(results)
        test_execution.report_pass_fail = all(r['status'] == 'executed' for r in results)
        test_execution.log = report
        test_execution.save()

        return HttpResponse(report, content_type="text/plain")
    except Exception as e:
        return HttpResponse(str(e), status=400, content_type="text/plain")

@csrf_exempt
def save_test_result(request, test_case_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            test_case = TestCase.objects.get(id=test_case_id)
            test_result = TestResult.objects.create(
                test_case=test_case,
                status=data.get('status', 'failed'),
                log=data.get('log', '')
            )
            test_result.save()
            return JsonResponse({'message': 'Test case content saved successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def save_test_case_content(request, test_case_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            test_case = TestCase.objects.get(id=test_case_id)
            test_case.content = data.get('content', test_case.content)
            test_case.save()
            return JsonResponse({'message': 'Test case content saved successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def test_case_detail_api(request, test_case_id):
    try:
        test_case = TestCase.objects.get(id=test_case_id)
        test_result = TestResult.objects.filter(test_case=test_case).last()
        return JsonResponse({'test_case': {
            'id': test_case.id,
            'url': test_case.url,
            'method': test_case.method,
            'body': test_case.body,
            'parameters': test_case.parameters,
            'content': test_case.content,
            'result': test_case.result,
            'error_details': test_case.error_details,
            'request_response': test_case.request_response,
            'status': test_case.status,
            'created_at': test_case.created_at,
            'updated_at': test_case.updated_at,
            'test_result': {
                'id': test_result.id,
                'status': test_result.status,
                'log': test_result.log,
                'created_at': test_result.created_at
            } if test_result else None
        }})
    except TestCase.DoesNotExist:
        return JsonResponse({'error': 'Test case not found'}, status=404)

@login_required
def update_base_url(request):
    if request.method == 'POST':
        new_base_url = request.POST.get('base_url')
        test_execution_id = request.POST.get('test_execution_id')
        try:
            test_execution = TestExecution.objects.get(id=test_execution_id)
            test_execution.base_url = new_base_url
            test_execution.save()
            return JsonResponse({'success': True})
        except TestExecution.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'TestExecution not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def update_test_summary(request):
    test_execution = TestExecution.objects.get(id=request.GET.get('test_execution_id'))
    passed_count = test_execution.test_cases.filter(test_results__status='passed').count()
    failed_count = test_execution.test_cases.filter(test_results__status='failed').count()
    pending_count = test_execution.test_cases.filter(test_results__status='pending').count()
    unprocessed_count = test_execution.test_cases.filter(test_results__isnull=True).count()
    data = {
        'passed_count': passed_count,
        'failed_count': failed_count,
        'pending_count': pending_count,
        'unprocessed_count': unprocessed_count,
    }
    return JsonResponse(data)
