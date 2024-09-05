import csv
from pathlib import Path
from typing import List, Dict, Any, Callable
from app.models.abstract import AbstractDecisionTable
from app.models.decision_data_holder import DecisionDataHolder

class DecisionTable(AbstractDecisionTable):
    def __init__(self, rows: List[Dict[str, str]], separator_index: int):
        self.rows = rows
        self.separator_index = separator_index
        self.input_columns = self._get_columns(is_input=True)
        self.output_columns = self._get_columns(is_input=False)

    @staticmethod
    def create_from_csv(filepath: Path) -> "DecisionTable":
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            rows = list(reader)
            separator_index = list(rows[0].keys()).index('*')
        return DecisionTable(rows, separator_index)

    def evaluate(self, ddh: DecisionDataHolder) -> bool:
        for row in self.rows:
            if self._row_matches(row, ddh):
                self._apply_outputs(row, ddh)
                return True
        return False

    def _get_columns(self, is_input: bool) -> List[str]:
        columns = list(self.rows[0].keys())
        if is_input:
            return columns[:self.separator_index]
        else:
            return columns[self.separator_index + 1:]

    def _row_matches(self, row: Dict[str, str], ddh: DecisionDataHolder) -> bool:
        for column in self.input_columns:
            if not self._condition_matches(row[column], ddh.get(column)):
                return False
        return True

    def _condition_matches(self, condition: str, value: Any) -> bool:
        condition = condition.strip()
        if condition.startswith('='):
            return self._equals(condition[1:], value)
        elif condition.startswith('>'):
            return self._greater_than(condition[1:], value)
        elif condition.startswith('<='):
            return self._less_than_or_equal(condition[2:], value)
        else:
            raise ValueError(f"Unsupported condition: {condition}")

    def _equals(self, condition: str, value: Any) -> bool:
        if condition.lower() == 'true':
            return value is True
        elif condition.lower() == 'false':
            return value is False
        else:
            return str(value) == condition

    def _greater_than(self, condition: str, value: Any) -> bool:
        return float(value) > float(condition)

    def _less_than_or_equal(self, condition: str, value: Any) -> bool:
        return float(value) <= float(condition)

    def _apply_outputs(self, row: Dict[str, str], ddh: DecisionDataHolder) -> None:
        for column in self.output_columns:
            ddh[column] = row[column].strip('"')