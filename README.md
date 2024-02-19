# Vault

![GitHub Release](https://img.shields.io/github/v/release/afesuazo/vault?include_prereleases)

A secure, user-friendly API for storing and retrieving encrypted sensitive data. 
All data is encrypted using public/private key encryption before being stored in a secure database. 
As privacy is a main concern, the server never stores the keys used to encrypt the data, so only the client can decrypt it.

The current version of the project is a work in progrss and handles simple text data such as passwords, API keys, etc. Future releases will include support for files, images, and other data types.

Key Features:

* **Data encryption**: Data is encrypted before being stored on the server.
* **Public/private key encryption**: Sets of keys are created and used to encrypt and decrypt data. Keys are kept by the user and never stored on the server.
* **User authentication**: Users can create accounts and log in to access their data with ease.
* **Data Association**: Data can be associated with particular websites, applications, or services.

## Getting Started

### Prerequisites
* Python 3.10
* Virtualenv (Recommended)

### (Optional) Create a virtual environment

```bash
# Create the venv
$ python3 -m venv env

# Activate it
$ source env/bin/activate
```

### Clone and Setup

```bash
# Clone the repository
$ git clone https://github.com/afesuazo/vault
$ cd vault

# Run the setup script to install packages
# Same as pip3 install -r requirements.txt
$ chmod +x ./setup.sh
$ ./setup.sh
```

### Configuration File

Create a config.py with the following content and replace the values with your own

```python
# config.py
SECRET_KEY = "SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DB_URL = "postgresql+asyncpg://<user>:<password>@<127.0.0.1>:<5432>/<db_name?"
REDIS_URL = "redis://<localhost>:<6379>"

TESTING = False
TEST_DB_URL = "postgresql+asyncpg://<test_user>:<test_password>@<127.0.0.1>:<5432>/<test_db_name>"
```

The file should be placed in the root directory of the project.

### Running the Program

```bash
$ chmod +x ./run.sh
$ ./run.sh
```

Or run it manually:

```bash
gunicorn -c gunicorn_conf.py app.main:app
```

Then visit http://localhost:4545 in your web browser. 
You should see the words "Vault Active!" printed to your screen.

You can also visit http://localhost:4545/docs to access the 
interactive API documentation interface created by FastAPI.

### Testing

The project uses pytest for testing. To run the tests, simply run the following command:

```bash
$ pytest
```


## Usage

API documentation will be available soon. In the meantime check the /docs endpoint for the interactive API documentation.

## Feedback

If you come across any bugs or have any ideas for improvements, 
please create an issue ticket in the repository.

## License

This project is licensed under the terms of the MIT license. See the LICENSE file for details.

## Planned Features and Improvements

- [ ] Move configuration to a .env file
- [ ] Loginless authentication
- [ ] Basic CLI
- [ ] Data Sharing
- [ ] Extend data types to include files, images, etc.