from aiohttp import ClientSession
from pandas import DataFrame
from pathlib import Path
from yarl import URL

import asyncio
import itertools


class HonorsChartFetcher:

    chunk_size = 1024

    def __init__(self, session: ClientSession, url: URL, file_location: Path, section: str, df: DataFrame):
        self.session = session
        self.url = url
        self.file_location = file_location
        self.df = df
        self.regions = df.region.unique().tolist()
        self.school_grades = df.school_grade.unique().tolist()
        self.section = 'ae.' + section if section != 'math' else section

    async def fetch_and_dump_honors_charts(self):
        """
        Loops over the dataframe, posting for and writing to disk all of the honors charts.
        """
        for grade, region in itertools.product(self.school_grades, self.regions):
            await self.fetch_charts(grade, region)

    async def fetch_charts(self, grade: int, region: str):
        """
        Fetches the three charts, not honors, honors, and high honors charts for the
        students for a given school grade and region.
        """
        view = self.df.loc[(self.df.school_grade == grade) & (self.df.region == region)]
        not_honors = view.loc[(~view.is_honor) & (~view.is_high_honor), 'user_id'].tolist()
        honors = view.loc[view.is_honor, 'user_id'].tolist()
        high_honors = view.loc[view.is_high_honor, 'user_id'].tolist()
        await asyncio.gather(
            self._post(not_honors, grade, region, 'regular'),
            self._post(honors, grade, region, 'honors'),
            self._post(high_honors, grade, region, 'high_honors')
        )

    async def _post(self, user_ids, school_grade: int, region: str, prefix: str):
        filename = self.file_location / f"{prefix}-chart-{school_grade}-{region.replace(' ', '-')}.png"
        body = {'user_ids': user_ids,
                'section_type': self.section,
                'options': {
                    'title': ' '
                }}
        async with self.session.post(self.url, json=body) as resp:
            with open(filename, 'wb') as writer:
                while True:
                    chunk = await resp.content.read(self.chunk_size)
                    if not chunk:
                        break
                    writer.write(chunk)
