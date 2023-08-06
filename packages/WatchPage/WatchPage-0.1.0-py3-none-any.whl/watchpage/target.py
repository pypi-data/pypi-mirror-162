##
#     Project: WatchPage
# Description: Watch webpages for changes
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2022 Fabio Castelli
#     License: GPL-3+
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
##

import re
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup


class Target(object):
    def __init__(self,
                 name: str,
                 url: str,
                 parser: str,
                 type: str,
                 use_absolute_urls: bool,
                 filters: list):
        self.name = name
        self.url = url
        self.parser = parser
        self.type = type
        self.use_absolute_urls = use_absolute_urls
        self.filters = filters

    def open_url(self) -> bytes:
        """
        Get the raw URL content

        :return: downloaded content from the URL
        """
        with urllib.request.urlopen(url=self.url) as request:
            return request.read()

    def parse_url(self) -> BeautifulSoup:
        """
        Parser the associated URL

        :return: parsed page
        """
        soup = BeautifulSoup(markup=self.open_url(),
                             features=self.parser)
        return soup

    def get_links(self) -> list[str]:
        """
        Get all the links in the page

        :return: list of URLs
        """
        parser = self.parse_url()
        results = []
        for anchor in parser.find_all('a'):
            # Find only anchors with href
            if 'href' in anchor.attrs:
                if self.use_absolute_urls:
                    # Make URL absolute
                    url = urllib.parse.urljoin(base=self.url,
                                               url=anchor['href'])
                else:
                    # Leave the URL as is
                    url = anchor['href']
                results.append(url)
        return results

    def get_rss_links(self) -> list[str]:
        """
        Get all the links from a RSS page

        :return: list of URLs
        """
        parser = self.parse_url()
        results = []
        for anchor in parser.find_all('item'):
            # Find only anchors with href
            if anchor.link:
                if self.use_absolute_urls:
                    # Make URL absolute
                    url = urllib.parse.urljoin(base=self.url,
                                               url=anchor.link.text)
                else:
                    # Leave the URL as is
                    url = anchor.link.text
                results.append(url)
        return results

    def get_results(self) -> list[str]:
        """
        Get the results from the downloaded page from the URL

        :return: results list
        """
        # Get results
        if self.type.casefold() == 'links':
            # Get only links from the page
            items = self.get_links()
        elif self.type.casefold() == 'text':
            # Filter empty lines and remove leading spaces
            items = filter(len,
                           map(str.strip,
                               self.open_url()
                               .decode('utf-8')
                               .replace('\r', '')
                               .split('\n')))
        elif self.type.casefold() == 'rss':
            # Get only links from a RSS feed
            items = self.get_rss_links()
        else:
            # Unexpected response type
            items = []
        # Filter results
        results = []
        for item in items:
            valid = True
            # Filter results
            for filter_type in self.filters:
                # Skip further checks if the result is not valid
                if not valid:
                    break
                if 'STARTS' in filter_type:
                    # Link starts with the pattern
                    filter_value = filter_type['STARTS']
                    valid = item.startswith(filter_value)
                elif 'NOT STARTS' in filter_type:
                    # Link doesn't start with the pattern
                    filter_value = filter_type['NOT STARTS']
                    valid = not item.startswith(filter_value)
                elif 'ENDS' in filter_type:
                    # Link ends with the pattern
                    filter_value = filter_type['ENDS']
                    valid = item.endswith(filter_value)
                elif 'NOT ENDS' in filter_type:
                    # Link doesn't end with the pattern
                    filter_value = filter_type['NOT ENDS']
                    valid = not item.endswith(filter_value)
                elif 'CONTAINS' in filter_type:
                    # Link contains the pattern
                    filter_value = filter_type['CONTAINS']
                    valid = filter_value in item
                elif 'NOT CONTAINS' in filter_type:
                    # Link doesn't contain the pattern
                    filter_value = filter_type['NOT CONTAINS']
                    valid = filter_value not in item
                elif 'REGEX' in filter_type:
                    # Link matches the pattern
                    filter_value = filter_type['REGEX']
                    valid = bool(re.search(filter_value, item))
                elif 'NOT REGEX' in filter_type:
                    # Link doesn't match the pattern
                    filter_value = filter_type['NOT REGEX']
                    valid = not bool(re.search(filter_value, item))
                else:
                    # Invalid filter
                    valid = False
            if valid:
                # Add a valid link
                results.append(item)
        return results
