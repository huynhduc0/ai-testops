let codeEditors = {};
let autosaveTimeouts = {};

document.addEventListener("DOMContentLoaded", function() {
    initializeCodeEditors();
});

function initializeCodeEditors() {
    document.querySelectorAll('.code-editor').forEach(function(textarea) {
        if (!codeEditors[textarea.id]) {
            const editor = CodeMirror.fromTextArea(textarea, {
                lineNumbers: true,
                mode: "javascript",
                theme: "default",
                viewportMargin: Infinity
            });
            codeEditors[textarea.id] = editor;

            // Add blur event for autosave functionality
            editor.on('blur', function() {
                const testCaseId = textarea.id.split('-')[1];
                autosaveTestCaseContent(testCaseId, editor.getValue());
            });
        }
    });
}

function autosaveTestCaseContent(test_case_id, content) {
    $.ajax({
        url: "/api_test/api/testcase/save/" + test_case_id + "/",
        type: "POST",
        data: JSON.stringify({ content: content }),
        contentType: "application/json",
        success: function(data) {
            console.log("Autosave successful for test case " + test_case_id);
        },
        error: function(xhr) {
            console.error("Autosave failed for test case " + test_case_id);
        }
    });
}

function toggleDetails(test_case_id) {
    $('#test-case-' + test_case_id).collapse('toggle');
}

function generateTestCaseContent(test_case_id) {
    $('#loading').show();
    const additionalPrompt = $('#additional-prompt-' + test_case_id).val();
    $.ajax({
        url: "/api_test/api/generate_test_case_content/" + test_case_id + '?additional_prompt=' + encodeURIComponent(additionalPrompt),
        type: "GET",
        success: function(data) {
            $('#loading').hide();
            const editor = codeEditors['content-' + test_case_id];
            editor.setValue(data.content);
        },
        error: function(xhr) {
            $('#loading').hide();
            const errorMessage = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
            $('#error-message').text(errorMessage).show();
        }
    });
}

function executeTestCase(test_case_id) {
    $('#loading').show();
    $('#execute-button-' + test_case_id).prop('disabled', true);
    $('#execute-button-' + test_case_id).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Executing...');
    $.ajax({
        url: "/api_test/api/execute_test_case/" + test_case_id,
        type: "GET",
        success: function(data) {
            $('#loading').hide();
            $('#test-result-' + test_case_id).html('<pre>' + data.report + '</pre>');
            if (data.error_details) {
                $('#test-result-' + test_case_id).append('<pre class="text-warning">' + data.error_details + '</pre>');
            }
            if (data.summary) {
                $('#test-result-' + test_case_id).append('<pre class="text-warning">' + data.summary + '</pre>');
            }
            if (data.log) {
                $('#test-result-' + test_case_id).append('<pre class="text-info">' + data.log + '</pre>');
            }
            checkTestCaseStatus(test_case_id);
        },
        error: function(xhr) {
            $('#loading').hide();
            const errorMessage = xhr.responseText ? xhr.responseText : 'An error occurred';
            $('#test-result-' + test_case_id).html('<pre>' + errorMessage + '</pre>');
            $('#execute-button-' + test_case_id).prop('disabled', false);
            $('#execute-button-' + test_case_id).html('<i class="fas fa-play"></i> Execute Test');
        }
    });
}

function checkTestCaseStatus(test_case_id) {
    const intervalId = setInterval(function() {
        console.log('Checking test case status...');
        $.ajax({
            url: "/api_test/api/test_case/" + test_case_id,
            type: "GET",
            success: function(data) {
                console.log(data);
                if (data.test_case && data.test_case.test_result && (data.test_case.test_result.status === 'passed' || data.test_case.test_result.status === 'failed')) {
                    clearInterval(intervalId);
                    updateTestResult(test_case_id, data.test_case.test_result);
                    $('#execute-button-' + test_case_id).html('<i class="fas fa-check"></i> Executed').addClass('btn-success').removeClass('btn-primary');
                }
            },
            error: function(xhr) {
                console.error(xhr.responseText);
            }
        });
    }, 5000);
}

function updateTestResult(test_case_id, test_result) {
    const testResultDiv = $('#test-result-' + test_case_id);
    testResultDiv.html('<pre>' + test_result.log + '</pre>');
    if (test_result.status === 'failed') {
        testResultDiv.append('<pre class="text-warning">Test failed</pre>');
    } else if (test_result.status === 'passed') {
        testResultDiv.append('<pre class="text-success">Test passed</pre>');
    }
}

function viewTestResult(test_case_id) {
    $('#testResultModalBody').html('<div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div>');
    $('#testResultModal').modal('show');
    $.ajax({
        url: "/api_test/api/test_case/" + test_case_id,
        type: "GET",
        success: function(data) {
            if (data.test_case.test_result) {
                $('#testResultModalBody').html('<pre>' + data.test_case.test_result.log + '</pre>');
            } else {
                $('#testResultModalBody').html('<pre>No test result available.</pre>');
            }
        },
        error: function(xhr) {
            const errorMessage = xhr.responseText ? xhr.responseText : 'An error occurred';
            $('#testResultModalBody').html('<pre>' + errorMessage + '</pre>');
        }
    });
}
