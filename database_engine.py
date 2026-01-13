"""
Database Engine for Simple RDBMS
Executes SQL commands and manages the database operations
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

from rdbms import Database, Table, Column, DataType, Constraint
from sql_parser import SQLParser, CreateTableCommand, InsertCommand, SelectCommand, UpdateCommand, DeleteCommand


@dataclass
class QueryResult:
    """Represents the result of a query"""
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    affected_rows: int = 0


class DatabaseEngine:
    """Main database engine that executes SQL commands"""
    
    def __init__(self):
        self.database = Database()
        self.parser = SQLParser()
    
    def execute(self, sql: str) -> QueryResult:
        """Execute a SQL command and return the result"""
        try:
            command = self.parser.parse(sql)
            
            if isinstance(command, CreateTableCommand):
                return self._execute_create_table(command)
            elif isinstance(command, InsertCommand):
                return self._execute_insert(command)
            elif isinstance(command, SelectCommand):
                return self._execute_select(command)
            elif isinstance(command, UpdateCommand):
                return self._execute_update(command)
            elif isinstance(command, DeleteCommand):
                return self._execute_delete(command)
            else:
                return QueryResult(False, f"Unsupported command type: {type(command)}")
                
        except Exception as e:
            return QueryResult(False, f"Error: {str(e)}")
    
    def _execute_create_table(self, command: CreateTableCommand) -> QueryResult:
        """Execute CREATE TABLE command"""
        try:
            table = self.database.create_table(command.table_name, command.columns)
            
            # Create a nice message showing the table structure
            column_info = []
            for col in command.columns:
                col_str = f"{col.name} {col.data_type.value}"
                if col.constraint == Constraint.PRIMARY_KEY:
                    col_str += " PRIMARY KEY"
                elif col.constraint == Constraint.UNIQUE:
                    col_str += " UNIQUE"
                if not col.nullable:
                    col_str += " NOT NULL"
                column_info.append(col_str)
            
            message = f"Table '{command.table_name}' created with columns: {', '.join(column_info)}"
            return QueryResult(True, message)
            
        except Exception as e:
            return QueryResult(False, f"Failed to create table: {str(e)}")
    
    def _execute_insert(self, command: InsertCommand) -> QueryResult:
        """Execute INSERT command"""
        try:
            table = self.database.get_table(command.table_name)
            row_id = table.insert_row(command.values)
            
            message = f"Inserted 1 row into '{command.table_name}' (ID: {row_id})"
            return QueryResult(True, message, affected_rows=1)
            
        except Exception as e:
            return QueryResult(False, f"Failed to insert: {str(e)}")
    
    def _execute_select(self, command: SelectCommand) -> QueryResult:
        """Execute SELECT command"""
        try:
            table = self.database.get_table(command.table_name)
            
            # Handle JOIN
            if command.join_table:
                return self._execute_join_select(command)
            
            # Get rows matching WHERE conditions
            rows = table.find_rows(command.where_conditions)
            
            # Filter columns if not SELECT *
            if command.columns != ['*']:
                filtered_rows = []
                for row in rows:
                    filtered_row = {}
                    for col in command.columns:
                        if col in row:
                            filtered_row[col] = row[col]
                    filtered_rows.append(filtered_row)
                rows = filtered_rows
            
            message = f"Selected {len(rows)} rows from '{command.table_name}'"
            return QueryResult(True, message, data=rows)
            
        except Exception as e:
            return QueryResult(False, f"Failed to select: {str(e)}")
    
    def _execute_join_select(self, command: SelectCommand) -> QueryResult:
        """Execute SELECT with JOIN"""
        try:
            left_table = self.database.get_table(command.table_name)
            right_table = self.database.get_table(command.join_table)
            
            left_rows = left_table.find_rows()
            right_rows = right_table.find_rows()
            
            # Simple inner join implementation
            joined_rows = []
            
            for left_row in left_rows:
                for right_row in right_rows:
                    # Check join conditions
                    match = True
                    if command.join_conditions:
                        for col, value in command.join_conditions.items():
                            # Handle table.column notation
                            if '.' in col:
                                table_name, col_name = col.split('.')
                                if table_name == command.table_name:
                                    if left_row.get(col_name) != value:
                                        match = False
                                        break
                                elif table_name == command.join_table:
                                    if right_row.get(col_name) != value:
                                        match = False
                                        break
                            else:
                                # Try to find the column in either table
                                if col in left_row and left_row[col] != value:
                                    match = False
                                    break
                                elif col in right_row and right_row[col] != value:
                                    match = False
                                    break
                    
                    if match:
                        # Apply WHERE conditions
                        if command.where_conditions:
                            where_match = True
                            for col, value in command.where_conditions.items():
                                if '.' in col:
                                    table_name, col_name = col.split('.')
                                    if table_name == command.table_name:
                                        if left_row.get(col_name) != value:
                                            where_match = False
                                            break
                                    elif table_name == command.join_table:
                                        if right_row.get(col_name) != value:
                                            where_match = False
                                            break
                                else:
                                    if col in left_row and left_row[col] != value:
                                        where_match = False
                                        break
                                    elif col in right_row and right_row[col] != value:
                                        where_match = False
                                        break
                            
                            if not where_match:
                                continue
                        
                        # Merge rows
                        joined_row = {}
                        
                        # Add left table columns with prefix
                        for col, value in left_row.items():
                            if col != '_row_id':
                                joined_row[f"{command.table_name}.{col}"] = value
                        
                        # Add right table columns with prefix
                        for col, value in right_row.items():
                            if col != '_row_id':
                                joined_row[f"{command.join_table}.{col}"] = value
                        
                        joined_rows.append(joined_row)
            
            # Filter columns if not SELECT *
            if command.columns != ['*']:
                filtered_rows = []
                for row in joined_rows:
                    filtered_row = {}
                    for col in command.columns:
                        if col in row:
                            filtered_row[col] = row[col]
                    filtered_rows.append(filtered_row)
                joined_rows = filtered_rows
            
            message = f"Selected {len(joined_rows)} rows from JOIN of '{command.table_name}' and '{command.join_table}'"
            return QueryResult(True, message, data=joined_rows)
            
        except Exception as e:
            return QueryResult(False, f"Failed to join: {str(e)}")
    
    def _execute_update(self, command: UpdateCommand) -> QueryResult:
        """Execute UPDATE command"""
        try:
            table = self.database.get_table(command.table_name)
            updated_count = table.update_rows(command.where_conditions, command.set_values)
            
            message = f"Updated {updated_count} rows in '{command.table_name}'"
            return QueryResult(True, message, affected_rows=updated_count)
            
        except Exception as e:
            return QueryResult(False, f"Failed to update: {str(e)}")
    
    def _execute_delete(self, command: DeleteCommand) -> QueryResult:
        """Execute DELETE command"""
        try:
            table = self.database.get_table(command.table_name)
            deleted_count = table.delete_rows(command.where_conditions)
            
            message = f"Deleted {deleted_count} rows from '{command.table_name}'"
            return QueryResult(True, message, affected_rows=deleted_count)
            
        except Exception as e:
            return QueryResult(False, f"Failed to delete: {str(e)}")
    
    def get_table_info(self, table_name: str) -> QueryResult:
        """Get information about a table"""
        try:
            table = self.database.get_table(table_name)
            
            info = {
                'name': table.name,
                'columns': [],
                'row_count': len(table.rows),
                'indexes': list(table.indexes.keys())
            }
            
            for col_name, column in table.columns.items():
                col_info = {
                    'name': col_name,
                    'type': column.data_type.value,
                    'constraint': column.constraint.value,
                    'nullable': column.nullable
                }
                info['columns'].append(col_info)
            
            return QueryResult(True, f"Table info for '{table_name}'", data=[info])
            
        except Exception as e:
            return QueryResult(False, f"Failed to get table info: {str(e)}")
    
    def list_tables(self) -> QueryResult:
        """List all tables in the database"""
        try:
            tables = self.database.list_tables()
            table_data = [{'name': table} for table in tables]
            
            message = f"Found {len(tables)} tables"
            return QueryResult(True, message, data=table_data)
            
        except Exception as e:
            return QueryResult(False, f"Failed to list tables: {str(e)}")
