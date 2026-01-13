# Simple RDBMS - A Relational Database Management System from Scratch

A complete relational database management system built from scratch using Python, featuring SQL-like interface, CRUD operations, indexing, and a Flask web application demonstration.

## 🚀 Features

- **SQL-like Interface**: Support for CREATE, INSERT, SELECT, UPDATE, DELETE, and JOIN operations
- **Data Types**: INT, TEXT, FLOAT with proper validation
- **Constraints**: Primary keys, unique constraints, and NOT NULL constraints
- **Indexing**: Hash-based indexing for fast lookups on indexed columns
- **JOIN Operations**: Inner joins between tables using foreign keys
- **Interactive REPL**: Command-line interface for testing SQL commands
- **Web Demo**: Flask application demonstrating CRUD operations
- **Clean Architecture**: Separation between SQL parsing, database engine, and user interface

## 📁 Project Structure

```
simple-rdbms/
├── rdbms.py              # Core database classes (Table, Column, Index, Database)
├── sql_parser.py         # SQL command parsing and validation
├── database_engine.py    # Query execution engine
├── repl.py              # Interactive command-line interface
├── app.py               # Flask web application
├── templates/           # HTML templates for web app
│   ├── base.html
│   ├── index.html
│   ├── users/
│   │   ├── list.html
│   │   ├── new.html
│   │   └── edit.html
│   ├── tasks/
│   │   ├── list.html
│   │   ├── new.html
│   │   └── edit.html
│   └── demo.html
└── README.md
```

## 🛠️ Installation

1. Clone or download the project files
2. Install Flask for the web demo:
```bash
pip install flask
```

## 💻 Usage

### Interactive REPL

Start the command-line interface:

```bash
python repl.py
```

Example SQL commands:

```sql
-- Create a table
CREATE TABLE users (
    id INT PRIMARY_KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
)

-- Insert data
INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')

-- Select data
SELECT * FROM users
SELECT name FROM users WHERE id = 1

-- Update data
UPDATE users SET name = 'Alice Smith' WHERE id = 1

-- Delete data
DELETE FROM users WHERE id = 1
```

### Web Application

Start the Flask demo:

```bash
python app.py
```

Visit `http://localhost:5000` to access the web interface featuring:
- User management (CRUD operations)
- Task management with user assignments
- SQL query demonstrations
- Real-time database statistics

## 🏗️ Architecture

### Core Components

1. **rdbms.py** - Data structures and storage
   - `Column`: Column definitions with types and constraints
   - `Table`: In-memory table storage with rows and indexes
   - `Index`: Hash-based indexing for fast lookups
   - `Database`: Container for multiple tables

2. **sql_parser.py** - SQL parsing
   - Parses SQL strings into structured command objects
   - Handles CREATE, INSERT, SELECT, UPDATE, DELETE, and JOIN
   - Validates syntax and converts to internal commands

3. **database_engine.py** - Query execution
   - Executes parsed commands against the database
   - Handles constraint validation
   - Manages transactions and error handling

4. **repl.py** - Command-line interface
   - Interactive SQL shell
   - Command history and help system
   - Formatted result display

### Data Model

- **Tables**: Stored in memory as Python objects
- **Rows**: Represented as dictionaries with metadata
- **Indexes**: Hash maps for O(1) lookups on indexed columns
- **Constraints**: Enforced during INSERT and UPDATE operations

## 📊 Supported SQL Features

### Data Definition Language (DDL)

```sql
CREATE TABLE table_name (
    column1 INT PRIMARY_KEY,
    column2 TEXT NOT NULL,
    column3 TEXT UNIQUE,
    column4 FLOAT
)
```

### Data Manipulation Language (DML)

```sql
-- Insert
INSERT INTO table_name (col1, col2) VALUES (value1, value2)

-- Select
SELECT * FROM table_name
SELECT col1, col2 FROM table_name WHERE condition
SELECT * FROM table1 JOIN table2 ON table1.id = table2.foreign_id

-- Update
UPDATE table_name SET col1 = value1, col2 = value2 WHERE condition

-- Delete
DELETE FROM table_name WHERE condition
```

### Data Types

- `INT`: Integer values
- `TEXT`: String values
- `FLOAT`: Floating point numbers

### Constraints

- `PRIMARY_KEY`: Unique identifier (automatically indexed)
- `UNIQUE`: All values must be unique (automatically indexed)
- `NOT NULL`: Column cannot contain NULL values

## 🎯 Learning Objectives

This project demonstrates:

1. **Database Architecture**: How relational databases work internally
2. **SQL Parsing**: Converting SQL strings to executable commands
3. **Data Storage**: In-memory table and index management
4. **Query Processing**: WHERE clause evaluation and JOIN operations
5. **Constraint Enforcement**: Maintaining data integrity
6. **Web Integration**: Using a custom database with web applications

## 🧪 Examples

### Basic Operations

```python
from database_engine import DatabaseEngine

# Create engine
engine = DatabaseEngine()

# Create table
engine.execute("""
    CREATE TABLE users (
        id INT PRIMARY_KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE
    )
""")

# Insert data
engine.execute("INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")

# Query data
result = engine.execute("SELECT * FROM users")
print(result.data)  # [{'id': 1, 'name': 'Alice', 'email': 'alice@example.com', '_row_id': 1}]
```

### JOIN Operations

```sql
-- Create tables
CREATE TABLE users (id INT PRIMARY_KEY, name TEXT NOT NULL)
CREATE TABLE tasks (id INT PRIMARY_KEY, title TEXT, user_id INT)

-- Insert data
INSERT INTO users (id, name) VALUES (1, 'Alice')
INSERT INTO tasks (id, title, user_id) VALUES (1, 'Complete project', 1)

-- Join query
SELECT tasks.title, users.name FROM tasks JOIN users ON tasks.user_id = users.id
```

## 🔧 Advanced Features

### Indexing

The system automatically creates hash-based indexes for:
- Primary key columns
- Columns with UNIQUE constraints

This provides O(1) lookup performance for WHERE clauses on indexed columns.

### Constraint Validation

- Primary key uniqueness is enforced
- Unique constraints prevent duplicate values
- NOT NULL constraints prevent null values
- Foreign key relationships are maintained through application logic

### Error Handling

Comprehensive error handling for:
- SQL syntax errors
- Constraint violations
- Type mismatches
- Missing tables or columns

## 🚀 Running the Demo

1. **Start the REPL**:
   ```bash
   python repl.py
   ```

2. **Start the Web App**:
   ```bash
   python app.py
   # Visit http://localhost:5000
   ```

3. **Try these commands in the REPL**:
   ```sql
   .tables
   CREATE TABLE products (id INT PRIMARY_KEY, name TEXT NOT NULL, price FLOAT)
   INSERT INTO products (id, name, price) VALUES (1, 'Laptop', 999.99)
   SELECT * FROM products
   ```


## 🤝 Contributing

Feel free to extend the system with:
- Additional data types (DATE, BOOLEAN, etc.)
- More SQL features (ORDER BY, GROUP BY, subqueries)
- Persistent storage (file-based or SQLite backend)
- Transaction support
- Advanced indexing (B-tree, composite indexes)

