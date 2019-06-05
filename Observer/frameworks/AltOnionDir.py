#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Andrey Glauzer'
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Andrey Glauzer"
__status__ = "Development"

import requests
from bs4 import BeautifulSoup
import logging
import re
from Observer.modules.database import DataBase


class AltOnionDir:
	def __init__(
		self,
		host_db=None,
		user_db=None,
		password_db=None,
		database=None):

		self.host_db = host_db
		self.user_db = user_db
		self.password_db = password_db

		self.database_name = database
		self.database = DataBase(
			host_db = self.host_db,
			user_db = self.user_db,
			password_db = self.password_db,
			database = self.database_name,
		)

		self.source = 'Alt OnionDir'
		compare_sorce = self.database.compare_source(source=self.source)

		if compare_sorce:
			pass
		else:
			self.database.save_source(source=self.source)

		self.logger = logging.getLogger('Class:AltOnionDir')
		self.session = requests.session()

		self.proxies = {
			'http': 'socks5h://localhost:9050',

		}

	@property
	def start(self):
		self.database.replaces()
		self.alt_onionDir()

	def alt_onionDir(self):

		url = 'http://onionf3ck2i74bmm.onion'

		self.logger.info(' Conectando em {url}'.format(url=url))

		request = self.session.get(url, proxies=self.proxies, timeout=1000)
		soup = BeautifulSoup(request.content, features="lxml")

		pages = []
		for raw in soup.find('navbar', {'id': 'content-navbar'}).findAll('a'):
			if '.html' in raw['href'].lower():
				pages.append("{url}/{page}".format(url=url, page=raw['href']))

		for urls in pages:

			try:
				request = self.session.get(urls, proxies=self.proxies, timeout=1000)
				soup = BeautifulSoup(request.content, features="lxml")

				next = []
				for paginator in soup.find('ul', {'id':'paginator'}).findAll('a'):
					next.append("{url}/{page}".format(url=url, page=paginator['href'].replace('..', '')))

				for nextpage in next:
					self.logger.info(' Realizando scraping em {url}'.format(url=nextpage))
					try:

						request = self.session.get(nextpage, proxies=self.proxies, timeout=1000)
						soup = BeautifulSoup(request.content, features="lxml")

						list_urls = []
						for raw in soup.find('div', {'class': 'generic-page'}).findAll('footer'):
							for get_onion in raw.findAll('a'):

								list_urls.append(get_onion['href'])


						regex = re.compile("[A-Za-z0-9]{0,12}\.?[A-Za-z0-9]{12,50}\.onion")

						for lines in list_urls:
							rurls = lines \
								.replace('\xad', '') \
			                    .replace('\n', '') \
			                    .replace("http://", '') \
			                    .replace("https://", '') \
			                    .replace(r'\s', '') \
			                    .replace('\t', '')

							xurl = regex.match(rurls)
							if xurl is not None:
								self.database.saveonion(
									url=xurl.group(),
									source=self.source)

					except(requests.exceptions.ConnectionError,
								requests.exceptions.ChunkedEncodingError,
								requests.exceptions.ReadTimeout,
								requests.exceptions.InvalidURL) as e:
						self.logger.error(' Não consegui conectar na url, porque ocorreu um erro.\n{e}'.format(e=e))
						pass

			except(requests.exceptions.ConnectionError,
						requests.exceptions.ChunkedEncodingError,
						requests.exceptions.ReadTimeout,
						requests.exceptions.InvalidURL) as e:
				self.logger.error(' Não consegui conectar na url, porque ocorreu um erro.\n{e}'.format(e=e))
				pass
