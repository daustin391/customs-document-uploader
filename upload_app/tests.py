"""
Unit tests for the document upload app.

This module contains tests to verify that the views and the MockAPIClient class work as
expected.
"""

from io import StringIO
from unittest.mock import patch
from datetime import datetime

from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from parameterized import parameterized

from .views import index
from .api_clients import MockAPIClient
from .forms import UploadForm


class TestViewFunctions(TestCase):
    @parameterized.expand(
        [
            (
                {
                    "trans_num": "1234567890",
                    "port_of_entry": "440",
                    "ccd_num": "1234567890",
                },
                r'^{"errors": {"trans_num": \[{"message": ".*", "code": "min_value"}]}}$',
            ),
            (
                {
                    "trans_num": "123456789000000",
                    "port_of_entry": "440",
                    "ccd_num": "1234567890",
                },
                r'^{"errors": {"trans_num": \[{"message": ".*", "code": "max_value"}]}}$',
            ),
            (
                {
                    "trans_num": "123467890abcd",
                    "port_of_entry": "440",
                    "ccd_num": "1234567890",
                },
                r'^{"errors": {"trans_num": \[{"message": ".*", "code": "invalid"}]}}$',
            ),
            (
                {
                    "trans_num": "10827900900900",
                    "port_of_entry": "44a",
                    "ccd_num": "1234567890",
                },
                r'^{"errors": {"port_of_entry": \[{"message": ".*", "code": "invalid"}]}}$',
            ),
            (
                {
                    "trans_num": "10827900900900",
                    "port_of_entry": "4444",
                    "ccd_num": "1234567890",
                },
                r'^{"errors": {"port_of_entry": \[{"message": ".*", "code": "max_value"}]}}$',
            ),
        ]
    )
    def test_invalid_form_returns_errors(self, form_dict, expected):
        """
        POST requests of invalid forms return the expected error messages.

        This test uses the parameterized library to run the same test with different
        parameters. Each parameter is a tuple containing a dictionary of form data
        where one field is invalid, and a regular expression that should match
        the error message returned by the view.
        """
        form_dict["userfile"] = StringIO("testing, testing, 1,2,3")
        request = RequestFactory().post("/", form_dict)

        response = index(request)

        self.assertRegex(response.content.decode(), expected)

    def test_valid_form_returns_success(self):
        """
        POST requests of valid forms make the expected API call.

        Verifies arguments sent from the view to make_api_call() match expected values.
        """
        form_dict = {
            "trans_num": "10827900900900",
            "port_of_entry": "440",
            "ccd_num": "1234567890",
            "userfile": StringIO("testing, testing, 1,2,3"),
        }
        request = RequestFactory().post("/", form_dict)

        with patch("upload_app.views.make_api_call") as mock_api_call:
            mock_api_call.return_value.status_code = 200
            response = index(request)

        self.assertNotIn("errors", response.content.decode())
        mock_api_call.assert_called_once()
        upload_form = mock_api_call.call_args[0][0]
        for key in ["trans_num", "port_of_entry"]:
            self.assertEqual(upload_form.cleaned_data[key], int(form_dict[key]))
        self.assertEqual(upload_form.cleaned_data["ccd_num"], form_dict["ccd_num"])
        self.assertEqual(
            upload_form.cleaned_data["userfile"].read(), b"testing, testing, 1,2,3"
        )

    def test_get_index_returns_form(self):
        """GET request returns a form with expected input fields."""
        request = RequestFactory().get("/")

        response = index(request)

        decoded_page = response.content.decode()
        for field in [
            "trans_num",
            "port_of_entry",
            "ccd_num",
            "userfile",
            "eta_date",
            "eta_time",
        ]:
            self.assertRegex(
                decoded_page, rf"""<\s*input[^>]*name\s*=\s*["']{field}["'].*?>"""
            )


class TestMockAPIClient(TestCase):
    def test_method_prepares_payload_correctly(self):
        """
        Client makes POST request with the expected payload when send_data() is called.

        Checks the arguments passed to the mock of requests.post() to verify that the
        payload is correct. File contents are not checked because requests.post()
        receives them as a stream that is closed after the call.
        """
        client = MockAPIClient("test")
        file = SimpleUploadedFile("test.txt", b"testing, testing, 1,2,3", "text/plain")
        form = UploadForm(
            {
                "trans_num": 10827900900900,
                "port_of_entry": 440,
                "ccd_num": "1234567890",
                "eta_date": datetime(2023, 1, 31).date(),
                "eta_time": datetime(2023, 1, 31, 12, 30).time(),
            },
            {
                "userfile": file,
            },
        )
        form.is_valid()

        with patch("requests.post") as mock_post:
            client.send_data(form)

        payload = mock_post.call_args.kwargs["data"]
        field_data = payload["field_data"].strip()
        self.assertEquals(payload["api_key"], "test")
        self.assertEquals(payload["workflow"], 101)
        self.assertEquals(field_data[:12], "<field_data>")
        self.assertEquals(field_data[-13:], "</field_data>")
        for name, value in (
            ("Transaction Number", form.cleaned_data["trans_num"]),
            ("Port of Entry", form.cleaned_data["port_of_entry"]),
            ("Cargo Control Number", form.cleaned_data["ccd_num"]),
            ("ETA Date", form.cleaned_data["eta_date"].strftime("%Y%m%d")),
            ("ETA Time", form.cleaned_data["eta_time"].strftime("%H%M")),
        ):
            self.assertRegex(
                field_data,
                rf"""<field[^>]*name\s*=\s*["']{name}["'].*?>{value}<\/field>""",
            )

        self.assertIn("userfile", mock_post.call_args.kwargs["files"])
