from typing import Dict
from pandas import DataFrame
from .map import board_map
from .filter import boards_filter


def pipeline(data: Dict[str, DataFrame], section: str) -> DataFrame:
    assignments = data.get('assignments')
    honors_boards = data.get('honors_boards')

    mapped_df = board_map(honors_boards, assignments, section)
    filtered_df = boards_filter(mapped_df)

    return filtered_df
