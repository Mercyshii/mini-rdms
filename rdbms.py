"""
Simple RDBMS Implementation from Scratch
A minimal relational database management system built with Python
"""

import re
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum


class DataType(Enum):
    """Supported data types in our RDBMS"""
    INT = "INT"
    TEXT = "TEXT"
    FLOAT = "FLOAT"


class Constraint(Enum):
    """Column constraints"""
    PRIMARY_KEY = "PRIMARY_KEY"
    UNIQUE = "UNIQUE"
    NONE = "NONE"


@dataclass
class Column:
    """Represents a column definition in a table"""
    name: str
    data_type: DataType
    constraint: Constraint = Constraint.NONE
    nullable: bool = True
    
    def validate_value(self, value: Any) -> bool:
        """Validate if a value matches the column's data type"""
        if value is None:
            return self.nullable
            
        if self.data_type == DataType.INT:
            return isinstance(value, int)
        elif self.data_type == DataType.TEXT:
            return isinstance(value, str)
        elif self.data_type == DataType.FLOAT:
            return isinstance(value, (int, float))
        return False


class Index:
    """Simple hash-based index for fast lookups"""
    def __init__(self, column_name: str):
        self.column_name = column_name
        self.index: Dict[Any, List[int]] = {}  # value -> list of row_ids
        
    def add(self, value: Any, row_id: int):
        """Add a value to the index"""
        if value not in self.index:
            self.index[value] = []
        self.index[value].append(row_id)
        
    def remove(self, value: Any, row_id: int):
        """Remove a value from the index"""
        if value in self.index and row_id in self.index[value]:
            self.index[value].remove(row_id)
            if not self.index[value]:
                del self.index[value]
                
    def find(self, value: Any) -> List[int]:
        """Find row IDs for a given value"""
        return self.index.get(value, [])


class Table:
    """Represents a database table"""
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.rows: List[Dict[str, Any]] = []
        self.indexes: Dict[str, Index] = {}
        self.next_row_id = 1
        
        # Create indexes for primary keys and unique constraints
        for column in columns:
            if column.constraint in [Constraint.PRIMARY_KEY, Constraint.UNIQUE]:
                self.indexes[column.name] = Index(column.name)
                
    def insert_row(self, values: Dict[str, Any]) -> int:
        """Insert a new row and return its ID"""
        # Validate all values
        for col_name, value in values.items():
            if col_name not in self.columns:
                raise ValueError(f"Unknown column: {col_name}")
            if not self.columns[col_name].validate_value(value):
                raise ValueError(f"Invalid value for column {col_name}: {value}")
                
        # Check constraints
        for col_name, value in values.items():
            column = self.columns[col_name]
            
            # Check primary key uniqueness
            if column.constraint == Constraint.PRIMARY_KEY:
                if value is None:
                    raise ValueError(f"Primary key {col_name} cannot be null")
                if self.indexes[col_name].find(value):
                    raise ValueError(f"Primary key violation: {col_name} = {value}")
                    
            # Check unique constraint
            elif column.constraint == Constraint.UNIQUE and value is not None:
                if self.indexes[col_name].find(value):
                    raise ValueError(f"Unique constraint violation: {col_name} = {value}")
        
        # Create row with default values for missing columns
        row = {'_row_id': self.next_row_id}
        for col_name, column in self.columns.items():
            row[col_name] = values.get(col_name, None)
            
        # Add row to table
        self.rows.append(row)
        row_id = self.next_row_id
        self.next_row_id += 1
        
        # Update indexes
        for col_name, value in values.items():
            if col_name in self.indexes:
                self.indexes[col_name].add(value, row_id)
                
        return row_id
        
    def find_rows(self, conditions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find rows matching given conditions"""
        if not conditions:
            return self.rows.copy()
            
        result = []
        for row in self.rows:
            match = True
            for col_name, value in conditions.items():
                if col_name not in row or row[col_name] != value:
                    match = False
                    break
            if match:
                result.append(row)
        return result
        
    def update_rows(self, conditions: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """Update rows matching conditions and return count of updated rows"""
        updated_count = 0
        rows_to_update = self.find_rows(conditions)
        
        for row in rows_to_update:
            row_id = row['_row_id']
            
            # Validate new values
            for col_name, new_value in updates.items():
                if col_name not in self.columns:
                    raise ValueError(f"Unknown column: {col_name}")
                if not self.columns[col_name].validate_value(new_value):
                    raise ValueError(f"Invalid value for column {col_name}: {new_value}")
            
            # Check constraints for updated values
            for col_name, new_value in updates.items():
                column = self.columns[col_name]
                old_value = row[col_name]
                
                # Only check if value is actually changing
                if old_value == new_value:
                    continue
                    
                # Remove from old index
                if col_name in self.indexes:
                    self.indexes[col_name].remove(old_value, row_id)
                
                # Check constraints
                if column.constraint == Constraint.PRIMARY_KEY:
                    if new_value is None:
                        raise ValueError(f"Primary key {col_name} cannot be null")
                    if self.indexes[col_name].find(new_value):
                        raise ValueError(f"Primary key violation: {col_name} = {new_value}")
                        
                elif column.constraint == Constraint.UNIQUE and new_value is not None:
                    if self.indexes[col_name].find(new_value):
                        raise ValueError(f"Unique constraint violation: {col_name} = {new_value}")
                
                # Update row
                row[col_name] = new_value
                
                # Add to new index
                if col_name in self.indexes:
                    self.indexes[col_name].add(new_value, row_id)
                    
            updated_count += 1
            
        return updated_count
        
    def delete_rows(self, conditions: Dict[str, Any]) -> int:
        """Delete rows matching conditions and return count of deleted rows"""
        rows_to_delete = self.find_rows(conditions)
        deleted_count = 0
        
        for row in rows_to_delete:
            row_id = row['_row_id']
            
            # Remove from indexes
            for col_name in self.indexes:
                if col_name in row:
                    self.indexes[col_name].remove(row[col_name], row_id)
            
            # Remove from table
            self.rows.remove(row)
            deleted_count += 1
            
        return deleted_count


class Database:
    """Main database engine that manages tables"""
    def __init__(self):
        self.tables: Dict[str, Table] = {}
        
    def create_table(self, name: str, columns: List[Column]) -> Table:
        """Create a new table"""
        if name in self.tables:
            raise ValueError(f"Table {name} already exists")
            
        table = Table(name, columns)
        self.tables[name] = table
        return table
        
    def get_table(self, name: str) -> Table:
        """Get a table by name"""
        if name not in self.tables:
            raise ValueError(f"Table {name} does not exist")
        return self.tables[name]
        
    def list_tables(self) -> List[str]:
        """List all table names"""
        return list(self.tables.keys())
