# Invoice Management API

## Description

A FastAPI-based web application for managing invoices, sellers, and products. The project provides secure RESTful APIs for user registration, authentication, product management, and invoice creation. It uses SQLModel for ORM and JWT for authentication.

## Table of Contents

- [Installation](#installation)
- [Dummy Data and Tests](#tests)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yacin-h/InvoiceManagementApi.git
   cd invoice
   ```
2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run database migrations:

   ```
   alembic upgrade head
   ```

   **By default, it will create a SQLite file. If you want to connect to other SQL database systems, you need to configure the environment file. See [Configuration](#configuration).**

## Tests

To run the test suite, use [pytest](https://docs.pytest.org/):

```bash
python -m pytest
```

Make sure you have installed all development dependencies listed in `requirements.txt`. Tests are located in the `tests/` directory. Running the above command will automatically discover and execute all tests.

## Usage

- Start the server:
  ```
  uvicorn app.main:app --reload
  ```
- Access the API docs at `http://localhost:8000/docs`
- Use the provided endpoints to register sellers, manage products, and create invoices.

## Configuration

For deployment, you need to change a few things in the `.env` file.
In order to use any other SQL DBMS that SQLAlchemy supports, you need to change the `#Database configuration` part:

- `DB_DRIVER` = example: "postgresql+psycopg"
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USERNAME`
- `DB_PASSWORD`

### Generate Secret Keys

You also need to change `SECRET_KEY`. **Don't use the default one for deployment.**

You have to change it with a secret key. To generate secret keys, you can run the following command:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the content and use that as a secret key. Run the command again to generate another secure key.

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to the branch and open a pull request
