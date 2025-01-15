import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

# Global variables
balance = 0  # Initialize balance to 0
transactions = []  # Initialize with no transactions
categories = ["Subscriptions", "Bills", "Food", "Entertainment", "Rent", "Transportation", "Other"]

# Database setup
def initialize_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        role TEXT DEFAULT 'user'
                     )''')
    conn.commit()
    conn.close()

# User credentials
USERNAME = "user"
PASSWORD = "password"

def update_balance_display():
    """Update the balance display on the main window."""
    balance_label.config(text=f"Balance: ${balance:.2f}")

def refresh_balance():
    """Refresh the balance and transaction display."""
    update_balance_display()
    update_transaction_table()
    messagebox.showinfo("Refresh", "Balance and transactions refreshed.")

def open_withdraw_window():
    """Open a pop-up window for withdrawals."""
    def submit_withdrawal():
        global balance
        try:
            amount = float(amount_entry.get())
            category = category_var.get()
            if amount > balance:
                messagebox.showerror("Error", "Insufficient balance!")
            else:
                balance -= amount
                transactions.append({
                    "category": category, "type": "Withdrawal", "amount": amount, "recurring": "N/A", "date": "1/11/25"
                })
                update_balance_display()
                update_transaction_table()
                withdraw_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount entered!")

    withdraw_window = tk.Toplevel(root)
    withdraw_window.title("Withdraw")
    tk.Label(withdraw_window, text="Enter withdrawal amount:").pack(pady=5)
    amount_entry = tk.Entry(withdraw_window)
    amount_entry.pack(pady=5)
    tk.Label(withdraw_window, text="Select category:").pack(pady=5)
    category_var = tk.StringVar(value=categories[0])
    category_menu = ttk.Combobox(withdraw_window, textvariable=category_var, values=categories)
    category_menu.pack(pady=5)
    tk.Button(withdraw_window, text="Submit", command=submit_withdrawal).pack(pady=5)

def open_deposit_window():
    """Open a pop-up window for deposits."""
    def submit_deposit():
        global balance
        try:
            amount = float(amount_entry.get())
            category = category_var.get()
            balance += amount
            transactions.append({
                "category": category, "type": "Deposit", "amount": amount, "recurring": "N/A", "date": "1/11/25"
            })
            update_balance_display()
            update_transaction_table()
            deposit_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount entered!")

    deposit_window = tk.Toplevel(root)
    deposit_window.title("Deposit")
    tk.Label(deposit_window, text="Enter deposit amount:").pack(pady=5)
    amount_entry = tk.Entry(deposit_window)
    amount_entry.pack(pady=5)
    tk.Label(deposit_window, text="Select category:").pack(pady=5)
    category_var = tk.StringVar(value=categories[0])
    category_menu = ttk.Combobox(deposit_window, textvariable=category_var, values=["Salary", "Disability", "Bonus"])
    category_menu.pack(pady=5)
    tk.Button(deposit_window, text="Submit", command=submit_deposit).pack(pady=5)

def open_edit_transaction_window():
    """Open a pop-up window to edit transactions."""
    def load_transaction_details(event):
        selected_index = transaction_listbox.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        transaction = transactions[index]

        amount_entry.delete(0, tk.END)
        amount_entry.insert(0, transaction["amount"])

        category_var.set(transaction["category"])
        recurring_var.set(transaction["recurring"])

    def save_transaction():
        selected_index = transaction_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No transaction selected to edit!")
            return

        index = selected_index[0]
        try:
            new_amount = float(amount_entry.get())
            new_category = category_var.get()
            new_recurring = recurring_var.get()

            transactions[index]["amount"] = new_amount
            transactions[index]["category"] = new_category
            transactions[index]["recurring"] = new_recurring

            update_transaction_table()
            edit_window.destroy()
            messagebox.showinfo("Success", "Transaction updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount entered!")

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Transaction")

    tk.Label(edit_window, text="Select a transaction to edit:").pack(pady=5)
    transaction_listbox = tk.Listbox(edit_window, width=50, height=10)
    transaction_listbox.pack(pady=5)

    for i, transaction in enumerate(transactions):
        transaction_listbox.insert(i, f"{transaction['type']} - {transaction['category']} - ${transaction['amount']:.2f}")

    transaction_listbox.bind("<<ListboxSelect>>", load_transaction_details)

    tk.Label(edit_window, text="Edit Amount:").pack(pady=5)
    amount_entry = tk.Entry(edit_window)
    amount_entry.pack(pady=5)

    tk.Label(edit_window, text="Edit Category:").pack(pady=5)
    category_var = tk.StringVar(value=categories[0])
    category_menu = ttk.Combobox(edit_window, textvariable=category_var, values=categories)
    category_menu.pack(pady=5)

    tk.Label(edit_window, text="Edit Recurring:").pack(pady=5)
    recurring_var = tk.StringVar(value="N/A")
    recurring_menu = ttk.Combobox(edit_window, textvariable=recurring_var, values=["N/A", "Weekly", "Bi-Weekly", "Monthly"])
    recurring_menu.pack(pady=5)

    tk.Button(edit_window, text="Save", command=save_transaction).pack(pady=5)

def update_transaction_table():
    """Refresh the transaction table with updated data."""
    for row in transaction_table.get_children():
        transaction_table.delete(row)

    for transaction in transactions:
        transaction_table.insert('', 'end', values=(
            transaction["type"],
            transaction["category"],
            f"${transaction['amount']:.2f}",
            transaction["recurring"],
            transaction["date"]
        ))

def show_instructions():
    messagebox.showinfo("Instructions", "By clicking on one of the buttons, a menu will pop up asking you specifics of your transaction depending on if it's a deposit, withdrawl, or even editing a transaction!.")

def open_admin_panel():
    """Open a window for user management (Admin only)."""
    def load_users():
        for row in user_table.get_children():
            user_table.delete(row)

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users")
        users = cursor.fetchall()
        conn.close()

        for user in users:
            user_table.insert('', 'end', values=user)

    admin_window = tk.Toplevel(root)
    admin_window.title("User Management")

    columns = ("Username", "Role")
    user_table = ttk.Treeview(admin_window, columns=columns, show="headings")
    for col in columns:
        user_table.heading(col, text=col)
        user_table.column(col, anchor="center")
    user_table.pack(pady=10)

    tk.Button(admin_window, text="Refresh", command=load_users).pack(pady=5)

    load_users()

def validate_login():
    username = username_entry.get()
    password = password_entry.get()
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        role = user[0]
        login_window.destroy()
        if role == "admin":
            show_main_window(admin=True)
        else:
            show_main_window()
    else:
        messagebox.showerror("Error", "Invalid username or password!")

def register_user():
    """Allow a new user to register."""
    def save_user():
        new_username = username_entry.get()
        new_password = password_entry.get()
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, new_password))
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully!")
            register_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")
        conn.close()

    register_window = tk.Toplevel(login_window)
    register_window.title("Register")
    register_window.geometry("500x300")

    tk.Label(register_window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(register_window)
    username_entry.pack(pady=5)

    tk.Label(register_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(register_window, show="*")
    password_entry.pack(pady=5)

    tk.Button(register_window, text="Register", command=save_user).pack(pady=10)

def login():
    """Handle the login process."""
    global login_window, username_entry, password_entry
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("500x300")

    tk.Label(login_window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    tk.Button(login_window, text="Login", command=validate_login).pack(pady=10)
    tk.Button(login_window, text="Register", command=register_user).pack(pady=10)

    login_window.mainloop()

def show_main_window(admin=False):
    """Display the main finance manager window."""
    global root, balance_label, transaction_table

    # Set initial size of the window (width x height)
    root = tk.Tk()
    root.title("Main page")
    root.geometry("1000x500")

    # Balance display
    balance_frame = tk.Frame(root)
    balance_frame.pack(pady=10)

    balance_label = tk.Label(balance_frame, text=f"Balance: ${balance:.2f}", font=("Arial", 16))
    balance_label.pack(side="left", padx=5)

    refresh_button = tk.Button(balance_frame, text="Refresh", command=refresh_balance)
    refresh_button.pack(side="left", padx=5)

    # Transaction table
    columns = ("Type", "Category", "Amount", "Recurring", "Date")
    transaction_table = ttk.Treeview(root, columns=columns, show="headings", height=15)
    for col in columns:
        transaction_table.heading(col, text=col)
        transaction_table.column(col, anchor="center")
    transaction_table.pack(pady=10)

    # Scrollbar for the transaction table
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=transaction_table.yview)
    transaction_table.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Withdraw", command=open_withdraw_window).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Deposit", command=open_deposit_window).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Edit Transaction", command=open_edit_transaction_window).grid(row=0, column=2, padx=5)

    if admin:
        tk.Button(root, text="Admin Panel", command=open_admin_panel).pack(pady=5)

    tk.Button(root, text="?", command=show_instructions).pack(pady=5)

    # Populate the transaction table with initial data
    update_transaction_table()

    root.mainloop()

# Initialize database
initialize_database()

# Start the program with the login window
login()
