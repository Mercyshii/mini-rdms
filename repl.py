"""
Interactive REPL (Read-Eval-Print-Loop) for Simple RDBMS
Provides a command-line interface for executing SQL commands
"""

import sys
import traceback
from typing import Optional

from database_engine import DatabaseEngine, QueryResult


class RDBMSRepl:
    """Interactive REPL for the RDBMS"""
    
    def __init__(self):
        self.engine = DatabaseEngine()
        self.running = True
        self.history = []
        
        # Welcome message
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║           Simple RDBMS - Interactive SQL Shell              ║")
        print("║                                                              ║")
        print("║  Supported Commands:                                        ║")
        print("║  • CREATE TABLE table_name (col1 TYPE, col2 TYPE, ...)      ║")
        print("║  • INSERT INTO table_name (col1, col2) VALUES (val1, val2) ║")
        print("║  • SELECT * FROM table_name [WHERE conditions]              ║")
        print("║  • SELECT col1, col2 FROM table_name [WHERE conditions]    ║")
        print("║  • SELECT * FROM table1 JOIN table2 ON table1.id = table2.id║")
        print("║  • UPDATE table_name SET col1 = val1, col2 = val2 [WHERE]   ║")
        print("║  • DELETE FROM table_name [WHERE conditions]                ║")
        print("║                                                              ║")
        print("║  Special Commands:                                         ║")
        print("║  • .tables - List all tables                               ║")
        print("║  • .schema table_name - Show table structure              ║")
        print("║  • .help - Show this help                                  ║")
        print("║  • .exit or .quit - Exit the REPL                         ║")
        print("║  • .history - Show command history                         ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
    
    def run(self):
        """Start the REPL loop"""
        while self.running:
            try:
                # Get user input
                command = self._get_input()
                
                if not command.strip():
                    continue
                
                # Add to history
                self.history.append(command)
                
                # Handle special commands
                if command.startswith('.'):
                    self._handle_special_command(command)
                    continue
                
                # Execute SQL command
                result = self.engine.execute(command)
                self._display_result(result)
                
            except KeyboardInterrupt:
                print("\nUse .exit to quit")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                traceback.print_exc()
    
    def _get_input(self) -> str:
        """Get input from user with prompt"""
        try:
            return input("sql> ").strip()
        except EOFError:
            return ".exit"
    
    def _handle_special_command(self, command: str):
        """Handle special REPL commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd in ['.exit', '.quit']:
            self.running = False
            print("Goodbye!")
            
        elif cmd == '.help':
            self._show_help()
            
        elif cmd == '.tables':
            result = self.engine.list_tables()
            self._display_result(result)
            
        elif cmd == '.schema':
            if len(parts) < 2:
                print("Usage: .schema table_name")
                return
            
            table_name = parts[1]
            result = self.engine.get_table_info(table_name)
            self._display_result(result)
            
        elif cmd == '.history':
            self._show_history()
            
        else:
            print(f"Unknown command: {command}")
            print("Type .help for available commands")
    
    def _display_result(self, result: QueryResult):
        """Display query result in a formatted way"""
        if result.success:
            print(f"✓ {result.message}")
            
            if result.data:
                self._display_table(result.data)
                
            if result.affected_rows > 0:
                print(f"Rows affected: {result.affected_rows}")
        else:
            print(f"✗ {result.message}")
        
        print()
    
    def _display_table(self, data: list):
        """Display tabular data in a formatted table"""
        if not data:
            return
        
        # Get all column names
        columns = list(data[0].keys())
        
        # Calculate column widths
        widths = {}
        for col in columns:
            widths[col] = max(len(str(col)), 8)  # Minimum width of 8
            
        for row in data:
            for col in columns:
                value = str(row.get(col, 'NULL'))
                widths[col] = max(widths[col], len(value))
        
        # Create separator line
        separator = "+" + "+".join("-" * (widths[col] + 2) for col in columns) + "+"
        
        # Print header
        print(separator)
        header = "|" + "|".join(f" {col:^{widths[col]}} " for col in columns) + "|"
        print(header)
        print(separator)
        
        # Print rows
        for row in data:
            row_str = "|" + "|".join(f" {str(row.get(col, 'NULL')):^{widths[col]}} " for col in columns) + "|"
            print(row_str)
        
        print(separator)
        print(f"({len(data)} rows)")
    
    def _show_help(self):
        """Show help information"""
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                          HELP                                ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║ SQL Commands:                                               ║")
        print("║                                                              ║")
        print("║ CREATE TABLE:                                               ║")
        print("║   CREATE TABLE users (                                      ║")
        print("║     id INT PRIMARY_KEY,                                     ║")
        print("║     name TEXT NOT NULL,                                     ║")
        print("║     email TEXT UNIQUE                                       ║")
        print("║   )                                                         ║")
        print("║                                                              ║")
        print("║ INSERT:                                                     ║")
        print("║   INSERT INTO users (name, email) VALUES ('Alice', 'a@e.com')║")
        print("║                                                              ║")
        print("║ SELECT:                                                     ║")
        print("║   SELECT * FROM users                                       ║")
        print("║   SELECT name FROM users WHERE id = 1                       ║")
        print("║                                                              ║")
        print("║ UPDATE:                                                     ║")
        print("║   UPDATE users SET name = 'Bob' WHERE id = 1               ║")
        print("║                                                              ║")
        print("║ DELETE:                                                     ║")
        print("║   DELETE FROM users WHERE id = 1                            ║")
        print("║                                                              ║")
        print("║ JOIN:                                                       ║")
        print("║   SELECT * FROM users JOIN posts ON users.id = posts.user_id ║")
        print("║                                                              ║")
        print("║ Special Commands:                                           ║")
        print("║   .tables      - List all tables                           ║")
        print("║   .schema name - Show table structure                      ║")
        print("║   .history     - Show command history                       ║")
        print("║   .exit/.quit  - Exit the REPL                             ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
    
    def _show_history(self):
        """Show command history"""
        print("Command History:")
        print("-" * 50)
        for i, cmd in enumerate(self.history, 1):
            print(f"{i:3d}: {cmd}")
        print()


def main():
    """Main entry point for the REPL"""
    repl = RDBMSRepl()
    repl.run()


if __name__ == "__main__":
    main()
