from pandas import DataFrame


def boards_filter(df: DataFrame) -> DataFrame:
    """
    This will handle filtering out the necessary columns and rows.

    This function will remove any non-honors student who's school grade
    is more than one grade below their honors grade, and will remove all
    columns that are not in the _final_columns list in the filter.py file.

    The required columns are: everything in _final_columns in filter.py and
    school_grade.
    """
    return (
        df
        .pipe(_filter_to_honors_and_almost_honors)
        .pipe(_remove_columns)
    )


_final_columns = [
    'user_id',
    'region',
    'initials',
    'start_ts',
    'current_subject',
    'current_grade',
    'school',
    'school_grade',
    'honor_grade',
    'is_honor',
    'is_high_honor',
]


def _filter_to_honors_and_almost_honors(df: DataFrame) -> DataFrame:
    mask = df.is_honor | df.is_high_honor | (df.honor_grade - df.current_grade <= 1)
    return df.loc[mask].copy()


def _remove_columns(df: DataFrame) -> DataFrame:
    return df.loc[:, _final_columns].copy()
