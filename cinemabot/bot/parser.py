import json
import os
import typing as tp
from dataclasses import dataclass
from http import HTTPStatus
from aiohttp import ClientSession
from typing import Optional, Union
from abc import ABC, abstractmethod
import json
from bs4 import BeautifulSoup


@abstractmethod
class BaseFilmFetcher(ABC):
    @abstractmethod
    async def fetch(self, session: ClientSession, film_name: str) -> tp.Dict[str, tp.Any]:
        pass


TOKEN_HUEKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'



class KinoPoisk(BaseFilmFetcher):
    async def fetch(self, session: ClientSession, movie: str):
        # search_url = os.environ.get('CUSTOM_SEARCH_URL', '')
        search_url = 'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={0}&page=1'.format(
            movie)
        # params = {
        #
        #     'key': os.environ.get('CUSTOM_SEARCH_URL', None),
        #     'cx': os.environ.get('CUSTOM_SEARCH_KINOPOISK', None),
        #     'q': movie
        # }
        params = {
            # "keyword": "мстители",
            "pagesCount": 1,
            "searchFilmsCountResult": 134,
            # "films": [
            #     None
            # ]
        }
        headers = {
            'X-API-KEY': TOKEN_HUEKEN,
            'Content-Type': 'application/json',
        }

        res = {
            'name': None,
            'poster': None,
            'description': None,
            'link_to_watch': None,
            'rating_kp': None
        }

        async with session.get(url=search_url, params=params, headers=headers) as responce:
            answer = await responce.text()
            if responce.status == HTTPStatus.OK:
                data = json.loads(answer)
                if len(data['films']) == 0:
                    print("что-то не то, перепроверьте пж")
                else:
                    # if data['films'][0]['nameRu'] not in
                    # else:
                    # сделать проверки на каждое обращение
                    res['name'] = data['films'][0]['nameRu']
                    res['link_to_watch'] = "aboba"
                    res['poster'] = data['films'][0]['posterUrl']
                    res['rating_kp'] = data['films'][0]['rating']

            return res


class WikiFetcher(BaseFilmFetcher):  # type: ignore

    async def fetch(self, session: ClientSession, film_name: str) -> tp.Dict[str, tp.Any]:
        """ Fetches all possible info of the film (from wiki page)
        :param film_name: film which we need
        :param session: session for async fetching
        :return: dict which contains path to poster, description
        """

        custom_search_url: str = os.environ.get('CUSTOM_SEARCH_URL', '')
        params = {
            'key': os.environ.get('CUSTOM_SEARCH_KEY', None),
            'cx': os.environ.get('CUSTOM_SEARCH_WIKI', None),
            'q': film_name
        }

        async with session.get(url=custom_search_url, params=params) as response:
            result = await response.text()

        link = json.loads(result)['items'][0]['link']

        async with session.get(url=link) as response:
            html = await response.text()

        return {
            'poster': self._extract_poster(html),
            'description': self._extract_description(html),
            'link_to_watch': None
        }

    @staticmethod
    def _extract_description(html: str) -> str:
        """ Extracts film description from wiki page.
        :param html: html of a wiki page
        :return: description of the film
        """

        soup = BeautifulSoup(html, features='html.parser')
        div = soup.html.body.findAll('div', {'id': 'mw-content-text'})[0]
        return div.findAll('p', {'class': None})[0].get_text()

    @staticmethod
    def _extract_poster(html: str) -> str:
        """ Extracts url of a film poster from wiki page.
        :param html: html of a wiki page
        :return: url of a film poster
        """

        soup = BeautifulSoup(html, features='html.parser')
        a_link = soup.html.body.findAll('a', {'class': 'image'})[0]
        url = a_link.findAll('img')[0]['src']

        return url[2:]
