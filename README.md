# Customs Document Uploader

Hello! This is a web-based application that allows you to upload Canadian customs documents to an API. The app is based on a similar web form that I developed for a customs brokerage, but I have made several improvements to the design and functionality.

## Features

The Customs Document Uploader include the following features:

- A drag-and-drop interface for easy file uploads
- Automatic form field population based on filenames
- A user-friendly interface

## Technologies

This app is built with the following technologies:

- Python 3.10
- jQuery 3.6: used for automatic field population, AJAX requests, and resetting the form.
- Django 4.1: the web framework this application is built on. I made use of Django's form features for field validations.

## Installation and Usage

To install and run this application, you'll need to follow these steps:

### Running the Development Server

1. Clone the repository to your local machine using Git:

```
git clone https://github.com/daustin391/customs-document-uploader.git
```

2. Navigate to the project directory:

```
cd customs-document-uploader
```

3. Install the required dependencies using pip:

```
pip install -r requirements.txt
```

4. Run the Django development server:

```
python manage.py runserver
```

5. Open a web browser and navigate to http://localhost:8000/ to view the application.

### Using in Production

If you want to use this project in a production environment, please exercise caution. Follow these steps:

1. Deploy as you would any other Django application.
2. Create a subclass of `APIClient` base class provided in `upload_app/api_clients.py`. This subclass should implement the required send_data() method to send the form data to your API endpoint. Here is an example:

```
from upload_app.api_clients import APIClient

class MyAPIClient(APIClient):
    def send_data(self, form):
        # Your implementation to send data and file to the API endpoint
        pass
```

Use this subclass to manipulate data coming from the web form into whatever is expected by your API.

3. Include the fully qualified class name in your Django settings:
   `API_CLIENT = "some_module.MyAPIClient"`

4. Create an environment variable named `API_KEY` and set it to your API key.

5. Run the Django server and navigate to the upload page. You should now be able to upload documents and have the form data sent to your API endpoint.

### Running tests

This project includes a `tests.py` file that contains unit tests which check the values returned by the views and the POST request made by the `MockAPIClient` class. To run the tests:

```
python manage.py test
```

## Contributing

If you have any feedback or suggestions, please feel free to create an issue on the Github repository or email me at dave@daveaustin.xyz.

## Acknowledgments

I am thankful for the Django documentation, which was very helpful during the development of this application, especially the getCsrf() function of main.js, which has only minor changes from the code provided in the documentation on [Using CSRF protection with AJAX](https://docs.djangoproject.com/en/4.1/howto/csrf/#using-csrf-protection-with-ajax).
