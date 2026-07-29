import argparse
from datetime import datetime
from decimal import Decimal, InvalidOperation
import sys
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.config = {
            "dbname": os.getenv("DB_NAME", "expense_db"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
        }
    def get_connection(self):
        return psycopg2.connect(**self.config)


class ExpenseManager:
    def __init__(self):
        # 1. Veritabanı bağlantı yöneticisini ayağa kaldırıyoruz
        self.db = DatabaseManager()

    def add_expense(self, amount: Decimal, description: str):
        if not description.strip():
            print("Error: Description cannot be empty.")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        query = "INSERT INTO expenses (amount, description, date) VALUES (%s, %s, %s) RETURNING id;"

        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Doğru Sıra: amount, description, date
                    cursor.execute(query, (amount, description, today))
                    new_id = cursor.fetchone()[0]
                    conn.commit()

            print(f"Added new expense: {description} (${amount:.2f}) (ID: {new_id})")
        except Exception as e:
            print(f"Database error while adding expense: {e}")

    def update_expense(
        self,
        expense_id: int,
        amount: Decimal = None,
        description: str = None,
    ):
        if amount is None and description is None:
            print("Error: Nothing to update. Provide amount or description.")
            return

        # Dinamik SQL güncelleme sorgusu hazırlama
        updates = []
        params = []

        if amount is not None:
            if amount <= 0:
                print("Error: Amount must be greater than 0.")
                return
            updates.append("amount = %s")
            params.append(amount)

        if description is not None:
            if not description.strip():
                print("Error: Description cannot be empty.")
                return
            updates.append("description = %s")
            params.append(description)

        params.append(expense_id)
        query = f"UPDATE expenses SET {', '.join(updates)} WHERE id = %s;"

        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if cursor.rowcount == 0:
                        print(f"Expense with ID {expense_id} not found.")
                    else:
                        conn.commit()
                        print(f"Expense with ID {expense_id} updated successfully.")
        except Exception as e:
            print(f"Database error while updating expense: {e}")

    def delete_expense(self, expense_id: int):
        query = "DELETE FROM expenses WHERE id = %s;"

        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (expense_id,))
                    if cursor.rowcount == 0:
                        print(f"Expense with ID {expense_id} not found.")
                    else:
                        conn.commit()
                        print(f"🗑️ Expense with ID {expense_id} deleted successfully.")
        except Exception as e:
            print(f"Database error while deleting expense: {e}")

    def list_expenses(self):
        query = "SELECT id, date, description, amount FROM expenses ORDER BY id ASC;"

        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()

            if not rows:
                print("No expenses found.")
                return

            print(f"\n{'ID':<5} {'Date':<12} {'Description':<25} {'Amount'}")
            print("-" * 55)

            for row in rows:
                print(f"{row[0]:<5} {str(row[1]):<12} {row[2]:<25} ${row[3]:.2f}")
            print("-" * 55 + "\n")

        except Exception as e:
            print(f"Database error while listing expenses: {e}")

    def get_summary(self, month: int = None):
        if month is not None and not (1 <= month <= 12):
            print("Error: Month must be between 1 and 12.")
            return

        if month:
            query = "SELECT SUM(amount) FROM expenses WHERE EXTRACT(MONTH FROM date) = %s;"
            params = (month,)
        else:
            query = "SELECT SUM(amount) FROM expenses;"
            params = ()

        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchone()[0]
                    total = Decimal(str(result)) if result is not None else Decimal("0.00")

            if month:
                print(f"💰 Month {month} total expense: ${total:.2f}")
            else:
                print(f"💰 Total expense: ${total:.2f}")

        except Exception as e:
            print(f"Database error while getting summary: {e}")

    def show_welcome(self):
        line = "=" * 60
        welcome_text = f"""{line}
      Welcome to Expense Tracker (PostgreSQL Edition)
    {line}
    This application helps you manage your personal expenses via SQL database.

    Available commands:
      add       Add a new expense
      list      List all expenses
      summary   Show total or monthly summary
      update    Update an expense
      delete    Delete an expense

    Examples:
      python expense-tracker.py add --description "Coffee" --amount 75
      python expense-tracker.py list
      python expense-tracker.py summary --month 7
      python expense-tracker.py update --id 1 --amount 120
      python expense-tracker.py delete --id 1
    {line}"""
        print(welcome_text)


def main():
    if len(sys.argv) == 1:
        manager = ExpenseManager()
        manager.show_welcome()
        return

    parser = argparse.ArgumentParser(description="Expense Tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    add_parser = subparsers.add_parser("add", help="Add an expense")
    add_parser.add_argument("--description", required=True, help="Description of the expense")
    add_parser.add_argument("--amount", required=True, help="Amount")

    # list
    subparsers.add_parser("list", help="List all expenses")

    # summary
    summary_parser = subparsers.add_parser("summary", help="Show total expenses")
    summary_parser.add_argument("--month", type=int, help="Month number (1-12)")

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete an expense")
    delete_parser.add_argument("--id", type=int, required=True, help="Expense ID to delete")

    # update
    update_parser = subparsers.add_parser("update", help="Update an expense")
    update_parser.add_argument("--id", type=int, required=True, help="Expense ID to update")
    update_parser.add_argument("--amount", help="New amount")
    update_parser.add_argument("--description", help="New description")

    args = parser.parse_args()
    manager = ExpenseManager()

    try:
        if args.command == "add":
            amount_dec = Decimal(args.amount)
            if amount_dec <= 0:
                print("Error: The spending amount must be greater than 0.")
                return
            manager.add_expense(description=args.description, amount=amount_dec)

        elif args.command == "list":
            manager.list_expenses()

        elif args.command == "summary":
            manager.get_summary(args.month)

        elif args.command == "delete":
            manager.delete_expense(args.id)

        elif args.command == "update":
            amount_dec = Decimal(args.amount) if args.amount is not None else None
            manager.update_expense(
                expense_id=args.id,
                amount=amount_dec,
                description=args.description,
            )

    except InvalidOperation:
        print("ERROR: Invalid amount! Please enter a valid number.")


if __name__ == "__main__":
    main()
