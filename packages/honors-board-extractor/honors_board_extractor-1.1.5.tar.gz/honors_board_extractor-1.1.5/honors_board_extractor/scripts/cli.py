from honors_board_extractor.config import Config

import aiohttp
import asyncio
import click
import logging
import motor.motor_asyncio as aio_motor
import pathlib
import os
import sys
import yarl

import honors_board_extractor.boards as boards
import honors_board_extractor.charts as charts


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


@click.command()
@click.option('-r', '--region', default='us', help='us or cn', required=True, type=str)
@click.option('-s', '--section', default='math', help='math, la, or voc', required=True, type=str)
def main(region: str, section: str):
    if region != 'us' and region != 'cn':
        raise ValueError(f'region must be us or cn, not {region}')

    if section != 'math' and section != 'la' and section != 'voc':
        raise ValueError(f'section must be math, la, or voc, not {section}')

    asyncio.run(async_main(region, section))


async def async_main(region, section):
    conf = Config(region, section)
    conf.setup_dump_dirs()
    url = conf.datastore_url
    chart_url = conf.go_chart_url
    dir_path = conf.dir_path
    user = {'username': conf.datastore_user, 'password': conf.datastore_password}
    client = aio_motor.AsyncIOMotorClient(conf.db_ip, conf.db_port, username=conf.db_username, password=conf.db_password)

    try:
        db = client.MathJoy
        logging.info('signing into datastore')
        async with await boards.create_session(url, user) as session:

            logging.info('starting board query')
            try:
                res = await boards.query(session, db, url, section)
            except aiohttp.ClientConnectionError as cre:
                logging.error(
                    f'Connection was refused. Check datastore url and login credentials - url: {url} user: {user}',
                    exc_info=cre)
                sys.exit(1)

            logging.info('starting data pipeline')
            res = boards.pipeline(res, section)

            logging.info('creating json files')
            boards.boards_dump(res, dir_path)

            logging.info('querying and dumping honors charts')
            try:
                chart_factory = charts.HonorsChartFetcher(session, chart_url, dir_path, section, res)
                await chart_factory.fetch_and_dump_honors_charts()
            except aiohttp.ClientConnectionError as cre:
                logging.error(
                    'Connection was refused. goChartService likely timed out.',
                    exc_info=cre)
                sys.exit(1)

            logging.info('run completed successfully')

    finally:
        client.close()


if __name__ == '__main__':
    main()
