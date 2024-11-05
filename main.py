import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("1000x700")
        
        # Configure colors
        self.colors = {
            'primary': '#2c3e50',    # Dark blue-gray
            'secondary': '#3498db',   # Bright blue
            'accent': '#e74c3c',     # Red
            'background': '#ecf0f1',  # Light gray
            'text': '#2c3e50'        # Dark blue-gray
        }
        
        # Set window background
        self.root.configure(bg=self.colors['background'])
        
        # Configure style with colors
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", 
                            font=("Helvetica", 24, "bold"), 
                            foreground=self.colors['primary'])
        self.style.configure("Header.TLabel", 
                            font=("Helvetica", 12, "bold"), 
                            foreground=self.colors['primary'])
        self.style.configure("Custom.TButton", 
                            font=("Helvetica", 10), 
                            padding=5)
        
        # Configure frame styles
        self.style.configure("Card.TLabelframe", 
                            background=self.colors['background'])
        self.style.configure("Card.TLabelframe.Label", 
                            font=("Helvetica", 11, "bold"),
                            foreground=self.colors['primary'])
        
        # Main container with padding
        self.main_container = ttk.Frame(root, padding="20", style="Card.TLabelframe")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(self.main_container, text="Personal Expense Tracker", style="Title.TLabel").pack(pady=(0, 20))
        
        # Initialize database
        self.init_database()
        
        # Create main frames with better organization
        self.input_frame = ttk.LabelFrame(self.main_container, text="Add New Expense", padding="15")
        self.input_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.summary_frame = ttk.LabelFrame(self.main_container, text="Expense Summary", padding="15")
        self.summary_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add footer frame
        self.footer_frame = ttk.Frame(self.main_container)
        self.footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Configure footer style
        self.style.configure("Footer.TLabel",
                            font=("Helvetica", 9),
                            foreground=self.colors['primary'])
        
        # Add footer text
        footer_text = "© 2024 KEVIN | All rights reserved"
        footer_label = ttk.Label(self.footer_frame, 
                                text=footer_text,
                                style="Footer.TLabel",
                                anchor="center")
        footer_label.pack(fill=tk.X)
        
        self.setup_input_fields()
        self.setup_summary_section()
        self.update_summary()

    def init_database(self):
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS expenses
                    (id INTEGER PRIMARY KEY,
                     amount REAL,
                     category TEXT,
                     date TEXT)''')
        conn.commit()
        conn.close()

    def setup_input_fields(self):
        # Create a container for input fields with better spacing
        input_container = ttk.Frame(self.input_frame)
        input_container.pack(fill=tk.X, pady=10)
        
        # Amount input with KSh symbol
        amount_frame = ttk.Frame(input_container)
        amount_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(amount_frame, text="Amount (KSh):", 
                 style="Header.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=15)
        amount_entry.pack(side=tk.LEFT)
        
        # Category input
        category_frame = ttk.Frame(input_container)
        category_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(category_frame, text="Category:", style="Header.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.categories = ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Health", "Education", "Other"]
        self.category_var = tk.StringVar()
        category_cb = ttk.Combobox(category_frame, textvariable=self.category_var, values=self.categories, width=15, state="readonly")
        category_cb.pack(side=tk.LEFT)
        
        # Submit button
        submit_btn = ttk.Button(input_container, text="Add Expense", command=self.add_expense, style="Custom.TButton")
        submit_btn.pack(side=tk.LEFT)

    def setup_summary_section(self):
        # Create container for summary controls
        controls_frame = ttk.Frame(self.summary_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add total expenses display
        self.total_var = tk.StringVar(value="Total: KSh 0.00")
        ttk.Label(controls_frame, textvariable=self.total_var, style="Header.TLabel").pack(side=tk.LEFT)
        
        # Visualization button on the right
        ttk.Button(controls_frame, text="Show Chart", command=self.show_visualization, 
                  style="Custom.TButton").pack(side=tk.RIGHT)
        
        # Improved tree view
        tree_frame = ttk.Frame(self.summary_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_frame, columns=("Amount", "Category", "Date"), 
                                show="headings", height=15)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        # Configure columns
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Date", text="Date")
        
        self.tree.column("Amount", width=150, anchor=tk.E)
        self.tree.column("Category", width=150, anchor=tk.CENTER)
        self.tree.column("Date", width=150, anchor=tk.CENTER)
        
        # Configure tree style
        self.style.configure("Treeview",
                            background="white",
                            foreground=self.colors['text'],
                            fieldbackground="white",
                            rowheight=25)
        self.style.configure("Treeview.Heading",
                            font=('Helvetica', 10, 'bold'),
                            background=self.colors['primary'],
                            foreground="white")
        
        # Configure tree selection colors
        self.style.map('Treeview',
                      background=[('selected', self.colors['secondary'])],
                      foreground=[('selected', 'white')])

    def add_expense(self):
        try:
            amount = float(self.amount_var.get())
            category = self.category_var.get()
            if not category:
                raise ValueError("Please select a category")
                
            date = datetime.now().strftime("%Y-%m-%d")
            
            conn = sqlite3.connect('expenses.db')
            c = conn.cursor()
            c.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
                     (amount, category, date))
            conn.commit()
            conn.close()
            
            self.amount_var.set("")
            self.category_var.set("")
            self.update_summary()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def update_summary(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        
        # Update expense list with KSh
        c.execute("SELECT amount, category, date FROM expenses ORDER BY date DESC")
        for row in c.fetchall():
            amount = f"KSh {row[0]:,.2f}"  # Added thousand separator
            self.tree.insert("", "end", values=(amount, row[1], row[2]))
        
        # Update total with KSh
        c.execute("SELECT SUM(amount) FROM expenses")
        total = c.fetchone()[0] or 0
        self.total_var.set(f"Total: KSh {total:,.2f}")  # Added thousand separator
        
        conn.close()

    def show_visualization(self):
        # Fetch category totals
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        data = c.fetchall()
        conn.close()
        
        if not data:
            messagebox.showinfo("Info", "No expenses to visualize")
            return
            
        # Create pie chart
        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]
        
        # Update the visualization window
        viz_window = tk.Toplevel(self.root)
        viz_window.title("Expense Visualization")
        viz_window.geometry("800x600")  # Larger window for chart
        
        # Add a title
        ttk.Label(viz_window, text="Expenses by Category", 
                 style="Title.TLabel").pack(pady=10)
        
        # Update pie chart colors
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', 
                 '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', colors=colors)
        
        # Set figure background color
        fig.patch.set_facecolor(self.colors['background'])
        ax.set_facecolor(self.colors['background'])
        
        canvas = FigureCanvasTkAgg(fig, viz_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Add footer frame
        footer_frame = ttk.Frame(viz_window)
        footer_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Configure footer style if not already configured
        self.style.configure("Footer.TLabel",
                            font=("Helvetica", 9),
                            foreground=self.colors['primary'])
        
        # Add footer text
        footer_text = "© 2024 KEVIN | All rights reserved"
        footer_label = ttk.Label(footer_frame, 
                                text=footer_text,
                                style="Footer.TLabel",
                                anchor="center")
        footer_label.pack(fill=tk.X)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
