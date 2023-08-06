from pathlib import Path
from pandas import DataFrame


def boards_dump(df: DataFrame, file_location: Path):
    """
    Dumps the DataFrame to a json file named honors_boards.json at file_location.

    :param df:
    :param file_location: The directory to store the json
    """
    high_honors_file = file_location / 'high_honors_boards.json'
    honors_file = file_location / 'honors_boards.json'
    almost_file = file_location / 'boards.json'
    df.loc[df.is_high_honor].to_json(high_honors_file, orient='records')
    df.loc[df.is_honor].to_json(honors_file, orient='records')
    df.loc[(~df.is_honor) & (~df.is_high_honor)].to_json(almost_file, orient='records')
