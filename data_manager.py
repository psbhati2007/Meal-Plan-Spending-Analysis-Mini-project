"""
data_manager.py
===============
Data Access and Storage Layer for Meal Plan & Spending Analysis.

Responsibilities:
1. Resolve directory paths (data/, reports/, charts/) using pathlib.
2. Initialize and manage the single source of truth: data/meal_records.csv.
3. Provide atomic CSV saving to prevent file corruption on interruption.
4. Validate dataset schema, column presence, and data integrity.
5. Provide safe missing-file recovery and initial data bootstrapping.
6. Support standalone execution and clean module import.
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Safe console reconfigure for Windows environments
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Central directory path resolution
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"
CHARTS_DIR = REPORT_DIR / "charts"
CSV_FILE = DATA_DIR / "meal_records.csv"

# Required column schema
COLUMNS = [
    "Meal_ID",
    "Date",
    "Meal",
    "Category",
    "Food_Item",
    "Cost"
]

# Standard 20 initial records from the original project
INITIAL_DATA = {
    "Meal_ID": list(range(1, 21)),
    "Date": [
        "2026-08-05", "2026-08-06", "2026-08-10", "2026-08-15", "2026-08-20", "2026-08-25",
        "2026-09-02", "2026-09-05", "2026-09-10", "2026-09-15", "2026-09-20", "2026-09-25",
        "2026-10-01", "2026-10-01", "2026-10-02", "2026-10-02", "2026-10-03", "2026-10-03",
        "2026-10-04", "2026-10-05"
    ],
    "Meal": [
        "Breakfast", "Lunch", "Dinner", "Breakfast", "Lunch", "Dinner",
        "Breakfast", "Lunch", "Dinner", "Breakfast", "Lunch", "Dinner",
        "Breakfast", "Lunch", "Dinner", "Breakfast", "Lunch", "Dinner",
        "Breakfast", "Dinner"
    ],
    "Category": [
        "Home", "Restaurant", "Home", "Home", "Restaurant", "Home",
        "Home", "Restaurant", "Home", "Home", "Restaurant", "Home",
        "Home", "Restaurant", "Home", "Home", "Restaurant", "Home",
        "Home", "Restaurant"
    ],
    "Food_Item": [
        "Poha", "Gujarati Thali", "Dal Rice", "Paratha", "Pizza", "Khichdi",
        "Upma", "Burger", "Roti Sabji", "Poha", "Paneer Thali", "Dal Rice",
        "Poha", "Gujarati Thali", "Pizza", "Paratha", "Burger", "Khichdi",
        "Upma", "Biryani"
    ],
    "Cost": [
        40.0, 180.0, 80.0, 60.0, 250.0, 70.0, 45.0, 150.0, 90.0, 40.0,
        200.0, 85.0, 40.0, 180.0, 250.0, 60.0, 150.0, 70.0, 45.0, 220.0
    ]
}


class DataManager:
    """Encapsulates all file I/O, directory lifecycle, and validation logic."""

    def __init__(self, data_dir: Path = DATA_DIR, report_dir: Path = REPORT_DIR):
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.charts_dir = self.report_dir / "charts"
        self.csv_file = self.data_dir / "meal_records.csv"
        self.columns = COLUMNS
        self.ensure_directories()

    def ensure_directories(self):
        """Create required data and report directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.charts_dir.mkdir(parents=True, exist_ok=True)

    def prepare_file(self, force_reset: bool = False) -> bool:
        """
        Ensure meal_records.csv exists. If missing or force_reset is True,
        generates the initial default dataset.
        """
        self.ensure_directories()
        if force_reset or not self.csv_file.exists():
            return self.create_dataset(overwrite=True)
        return True

    def create_dataset(self, overwrite: bool = False) -> bool:
        """
        Generate data/meal_records.csv with default sample records.
        """
        try:
            self.ensure_directories()
            if self.csv_file.exists() and not overwrite:
                return True

            df = pd.DataFrame(INITIAL_DATA)
            self.save_data(df)
            return True
        except Exception as e:
            print(f"Error creating dataset: {e}")
            return False

    def load_data(self) -> pd.DataFrame:
        """
        Load meal records from data/meal_records.csv.
        Returns a sanitized DataFrame conforming to COLUMNS schema.
        """
        try:
            self.ensure_directories()
            if not self.csv_file.exists():
                self.prepare_file()

            df = pd.read_csv(self.csv_file)

            # Ensure all schema columns exist
            for col in self.columns:
                if col not in df.columns:
                    df[col] = None

            if not df.empty:
                df["Meal_ID"] = pd.to_numeric(df["Meal_ID"], errors="coerce").fillna(0).astype(int)
                df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0.0).astype(float)
                df["Date"] = df["Date"].astype(str)
                df["Meal"] = df["Meal"].astype(str)
                df["Category"] = df["Category"].astype(str)
                df["Food_Item"] = df["Food_Item"].astype(str)

            return df[self.columns]

        except Exception as e:
            print(f"Error loading meal data ({e}). Returning empty DataFrame.")
            return pd.DataFrame(columns=self.columns)

    def save_data(self, df: pd.DataFrame) -> bool:
        """
        Save DataFrame atomically into data/meal_records.csv.
        Writes to a temporary file first, then atomically replaces target.
        """
        try:
            self.ensure_directories()
            for col in self.columns:
                if col not in df.columns:
                    df[col] = None

            ordered_df = df[self.columns].copy()

            # Atomic save: write to temporary file first
            temp_file = self.data_dir / "meal_records.csv.tmp"
            ordered_df.to_csv(temp_file, index=False)

            # Atomically replace target file
            if temp_file.exists():
                temp_file.replace(self.csv_file)

            return True
        except Exception as e:
            print(f"Error saving meal data: {e}")
            return False

    def validate_structure(self) -> tuple:
        """
        Validate dataset existence, columns, and data integrity.
        Returns: (is_valid: bool, message: str)
        """
        if not self.csv_file.exists():
            return False, f"File '{self.csv_file.name}' does not exist."

        try:
            df = pd.read_csv(self.csv_file)
            missing = [c for c in self.columns if c not in df.columns]
            if missing:
                return False, f"Missing required columns: {missing}"

            costs = pd.to_numeric(df["Cost"], errors="coerce")
            negative_count = (costs < 0).sum()
            if negative_count > 0:
                return False, f"Found {negative_count} record(s) with negative cost."

            return True, f"Dataset is valid ({len(df)} records, schema verified)."
        except Exception as e:
            return False, f"Dataset parsing error: {e}"


# Global singleton instance for convenient module-level usage
_DEFAULT_MANAGER = DataManager()

# Module-level convenience functions mirroring DataManager methods
def ensure_directories():
    _DEFAULT_MANAGER.ensure_directories()

def prepare_file(force_reset: bool = False) -> bool:
    return _DEFAULT_MANAGER.prepare_file(force_reset)

def create_dataset(overwrite: bool = False) -> bool:
    return _DEFAULT_MANAGER.create_dataset(overwrite)

def load_data() -> pd.DataFrame:
    return _DEFAULT_MANAGER.load_data()

def save_data(df: pd.DataFrame) -> bool:
    return _DEFAULT_MANAGER.save_data(df)

def validate_dataset_structure() -> tuple:
    return _DEFAULT_MANAGER.validate_structure()


def data_manager_menu():
    """Interactive command-line interface for standalone data management."""
    manager = _DEFAULT_MANAGER
    while True:
        print("\n" + "=" * 48)
        print("          DATA STORAGE & FILE MANAGER")
        print("=" * 48)
        print("1. Initialize / Prepare Dataset File")
        print("2. Reset Dataset to Default 20 Records")
        print("3. Validate Dataset Structure & Schema")
        print("4. View Storage Summary & File Paths")
        print("0. Back / Exit")
        print("=" * 48)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            manager.prepare_file()
            print(f"Dataset ready at: {manager.csv_file}")
        elif choice == "2":
            confirm = input("Reset to original 20 records? All new records will be overwritten (y/n): ").strip().lower()
            if confirm == "y":
                manager.create_dataset(overwrite=True)
                print("Dataset reset successfully!")
            else:
                print("Reset cancelled.")
        elif choice == "3":
            is_valid, msg = manager.validate_structure()
            status = "SUCCESS" if is_valid else "WARNING/ERROR"
            print(f"[{status}] {msg}")
        elif choice == "4":
            df = manager.load_data()
            print(f"\nData Folder   : {manager.data_dir}")
            print(f"CSV Path      : {manager.csv_file}")
            print(f"Reports Folder: {manager.report_dir}")
            print(f"File Exists   : {manager.csv_file.exists()}")
            print(f"Total Records : {len(df)}")
            print(f"Columns       : {', '.join(manager.columns)}")
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please choose 0-4.")


def main():
    data_manager_menu()


if __name__ == "__main__":
    main()
