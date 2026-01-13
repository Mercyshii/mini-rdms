"""
SQL Parser for Simple RDBMS
Handles parsing of basic SQL commands into structured operations
"""

import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from rdbms import DataType, Constraint, Column


class CommandType(Enum):
    """Types of SQL commands"""
    CREATE_TABLE = "CREATE_TABLE"
    INSERT = "INSERT"
    SELECT = "SELECT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    JOIN = "JOIN"


@dataclass
class CreateTableCommand:
    """Command for creating a table"""
    table_name: str
    columns: List[Column]


@dataclass
class InsertCommand:
    """Command for inserting data"""
    table_name: str
    values: Dict[str, Any]


@dataclass
class SelectCommand:
    """Command for selecting data"""
    table_name: str
    columns: List[str]  # * or list of column names
    where_conditions: Optional[Dict[str, Any]] = None
    join_table: Optional[str] = None
    join_conditions: Optional[Dict[str, Any]] = None


@dataclass
class UpdateCommand:
    """Command for updating data"""
    table_name: str
    set_values: Dict[str, Any]
    where_conditions: Optional[Dict[str, Any]] = None


@dataclass
class DeleteCommand:
    """Command for deleting data"""
    table_name: str
    where_conditions: Optional[Dict[str, Any]] = None


class SQLParser:
    """Simple SQL parser for basic commands"""
    
    def __init__(self):
        self.patterns = {
            'create_table': re.compile(
                r'^CREATE\s+TABLE\s+(\w+)\s*\(\s*(.+?)\s*\)$', 
                re.IGNORECASE
            ),
            'insert': re.compile(
                r'^INSERT\s+INTO\s+(\w+)\s*\((.*?)\)\s*VALUES\s*\((.*?)\)$', 
                re.IGNORECASE
            ),
            'select': re.compile(
                r'^SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+?))?(?:\s+JOIN\s+(\w+)\s+ON\s+(.+?))?$', 
                re.IGNORECASE
            ),
            'update': re.compile(
                r'^UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+?))?$', 
                re.IGNORECASE
            ),
            'delete': re.compile(
                r'^DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+?))?$', 
                re.IGNORECASE
            )
        }
    
    def parse(self, sql: str) -> Union[CreateTableCommand, InsertCommand, SelectCommand, 
                                      UpdateCommand, DeleteCommand]:
        """Parse a SQL string into a command object"""
        # Normalize SQL - remove extra whitespace and newlines
        sql = ' '.join(sql.split()).strip()
        
        # Try to match each command type
        for command_type, pattern in self.patterns.items():
            match = pattern.match(sql)
            if match:
                if command_type == 'create_table':
                    return self._parse_create_table(match)
                elif command_type == 'insert':
                    return self._parse_insert(match)
                elif command_type == 'select':
                    return self._parse_select(match)
                elif command_type == 'update':
                    return self._parse_update(match)
                elif command_type == 'delete':
                    return self._parse_delete(match)
        
        raise ValueError(f"Unsupported SQL syntax: {sql}")
    
    def _parse_create_table(self, match) -> CreateTableCommand:
        """Parse CREATE TABLE command"""
        table_name = match.group(1)
        columns_str = match.group(2)
        
        columns = []
        column_defs = [col.strip() for col in columns_str.split(',')]
        
        for col_def in column_defs:
            parts = col_def.split()
            if len(parts) < 2:
                raise ValueError(f"Invalid column definition: {col_def}")
            
            col_name = parts[0]
            col_type_str = parts[1].upper()
            
            # Parse data type
            if col_type_str == 'INT':
                data_type = DataType.INT
            elif col_type_str == 'TEXT':
                data_type = DataType.TEXT
            elif col_type_str == 'FLOAT':
                data_type = DataType.FLOAT
            else:
                raise ValueError(f"Unsupported data type: {col_type_str}")
            
            # Parse constraints
            constraint = Constraint.NONE
            nullable = True
            
            for part in parts[2:]:
                part_upper = part.upper()
                if part_upper == 'PRIMARY_KEY' or part_upper == 'PRIMARY':
                    constraint = Constraint.PRIMARY_KEY
                    nullable = False
                elif part_upper == 'UNIQUE':
                    constraint = Constraint.UNIQUE
                elif part_upper == 'NOT' and len(parts) > parts.index(part) + 1 and parts[parts.index(part) + 1].upper() == 'NULL':
                    nullable = False
            
            columns.append(Column(col_name, data_type, constraint, nullable))
        
        return CreateTableCommand(table_name, columns)
    
    def _parse_insert(self, match) -> InsertCommand:
        """Parse INSERT command"""
        table_name = match.group(1)
        columns_str = match.group(2)
        values_str = match.group(3)
        
        columns = [col.strip() for col in columns_str.split(',')]
        values = self._parse_values(values_str)
        
        if len(columns) != len(values):
            raise ValueError("Number of columns doesn't match number of values")
        
        values_dict = dict(zip(columns, values))
        return InsertCommand(table_name, values_dict)
    
    def _parse_select(self, match) -> SelectCommand:
        """Parse SELECT command"""
        columns_str = match.group(1).strip()
        table_name = match.group(2)
        where_str = match.group(3)
        join_table = match.group(4)
        join_condition_str = match.group(5)
        
        # Parse columns
        if columns_str == '*':
            columns = ['*']
        else:
            columns = [col.strip() for col in columns_str.split(',')]
        
        # Parse WHERE conditions
        where_conditions = None
        if where_str:
            where_conditions = self._parse_conditions(where_str)
        
        # Parse JOIN conditions
        join_conditions = None
        if join_condition_str:
            join_conditions = self._parse_conditions(join_condition_str)
        
        return SelectCommand(
            table_name=table_name,
            columns=columns,
            where_conditions=where_conditions,
            join_table=join_table,
            join_conditions=join_conditions
        )
    
    def _parse_update(self, match) -> UpdateCommand:
        """Parse UPDATE command"""
        table_name = match.group(1)
        set_str = match.group(2)
        where_str = match.group(3)
        
        # Parse SET values
        set_values = {}
        set_pairs = [pair.strip() for pair in set_str.split(',')]
        
        for pair in set_pairs:
            if '=' not in pair:
                raise ValueError(f"Invalid SET clause: {pair}")
            
            col, value = pair.split('=', 1)
            set_values[col.strip()] = self._parse_value(value.strip())
        
        # Parse WHERE conditions
        where_conditions = None
        if where_str:
            where_conditions = self._parse_conditions(where_str)
        
        return UpdateCommand(table_name, set_values, where_conditions)
    
    def _parse_delete(self, match) -> DeleteCommand:
        """Parse DELETE command"""
        table_name = match.group(1)
        where_str = match.group(2)
        
        # Parse WHERE conditions
        where_conditions = None
        if where_str:
            where_conditions = self._parse_conditions(where_str)
        
        return DeleteCommand(table_name, where_conditions)
    
    def _parse_conditions(self, conditions_str: str) -> Dict[str, Any]:
        """Parse WHERE conditions into a dictionary"""
        conditions = {}
        
        # Simple parsing for AND conditions only
        and_parts = [part.strip() for part in conditions_str.split('AND')]
        
        for part in and_parts:
            if '=' not in part:
                raise ValueError(f"Invalid condition: {part}")
            
            col, value = part.split('=', 1)
            conditions[col.strip()] = self._parse_value(value.strip())
        
        return conditions
    
    def _parse_values(self, values_str: str) -> List[Any]:
        """Parse a comma-separated list of values"""
        values = []
        
        # Simple parsing - split by comma and handle quotes
        parts = []
        current = ''
        in_quotes = False
        
        i = 0
        while i < len(values_str):
            char = values_str[i]
            
            if char == "'" and (i == 0 or values_str[i-1] != '\\'):
                in_quotes = not in_quotes
                current += char
            elif char == ',' and not in_quotes:
                parts.append(current.strip())
                current = ''
            else:
                current += char
            
            i += 1
        
        if current:
            parts.append(current.strip())
        
        # Parse each value
        for part in parts:
            values.append(self._parse_value(part))
        
        return values
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse a single value (string, number, or NULL)"""
        value_str = value_str.strip()
        
        # Handle NULL
        if value_str.upper() == 'NULL':
            return None
        
        # Handle quoted strings
        if value_str.startswith("'") and value_str.endswith("'"):
            # Remove quotes and unescape
            return value_str[1:-1].replace("''", "'")
        
        # Handle numbers
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass
        
        # Default to string
        return value_str
