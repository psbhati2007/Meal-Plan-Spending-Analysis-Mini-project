"""
gui.py
======
Presentation and Graphical User Interface Layer.

Responsibilities:
1. Provide a professional desktop Tkinter interface with TTK widgets.
2. Delegate all CRUD operations directly to meal_manager.py.
3. Delegate all analytics and chart generation to analytics.py.
4. Render interactive charts embedded via FigureCanvasTkAgg.
5. Display formatted modal dialogues for analytical summaries.
6. Support standalone execution and launcher invocation.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data_manager import load_data, COLUMNS
import meal_manager
import analytics

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class MealPlanApp(tk.Tk):
    """Main desktop application window for Meal Plan & Spending Analysis."""

    def __init__(self):
        super().__init__()
        self.title("Meal Plan & Spending Analysis")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # State Variables
        self.meal_id_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.meal_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.food_var = tk.StringVar()
        self.cost_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        """Construct the graphical interface widgets and layout."""
        # Main Title Header
        title_label = tk.Label(
            self,
            text="MEAL PLAN & SPENDING ANALYSIS",
            font=("Times New Roman", 22, "bold")
        )
        title_label.pack(pady=(12, 2))

        subtitle_label = tk.Label(
            self,
            text="Modular Desktop Meal Record Management & Visual Analytics System",
            font=("Times New Roman", 12)
        )
        subtitle_label.pack(pady=(0, 10))

        # Input Form Section
        input_frame = tk.LabelFrame(
            self,
            text="Meal Information",
            font=("Times New Roman", 12, "bold"),
            padx=10,
            pady=10
        )
        input_frame.pack(fill=tk.X, padx=15, pady=5)

        # Row 0: Meal ID & Date
        tk.Label(input_frame, text="Meal ID:", font=("Times New Roman", 11)).grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(input_frame, textvariable=self.meal_id_var, font=("Times New Roman", 11), width=20).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Date (YYYY-MM-DD):", font=("Times New Roman", 11)).grid(row=0, column=2, padx=5, pady=5)
        tk.Entry(input_frame, textvariable=self.date_var, font=("Times New Roman", 11), width=20).grid(row=0, column=3, padx=5, pady=5)

        # Row 1: Meal Type & Category
        tk.Label(input_frame, text="Meal Type:", font=("Times New Roman", 11)).grid(row=1, column=0, padx=5, pady=5)
        ttk.Combobox(
            input_frame,
            textvariable=self.meal_var,
            values=["Breakfast", "Lunch", "Dinner"],
            state="readonly",
            width=18
        ).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Category:", font=("Times New Roman", 11)).grid(row=1, column=2, padx=5, pady=5)
        ttk.Combobox(
            input_frame,
            textvariable=self.category_var,
            values=["Home", "Restaurant", "Other"],
            state="readonly",
            width=18
        ).grid(row=1, column=3, padx=5, pady=5)

        # Row 2: Food Item & Cost
        tk.Label(input_frame, text="Food Item:", font=("Times New Roman", 11)).grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(input_frame, textvariable=self.food_var, font=("Times New Roman", 11), width=20).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Cost (Rs.):", font=("Times New Roman", 11)).grid(row=2, column=2, padx=5, pady=5)
        tk.Entry(input_frame, textvariable=self.cost_var, font=("Times New Roman", 11), width=20).grid(row=2, column=3, padx=5, pady=5)

        # CRUD Action Buttons
        crud_frame = tk.Frame(self)
        crud_frame.pack(fill=tk.X, padx=15, pady=8)

        tk.Button(crud_frame, text="Add Meal", command=self.on_add_meal, font=("Times New Roman", 11), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(crud_frame, text="Update Meal", command=self.on_update_meal, font=("Times New Roman", 11), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(crud_frame, text="Delete Meal", command=self.on_delete_meal, font=("Times New Roman", 11), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(crud_frame, text="Clear Fields", command=self.clear_fields, font=("Times New Roman", 11), width=15).pack(side=tk.LEFT, padx=5)

        # Search Controls
        search_frame = tk.Frame(self)
        search_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(search_frame, text="Search:", font=("Times New Roman", 11, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.search_var, font=("Times New Roman", 11), width=35).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.on_search, font=("Times New Roman", 11), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Show All", command=lambda: self.refresh_table(), font=("Times New Roman", 11), width=12).pack(side=tk.LEFT, padx=5)

        # Treeview Data Table
        table_frame = tk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=tuple(COLUMNS), show="headings")
        for column in COLUMNS:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=140, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<ButtonRelease-1>", self.on_select_record)

        # Analytics Action Buttons
        analysis_frame = tk.LabelFrame(
            self,
            text="Analysis and Visualization",
            font=("Times New Roman", 11, "bold")
        )
        analysis_frame.pack(fill=tk.X, padx=15, pady=8)

        tk.Button(analysis_frame, text="Spending Summary", command=self.on_spending_summary, font=("Times New Roman", 10), width=18).pack(side=tk.LEFT, padx=4, pady=6)
        tk.Button(analysis_frame, text="Category Analysis", command=self.on_category_analysis, font=("Times New Roman", 10), width=18).pack(side=tk.LEFT, padx=4)
        tk.Button(analysis_frame, text="Monthly Analysis", command=self.on_monthly_analysis, font=("Times New Roman", 10), width=18).pack(side=tk.LEFT, padx=4)
        tk.Button(analysis_frame, text="Category Chart", command=self.on_category_chart, font=("Times New Roman", 10), width=16).pack(side=tk.LEFT, padx=4)
        tk.Button(analysis_frame, text="Monthly Chart", command=self.on_monthly_chart, font=("Times New Roman", 10), width=16).pack(side=tk.LEFT, padx=4)
        tk.Button(analysis_frame, text="Dashboard", command=self.on_dashboard, font=("Times New Roman", 10), width=14).pack(side=tk.LEFT, padx=4)

        # Exit Button
        tk.Button(self, text="Exit Application", command=self.destroy, font=("Times New Roman", 11, "bold"), width=16).pack(pady=8)

    # ----------------------------------------------------
    # Form Helpers
    # ----------------------------------------------------
    def clear_fields(self):
        """Reset all input fields in the meal form."""
        self.meal_id_var.set("")
        self.date_var.set("")
        self.meal_var.set("")
        self.category_var.set("")
        self.food_var.set("")
        self.cost_var.set("")

    def refresh_table(self, data: pd.DataFrame = None):
        """Repopulate the Treeview table with current or filtered data."""
        try:
            if data is None:
                data = load_data()

            for item in self.tree.get_children():
                self.tree.delete(item)

            if data.empty:
                return

            for _, row in data.iterrows():
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        row["Meal_ID"],
                        row["Date"],
                        row["Meal"],
                        row["Category"],
                        row["Food_Item"],
                        row["Cost"]
                    )
                )
        except Exception as e:
            messagebox.showerror("Table Error", f"Unable to refresh table:\n{e}")

    def on_select_record(self, event):
        """Populate form fields when a table row is clicked."""
        try:
            selected = self.tree.focus()
            if not selected:
                return
            values = self.tree.item(selected, "values")
            if not values:
                return

            self.meal_id_var.set(values[0])
            self.date_var.set(values[1])
            self.meal_var.set(values[2])
            self.category_var.set(values[3])
            self.food_var.set(values[4])
            self.cost_var.set(values[5])
        except Exception as e:
            print(f"Selection error: {e}")

    # ----------------------------------------------------
    # CRUD Operations (Delegated to meal_manager)
    # ----------------------------------------------------
    def on_add_meal(self):
        """Validate input and call meal_manager.add_meal."""
        date = self.date_var.get().strip()
        meal = self.meal_var.get().strip()
        category = self.category_var.get().strip()
        food = self.food_var.get().strip()
        cost_text = self.cost_var.get().strip()

        if not date or not meal or not category or not food or not cost_text:
            messagebox.showwarning("Missing Fields", "Please fill in all meal fields.")
            return

        try:
            cost = float(cost_text)
            if cost < 0:
                messagebox.showwarning("Invalid Cost", "Cost cannot be negative.")
                return

            success = meal_manager.add_meal(
                date=date,
                meal=meal,
                category=category,
                food_item=food,
                cost=cost
            )

            if success:
                messagebox.showinfo("Success", "Meal record added successfully.")
                self.refresh_table()
                self.clear_fields()
            else:
                messagebox.showerror("Error", "Could not add meal. Please check console logs.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric cost.")

    def on_update_meal(self):
        """Validate ID and call meal_manager.update_meal."""
        id_text = self.meal_id_var.get().strip()
        if not id_text:
            messagebox.showwarning("Missing ID", "Please select or enter a Meal ID to update.")
            return

        date = self.date_var.get().strip()
        meal = self.meal_var.get().strip()
        category = self.category_var.get().strip()
        food = self.food_var.get().strip()
        cost_text = self.cost_var.get().strip()

        if not date or not meal or not category or not food or not cost_text:
            messagebox.showwarning("Missing Fields", "Please complete all fields to update.")
            return

        try:
            meal_id = int(id_text)
            cost = float(cost_text)
            if cost < 0:
                messagebox.showwarning("Invalid Cost", "Cost cannot be negative.")
                return

            success = meal_manager.update_meal(
                meal_id=meal_id,
                date=date,
                meal=meal,
                category=category,
                food_item=food,
                cost=cost
            )

            if success:
                messagebox.showinfo("Success", f"Meal ID {meal_id} updated successfully.")
                self.refresh_table()
            else:
                messagebox.showerror("Not Found", f"Could not update Meal ID {meal_id}.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Meal ID and Cost must be numeric.")

    def on_delete_meal(self):
        """Prompt confirmation and call meal_manager.delete_meal."""
        id_text = self.meal_id_var.get().strip()
        if not id_text:
            messagebox.showwarning("Missing ID", "Please enter or select a Meal ID to delete.")
            return

        try:
            meal_id = int(id_text)
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Meal ID {meal_id}?")
            if not confirm:
                return

            success = meal_manager.delete_meal(meal_id=meal_id)
            if success:
                messagebox.showinfo("Success", f"Meal ID {meal_id} deleted successfully.")
                self.refresh_table()
                self.clear_fields()
            else:
                messagebox.showwarning("Not Found", f"Meal ID {meal_id} was not found.")

        except ValueError:
            messagebox.showerror("Invalid ID", "Meal ID must be an integer.")

    def on_search(self):
        """Filter data using meal_manager.search_meals."""
        query = self.search_var.get().strip()
        if not query:
            self.refresh_table()
            return

        df = load_data()
        if df.empty:
            self.refresh_table(df)
            return

        # Multi-column search matching any field
        matched = df[
            df.astype(str).apply(
                lambda row: row.str.lower().str.contains(query.lower(), na=False).any(),
                axis=1
            )
        ]
        self.refresh_table(matched)

        if matched.empty:
            messagebox.showinfo("Search Results", f"No records found matching '{query}'.")

    # ----------------------------------------------------
    # Analytics Modals & Embedded Visualizations
    # ----------------------------------------------------
    def _show_modal(self, title: str, text: str):
        """Display analytical output in a dedicated scrollable modal window."""
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("550x420")
        win.resizable(True, True)

        txt = tk.Text(win, font=("Times New Roman", 12), wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        txt.insert(tk.END, text)
        txt.config(state=tk.DISABLED)

    def _show_chart_modal(self, title: str, fig):
        """Display a Matplotlib Figure embedded into a Tkinter Toplevel window."""
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("850x550")
        win.minsize(700, 450)

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def on_spending_summary(self):
        """Fetch summary metrics from analytics and display modal."""
        metrics = analytics.spending_summary()
        if not metrics:
            messagebox.showinfo("Spending Summary", "No meal records available.")
            return

        text = (
            "========================================\n"
            "           SPENDING SUMMARY\n"
            "========================================\n\n"
            f"Total Spending   : Rs. {metrics['Total Spending']:.2f}\n"
            f"Average Meal Cost: Rs. {metrics['Average Cost']:.2f}\n"
            f"Highest Cost     : Rs. {metrics['Highest Cost']:.2f}\n"
            f"Lowest Cost      : Rs. {metrics['Lowest Cost']:.2f}\n\n"
            "========================================"
        )
        self._show_modal("Spending Summary", text)

    def on_category_analysis(self):
        """Fetch category breakdown from analytics and display modal."""
        cat_df = analytics.category_analysis()
        if cat_df.empty:
            messagebox.showinfo("Category Analysis", "No meal records available.")
            return

        text = (
            "========================================\n"
            "           CATEGORY ANALYSIS\n"
            "========================================\n\n"
        )
        for _, row in cat_df.iterrows():
            text += (
                f"Category: {row['Category']}\n"
                f"Total Spending : Rs. {row['Total_Spending']:.2f}\n"
                f"Average Cost   : Rs. {row['Average_Cost']:.2f}\n"
                f"Number of Meals: {int(row['Number_of_Meals'])}\n"
                f"{'-' * 40}\n"
            )
        self._show_modal("Category Analysis", text)

    def on_monthly_analysis(self):
        """Fetch monthly breakdown from analytics and display modal."""
        monthly_series = analytics.monthly_analysis()
        if monthly_series.empty:
            messagebox.showinfo("Monthly Analysis", "No valid date records available.")
            return

        text = (
            "========================================\n"
            "           MONTHLY SPENDING\n"
            "========================================\n\n"
        )
        for month, amount in monthly_series.items():
            text += f"{month} : Rs. {amount:.2f}\n"
        text += "\n========================================"
        self._show_modal("Monthly Analysis", text)

    def on_category_chart(self):
        """Generate Matplotlib Figure via analytics and embed inside modal."""
        fig = analytics.category_chart(save_png=True, show=False)
        self._show_chart_modal("Category Spending Chart", fig)

    def on_monthly_chart(self):
        """Generate monthly trend Figure via analytics and embed inside modal."""
        fig = analytics.monthly_chart(save_png=True, show=False)
        self._show_chart_modal("Monthly Spending Chart", fig)

    def on_dashboard(self):
        """Fetch executive dashboard metrics from analytics and display modal."""
        metrics = analytics.dashboard()
        if not metrics:
            messagebox.showinfo("Dashboard", "No meal records available.")
            return

        text = (
            "========================================\n"
            "       MEAL PLAN & SPENDING ANALYZER\n"
            "========================================\n\n"
            f"Total Meals          : {metrics['Total Meals']}\n"
            f"Total Spending       : Rs. {metrics['Total Spending']:.2f}\n"
            f"Average Meal Cost    : Rs. {metrics['Average Meal Cost']:.2f}\n"
            f"Most Common Category : {metrics['Most Common Category']}\n\n"
            "========================================"
        )
        self._show_modal("Executive Dashboard", text)


def launch_gui():
    """Entry point function to instantiate and run the desktop application."""
    app = MealPlanApp()
    app.mainloop()


def main():
    launch_gui()


if __name__ == "__main__":
    main()
