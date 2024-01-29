"""
My first application
"""
import os
from pathlib import Path, PurePath
from tempfile import mkdtemp

import locale
import toga
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

        self.main_window = toga.MainWindow(title=self.formal_name)
        cur = self.con.cursor()
        res = cur.execute("SELECT id, name FROM accounts ORDER BY Name")

        left_container = self.build_desktop_account_list(res)
        cur.close()

        trans_cur = self.con.cursor()
        trans_res = trans_cur.execute("SELECT id, amount, date, account_id, merchant, category, sub_category FROM transactions ORDER BY date")
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        right_container = self.build_desktop_transaction_list(trans_res)

        split = toga.SplitContainer(content=[left_container, right_container])

        self.main_window.content = split

        cmd1 = toga.Command(
            self.show_add_account_window,
            "Edit Accounts",
            tooltip="Edit Accounts",
            icon=toga.Icon.DEFAULT_ICON,
        )
        cmd2 = toga.Command(
            self.show_add_transaction_window,
            "Add Transaction",
            tooltip="Add New Transactions",
            icon=toga.Icon.DEFAULT_ICON,
        )
        cmd3 = toga.Command(
            self.switch_to_main_window,
            "Main Window",
            tooltip="Switch back to main window",
            icon=toga.Icon.DEFAULT_ICON,
        )
        self.main_window.toolbar.add(cmd1, cmd2, cmd3)

        self.main_window.show()


    async def switch_to_main_window(self, widget):
        print("Switching to main window")
        self.show_main_window

    
    async def show_main_window(self):
        print("Showing main window")
        self.main_window = toga.MainWindow(title=self.formal_name)
        cur = self.con.cursor()
        res = cur.execute("SELECT id, name FROM accounts ORDER BY Name")

        left_container = self.build_desktop_account_list(res)
        cur.close()

        trans_cur = self.con.cursor()
        trans_res = trans_cur.execute("SELECT id, amount, date, account_id, merchant, category, sub_category FROM transactions ORDER BY date")
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        right_container = self.build_desktop_transaction_list(trans_res)

        split = toga.SplitContainer(content=[left_container, right_container])

        self.main_window.content = split

        cmd1 = toga.Command(
            self.show_add_account_window,
            "Edit Accounts",
            tooltip="Edit Accounts",
            icon=toga.Icon.DEFAULT_ICON,
        )
        cmd2 = toga.Command(
            self.show_add_transaction_window,
            "Add Transaction",
            tooltip="Add New Transactions",
            icon=toga.Icon.DEFAULT_ICON,
        )
        cmd3 = toga.Command(
            self.show_main_window,
            "Main Window",
            tooltip="Switch back to main window",
            icon=toga.Icon.DEFAULT_ICON,
        )
        self.main_window.toolbar.add(cmd1, cmd2, cmd3)
        self.main_window.show()
    

    async def show_add_account_window(self, widget):
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
            ],
            accessor="name",
        )
        account_type_box.add(self.account_type_selection)

        add_account_box.add(account_name_box)
        add_account_box.add(account_type_box)
        add_account_button = toga.Button("Add Account", on_press=self.add_account_callback, style=Pack(width=200))
        add_account_box.add(add_account_button)
        self.main_window.content = add_account_box


    def add_account_callback(self, widget):
        trans_cur = self.con.cursor()
        sql_statement = f"INSERT INTO accounts (name, type) values (?, ?)"
        print(f"Running {sql_statement} with values {self.account_name_input.value} and {self.account_type_selection.value.name}")
        trans_cur.execute(sql_statement, (self.account_name_input.value, self.account_type_selection.value.name))
        self.con.commit()


    def show_add_transaction_window(self, widget):
        transaction_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        transaction_box.add(toga.Label("Add Transaction:"))
        transaction_date_box = toga.Box(style=Pack(direction=ROW, padding=5))
        transaction_date_box.add(toga.Label("Date:"))
        self.transaction_date_input = toga.TextInput(placeholder="Date", style=Pack(width=200))
        transaction_date_box.add(self.transaction_date_input)
        transaction_box.add(transaction_date_box)
        self.main_window.content = transaction_box


    async def action2(self, widget):
        if await self.main_window.question_dialog("Toga", "Is this cool or what?"):
            self.main_window.info_dialog("Happiness", "I know, right! :-)")
        else:
            self.main_window.info_dialog(
                "Shucks...", "Well aren't you a spoilsport... :-("
            )

    def build_desktop_account_list(self, accounts_res):
        rows = []
        for row in accounts_res.fetchall():
            data = {
                "subtitle": row[1],
            }
            rows.append(data)

        # display table
        left_container = toga.Box()
        table = toga.DetailedList(
            # headings=["ID", "Track Name"],
            data=rows,
            style=Pack(flex=1),
        )
        left_container.add(table)
        return left_container
    
    def build_desktop_transaction_list(self, transactions_res):
        trans_rows = []
        for trans_row in transactions_res.fetchall():
            trans_data = {
                "title": trans_row[4],
                "subtitle": locale.currency(trans_row[1], grouping=True),
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
	id INTEGER,
	name TEXT,
	"type" TEXT DEFAULT ('Checking') NOT NULL,
	CONSTRAINT ACCOUNTS_PK PRIMARY KEY (id)
);
                    ''')
        cur.execute('''
CREATE TABLE transactions (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	amount NUMERIC NOT NULL,
	date NUMERIC NOT NULL,
	"type" text DEFAULT ('debit') NOT NULL
, account_id INTEGER NOT NULL, merchant TEXT, category TEXT DEFAULT ('Uncategorized') NOT NULL, sub_category TEXT DEFAULT ('None') NOT NULL);
                          ''')
        cur.execute('''
INSERT INTO accounts (id,name,"type") VALUES
	 (1,'Checking','Checking'),
	 (2,'Savings','Savings');
                    ''')
        cur.execute('''
INSERT INTO transactions (amount,date,"type",account_id,merchant,category,sub_category) VALUES
	 (100.00,'2024-01-01','Credit',1,'Starting Balance','System Category','Starting Balance'),
	 (500.00,'2024-01-01','Credit',2,'Starting Balance','System Category','Starting Balance');
                    ''')
        new_connection.commit()
        print(f"Successfully created sqlite file {dest_path}")

    def button_handler(self, widget):
        print("button press")


def main():
    return SQLTest()
