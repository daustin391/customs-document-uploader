"""Form for document uploading web application."""

from django import forms


class DateInput(forms.DateInput):
    """Use type 'date' for input widget."""

    input_type = "date"


class TimeInput(forms.TimeInput):
    """Use type 'time' for input widget."""

    input_type = "time"


class UploadForm(forms.Form):
    """
    Form for uploading a document.

    This form has six fields:
    - userfile: a document of customs paperwork
    - trans_num: a 14-digit CBSA transaction number
    - ccd_num: a cargo control document number, 5-25 characters
    - port_of_entry: a 3-digit port of entry code
    - eta_date: an estimated date of arrival
    - eta_time: an estimated time of arrival
    """

    userfile = forms.FileField(
        required=False,
        label="Choose a file to upload, or drag-and-drop a file onto this box.",
        label_suffix="",
    )
    trans_num = forms.IntegerField(
        min_value=10**13,
        max_value=10**14 - 1,
        label="Trans#",
        widget=forms.TextInput,
        error_messages={
            "min_value": "Transaction must be 14 digits.",
            "max_value": "Transaction must be 14 digits.",
            "invalid": "Please enter a valid transaction number.",
        },
    )
    ccd_num = forms.CharField(min_length=5, max_length=25, label="CCD#")
    port_of_entry = forms.IntegerField(
        max_value=10**3 - 1,
        widget=forms.TextInput,
        error_messages={
            "invalid": "Please enter a valid port of entry.",
            "max_value": "Please enter a valid port of entry.",
        },
    )
    eta_date = forms.DateField(widget=DateInput, required=False)
    eta_time = forms.TimeField(widget=TimeInput, required=False)
