let codeEditors = {};
let autosaveTimeouts = {};

document.addEventListener("DOMContentLoaded", function() {
    initializeCodeEditors();
});

// Initialize the testCases variable with the test cases data
let testCases = JSON.parse(document.getElementById('test-cases-data').textContent);

function initializeCodeEditors() {
    require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.30.1/min/vs' }});
    require(['vs/editor/editor.main'], function() {
        document.querySelectorAll('.code-editor').forEach(function(textarea) {
            if (!codeEditors[textarea.id]) {
                const editorContainer = document.createElement('div');
                editorContainer.style.height = '300px';
                textarea.parentNode.replaceChild(editorContainer, textarea);

                let content = '';
                try {
                    content = decodeURIComponent(JSON.parse('"' + textarea.getAttribute('data-content').replace(/\"/g, '\\"') + '"')).trim();
                } catch (e) {
                    console.error('Error decoding content:', e);
                }

                const editor = monaco.editor.create(editorContainer, {
                    value: content,
                    language: 'python',
                    theme: 'vs-dark',
                    automaticLayout: true
                });
                codeEditors[textarea.id] = editor;

                // Add blur event for autosave functionality
                editor.onDidBlurEditorText(function() {
                    const testCaseId = textarea.id.split('-')[1];
                    autosaveTestCaseContent(testCaseId, editor.getValue());
                    showToast(`Test case ${testCaseId} content autosaved`, 'info');
                });
            }
        });
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
    return $.ajax({
        url: "/api_test/api/generate_test_case_content/" + test_case_id + '?additional_prompt=' + encodeURIComponent(additionalPrompt),
        type: "GET",
        success: function(data) {
            $('#loading').hide();
            const editor = codeEditors['content-' + test_case_id];
            editor.setValue(data.content);
            addLogMessage(`Generated test case ${test_case_id}`, 'success');
            // toggleDetails(test_case_id); // Auto expand test case details
        },
        error: function(xhr) {
            $('#loading').hide();
            const errorMessage = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
            $('#error-message').text(errorMessage).show();
            addLogMessage(`Failed to generate test case ${test_case_id}: ${errorMessage}`, 'danger');
        }
    });
}

function executeTestCase(test_case_id) {
    $('#loading').show();
    $('#execute-button-' + test_case_id).prop('disabled', true);
    $('#execute-button-' + test_case_id).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Executing...');
    return $.ajax({
        url: "/api_test/api/execute_test_case/" + test_case_id,
        type: "GET",
        success: function(data) {
            $('#loading').hide();
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
            addLogMessage(`Executed test case ${test_case_id}`, 'success');
        },
        error: function(xhr) {
            $('#loading').hide();
            const errorMessage = xhr.responseText ? xhr.responseText : 'An error occurred';
            $('#test-result-' + test_case_id).html('<pre>' + errorMessage + '</pre>');
            $('#execute-button-' + test_case_id).prop('disabled', false);
            $('#execute-button-' + test_case_id).html('<i class="fas fa-play"></i> Execute Test');
            addLogMessage(`Failed to execute test case ${test_case_id}: ${errorMessage}`, 'danger');
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
                    $('#execute-button-' + test_case_id).prop('disabled', false);
                    if (data.test_case.test_result.status === 'failed') {
                        showToast(`Test case ${data.test_case.url} - id: ${test_case_id} failed`, 'warning');
                    } else {
                        showToast(`Test case ${data.test_case.url} - id: ${test_case_id} executed successfully`, 'success');
                    }
                    updateTestSummary();
                    reloadTestResult(test_case_id);
                    // toggleDetails(test_case_id);
                }
            },
            error: function(xhr) {
                console.error(xhr.responseText);
            }
        });
    }, 2000);
}

function updateTestSummary() {
    const testExecutionId = document.querySelector('[name="test_execution_id"]').value;
    $('#loading').show();
    $.ajax({
        url: "/api_test/api/update_test_summary/",
        type: "GET",
        data: { test_execution_id: testExecutionId },
        success: function(data) {
            $('#loading').hide();
            // Update the test summary UI with the new data
            $('#passed-count').text(data.passed_count);
            $('#failed-count').text(data.failed_count);
            $('#pending-count').text(data.pending_count);
            $('#unprocessed-count').text(data.unprocessed_count);
        },
        error: function(xhr) {
            $('#loading').hide();
            console.error("Failed to update test summary:", xhr.responseText);
        }
    });
}

function updateTestResult(test_case_id, test_result) {
    const testResultDiv = $('#test-result-' + test_case_id);
    const logContent = test_result.log;
    const shortLog = logContent.length > 200 ? logContent.substring(0, 200) + '...' : logContent;
    testResultDiv.html('<pre>' + shortLog + '</pre>');
    if (logContent.length > 200) {
        const expandButton = $('<button class="btn btn-link btn-sm">Show More</button>');
        expandButton.on('click', function() {
            testResultDiv.html('<pre>' + logContent + '</pre>');
            $(this).remove();
        });
        testResultDiv.append(expandButton);
    }
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

function reloadTestResult(test_case_id) {
    $('#loading').show();
    $.ajax({
        url: "/api_test/api/test_case/" + test_case_id,
        type: "GET",
        success: function(data) {
            $('#loading').hide();
            if (data.test_case.test_result) {
                updateTestResult(test_case_id, data.test_case.test_result);
                updateTestCaseCardColor(test_case_id, data.test_case.test_result.status); // Change card color based on result
                // showToast(`Test result for test case ${test_case_id} reloaded successfully`, 'success');
            } else {
                showToast(`No test result available for test case ${test_case_id}`, 'info');
            }
        },
        error: function(xhr) {
            $('#loading').hide();
            const errorMessage = xhr.responseText ? xhr.responseText : 'An error occurred';
            showToast(`Failed to reload test result for test case ${test_case_id}: ${errorMessage}`, 'danger');
        }
    });
}

function updateTestCaseCardColor(test_case_id, status) {
    const card = document.getElementById('test-case-' + test_case_id+'-card');
    card.classList.remove('border-light', 'border-success', 'bg-light-success', 'border-danger', 'bg-light-danger', 'border-warning', 'bg-light-warning');
    if (status === 'passed') {
        card.classList.add('border-success', 'bg-light-success');
    } else if (status === 'failed') {
        card.classList.add('border-danger', 'bg-light-danger');
    } else {
        card.classList.add('border-warning', 'bg-light-warning');
    }
}

function showToast(message, type = 'success') {
    const toastContainer = document.querySelector('.toast-container');
    console.log('Toast container:', toastContainer); // Debug log
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.role = 'alert';
    toast.ariaLive = 'assertive';
    toast.ariaAtomic = 'true';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    console.log('Showing toast:', toast); // Debug log
    bsToast.show();
    setTimeout(() => {
        bsToast.hide();
        toast.remove();
    }, 3000);
}

function resetProgressBar() {
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-bar').innerText = '0%';
    document.getElementById('progress-bar').setAttribute('aria-valuenow', 0);
}

function addLogMessage(message, type = 'info') {
    const logContainer = document.getElementById('log-container');
    const logMessage = document.createElement('div');
    logMessage.className = `log-message text-bg-${type}`;
    logMessage.innerHTML = `
        <div class="d-flex justify-content-between">
            <span>${message}</span>
            <span class="text-muted">${new Date().toLocaleTimeString()}</span>
        </div>
    `;
    logMessage.style.opacity = 0;
    logContainer.prepend(logMessage);

    setTimeout(() => {
        logMessage.style.opacity = 1;
    }, 10);
}

document.getElementById('generate-all-tests').addEventListener('click', async function() {
    resetProgressBar();
    const totalTestCases = testCases.length;
    let completedTestCases = 0;

    document.getElementById('progress-container').style.display = 'block';

    for (const testCase of testCases) {
        addLogMessage(`Requesting generation for test case ${testCase.id}`, 'secondary');
        await generateTestCaseContent(testCase.id);
        completedTestCases++;
        const progress = Math.round((completedTestCases / totalTestCases) * 100);
        document.getElementById('progress-bar').style.width = `${progress}%`;
        document.getElementById('progress-bar').innerText = `${progress}%`;
        document.getElementById('progress-bar').setAttribute('aria-valuenow', progress);
    }

    showToast('All test cases generated successfully', 'success');
});

document.getElementById('generate-missing-tests').addEventListener('click', async function() {
    resetProgressBar();
    const totalTestCases = testCases.length;
    let completedTestCases = 0;
    let missingTestCases = 0;

    document.getElementById('progress-container').style.display = 'block';

    for (const testCase of testCases) {
        const editor = codeEditors['content-' + testCase.id];
        if (!editor.getValue()) {
            missingTestCases++;
            addLogMessage(`Requesting generation for missing test case ${testCase.id}`, 'secondary');
            await generateTestCaseContent(testCase.id);
            completedTestCases++;
            const progress = Math.round((completedTestCases / totalTestCases) * 100);
            document.getElementById('progress-bar').style.width = `${progress}%`;
            document.getElementById('progress-bar').innerText = `${progress}%`;
            document.getElementById('progress-bar').setAttribute('aria-valuenow', progress);
        }
    }

    if (missingTestCases === 0) {
        document.getElementById('generate-missing-tests').disabled = true;
        showToast('No missing test cases to generate', 'info');
    } else {
        showToast('Missing test cases generated successfully', 'success');
    }
});

document.getElementById('run-all-tests').addEventListener('click', async function() {
    resetProgressBar();
    const totalTestCases = testCases.length;
    let completedTestCases = 0;

    document.getElementById('progress-container').style.display = 'block';

    for (const testCase of testCases) {
        try {
            addLogMessage(`Requesting execution for test case ${testCase.id}`, 'secondary');
            await executeTestCase(testCase.id);
            completedTestCases++;
            const progress = Math.round((completedTestCases / totalTestCases) * 100);
            document.getElementById('progress-bar').style.width = `${progress}%`;
            document.getElementById('progress-bar').innerText = `${progress}%`;
            document.getElementById('progress-bar').setAttribute('aria-valuenow', progress);
        } catch (error) {
            console.error('Error:', error);
        }
    }

    showToast('All tests executed successfully', 'success');
});

function reloadTestCaseSummary() {
    const testExecutionId = document.querySelector('[name="test_execution_id"]').value;
    $('#loading').show();
    $.ajax({
        url: "/api_test/api/update_test_summary/",
        type: "GET",
        data: { test_execution_id: testExecutionId },
        success: function(data) {
            $('#loading').hide();
            // Update the test summary UI with the new data
            $('#passed-count').text(data.passed_count);
            $('#failed-count').text(data.failed_count);
            $('#pending-count').text(data.pending_count);
            $('#unprocessed-count').text(data.unprocessed_count);
            showToast('Test case summary reloaded successfully', 'success');
        },
        error: function(xhr) {
            $('#loading').hide();
            const errorMessage = xhr.responseText ? xhr.responseText : 'An error occurred';
            showToast(`Failed to reload test case summary: ${errorMessage}`, 'danger');
        }
    });
}

function updateBaseUrl() {
    const baseUrl = document.getElementById('base-url').value;
    const testExecutionId = document.querySelector('[name="test_execution_id"]').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch("/api_test/update_base_url/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            base_url: baseUrl,
            test_execution_id: testExecutionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Base URL updated successfully');
        } else {
            alert('Failed to update Base URL: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the Base URL');
    });
}
