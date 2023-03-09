# AT_project


This application parses a set of URLs for online stores that sell yarn, collects data on the availability and cost of goods, and helps to analyze the price difference on visual graphs.

* The application is under development and will be improved.

In order to start working with the application, you need to do the following steps:
1. create a virtual environment for a new project:
>>> python -m venv env

2. download project files or clone the repository into the space of a new virtual environment;

3. install the necessary packages for the project to work from the recoirements.txt file
>>> pip install -r requirements.txt

4. because it's not good practice to put some django project secret data, this data has been hidden in an environment variable.
Create a file ".env" in the root directory of the project and write down the values of the constants in it:
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'some secret key'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=True

* create database file
>>> python manage.py makemigrations
>>> python manage.py migrate

Now you can start the project :)

OS: Windows 11
python: 3.11.0
VSCode: 1.76.0