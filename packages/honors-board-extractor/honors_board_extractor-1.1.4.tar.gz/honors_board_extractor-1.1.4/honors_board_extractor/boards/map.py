from pandas import DataFrame
from honors_board_extractor.config.constants import *


def board_map(df: DataFrame, assignments: DataFrame, section: str) -> DataFrame:
    """
    Mutates and adds columns to the DataFrame.

    This function will set is_honors to false for every student
    that is high honors. It will add the initials column, the honors
    grade column, and the current subject column.

    Required columns are: is_honors, is_high_honors, school_grade,
    firstname, and lastname.

    Required columns for assignments are user_id and honor_status.honor_grade.
    """
    if section == "math":
        grade_subject_map = AM_GRADE_SUBJECT_MAP
        subject_grade_map = AM_SUBJECT_GRADE_MAP
    elif section in ["la", "voc"]:
        grade_subject_map = AE_GRADE_SUBJECT_MAP
        subject_grade_map = AE_SUBJECT_GRADE_MAP
    else:
        grade_subject_map = GRADE_SUBJECT_MAP
        subject_grade_map = GENERAL_SUBJECT_GRADE_MAP
    return (
        df
        .pipe(_add_initials)
        .pipe(_fix_honors_overlap)
        .pipe(_add_current_subject, subject_grade_map, grade_subject_map)
        .pipe(_add_honors_grade, assignments, subject_grade_map)
        .pipe(_format_start_date)
    )


def _add_initials(df: DataFrame) -> DataFrame:
    return df.assign(
        initials=df.firstname.str.capitalize() + ' ' + df.lastname.str.capitalize().str.get(0) + '.'
    )


def _fix_honors_overlap(df: DataFrame) -> DataFrame:
    ret = df.copy()
    ret.loc[ret.is_high_honor.isna(), 'is_high_honor'] = False
    ret.loc[ret.is_honor.isna(), 'is_honor'] = False
    ret.loc[ret.is_high_honor, 'is_honor'] = False
    ret.is_honor = ret.is_honor.astype('bool')
    ret.is_high_honor = ret.is_high_honor.astype('bool')
    return ret


def _add_current_subject(df: DataFrame, subject_grade_map: dict, grade_subject_map: dict) -> DataFrame:
    return df.assign(
        current_subject=df.current_grade.apply(lambda x: grade_subject_map[x]),
        current_grade=lambda x: x['current_subject'].apply(lambda y: subject_grade_map[y])
    )


def _add_honors_grade(df: DataFrame, assignments: DataFrame, subject_grade_map: dict) -> DataFrame:
    """
    Default behavior is to set missing honor grades to 14. This way
    those students with missing honors grades won't be included in the
    almost honors category.
    """
    ret = df.copy()
    assign = assignments.loc[:, ['user_id', 'honor_status.honor_grade']].copy()
    ret = ret.merge(assign, on='user_id', how='left')
    ret.rename(columns={'honor_status.honor_grade': 'honor_grade'}, inplace=True)
    ret.loc[ret.honor_grade.isna(), 'honor_grade'] = 14
    ret = ret.assign(
        honor_grade=ret.honor_grade.apply(lambda x: subject_grade_map[x])
    )
    return ret


def _format_start_date(df: DataFrame) -> DataFrame:
    return df.assign(
        start_ts=df.start_ts.str.slice(start=0, stop=10)
    )
