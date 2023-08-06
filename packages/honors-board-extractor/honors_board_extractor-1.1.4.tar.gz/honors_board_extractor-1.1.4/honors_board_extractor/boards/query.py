from typing import Dict, List, Optional
from aiohttp import ClientSession
from pandas import DataFrame
from yarl import URL

import asyncio
import itertools
import motor.motor_asyncio as aio_motor
import pandas as pd

from .region_query import regions_query
from .assignments_query import assignments_query


async def query(session: ClientSession, db: aio_motor.AsyncIOMotorDatabase, url: URL, section: str) -> Dict[str, DataFrame]:
    """
    This will query the database for the most recent set of user assignments,
    and query datastore for the HonorsBoards info.

    This will query both datastore and the database concurrently. We need
    the assignments as well because they have each students honor_grade
    pre-computed.

    :param session:
    :param db:
    :param url:
    :param section:
    :return: the dict will have two strings, 'honors_boards' and 'assignments'.
    """
    regions = await regions_query(db)
    honor_boards, assignments = await asyncio.gather(honors_board_query(session, url, regions, section),
                                                     assignments_query(db, section))
    return {
        'honors_boards': honor_boards,
        'assignments': assignments
    }


async def honors_board_query(session: ClientSession, url: URL, regions: Dict[str, List[int]], section: str) -> DataFrame:
    board_coroutines = []
    for grade, (region_name, region) in itertools.product(range(1, 13), regions.items()):
        board_coroutines.append(_execute_query_for_honors_board(
            session,
            _build_query(grade, region, section),
            url,
            region_name,
            grade
        ))
    dfs = await asyncio.gather(*board_coroutines)
    return pd.concat(dfs, ignore_index=True)


def _build_query(school_grade: int, region: List[int], section: str) -> Dict:
    gql_query = """
    query HonorBoards($filter: StudentsProgressFilterInput!) {
        allStudentsProgress(filter: $filter) {
            user_id
            firstname
            lastname
            current_grade
            start_ts
            school
            is_honor
            is_high_honor
        }
    }
    """
    if section == 'math':
        return {
            'operationName': 'HonorBoards',
            'query': gql_query,
            'variables': {
                'filter': {
                    'product_id': 1,
                    'grade': school_grade,
                    'learning_center_id': region,
                    'onlyActive': True,
                }
            }
        }
    else:
        return {
            'operationName': 'HonorBoards',
            'query': gql_query,
            'variables': {
                'filter': {
                    'product_id': 20,
                    'section_type': 'ae.' + section,
                    'grade': school_grade,
                    'learning_center_id': region,
                    'onlyActive': True,
                }
            }
        }


async def _execute_query_for_honors_board(
        session: ClientSession,
        board_query: Dict,
        url: URL,
        region_name: str,
        school_grade: int
) -> Optional[DataFrame]:

    gql_url = url / 'graphql'
    async with session.post(gql_url, json=board_query) as resp:
        json_resp = await resp.json()
        data = json_resp.get('data')
        progress = data.get('allStudentsProgress') if type(data) is dict else None
        if type(progress) is list:
            df = DataFrame(progress)
            df = df.assign(
                region=region_name,
                school_grade=school_grade
            )
            return df
        else:
            return None
