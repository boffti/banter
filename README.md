# Banter

![Build Status](https://img.shields.io/badge/build-passing-green)
![Python Verion](https://img.shields.io/badge/python-3.10-blue)

This project is being done as part of CSE 6324 at UT Arlington.

## Getting Started

### Installing Dependencies

#### Python 3.10

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by navigating to the project directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

## Running the server

From within the `project` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

### Running the App

To run the sample, make sure you have `python` and `pip` installed.

Run `pip install -r requirements.txt` to install the dependencies and run `python server.py`. 
The app will be served at [http://localhost:3000/](http://localhost:3000/).

<hr>

## Testing
To run the tests, run
```bash
python test.py
```

## Hosting
To host your app follow these steps - 
 - Create a `Procfile` in the project directory.
 - Inside the Procfile put the following
 ```text
 web: gunicorn app:app
 ```
 - Push the entire project to GIT
 - Go to Heroku and create a new app
 - Link your Github account on heroku
 - Link the project Github repo in the Heroku App Settings
 - Configure it for auto deployment
 - In Heroku App Setting, copy all the `.env` file contents.
 - Add a hobby dev Postgres server from Heroku addons

<hr>

## Author

#### Aneesh Melkot
#### Aditya Kulkarni
#### Anamika Karolla
#### Deepika Rajaneni
#### Sai Theja Bikumalla
#### Sahana Balakrishna
#### Vishwa Naik

