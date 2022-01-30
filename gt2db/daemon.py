# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
from datetime import datetime, timedelta
from os import environ
from time import sleep

import psycopg2
from pandas import Timestamp, Series, DataFrame
from psycopg2._psycopg import connection, cursor
from pytrends.request import TrendReq
from sdnotify import SystemdNotifier


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level='DEBUG')

    span = timedelta(days=100)
    gt_res = timedelta(hours=1)
    tr = TrendReq(tz=0, retries=3)

    conn: connection
    with psycopg2.connect(environ['DB'] if 'DB' in environ else '') as conn:
        cur: cursor
        with conn.cursor() as cur:
            SystemdNotifier().notify('READY=1')

            while True:
                cur.execute(
                    'SELECT kw.id, kw.keyword, kw.past_done,'
                    ' (SELECT MIN(sc.time) FROM searches sc WHERE sc.keyword=kw.id) searches_from,'
                    ' (SELECT MAX(sc.time) FROM searches sc WHERE sc.keyword=kw.id) searches_to'
                    ' FROM keyword kw'
                    ' ORDER BY kw.updated'
                    ' LIMIT 1'
                )

                for (id, keyword, past_done, searches_from, searches_to) in cur.fetchall():
                    dig_past = False

                    if searches_from is None:
                        now = datetime.now()
                        new_from = now - span
                        new_to = now
                    elif past_done:
                        new_from = searches_to + gt_res
                        new_to = searches_to + span
                    else:
                        new_from = searches_from - span
                        new_to = searches_from - gt_res
                        dig_past = True

                    logging.info('Fetching searches [%s, %s] for "%s"', new_from, new_to, keyword)

                    timeline: DataFrame = tr.get_historical_interest(
                        [keyword], year_start=new_from.year, month_start=new_from.month, day_start=new_from.day,
                        hour_start=new_from.hour, year_end=new_to.year, month_end=new_to.month, day_end=new_to.day,
                        hour_end=new_to.hour, sleep=10
                    )

                    logging.info('Updating "%s"', keyword)

                    has_some = False

                    ts: Timestamp
                    series: Series
                    for (ts, series) in timeline.iterrows():
                        has_some = True

                        if series['isPartial']:
                            break

                        cur.execute(
                            'INSERT INTO searches(keyword, time, searches) VALUES (%s, %s, %s)',
                            (id, ts.isoformat(), series[keyword])
                        )

                    if dig_past and not has_some:
                        cur.execute('UPDATE keyword SET past_done=TRUE WHERE id=%s', (id,))

                    cur.execute('UPDATE keyword SET updated=NOW() WHERE id=%s', (id,))
                    conn.commit()
                else:
                    logging.debug('Nothing to do (no keywords)')

                sleep(15)


if __name__ == '__main__':
    main()
