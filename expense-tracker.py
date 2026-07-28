from datetime import datetime
from decimal import Decimal ,InvalidOperation
import json
import argparse
import sys


class Expense:
    def __init__(self, id:int, amount:Decimal, description:str, date:str=None):
        self.id = id
        self.amount = amount
        self.description = description
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")
        #eğer dışarıdan tarih gelmezse bugünün tarihini yazar

    def to_dict(self): #verileri JSON'a yazılabilir bir dictionarya çevir
        return {
            "id": self.id,
            "amount": str(self.amount), #decimal nesneleri str çevir çünkü JSON
            "description": self.description,
            "date": self.date
        }

    def __str__(self):
        return f"{self.description} (${self.amount})"

class ExpenseManager:
    def __init__(self, file_path: str = "expenses.json"):
        self.file_path = file_path
        self.all_expenses = [] #expenseleri burda listede tutulur
        self._load_data() #sınıf başlayınca eski veriler de yüklenir

    def _load_data(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
                self.all_expenses = []

                for item in raw_data:
                    expense_object = Expense(
                        id=int(item["id"]),
                        amount=Decimal(item["amount"]),# Metni tekrar Decimal yaptık!
                        description=item["description"],
                        date=item["date"]
                    )
                    #Ürettiğimiz bu nesneyi listemize ekliyoruz
                    self.all_expenses.append(expense_object)

            print("Done: Old data loaded successfully.")

        except FileNotFoundError: #dosya henüz yoksa boş liste açıyoruz
            self.all_expenses = []
            print("Info: No existing data")

        except Exception as e:
            print(f"Error while loading data: {e}")


    def _save_data(self):
        try:
            savable_list = [
                expense.to_dict()
                for expense in self.all_expenses
            ]

            with open(self.file_path, "w",encoding="utf-8") as file:
                json.dump(savable_list, file, ensure_ascii=False, indent=4)

            print(f"Done: Data saved to {self.file_path}")

        except Exception as e:
            print(f"Error while saving data: {e}")


    def add_expense(self, amount: Decimal, description: str):
        if not description.strip():
            print("❌ Error: Description cannot be empty.")
            return

        next_id = (
            max(exp.id for exp in self.all_expenses) + 1
            if self.all_expenses
            else 1
        )

        new_expense = Expense(
            id=next_id,
            amount=amount,
            description=description
        )

        self.all_expenses.append(new_expense)
        self._save_data()

        print(f"Added new expense: {new_expense} (ID: {next_id})")

    def update_expense(
            self,
            expense_id: int,
            amount: Decimal = None,
            description: str = None
    ):
        for expense in self.all_expenses:
            if expense.id == expense_id:

                if amount is not None:
                    if amount <= 0:
                        print("Amount must be greater than 0.")
                        return
                    expense.amount = amount

                if description is not None:
                    if not description.strip():
                        print("Description cannot be empty.")
                        return
                    expense.description = description

                self._save_data()

                print(f"Expense with ID {expense_id} updated: {expense}")
                return

        print(f"Expense with ID {expense_id} not found.")

    def delete_expense(self, expense_id: int):
        for expense in self.all_expenses:
            if expense.id == expense_id:
                self.all_expenses.remove(expense)
                self._save_data()
                print(f"🗑️ Expense with ID {expense_id} deleted.")
                return

        print(f"Expense with ID {expense_id} not found.")

    def list_expenses(self):
        #harcama yok mu kontrolü
        if not self.all_expenses:
            print("No expenses found")
            return

            #5 karakter genişlik sola yasla, 12 karakter genişlik sola yasla...
        print(f"\n{'ID':<5} {'Date':<12} {'Description':<25} {'Amount'}")
        print("-" * 55)  # Araya düzgün bir çizgi çekelim

        for expense in self.all_expenses:
            print(
                f"{expense.id:<5} {expense.date:<12} "
                f"{expense.description:<25} ${expense.amount:.2f}"
            )
        print("-" * 55 + "\n")

    def get_summary(self, month: int = None):
        total = Decimal("0.00")

        if not self.all_expenses:
            print(f"Total expense: ${total:.2f}")
            return

        if month is not None:
            if not 1 <= month <= 12:
                print("Error: Month must be between 1 and 12.")
                return

            for expense in self.all_expenses:
                expense_month = int(expense.date.split("-")[1])

                if expense_month == month:
                    total += expense.amount

            print(f"Month {month} total expense: ${total:.2f}")

        else:
            for expense in self.all_expenses:
                total += expense.amount

            print(f"Total expense: ${total:.2f}")


    def show_welcome(self):
        line = "=" * 60
        welcome_text = f"""{line}
      Welcome to Expense Tracker
    {line}
    This application helps you manage your personal expenses.

    You can:
      • Add new expenses        • View monthly summaries
      • List all expenses       • Update existing expenses
      • View total expenses     • Delete expenses

    Available commands:
      add      Add a new expense
      list     List all expenses
      summary  Show total or monthly summary
      update   Update an expense
      delete   Delete an expense

    Examples:
      python expense-tracker.py add --description "Coffee" --amount 75
      python expense-tracker.py list
      python expense-tracker.py summary
      python expense-tracker.py summary --month 7
      python expense-tracker.py update --id 1 --amount 120
      python expense-tracker.py delete --id 1

    Run a command to get started! 
    {line}"""

        print(welcome_text)

def main():
    # Kullanıcı terminale parametre girmeden çalıştırmışsa Karşılama Ekranını göster
    if len(sys.argv) == 1:
        manager = ExpenseManager()
        manager.show_welcome()
        return

    parser = argparse.ArgumentParser(description="Expense Tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    add_parser = subparsers.add_parser("add", help="Add an expense")
    add_parser.add_argument("--description", required=True,
                            help="Description of the expense")
    add_parser.add_argument("--amount", required=True, help="Amount")

    # list
    subparsers.add_parser("list", help="List all expenses")

    # summary
    summary_parser = subparsers.add_parser(
        "summary",
        help="Show total expenses"
    )
    summary_parser.add_argument(
        "--month",
        type=int,
        help="Month number (1-12)"
    )
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete an expense"
    )
    delete_parser.add_argument(
        "--id",
        type=int,
        required=True,
        help="Expense ID to delete"
    )

    # update
    update_parser = subparsers.add_parser(
        "update",
        help="Update an expense"
    )
    update_parser.add_argument(
        "--id",
        type=int,
        required=True,
        help="Expense ID to update"
    )
    update_parser.add_argument(
        "--amount",
        help="New amount"
    )
    update_parser.add_argument(
        "--description",
        help="New description"
    )

    args = parser.parse_args()
    manager = ExpenseManager()

    try:
        if args.command == "add":
            # Gelen string veriyi sayıya (Decimal) çevirip doğruluyoruz
            amount_dec = Decimal(args.amount)

            if amount_dec <= 0:
                print("Error: The spending amount must be greater than 0.")
                return

            #Sınıfın metodunu terminalden gelen verilerle çağırıyoruz
            manager.add_expense(
                description=args.description,
                amount=amount_dec
            )

        elif args.command == "list":
            #Listeleme metodunu çağırıyoruz
            manager.list_expenses()

        elif args.command == "summary":
            manager.get_summary(args.month)

        elif args.command == "delete":
            manager.delete_expense(args.id)

        elif args.command == "update":
            amount_dec = None

            if args.amount is not None:
                amount_dec = Decimal(args.amount)

            manager.update_expense(
                expense_id=args.id,
                amount=amount_dec,
                description=args.description
            )

    except InvalidOperation:
        print("ERROR: Invalid amount! Please enter a number.")

if __name__ == "__main__":
    main()