"""
Take form data and send it to the API.

This module contains an abstract base class for API clients and a mock client, as well
as functions to send form data to an API and instantiate an API client.

APIClient subclasses can be swapped out by providing the fully qualified class name to
the API_CLIENT setting. API keys can be set in an environment variable named API_KEY.
The URL of the API to upload documents to can be set in the API_URL setting.
"""
from tempfile import TemporaryFile

import requests
from django.conf import settings
from django.utils.module_loading import import_string

from .forms import UploadForm


def make_api_call(form):
    """Pass form data to API client."""
    api_key = settings.API_KEY
    client = get_api_client(api_key)
    response = client.send_data(form)
    return response


def get_api_client(api_key):
    """Instantiate an API client."""
    client = import_string(settings.API_CLIENT)
    return client(api_key)


class APIClient:
    """Abstract base class for API client."""

    def __init__(self, api_key):
        self.api_key = api_key

    def send_data(self, form):
        """Send form data to API."""
        raise NotImplementedError


class MockAPIClient(APIClient):
    """
    Mock API client. Requests sent by this client are not intended for an actual API.

    In addition to the method for sending data, this client also has a method for
    preparing the data for a hypothetical XML API.
    """

    workflow = 101

    def prepare_data(self, form: UploadForm):
        """Takes form data and prepares it in XML format."""
        eta_date = form.cleaned_data["eta_date"]
        eta_time = form.cleaned_data["eta_time"]
        eta_date = eta_date.strftime("%Y%m%d") if eta_date else None
        eta_time = eta_time.strftime("%H%M") if eta_time else None

        payload = {}
        payload["api_key"] = self.api_key
        payload["workflow"] = self.workflow
        payload[
            "field_data"
        ] = f"""
        <field_data>
            <field name='Transaction Number'>{form.cleaned_data["trans_num"]}</field>
            <field name='Port of Entry'>{form.cleaned_data["port_of_entry"]}</field>
            <field name='Cargo Control Number'>{form.cleaned_data["ccd_num"]}</field>
            <field name='ETA Date'>{eta_date}</field>
            <field name='ETA Time'>{eta_time}</field>
          </field_data>"""

        return payload

    def send_data(self, form: UploadForm):
        """
        Send prepared data to API.

        The file is read in chunks from Django's UploadedFile object and written to a
        temporary file to prevent the entire file from being loaded into memory.
        """
        payload = self.prepare_data(form)
        with TemporaryFile() as f:
            for chunk in form.cleaned_data["userfile"].chunks():
                f.write(chunk)
            f.seek(0)
            response = requests.post(
                settings.API_URL, data=payload, files={"userfile": f}
            )
        return response
