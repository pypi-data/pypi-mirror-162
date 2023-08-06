from pandas import DataFrame
import pandas as pd
import motor.motor_asyncio as aio_motor
from datetime import date, timedelta
from honors_board_extractor.config.constants import AE_GRADE_SUBJECT_MAP


_assignment_projection = {
    '_id': 0,
    'user_id': 1,
    'honor_status.honor_grade': 1,
}


_la_assignment_projection = {
    '_id': 0,
    'user_id': 1,
    'honor_status.la.honor_grade': 1,
}


_voc_assignment_projection = {
    '_id': 0,
    'user_id': 1,
    'honor_status.voc.honor_grade': 1,
}


_la_mapper = {'honor_status.la.honor_grade': 'honor_status.honor_grade'}


_voc_mapper = {'honor_status.voc.honor_grade': 'honor_status.honor_grade'}


async def assignments_query(db: aio_motor.AsyncIOMotorDatabase, section: str) -> DataFrame:
    """
    Query's the user_assignment collection to find honor grades for users.

    Grabs the assignment that started on the previous Monday.

    NOTE: the honors grades will come through as strings because they're
    actually honors subjects. -_-

    NEW NOTE: the honors grades for english are ints. Careful of the lack of consistency
    in types.

    DataFrame should have the shape ['user_id': str, 'honors_status.honor_grade': str]

    :param db:
    :param section:
    :return:
    """
    now = date.today()
    previous_monday = now - timedelta(days=now.weekday())
    assignment_query = {
        'start_date': previous_monday.isoformat()
    }

    if section == 'math':
        c = db.user_assignment
        cursor = c.find(assignment_query, _assignment_projection)
        ls = await cursor.to_list(None)
        return pd.json_normalize(ls)
    else:
        c = db.ae_user_assignment
        projection = _la_assignment_projection if section == 'la' else _voc_assignment_projection
        cursor = c.find(assignment_query, projection)
        ls = await cursor.to_list(None)
        df = pd.json_normalize(ls)
        mapper = _la_mapper if section == 'la' else _voc_mapper
        df.rename(columns=mapper, inplace=True)
        df.dropna(inplace=True)
        df['honor_status.honor_grade'] = df['honor_status.honor_grade'].astype('int')
        df['honor_status.honor_grade'] = df['honor_status.honor_grade'].apply(lambda x: AE_GRADE_SUBJECT_MAP.get(str(x), 'Grade ' + str(x)))
        return df
