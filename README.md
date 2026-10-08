# Meal Plan & Spending Analysis

A professional, modular Python desktop application for tracking daily meal consumption, analyzing food expenditures, managing records, and visualizing spending patterns through both an interactive Command-Line Interface (CLI) and a desktop Tkinter Graphical User Interface (GUI).

---

## 📌 Project Overview

**Meal Plan & Spending Analysis** provides a structured, offline system for managing personal food consumption and budgeting. The project has been refactored from a single script into an enterprise-grade Model/Logic/View desktop architecture, adhering to clean separation of concerns, defensive file handling, and automated unit testing.

---

## 🌟 Key Features

- **Centralized Data Storage Layer (`data_manager.py`)**:
  - Manages the single source of truth at `data/meal_records.csv`.
  - Atomic file writes using temporary swap files (`.tmp`) to prevent corrupted data on unexpected exit.
  - Automatic directory provisioning and missing-file recovery.
  - Full schema and data structure validation.
- **Meal Management & CRUD Logic (`meal_manager.py`)**:
  - Add meal records with auto-generated unique `Meal_ID`s and cost validation.
  - Formatted tabular console viewer for all records.
  - Multi-criteria filtering by meal category (Home, Restaurant, Other) or meal type (Breakfast, Lunch, Dinner).
  - Update and delete operations with ID verification and non-negative constraints.
- **Analytics & Visualizations (`analytics.py`)**:
  - High-performance Pandas calculations: Total spending, average cost, maximum, and minimum expense.
  - Category-wise aggregations: Total spending, average cost, and meal frequencies.
  - Monthly time-series expenditure trends.
  - Pure Matplotlib `Figure` generation (Category Bar Chart and Monthly Trend Line).
  - One-click high-resolution PNG chart export to `reports/charts/`.
- **Desktop Graphical Interface (`gui.py`)**:
  - Intuitive input forms and dropdown controls.
  - Interactive Treeview data table with row selection binding.
  - Responsive search bar filtering.
  - Dedicated modal dialogs for analytical reports.
  - Embedded Matplotlib canvases (`FigureCanvasTkAgg`) rendering charts directly inside desktop windows.
- **Central Application Controller (`main.py`)**:
  - Dependency verification on launch (Tkinter, NumPy, Pandas, Matplotlib).
  - Master menu routing between Meal Management, Analytics, Desktop GUI, and Full Workflow.
  - Independent standalone execution supported across every module.
- **Automated Quality Assurance (`tests/test_app.py`)**:
  - 15 comprehensive unit tests verifying data persistence, CRUD logic, analytics, chart generation, and GUI lifecycle.

---

## 🛠️ Technologies Used

- **Language**: Python 3.10+
- **Data Analysis**: Pandas, NumPy
- **Visualizations**: Matplotlib (embedded via `FigureCanvasTkAgg`)
- **Desktop GUI**: Tkinter & TTK (Standard Library)
- **Path Resolution**: `pathlib` (Platform-independent Windows/macOS/Linux support)
- **Testing**: `unittest`

---

## 📁 Project Structure

```text
Meal-Plan-Spending-Analysis/
│
├── main.py                      # Central launcher & master controller
├── data_manager.py              # Data access layer: CSV I/O, atomic writes, recovery
├── meal_manager.py              # Business logic: Meal CRUD operations & validation
├── analytics.py                 # Analytics layer: Pandas calculations & Matplotlib figures
├── gui.py                       # Presentation layer: Tkinter desktop GUI
│
├── data/
│   └── meal_records.csv         # Single source of truth CSV dataset
│
├── reports/
│   └── charts/                  # Generated PNG visualization exports
│       ├── category_spending.png
│       └── monthly_spending.png
│
├── tests/
│   ├── __init__.py
│   └── test_app.py              # Automated unit test suite (15 tests)
│
├── requirements.txt             # Third-party Python dependencies
├── README.md                    # Project manual & documentation
└── .gitignore                   # Version control ignore rules
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/psbhati2007/Meal-Plan-Spending-Analysis-Mini-project.git
cd Meal-Plan-Spending-Analysis-Mini-project
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Application

### 1. Run the Central Launcher
```bash
python main.py
```

Master application menu:
```text
================================================
         MEAL PLAN & SPENDING ANALYSIS
================================================
1. Meal Management
2. Analysis & Visualization
3. Open Tkinter GUI
4. Run Complete Project
0. Exit
================================================
```

### 2. Standalone Module Execution
Every module is executable on its own:

- **Run Data Storage Layer**:
  ```bash
  python data_manager.py
  ```
- **Run Meal Management (CRUD)**:
  ```bash
  python meal_manager.py
  ```
- **Run Analytics & Visualizations**:
  ```bash
  python analytics.py
  ```
- **Run Desktop GUI Directly**:
  ```bash
  python gui.py
  ```

### 3. Run Automated Unit Tests
```bash
python -m unittest discover -s tests -t .
```

---

## 📊 Dataset Specification (`data/meal_records.csv`)

| Column | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| **`Meal_ID`** | Integer | Unique identifier for each meal record | `1` |
| **`Date`** | String (YYYY-MM-DD) | Date of meal consumption | `2026-10-01` |
| **`Meal`** | String | Meal timing | `Breakfast`, `Lunch`, `Dinner` |
| **`Category`** | String | Source category | `Home`, `Restaurant`, `Other` |
| **`Food_Item`** | String | Dish or meal item name | `Poha`, `Dal Rice` |
| **`Cost`** | Float | Expense incurred in Rs. | `40.0`, `180.0` |

---

## 📄 License
This project is open-source and released under the MIT License.
