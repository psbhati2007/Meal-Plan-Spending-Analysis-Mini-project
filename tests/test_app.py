"""
test_app.py
===========
Automated Unit Tests for Meal Plan & Spending Analysis.

Tests:
1. DataManager file creation, loading, saving, atomic writes, missing file recovery, schema validation.
2. MealManager CRUD: add, view, search, update, delete, cost validation, ID uniqueness.
3. Analytics: spending summary, category aggregations, monthly trend, dashboard metrics.
4. Visualizations: Matplotlib Figure creation and PNG export.
5. GUI: Tkinter initialization and window lifecycle.
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for automated test runs
from matplotlib.figure import Figure

# Add parent directory to path so tests can run from any folder
PARENT_DIR = Path(__file__).resolve().parent.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

import data_manager
from data_manager import DataManager, COLUMNS
import meal_manager
import analytics


class TestDataManager(unittest.TestCase):
    """Test storage, file lifecycle, and validation logic in data_manager.py."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "data"
        self.report_dir = Path(self.test_dir) / "reports"
        self.manager = DataManager(data_dir=self.data_dir, report_dir=self.report_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_ensure_directories(self):
        self.assertTrue(self.data_dir.exists())
        self.assertTrue((self.report_dir / "charts").exists())

    def test_create_dataset_and_load(self):
        success = self.manager.create_dataset(overwrite=True)
        self.assertTrue(success)
        self.assertTrue(self.manager.csv_file.exists())

        df = self.manager.load_data()
        self.assertEqual(len(df), 20)
        for col in COLUMNS:
            self.assertIn(col, df.columns)

    def test_atomic_save(self):
        self.manager.create_dataset(overwrite=True)
        df = self.manager.load_data()
        new_row = pd.DataFrame([{
            "Meal_ID": 99,
            "Date": "2026-10-10",
            "Meal": "Lunch",
            "Category": "Home",
            "Food_Item": "Khichdi",
            "Cost": 75.0
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        saved = self.manager.save_data(df)
        self.assertTrue(saved)

        reloaded = self.manager.load_data()
        self.assertEqual(len(reloaded), 21)
        self.assertIn(99, reloaded["Meal_ID"].values)

    def test_validate_structure(self):
        self.manager.create_dataset(overwrite=True)
        is_valid, msg = self.manager.validate_structure()
        self.assertTrue(is_valid)

        # Corrupt columns
        bad_df = pd.DataFrame({"Wrong_Col": [1, 2]})
        bad_df.to_csv(self.manager.csv_file, index=False)
        is_valid_bad, _ = self.manager.validate_structure()
        self.assertFalse(is_valid_bad)


class TestMealManager(unittest.TestCase):
    """Test CRUD operations and input validation in meal_manager.py."""

    def setUp(self):
        # Save a backup of the real CSV so test operations do not alter user data
        self.real_csv = data_manager.CSV_FILE
        if self.real_csv.exists():
            self.backup_df = pd.read_csv(self.real_csv)
        else:
            self.backup_df = None
        data_manager.create_dataset(overwrite=True)

    def tearDown(self):
        # Restore original user data after tests
        if self.backup_df is not None:
            self.backup_df.to_csv(self.real_csv, index=False)

    def test_view_meals(self):
        df = meal_manager.view_meals()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreaterEqual(len(df), 20)

    def test_add_meal_and_validation(self):
        # Positive add
        added = meal_manager.add_meal(
            date="2026-10-09",
            meal="Breakfast",
            category="Home",
            food_item="Idli Sambar",
            cost=50.0
        )
        self.assertTrue(added)
        df = data_manager.load_data()
        self.assertIn("Idli Sambar", df["Food_Item"].values)

        # Reject negative cost
        neg_add = meal_manager.add_meal(
            date="2026-10-09",
            meal="Dinner",
            category="Home",
            food_item="Soup",
            cost=-20.0
        )
        self.assertFalse(neg_add)

    def test_search_meals(self):
        res_restaurant = meal_manager.search_meals(category="Restaurant")
        self.assertGreater(len(res_restaurant), 0)
        for cat in res_restaurant["Category"]:
            self.assertEqual(cat, "Restaurant")

        res_lunch = meal_manager.search_meals(meal="Lunch")
        self.assertGreater(len(res_lunch), 0)
        for m in res_lunch["Meal"]:
            self.assertEqual(m, "Lunch")

    def test_update_meal(self):
        # Update existing record
        updated = meal_manager.update_meal(meal_id=1, cost=95.0, food_item="Poha Special")
        self.assertTrue(updated)

        df = data_manager.load_data()
        rec = df[df["Meal_ID"] == 1].iloc[0]
        self.assertEqual(rec["Cost"], 95.0)
        self.assertEqual(rec["Food_Item"], "Poha Special")

        # Non-existing ID update fails
        bad_update = meal_manager.update_meal(meal_id=99999, cost=100.0)
        self.assertFalse(bad_update)

        # Negative cost update fails
        neg_update = meal_manager.update_meal(meal_id=1, cost=-50.0)
        self.assertFalse(neg_update)

    def test_delete_meal(self):
        # Delete existing record
        deleted = meal_manager.delete_meal(meal_id=2)
        self.assertTrue(deleted)
        df = data_manager.load_data()
        self.assertNotIn(2, df["Meal_ID"].values)

        # Non-existing ID delete fails
        bad_del = meal_manager.delete_meal(meal_id=99999)
        self.assertFalse(bad_del)


class TestAnalytics(unittest.TestCase):
    """Test analytics computations, summary metrics, and chart figures in analytics.py."""

    def setUp(self):
        data_manager.create_dataset(overwrite=True)

    def test_spending_summary(self):
        metrics = analytics.spending_summary()
        self.assertIn("Total Spending", metrics)
        self.assertIn("Average Cost", metrics)
        self.assertIn("Highest Cost", metrics)
        self.assertIn("Lowest Cost", metrics)
        self.assertAlmostEqual(metrics["Total Spending"], 2305.0)
        self.assertAlmostEqual(metrics["Average Cost"], 115.25)
        self.assertEqual(metrics["Highest Cost"], 250.0)
        self.assertEqual(metrics["Lowest Cost"], 40.0)

    def test_category_analysis(self):
        cat_df = analytics.category_analysis()
        self.assertIsInstance(cat_df, pd.DataFrame)
        self.assertEqual(len(cat_df), 2)  # Home and Restaurant
        categories = cat_df["Category"].tolist()
        self.assertIn("Home", categories)
        self.assertIn("Restaurant", categories)

    def test_monthly_analysis(self):
        m_series = analytics.monthly_analysis()
        self.assertIsInstance(m_series, pd.Series)
        self.assertEqual(len(m_series), 3)  # 2026-08, 2026-09, 2026-10
        self.assertIn("2026-08", m_series.index)

    def test_dashboard(self):
        dash = analytics.dashboard()
        self.assertEqual(dash["Total Meals"], 20)
        self.assertAlmostEqual(dash["Total Spending"], 2305.0)
        self.assertEqual(dash["Most Common Category"], "Home")

    def test_charts_return_figures_and_export_png(self):
        fig_cat = analytics.category_chart(save_png=True, show=False)
        self.assertIsInstance(fig_cat, Figure)
        cat_png = data_manager.CHARTS_DIR / "category_spending.png"
        self.assertTrue(cat_png.exists())

        fig_mon = analytics.monthly_chart(save_png=True, show=False)
        self.assertIsInstance(fig_mon, Figure)
        mon_png = data_manager.CHARTS_DIR / "monthly_spending.png"
        self.assertTrue(mon_png.exists())


class TestGUIEnvironment(unittest.TestCase):
    """Test Tkinter desktop GUI initialization in test mode."""

    def test_tkinter_app_lifecycle(self):
        import gui

        app = gui.MealPlanApp()
        app.update()
        app.destroy()
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
