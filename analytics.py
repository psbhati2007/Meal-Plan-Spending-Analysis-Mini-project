"""
analytics.py
============
Analytics, Metrics Calculation, and Visualization Layer.

Responsibilities:
1. Compute overall spending statistics (total, average, min, max).
2. Generate category-wise aggregations (spending, average cost, meal count).
3. Compute monthly expenditure trends.
4. Generate Matplotlib Figure objects (bar chart and trend line) for GUI embedding and PNG export.
5. Provide a consolidated high-level Dashboard summary.
6. Support standalone menu execution and programmatic access.
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from data_manager import load_data, CHARTS_DIR

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def spending_summary() -> dict:
    """
    Calculate and display total, average, highest, and lowest meal costs.
    Returns dictionary with calculated metrics for programmatic consumption.
    """
    try:
        df = load_data()
        if df.empty:
            print("\nNo data available to calculate spending summary.")
            return {}

        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0.0)

        total_spending = df["Cost"].sum()
        average_cost = df["Cost"].mean()
        highest_cost = df["Cost"].max()
        lowest_cost = df["Cost"].min()

        metrics = {
            "Total Spending": total_spending,
            "Average Cost": average_cost,
            "Highest Cost": highest_cost,
            "Lowest Cost": lowest_cost
        }

        print("\n" + "=" * 45)
        print("             SPENDING SUMMARY")
        print("=" * 45)
        print(f"Total Spending   : Rs. {total_spending:.2f}")
        print(f"Average Meal Cost: Rs. {average_cost:.2f}")
        print(f"Highest Cost     : Rs. {highest_cost:.2f}")
        print(f"Lowest Cost      : Rs. {lowest_cost:.2f}")
        print("=" * 45)

        return metrics

    except Exception as e:
        print(f"Error calculating spending summary: {e}")
        return {}


def category_analysis() -> pd.DataFrame:
    """
    Calculate total spending, average cost, and meal count grouped by Category.
    Returns the aggregated DataFrame.
    """
    try:
        df = load_data()
        if df.empty:
            print("\nNo data available for category analysis.")
            return pd.DataFrame()

        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0.0)

        category_summary = df.groupby("Category")["Cost"].agg(
            ["sum", "mean", "count"]
        ).reset_index()

        category_summary.columns = [
            "Category",
            "Total_Spending",
            "Average_Cost",
            "Number_of_Meals"
        ]

        category_summary = category_summary.sort_values(
            "Total_Spending",
            ascending=False
        )

        print("\n" + "=" * 65)
        print("                     CATEGORY ANALYSIS")
        print("=" * 65)
        formatted_df = category_summary.copy()
        formatted_df["Total_Spending"] = formatted_df["Total_Spending"].map("Rs. {:.2f}".format)
        formatted_df["Average_Cost"] = formatted_df["Average_Cost"].map("Rs. {:.2f}".format)
        print(formatted_df.to_string(index=False))
        print("=" * 65)

        return category_summary

    except Exception as e:
        print(f"Error performing category analysis: {e}")
        return pd.DataFrame()


def monthly_analysis() -> pd.Series:
    """
    Group meal records by month and calculate spending per month.
    Returns Series with Month index and total spending values.
    """
    try:
        df = load_data()
        if df.empty:
            print("\nNo data available for monthly analysis.")
            return pd.Series(dtype=float)

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0.0)

        valid_df = df.dropna(subset=["Date"]).copy()
        if valid_df.empty:
            print("\nNo valid dates found for monthly analysis.")
            return pd.Series(dtype=float)

        valid_df["Month"] = valid_df["Date"].dt.to_period("M").astype(str)
        monthly = valid_df.groupby("Month")["Cost"].sum().sort_index()

        print("\n" + "=" * 45)
        print("             MONTHLY SPENDING")
        print("=" * 45)
        for month, amount in monthly.items():
            print(f"{month} : Rs. {amount:.2f}")
        print("=" * 45)

        return monthly

    except Exception as e:
        print(f"Error calculating monthly spending: {e}")
        return pd.Series(dtype=float)


def category_chart(save_png: bool = True, show: bool = False) -> Figure:
    """
    Generate a Matplotlib bar chart of total spending by category.
    Returns the Matplotlib Figure object so it can be embedded in GUI or saved to disk.
    """
    try:
        df = load_data()
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)

        if df.empty:
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")
            return fig

        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0.0)
        category_data = df.groupby("Category")["Cost"].sum().sort_values(ascending=False)

        if category_data.empty:
            ax.text(0.5, 0.5, "No Category Data Available", ha="center", va="center")
            return fig

        cat_names = [str(c) for c in category_data.index]
        bars = ax.bar(cat_names, category_data.values, color="#2b5b84", edgecolor="black")
        ax.set_title("Spending by Meal Category", fontsize=14, fontweight="bold")
        ax.set_xlabel("Category", fontsize=11)
        ax.set_ylabel("Total Spending (Rs.)", fontsize=11)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Annotate values on top of bars
        for bar in bars:
            height = float(bar.get_height())
            ax.annotate(f"Rs. {height:.0f}",
                        xy=(float(bar.get_x() + bar.get_width() / 2), height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=9)

        fig.tight_layout()

        if save_png:
            CHARTS_DIR.mkdir(parents=True, exist_ok=True)
            export_path = CHARTS_DIR / "category_spending.png"
            fig.savefig(export_path)

        if show:
            plt.figure(figsize=(8, 5))
            category_data.plot(kind="bar", color="#2b5b84", edgecolor="black")
            plt.title("Spending by Meal Category", fontsize=14, fontweight="bold")
            plt.xlabel("Category", fontsize=11)
            plt.ylabel("Total Spending (Rs.)", fontsize=11)
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.show()

        return fig

    except Exception as e:
        print(f"Error generating category chart: {e}")
        return Figure(figsize=(8, 5))


def monthly_chart(save_png: bool = True, show: bool = False) -> Figure:
    """
    Generate a Matplotlib line chart of monthly spending trend.
    Returns the Matplotlib Figure object so it can be embedded in GUI or saved to disk.
    """
    try:
        df = load_data()
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)

        if df.empty:
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")
            return fig

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0.0)

        valid_df = df.dropna(subset=["Date"]).copy()
        if valid_df.empty:
            ax.text(0.5, 0.5, "No Valid Date Records Available", ha="center", va="center")
            return fig

        valid_df["Month"] = valid_df["Date"].dt.to_period("M").astype(str)
        monthly_data = valid_df.groupby("Month")["Cost"].sum().sort_index()

        ax.plot(monthly_data.index.astype(str), monthly_data.values,
                marker="o", color="#d9534f", linewidth=2.5, markersize=7)
        ax.set_title("Monthly Meal Spending Trend", fontsize=14, fontweight="bold")
        ax.set_xlabel("Month", fontsize=11)
        ax.set_ylabel("Total Spending (Rs.)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.7)

        # Annotate points
        for x, y in zip(monthly_data.index.astype(str), monthly_data.values):
            ax.annotate(f"Rs. {float(y):.0f}",
                        xy=(str(x), float(y)),
                        xytext=(0, 6),
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=9)

        fig.tight_layout()

        if save_png:
            CHARTS_DIR.mkdir(parents=True, exist_ok=True)
            export_path = CHARTS_DIR / "monthly_spending.png"
            fig.savefig(export_path)

        if show:
            plt.figure(figsize=(9, 5))
            plt.plot(monthly_data.index.astype(str), monthly_data.values,
                     marker="o", color="#d9534f", linewidth=2.5, markersize=7)
            plt.title("Monthly Meal Spending Trend", fontsize=14, fontweight="bold")
            plt.xlabel("Month", fontsize=11)
            plt.ylabel("Total Spending (Rs.)", fontsize=11)
            plt.grid(True, linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.show()

        return fig

    except Exception as e:
        print(f"Error generating monthly chart: {e}")
        return Figure(figsize=(8, 5))


def dashboard() -> dict:
    """
    Display consolidated dashboard showing total meals, total spending,
    average meal cost, and the most common meal category.
    """
    try:
        df = load_data()
        if df.empty:
            print("\nNo meal records available to build dashboard.")
            return {}

        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0.0)

        total_meals = len(df)
        total_spending = df["Cost"].sum()
        average_cost = df["Cost"].mean()

        categories = df["Category"].dropna().astype(str).str.strip()
        most_common_category = categories.mode()[0] if not categories.empty else "N/A"

        metrics = {
            "Total Meals": total_meals,
            "Total Spending": total_spending,
            "Average Meal Cost": average_cost,
            "Most Common Category": most_common_category
        }

        print("\n" + "=" * 50)
        print("          MEAL PLAN & SPENDING ANALYZER")
        print("=" * 50)
        print(f"Total Meals              : {total_meals}")
        print(f"Total Spending           : Rs. {total_spending:.2f}")
        print(f"Average Meal Cost        : Rs. {average_cost:.2f}")
        print(f"Most Common Category     : {most_common_category}")
        print("=" * 50)

        return metrics

    except Exception as e:
        print(f"Error generating dashboard: {e}")
        return {}


def analytics_menu():
    """Interactive command-line menu for Module 3."""
    while True:
        print("\n" + "=" * 40)
        print("       ANALYSIS & VISUALIZATION")
        print("=" * 40)
        print("1. Spending Summary")
        print("2. Category Analysis")
        print("3. Monthly Analysis")
        print("4. Category Chart")
        print("5. Monthly Chart")
        print("6. Dashboard")
        print("0. Back to Main Menu")
        print("=" * 40)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            spending_summary()
        elif choice == "2":
            category_analysis()
        elif choice == "3":
            monthly_analysis()
        elif choice == "4":
            category_chart(show=True)
        elif choice == "5":
            monthly_chart(show=True)
        elif choice == "6":
            dashboard()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please select 0-6.")


def main():
    analytics_menu()


if __name__ == "__main__":
    main()
