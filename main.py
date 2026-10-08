"""
main.py
=======
Central Controller and Application Launcher for Meal Plan & Spending Analysis.

Responsibilities:
1. Verify required libraries (numpy, pandas, matplotlib, tkinter).
2. Ensure data directories and data/meal_records.csv are initialized.
3. Display the interactive master application menu.
4. Delegate execution to meal_manager, analytics, and gui without holding business logic.
"""

import sys
from pathlib import Path

REQUIRED_LIBRARIES = ("tkinter", "numpy", "pandas", "matplotlib")


def check_dependencies():
    """Verify that all required third-party and standard libraries are installed."""
    missing = []
    for lib in REQUIRED_LIBRARIES:
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)
    return missing


def run_complete_project():
    """Execute end-to-end demonstration workflow across all modules."""
    import data_manager
    import meal_manager
    import analytics
    import gui

    print("\n" + "=" * 60)
    print("      RUNNING COMPLETE MEAL PLAN & SPENDING WORKFLOW")
    print("=" * 60)

    print("\n[Step 1/5] Verifying & preparing dataset storage...")
    data_manager.prepare_file()

    print("\n[Step 2/5] Displaying all current meal records...")
    meal_manager.view_meals()

    print("\n[Step 3/5] Calculating spending summary & category analysis...")
    analytics.spending_summary()
    analytics.category_analysis()
    analytics.monthly_analysis()

    print("\n[Step 4/5] Loading executive dashboard snapshot...")
    analytics.dashboard()

    print("\n[Step 5/5] Launching Desktop GUI...")
    try:
        gui.launch_gui()
    except Exception as e:
        print(f"Could not open graphical display ({e}). Terminal workflow completed.")


def main():
    """Central launcher displaying the master application menu."""
    missing = check_dependencies()
    if missing:
        print("=" * 55)
        print("Meal Plan & Spending Analysis cannot start.")
        print(f"Missing required libraries: {', '.join(missing)}")
        print("Please install them using: pip install numpy pandas matplotlib")
        print("=" * 55)
        return 1

    # Safe imports after dependency verification
    import data_manager
    import meal_manager
    import analytics
    import gui

    # Ensure dataset is ready upon start
    data_manager.prepare_file()

    while True:
        print("\n" + "=" * 48)
        print("         MEAL PLAN & SPENDING ANALYSIS")
        print("=" * 48)
        print("1. Meal Management")
        print("2. Analysis & Visualization")
        print("3. Open Tkinter GUI")
        print("4. Run Complete Project")
        print("0. Exit")
        print("=" * 48)

        choice = input("Enter your choice (0-4): ").strip()

        try:
            if choice == "1":
                meal_manager.meal_manager_menu()
            elif choice == "2":
                analytics.analytics_menu()
            elif choice == "3":
                print("\nOpening Tkinter GUI window...")
                gui.launch_gui()
            elif choice == "4":
                run_complete_project()
            elif choice == "0":
                print("\nThank you for using Meal Plan & Spending Analysis. Goodbye!")
                return 0
            else:
                print("Invalid choice. Please select an option between 0 and 4.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    sys.exit(main() or 0)
