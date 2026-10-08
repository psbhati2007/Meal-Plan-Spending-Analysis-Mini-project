"""
meal_manager.py
===============
Meal Record Management and CRUD Business Logic Layer.

Responsibilities:
1. Provide Add, View, Search, Update, and Delete operations for meal records.
2. Validate user input (valid dates, non-negative costs, existing Meal IDs).
3. Utilize data_manager as the single source of truth for persistence.
4. Support standalone menu execution and programmatic invocation from GUI and launcher.
"""

import sys
from datetime import datetime
import pandas as pd
from data_manager import load_data, save_data, COLUMNS

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def format_table(df: pd.DataFrame) -> str:
    """Format DataFrame as an aligned tabular string for console output."""
    if df.empty:
        return "No records found."
    return df.to_string(index=False)


def add_meal(date: str = None, meal: str = None, category: str = None,
             food_item: str = None, cost: float = None) -> bool:
    """
    Add a new meal record after validation and auto-generating a unique Meal_ID.
    If parameters are omitted, interactively prompts the user via console input.
    """
    try:
        if date is None:
            date = input("Enter date (YYYY-MM-DD): ").strip()
        if not date:
            print("Error: Date cannot be empty.")
            return False

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Warning: Date is not in standard YYYY-MM-DD format, saving as provided.")

        if meal is None:
            meal = input("Enter meal (Breakfast/Lunch/Dinner): ").strip()
        if not meal:
            print("Error: Meal type cannot be empty.")
            return False

        if category is None:
            category = input("Enter category (Home/Restaurant/Other): ").strip()
        if not category:
            category = "Other"

        if food_item is None:
            food_item = input("Enter food item: ").strip()
        if not food_item:
            print("Error: Food item cannot be empty.")
            return False

        if cost is None:
            cost_input = input("Enter cost (Rs.): ").strip()
            cost = float(cost_input)
        else:
            cost = float(cost)

        if cost < 0:
            print("Error: Cost cannot be negative.")
            return False

        df = load_data()

        # Generate unique Meal_ID
        if df.empty or "Meal_ID" not in df.columns:
            new_id = 1
        else:
            valid_ids = pd.to_numeric(df["Meal_ID"], errors="coerce").dropna()
            new_id = int(valid_ids.max()) + 1 if not valid_ids.empty else 1

        new_record = pd.DataFrame([{
            "Meal_ID": new_id,
            "Date": date,
            "Meal": meal,
            "Category": category,
            "Food_Item": food_item,
            "Cost": float(cost)
        }])

        df = pd.concat([df, new_record], ignore_index=True)

        if save_data(df):
            print(f"\nMeal added successfully! Generated Meal ID: {new_id}")
            return True
        else:
            print("Error: Failed to save record to CSV.")
            return False

    except ValueError as e:
        print(f"Invalid input: {e}")
        return False
    except Exception as e:
        print(f"Error adding meal: {e}")
        return False


def view_meals() -> pd.DataFrame:
    """Display all available meal records in a readable table and return DataFrame."""
    try:
        df = load_data()
        if df.empty:
            print("\nNo meal records found in dataset.")
            return df

        print("\n" + "=" * 70)
        print("                     ALL MEAL RECORDS")
        print("=" * 70)
        print(format_table(df))
        print("=" * 70)
        print(f"Total Records: {len(df)}")
        return df

    except Exception as e:
        print(f"Error displaying meals: {e}")
        return pd.DataFrame(columns=COLUMNS)


def search_meals(category: str = None, meal: str = None) -> pd.DataFrame:
    """
    Search and filter meals by category and/or meal type.
    Allows either filter to be omitted or skipped.
    """
    try:
        df = load_data()
        if df.empty:
            print("No records available to search.")
            return df

        result = df.copy()

        if category and str(category).strip():
            result = result[
                result["Category"].astype(str).str.contains(category.strip(), case=False, na=False)
            ]

        if meal and str(meal).strip():
            result = result[
                result["Meal"].astype(str).str.contains(meal.strip(), case=False, na=False)
            ]

        if result.empty:
            print("\nNo matching records found for given filter criteria.")
        else:
            print("\n" + "=" * 70)
            print("                     SEARCH RESULTS")
            print("=" * 70)
            print(format_table(result))
            print("=" * 70)
            print(f"Matches Found: {len(result)}")

        return result

    except Exception as e:
        print(f"Error searching meals: {e}")
        return pd.DataFrame(columns=COLUMNS)


def update_meal(meal_id: int = None, date: str = None, meal: str = None,
                category: str = None, food_item: str = None, cost: float = None) -> bool:
    """
    Update an existing meal record by Meal_ID.
    Validates Meal_ID existence and cost constraints.
    """
    try:
        df = load_data()
        if df.empty:
            print("Dataset is empty. No records to update.")
            return False

        if meal_id is None:
            id_input = input("Enter Meal ID to update: ").strip()
            if not id_input:
                print("Error: Meal ID is required.")
                return False
            meal_id = int(id_input)
        else:
            meal_id = int(meal_id)

        df["Meal_ID"] = pd.to_numeric(df["Meal_ID"], errors="coerce")
        matching_indices = df.index[df["Meal_ID"] == meal_id].tolist()

        if not matching_indices:
            print(f"Error: Meal ID {meal_id} not found.")
            return False

        idx = matching_indices[0]
        current_record = df.loc[idx]

        print(f"\nCurrent Record (Meal ID: {meal_id}):")
        print(f"Date: {current_record['Date']} | Meal: {current_record['Meal']} | "
              f"Category: {current_record['Category']} | Food: {current_record['Food_Item']} | Cost: Rs. {current_record['Cost']}")

        # If interactive CLI (no specific fields passed as arguments)
        if date is None and meal is None and category is None and food_item is None and cost is None:
            new_date = input("Enter new Date (leave empty to keep current): ").strip()
            if new_date:
                df.at[idx, "Date"] = new_date

            new_meal = input("Enter new Meal type (leave empty to keep current): ").strip()
            if new_meal:
                df.at[idx, "Meal"] = new_meal

            new_cat = input("Enter new Category (leave empty to keep current): ").strip()
            if new_cat:
                df.at[idx, "Category"] = new_cat

            new_food = input("Enter new Food Item (leave empty to keep current): ").strip()
            if new_food:
                df.at[idx, "Food_Item"] = new_food

            new_cost_str = input("Enter new Cost (leave empty to keep current): ").strip()
            if new_cost_str:
                new_cost = float(new_cost_str)
                if new_cost < 0:
                    print("Error: Cost cannot be negative. Update aborted.")
                    return False
                df.at[idx, "Cost"] = new_cost
        else:
            if date is not None:
                df.at[idx, "Date"] = str(date)
            if meal is not None:
                df.at[idx, "Meal"] = str(meal)
            if category is not None:
                df.at[idx, "Category"] = str(category)
            if food_item is not None:
                df.at[idx, "Food_Item"] = str(food_item)
            if cost is not None:
                float_cost = float(cost)
                if float_cost < 0:
                    print("Error: Cost cannot be negative.")
                    return False
                df.at[idx, "Cost"] = float_cost

        if save_data(df):
            print(f"Meal ID {meal_id} updated successfully!")
            return True
        else:
            print("Error: Failed to save changes to CSV.")
            return False

    except ValueError as e:
        print(f"Error: Invalid numeric input entered ({e}).")
        return False
    except Exception as e:
        print(f"Error updating meal: {e}")
        return False


def delete_meal(meal_id: int = None) -> bool:
    """
    Delete a meal record using its Meal_ID.
    Handles invalid and non-existing IDs cleanly.
    """
    try:
        df = load_data()
        if df.empty:
            print("Dataset is empty. No records to delete.")
            return False

        if meal_id is None:
            id_input = input("Enter Meal ID to delete: ").strip()
            if not id_input:
                print("Error: Meal ID is required.")
                return False
            meal_id = int(id_input)
        else:
            meal_id = int(meal_id)

        df["Meal_ID"] = pd.to_numeric(df["Meal_ID"], errors="coerce")
        if meal_id not in df["Meal_ID"].values:
            print(f"Error: Meal ID {meal_id} does not exist.")
            return False

        df = df[df["Meal_ID"] != meal_id]

        if save_data(df):
            print(f"Meal ID {meal_id} deleted successfully!")
            return True
        else:
            print("Error: Failed to save changes to CSV.")
            return False

    except ValueError:
        print("Error: Meal ID must be a valid integer.")
        return False
    except Exception as e:
        print(f"Error deleting meal: {e}")
        return False


def meal_manager_menu():
    """Interactive command-line menu for meal records."""
    while True:
        print("\n" + "=" * 40)
        print("        MEAL RECORD MANAGEMENT")
        print("=" * 40)
        print("1. Add Meal")
        print("2. View Meals")
        print("3. Search Meals")
        print("4. Update Meal")
        print("5. Delete Meal")
        print("0. Back to Main Menu")
        print("=" * 40)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_meal()
        elif choice == "2":
            view_meals()
        elif choice == "3":
            cat = input("Enter category to search (press Enter to skip): ").strip()
            meal = input("Enter meal type to search (press Enter to skip): ").strip()
            search_meals(category=cat if cat else None, meal=meal if meal else None)
        elif choice == "4":
            update_meal()
        elif choice == "5":
            delete_meal()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please select 0-5.")


def main():
    meal_manager_menu()


if __name__ == "__main__":
    main()
