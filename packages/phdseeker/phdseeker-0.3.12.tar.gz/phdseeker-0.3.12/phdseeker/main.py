#!/usr/bin/env python3

import re
import sys
import httpx
import http3
import pandas as pd
import asyncio
import rich
from datetime import date
from dataclasses import dataclass
from bs4 import BeautifulSoup as bs
from pathlib import Path
sys.path.append(Path(__file__).parent.parent.as_posix()) # https://stackoverflow.com/questions/16981921
from phdseeker.rich_dataframe import prettify

# Turns off some warnings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class Config:
    config = {
        'scholarshipdb': {
            'sought#': 'h1.title',
            'query':
            'https://scholarshipdb.net/scholarships/Program-PhD?page={page}&q={fields}',
            'title': 'h4 a',
            'country': '.list-unstyled a.text-success',
            'date': '.list-unstyled span.text-muted',
            'link': ".list-unstyled h4 a",
        },
        'findaphd': {
            'sought#': 'h4.course-count.d-none.d-md-block.h6.mb-0.mt-1',
            'query':
            'https://www.findaphd.com/phds/non-eu-students/?01w0&Keywords={fields}&PG={page}',
            'title': "h4 text-dark mx-0 mb-3",
            'country':
            "country-flag img-responsive phd-result__dept-inst--country-icon",
            'date': "apply py-2 small",
            'link': "h4 text-dark mx-0 mb-3",
        },
    }

    def __init__(self, repo='scholarshipdb'):
        self.repo = repo

    @classmethod
    def repos(cls):
        return ','.join(list(cls.config))

    @property
    def query(self):
        return Config.config[self.repo]['query']

    @property
    def sought(self):
        return Config.config[self.repo]['sought#']

    @property
    def title(self):
        return Config.config[self.repo]['title']

    @property
    def link(self):
        return Config.config[self.repo]['link']

    @property
    def country(self):
        return Config.config[self.repo]['country']

    @property
    def date(self):
        return Config.config[self.repo]['date']

    @property
    def baseURL(self):
        return next(
            re.finditer(r'^.+?[^\/:](?=[?\/]|$)',
                        Config.config[self.repo]['query'])).group()


class PhDSeeker:

    def __init__(self,
                keywords: str,
                repos: str = 'scholarshipdb, findaphd',
                maxpage: int = 10):
        self.repos = map(str.strip,
                        repos.split(','))  # 'scholarshipdb, findaphd'
        self.keywords = keywords
        self.fields = '%20'.join([
            f"\"{item.replace(' ', '%20')}\""
            for item in map(str.strip, keywords.split(','))
        ])
        self.titles = []
        self.countries = []
        self.dates = []
        self.links = []
        self.maxpage = maxpage + 1
        self.file_name = f"PhD_Positions_{date.today()}"
        self.df = None # DataFrame of found positions
        self.sought_number = 0
        self.loop = asyncio.get_event_loop()

    def __str__(self):
        if self.sought_number:
            s = ('=' * 80 + '\n#') + 'Sought Ph.D. Positions'.center(78) + (
                '#\n' + '=' * 80 + '\n')
            prettify(self.df[['Country', 'Date', 'Title']], clear_console=False)
            return ''#s + self.df.to_csv(index=False)

    async def __get_page__(self, repo, page):
        headers = {
            'user-agent': 'curl/7.83.0',
            'accept': '*/*',
            'scheme': 'http',
            # 'Content-Length': '0',
        }
        c = Config(repo)
        try:
            query = c.query.format(fields=self.fields, page=page)
            if repo!='findaphd':
                client = http3.AsyncClient()
                keywords = {'verify': False}
            else:
                client = httpx.AsyncClient()
                keywords = {}
            response = await client.get(query,
                        headers=headers,
                        **keywords,
                        )
            # print(' '*70+str(type(client)))
            if isinstance(client, http3.client.AsyncClient):
                await client.close()
            if isinstance(client, httpx._client.AsyncClient):
                await client.aclose()
            soup = bs(response.text, "html.parser")
            if page == 1:  # get the number of sought positions
                if (n := soup.select_one(c.sought)) is not None:
                    foundPositions = int(re.search('(\d+[,\d*]*)', n.text)[1].replace(',',''))
                    self.sought_number += foundPositions
                sn = f"<< {foundPositions} positions found >>"
                print(
                    # f"\r[[ {self.sought_number} positions found ]] {' '*(55-len(self.keywords))}"
                    f"\r {sn.center(80)}"
                )
            titles, countries, dates, links = [
                soup.select(item) if repo == 'scholarshipdb' else
                soup.find_all(class_=item)
                for item in (c.title, c.country, c.date, c.link)
            ]
            assert titles != [], 'No titles found'
            for title, country, date, link in zip(
                    titles, countries, dates, links):
                self.titles.append((title.text).strip())
                self.countries.append(
                    country.text if repo ==
                    'scholarshipdb' else country['title'])
                self.dates.append(date.text.replace('\n', ''))
                self.links.append(c.baseURL + link['href'])
            if self.sought_number:
                print(
                    f"\rPage {page} has been fetched from {c.baseURL}!",
                    end="")
            return True
        except AssertionError:
            return False # break
        except Exception as e:
            print(e)
            return False # break

    async def prepare(self):
        for repo in self.repos:
            print(f"\r{('::[ '+repo+' ]::').center(80, '=')}")
            tasks = [asyncio.create_task(self.__get_page__(repo, page)) for page in range(1, self.maxpage)]
            try:
                await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            except Exception:
                for t in tasks:
                    t.cancel()

    @property
    def positions(self, ):
        # asyncio.run(self.prepare())
        try:
            self.loop.run_until_complete(self.prepare())
        finally:
            self.loop.close()
        positions = {
            "Country": self.countries,
            "Date": self.dates,
            "Title": self.titles,
            "Link": self.links
        }
        self.df = pd.DataFrame.from_dict(positions, orient='index').transpose()
        self.df['timedelta'] = self.df["Date"].apply(lambda x: re.sub('about|ago', '', x).strip())
        name2days ={'minutes':'*1', 'hours':'*60', 'hour':'*60', 'days':'*1440', 'day':'*1440',
                    'weeks':'*10080', 'week':'*10080', 'months':'*43200', 'month':'*43200'}
        self.df.replace({'timedelta': name2days }, regex=True, inplace=True)
        # eval is not applicable to the empty string
        self.df['timedelta'] = self.df['timedelta'].apply(lambda x: eval(x) if x else x)
        self.df.sort_values(by=['Country', 'timedelta', 'Title'], inplace=True)
        self.df = self.df.drop('timedelta', axis=1).reset_index(drop=True)
        return self.df

    def save(self, output='both'):
        """Creates excel/csv files based on all revceived data"""
        df = self.positions
        if self.sought_number:
            rich.print(f"\n{self.sought_number} positions have been found in total.")
            if output in ('csv', 'both'):
                df.to_csv(f'{self.file_name}.csv', index=False)
            if output in ('xlsx', 'both'):
                df.to_excel(f'{self.file_name}.xlsx', index=False)
        else:
            print('[blink][red] >>> No positions found, change your keyword. <<< [/red][/blink]')


def main():
    # Comma seperated list of keywords for the field of desired PhD career + presets
    keywords = 'Computer Science, Machine Learning, Deep Learning'

    ps = PhDSeeker(keywords, maxpage=10)
    ps.save()


if __name__ == "__main__":
    main()
