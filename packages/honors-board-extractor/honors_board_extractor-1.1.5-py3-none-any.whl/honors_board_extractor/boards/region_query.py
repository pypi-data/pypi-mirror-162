from typing import Dict, List
import motor.motor_asyncio as aio_motor


_lc_query = {
    'region': {
        '$exists': True
    }
}


_lc_projection = {
    '_id': 0,
    'id': 1,
    'region': 1,
}


async def regions_query(db: aio_motor.AsyncIOMotorDatabase) -> Dict[str, List[int]]:
    """
    Query's the learningcenters collection to find the regions for the learning centers.

    :param db:
    :return: each key is a unique region, each value is every center corresponding to that region
    """
    c = db.learningcenters
    cursor = c.find(_lc_query, _lc_projection)
    regions = {}
    async for lc in cursor:
        if lc.get('region') in regions:
            lc_id = lc.get('id')
            if lc_id is not None:
                regions.get(lc.get('region')).append(lc_id)
        else:
            lc_region = lc.get('region')
            lc_id = lc.get('id')
            if lc_region != '' and lc_id is not None:
                regions.update({lc_region: [lc_id]})
    return regions
