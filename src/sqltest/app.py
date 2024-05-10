"""
My first application
"""
import os
import time
import datetime
from pathlib import Path, PurePath
from tempfile import mkdtemp

import locale
import toga
from toga.sources import ListSource
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import sqlite3
import urllib.request


class SQLTest(toga.App):
    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        # download db

        data_dir = self.app.paths.data
        if (not os.path.exists(data_dir)):
            print(f"Data dir {data_dir} does not exist, creating...")
            os.makedirs(data_dir)

        dest = Path(data_dir) / Path("budget")

        if not os.path.isfile(dest):
            self.create_empty_db(dest)


        print(f"Opening data from {dest}")

        #dest = Path("/var/folders/3q/f_7507pn20d28hc11nlvntb80000gn/T/tmpu4d43zf3/budget") 
        #expected_path = Path(mkdtemp()) / Path("Chinook_Sqlite.sqlite")
        #print(f"expected path is {expected_path}")
        #url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
        #response = urllib.request.urlopen(url)
        #dest.write_bytes(response.read())

        # query db
        self.con = None
        try:
            self.con = sqlite3.connect(dest)
            if self.con is None:
                print("FAILED TO CONNECT TO sqlite DB")
            else:
                print("Successfully connected to sqlite DB")
        except:
            print(f"Failed to connect to sqlite db with error")

        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.main_window = toga.MainWindow(title=self.formal_name)

        account_list_container = toga.Box()
        account_loading_label = toga.Label("Loading Account List...")
        account_list_container.add(account_loading_label)
        self.account_list_container = account_list_container

        transaction_container = toga.Box()
        transaction_loading_label = toga.Label("Loading Transaction List...")
        transaction_container.add(transaction_loading_label)
        self.transaction_container = transaction_container

        self.build_desktop_account_list()
        self.build_desktop_transaction_list()

        split = toga.SplitContainer(content=[self.account_list_container, self.transaction_container])

        self.main_window.content = split
        self.main_window.show()
        self.show_main_window()


    def switch_to_main_window(self, widget):
        print("Switching to main window")
        self.show_main_window()


    def build_desktop_navigation(self):
        accounts_cmd = toga.Command(
            self.show_add_account_window,
            "Accounts",
            tooltip="Accounts",
            icon=toga.Icon.DEFAULT_ICON,
        )
        categories_cmd = toga.Command(
            self.show_categories_window,
            "Categories",
            tooltip="Categories",
            icon=toga.Icon.DEFAULT_ICON,
        )
        transactions_cmd = toga.Command(
            self.show_add_transaction_window,
            "Transactions",
            tooltip="Transactions",
            icon=toga.Icon.DEFAULT_ICON,
        )
        main_window_cmd = toga.Command(
            self.switch_to_main_window,
            " @ Main Window",
            tooltip="Switch back to main window",
            icon=toga.Icon.DEFAULT_ICON,
        )
        self.main_window.toolbar.add(main_window_cmd, accounts_cmd, categories_cmd, transactions_cmd)

    
    def show_main_window(self):
        print("Showing main window")
        self.main_window = toga.MainWindow(title=self.formal_name)

        self.build_desktop_account_list()

        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.transaction_container = self.build_desktop_transaction_list()

        split = toga.SplitContainer(content=[self.account_list_container, self.transaction_container])

        self.main_window.content = split

        self.build_desktop_navigation()
        self.main_window.show()


    def get_budget_category_list(self):
        budget_cur = self.con.cursor()
        categories_res = budget_cur.execute("SELECT id, name FROM budget_categories ORDER BY Name")
        self.budget_category_rows = []
        self.budget_category_list = categories_res.fetchall()
        for row in self.budget_category_list:
            data = {
                "subtitle": row[1],
            }
            self.budget_category_rows.append(data)
        budget_cur.close()


    def get_spending_category_list(self):
        spending_cur = self.con.cursor()
        spending_categories_res = spending_cur.execute("SELECT id, name FROM spending_categories ORDER BY Name")
        self.spending_category_rows = []
        self.spending_category_list = spending_categories_res.fetchall()
        for row in self.spending_category_list:
            data = {
                "subtitle": row[1],
            }
            self.spending_category_rows.append(data)
        spending_cur.close()


    def show_add_account_window(self, widget):
        add_account_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        add_account_box.add(toga.Label("Add Account:"))
        account_name_box = toga.Box(style=Pack(direction=ROW, padding=5))
        account_name_box.add(toga.Label("Name:"))
        self.account_name_input = toga.TextInput(placeholder="Account name", style=Pack(width=200))
        account_name_box.add(self.account_name_input)
        account_type_box = toga.Box(style=Pack(direction=ROW, padding=5))
        account_type_box.add(toga.Label("Account type:"))
        self.account_type_selection = toga.Selection(
            items=[
                {"name": "Cash"},
                {"name": "Checking"},
                {"name": "Savings"},
                {"name": "Credit Card"}
            ],
            accessor="name",
        )
        account_type_box.add(self.account_type_selection)

        add_account_box.add(account_name_box)
        add_account_box.add(account_type_box)
        add_account_button = toga.Button("Add Account", on_press=self.add_account_callback, style=Pack(width=200))
        add_account_box.add(add_account_button)
        self.main_window.content = add_account_box


    def add_account_to_db(self):
        account_cur = self.con.cursor()
        sql_statement = f"INSERT INTO accounts (name, account_type) values (?, ?)"
        print(f"Running {sql_statement} with values {self.account_name_input.value} and {self.account_type_selection.value.name}")
        account_cur.execute(sql_statement, (self.account_name_input.value, self.account_type_selection.value.name))
        self.con.commit()


    def add_account_callback(self, widget):
        self.add_account_to_db()
        self.build_desktop_account_list()
        split = toga.SplitContainer(content=[self.account_list_container, self.transaction_container])

        self.main_window.content = split


    def show_categories_window(self, widget):
        self.get_budget_category_list()
        self.get_spending_category_list()
        categories_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        categories_box.add(toga.Label("Add Category:"))
        categories_box.add(toga.Label("Category Name:"))
        self.category_name_input = toga.TextInput(placeholder="Category name", style=Pack(width=200))
        categories_box.add(self.category_name_input)
        add_category_button = toga.Button("Add Category", on_press=self.add_category_callback, style=Pack(width=200))
        categories_box.add(add_category_button)
    
        categories_box.add(toga.Label("Add Spending Category:"))

        budget_list_options = ListSource(
            accessors=["name", "id"],
            data = []
        )

        for row in self.budget_category_list:
            data = {
                "name": row[1],
                "id": row[0]
            }
            budget_list_options.append(data)

        self.parent_budget_category_selection = toga.Selection(
            items=budget_list_options,
            accessor="name"
        )

        categories_box.add(toga.Label("Parent Budget Category:"))
        categories_box.add(self.parent_budget_category_selection)

        categories_box.add(toga.Label("Spending Category Name:"))
        self.spending_category_name_input = toga.TextInput(placeholder="Spending Category Name", style=Pack(width=300))
        categories_box.add(self.spending_category_name_input)
        add_spending_category_button = toga.Button("Add Spending Category", on_press=self.add_spending_category_callback, style=Pack(width=200))
        categories_box.add(add_spending_category_button)

        # display table
        budget_categories_table = toga.DetailedList(
            data=self.budget_category_rows,
            style=Pack(flex=1),
        )
        categories_box.add(budget_categories_table)

        # display table
        spending_categories_table = toga.DetailedList(
            data=self.spending_category_rows,
            style=Pack(flex=1),
        )
        categories_box.add(spending_categories_table)

        self.main_window.content = categories_box


    def add_category_callback(self, widget):
        print("Adding category:")
        categories_cur = self.con.cursor()
        sql_statement = "INSERT INTO budget_categories (name) values (?)"
        category_name = self.category_name_input.value
        print(f"Running SQL statement {sql_statement} with value {category_name}")
        #TODO: get this using proper id's. If you only pass in one arg and it's a string, Python/sqlite interpret this as a list of chars.
        # wrapping the variable in [] fixes this.
        # See: https://techoverflow.net/2019/10/14/how-to-fix-sqlite3-python-incorrect-number-of-bindings-supplied-the-current-statement-uses-1-supplied/
        categories_cur.execute(sql_statement, ([category_name]))
        self.con.commit()
        self.show_categories_window(widget)


    def add_spending_category_callback(self, widget):
        print("Adding spending category:")
        spending_categories_cur = self.con.cursor()
        sql_statement = "INSERT INTO spending_categories (name, parent_category_id) values (?, ?)"
        category_name = self.spending_category_name_input.value
        parent_category_id = self.parent_budget_category_selection.value.id
        print(f"Running SQL statement {sql_statement} with value {category_name} and {parent_category_id}")
        #TODO: get this using proper id's. If you only pass in one arg and it's a string, Python/sqlite interpret this as a list of chars.
        # wrapping the variable in [] fixes this.
        # See: https://techoverflow.net/2019/10/14/how-to-fix-sqlite3-python-incorrect-number-of-bindings-supplied-the-current-statement-uses-1-supplied/
        spending_categories_cur.execute(sql_statement, ([category_name, parent_category_id]))
        self.con.commit()
        self.show_categories_window(widget)


    def show_add_transaction_window(self, widget):
        transaction_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        transaction_box.add(toga.Label("Add Transaction:"))


        transaction_date_box = toga.Box(style=Pack(direction=ROW, padding=5))
        transaction_date_box.add(toga.Label("Date:"))
        self.transaction_date_input = toga.TextInput(style=Pack(width=200))
        transaction_date_box.add(self.transaction_date_input)

        self.transaction_amount_input = toga.NumberInput(style=Pack(width=200))
        transaction_amount_box = toga.Box(style=Pack(direction=ROW, padding=5))
        transaction_amount_box.add(toga.Label("Amount:"))
        transaction_amount_box.add(self.transaction_amount_input)

        self.transaction_merchant_input = toga.TextInput(placeholder="Merchant", style=Pack(width=200))
        transaction_merchant_box = toga.Box(style=Pack(direction=ROW, padding=5))
        transaction_merchant_box.add(toga.Label("Merchant:"))
        transaction_merchant_box.add(self.transaction_merchant_input)

        transaction_type_box = toga.Box(style=Pack(direction=ROW, padding=5))
        transaction_type_box.add(toga.Label("Type:"))
        self.transaction_type_selection = toga.Selection(
            items=[
                {"name": "Debit"},
                {"name": "Credit"},
                {"name": "Transfer"},
            ],
            accessor="name",
        )
        transaction_type_box.add(self.transaction_type_selection)

        account_list_options = ListSource(
            accessors=["name", "account_id"],
            data = []
        )

        for row in self.accounts_list:
            data = {
                "name": row[1],
                "account_id": row[0]
            }
            account_list_options.append(data)

        self.transaction_account_selection = toga.Selection(
            items=account_list_options,
            accessor="name"
        )

        transaction_account_box = toga.Box(style=Pack(direction=ROW, padding=5))
        transaction_account_box.add(toga.Label("Account:"))
        transaction_account_box.add(self.transaction_account_selection)

        self.transaction_merchant_input = toga.TextInput(placeholder="Merchant Name", style=Pack(width=200))
        transaction_merchant_box = toga.Box(style=Pack(direction=ROW, padding=5))
        transaction_merchant_box.add(toga.Label("Merchant:"))
        transaction_merchant_box.add(self.transaction_merchant_input)

        self.transaction_category_input = toga.TextInput(placeholder="Category", style=Pack(width=200))
        transaction_category_box = toga.Box(style=Pack(direction=ROW, padding=5))

        cur = self.con.cursor()
        categories_res = cur.execute("SELECT id, name FROM budget_categories ORDER BY Name")
        rows = []
        self.budget_category_list = categories_res.fetchall()


        budget_list_options = ListSource(
            accessors=["name", "budget_category_id"],
            data = []
        )

        for row in self.budget_category_list:
            data = {
                "name": row[1],
                "budget_category_id": row[0]
            }
            budget_list_options.append(data)

        self.transaction_budget_selection = toga.Selection(
            items=budget_list_options,
            accessor="name"
        )

        transaction_category_box.add(toga.Label("Budget Category:"))
        transaction_category_box.add(self.transaction_budget_selection)


        # self.transaction_sub_category_input = toga.TextInput(placeholder="Sub-Category", style=Pack(width=200))
        # transaction_sub_category_box = toga.Box(style=Pack(direction=ROW, padding=5))
        # transaction_sub_category_box.add(toga.Label("Sub-Category:"))
        # transaction_sub_category_box.add(self.transaction_sub_category_input)

        spending_list_options = ListSource(
            accessors=["name", "id"],
            data = []
        )
        self.get_spending_category_list()

        for row in self.spending_category_list:
            data = {
                "name": row[1],
                "id": row[0]
            }
            spending_list_options.append(data)

        self.transaction_spending_selection = toga.Selection(
            items=spending_list_options,
            accessor="name"
        )

        transaction_category_box.add(toga.Label("Spending Category:"))
        transaction_category_box.add(self.transaction_spending_selection)
        
        transaction_box.add(transaction_date_box,
                            transaction_amount_box,
                            transaction_merchant_box,
                            transaction_type_box,
                            transaction_account_box,
                            transaction_merchant_box,
                            transaction_category_box)
        
        add_transaction_button = toga.Button("Add Transaction", on_press=self.add_transaction_callback, style=Pack(width=200))
        transaction_box.add(add_transaction_button)
        self.main_window.content = transaction_box

    
    def add_transaction_callback(self, widget):
        print("Adding transaction:")
        trans_cur = self.con.cursor()
        sql_statement = f"INSERT INTO transactions (date, amount, account_id, merchant, budget_category_id, spending_category_id) values (?, ?, ?, ?, ?, ?)"

        transaction_datetime = time.mktime(datetime.datetime.strptime(self.transaction_date_input.value,
                                            "%m/%d/%Y").timetuple())

        print(f"Running {sql_statement} with values {transaction_datetime} and {int(self.transaction_amount_input.value)}")
        trans_cur.execute(sql_statement, (transaction_datetime, int(self.transaction_amount_input.value), int(self.transaction_account_selection.value.account_id), self.transaction_merchant_input.value, self.transaction_budget_selection.value.budget_category_id, self.transaction_spending_selection.value.id))
        self.con.commit()


    def build_desktop_account_list(self):
        cur = self.con.cursor()
        accounts_res = cur.execute("SELECT id, name FROM accounts ORDER BY Name")
        rows = []
        self.accounts_list = accounts_res.fetchall()
        for row in self.accounts_list:
            data = {
                "subtitle": row[1],
            }
            rows.append(data)
        cur.close()

        # display table
        left_container = toga.Box()
        table = toga.DetailedList(
            # headings=["ID", "Track Name"],
            data=rows,
            style=Pack(flex=1),
        )
        left_container.add(table)
        self.account_list_container = left_container
        
        
    
    def build_desktop_transaction_list(self):
        trans_cur = self.con.cursor()
        trans_res = trans_cur.execute("SELECT t.id, amount, datetime(date, 'unixepoch', 'localtime') as date, account_id, merchant, b.name, s.name FROM transactions t, budget_categories b, spending_categories s where t.budget_category_id = b.id and t.spending_category_id = s.id ORDER BY date")
        trans_rows = []
        for trans_row in trans_res.fetchall():
            trans_data = {
                "title": f"{trans_row[4]} {trans_row[5]} {trans_row[6]}",
                "subtitle": f"{locale.currency(trans_row[1], grouping=True)} Date: {trans_row[2]}",
            }
            # trans_data = {
            #     "id": trans_row[0],
            #     "amount": locale.currency(trans_row[1], grouping=True),
            #     "date": trans_row[2],
            #     "account_id": trans_row[3],
            #     "merchant": trans_row[4],
            #     "category": trans_row[5],
            #     "sub_category": trans_row[6],
            # }
            trans_rows.append(trans_data)

        print(f"Transactions rows: {trans_rows}")
        trans_cur.close()

        right_container = toga.ScrollContainer()
        transactions_list = toga.DetailedList(
            data=trans_rows
        )
        right_content = transactions_list
        # transaction_table = toga.Table(
        #     headings=["Id", "Amount", "Date", "Account Id", "Merchant", "Category", "Sub category"],
        #     data=trans_rows,
        #     style=Pack(flex=1)
        # )
        # right_content = transaction_table
        right_container.content = right_content

        # right_content = toga.Box(style=Pack(direction=COLUMN))
        # right_content.add(
        #     toga.Button(
        #         "Hello world!",
        #         on_press=self.button_handler,
        #         style=Pack(padding=20),
        #     )
        # )
        # right_container = toga.ScrollContainer()
        # right_container.content = right_content
        return right_container
    

    def create_empty_db(self, dest_path):
        print(f"Creating new sqlite file {dest_path}")
        new_connection = sqlite3.connect(dest_path)
        cur = new_connection.cursor()
        cur.execute('''
CREATE TABLE accounts (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	name TEXT,
	account_type TEXT DEFAULT ('Checking') NOT NULL
);
                    ''')
        cur.execute('''
CREATE TABLE budget_categories(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT);
                    ''')
        cur.execute('''
CREATE TABLE spending_categories(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    parent_category_id INTEGER NOT NULL,
    name TEXT,
    FOREIGN KEY(parent_category_id) REFERENCES budget_categories(id));
                    ''')
        cur.execute('''
INSERT INTO budget_categories (name) VALUES
                    ('System Category')
                    ,('Unknown Budget Category');
                    ''')
        cur.execute('''
INSERT INTO spending_categories(parent_category_id, name) VALUES
                    (1, 'Starting Balance')
                    ,(1, 'Unknown Spending Category');
                    ''')
        cur.execute('''
CREATE TABLE transactions (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	amount INTEGER NOT NULL,
	date INTEGER NOT NULL,
	transaction_type text DEFAULT ('debit') NOT NULL,
    account_id INTEGER NOT NULL,
    merchant TEXT,
    budget_category_id INTEGER,
    spending_category_id INTEGER);
                          ''')
        cur.execute('''
INSERT INTO accounts (name,account_type) VALUES
	 ('Checking','Checking'),
	 ('Savings','Savings');
                    ''')

        transaction_datetime = time.mktime(datetime.datetime.strptime("2024-04-01", "%Y-%m-%d").timetuple())
        cur.execute('''
INSERT INTO transactions (amount, date, transaction_type, account_id, merchant, budget_category_id, spending_category_id) VALUES
	 (10000, ?, 'Credit', 1, 'Starting Balance', 1, 1),
	 (50000, ?, 'Credit', 2, 'Starting Balance', 1, 1);
                    ''', (transaction_datetime, transaction_datetime))

        new_connection.commit()
        print(f"Successfully created sqlite file {dest_path}")

    def button_handler(self, widget):
        print("button press")


def main():
    return SQLTest()
