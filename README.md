# Expense Tracker

A command-line expense tracking application developed with **Python** and **PostgreSQL**.
The project was initially built with JSON-based storage and later migrated to PostgreSQL in version 2.

## Features

* User registration and login
* Secure password hashing with **bcrypt**
* Add expenses
* List expenses
* Delete expenses
* Expense categorization
* Monthly expense summary
* PostgreSQL-based persistent storage

## Technologies

* Python 3
* PostgreSQL
* psycopg2-binary
* argparse

## Project Architecture

The application is designed with a simple layered architecture:

* **CLI Layer:** Parses terminal commands using `argparse`
* **Business Logic Layer:** Handles users and expenses with OOP principles
* **Data Layer:** Stores data in PostgreSQL

## Database Schema

### users

* `id`
* `username`
* `password_hash`

### expenses

* `id`
* `user_id`
* `description`
* `amount`
* `category`
* `date`

## Installation

### Clone the repository

```bash
git clone https://github.com/Venusist/Expense-Tracker.git
cd Expense-Tracker
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create a PostgreSQL database

Create a database and update the connection settings in the Python source file.

### Run the application

```bash
python expense-tracker.py
```

## Example Commands

```bash
python expense-tracker.py register --username ipek --password secret123
python expense-tracker.py login --username ipek --password secret123
python expense-tracker.py add --description "Coffee" --amount 85 --category Food
python expense-tracker.py list
python expense-tracker.py summary
```

## Security Notes

* Passwords are **never stored in plain text**.
* Passwords are salted and hashed with **bcrypt** before being stored in the database.

## Version History

* **v1.0:** JSON storage
* **v2.0:** PostgreSQL migration and secure authentication

## Author

**İpek Köse**
Computer Engineering Student
