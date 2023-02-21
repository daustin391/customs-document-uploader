"""
Views for document uploading application.

GET requests render the index page template with an empty form.
The application makes AJAX POST requests which are handled by the index_post() view.

For demonstration purposes, a mock API endpoint is provided that returns the same
response regardless of the request payload.
"""

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .api_clients import make_api_call
from .forms import UploadForm


def index(request):
    """Forward GET and POST requests to appropriate handlers."""
    if request.method == "POST":
        return index_post(request)
    return index_get(request)


@require_GET
def index_get(request):
    """GET requests receive index page template with empty form."""
    form = UploadForm()
    return render(request, "upload_app/index.html", {"form": form})


@require_POST
def index_post(request):
    """
    Handle AJAX POST requests from upload form page.

    If the form passes validation, an API call is made and success message returned.
    Otherwise, the form errors are returned as JSON.
    """
    form = UploadForm(request.POST, request.FILES)
    if form.is_valid():
        response = make_api_call(form)
    else:
        response = None
    if response and response.status_code == 200:
        return HttpResponse(f"Success! {form.cleaned_data['trans_num']} uploaded.")
    return JsonResponse({"errors": form.errors.get_json_data()})


@require_POST
@csrf_exempt
def mock_api(request):
    """Mock API endpoint."""
    return HttpResponse("OK")
