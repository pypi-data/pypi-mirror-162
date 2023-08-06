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

import yaml

from watchpage.target import Target


class Configuration(object):
    """
    Configuration object for loading the settings from a YAML file
    """
    def __init__(self, filename: str):
        self.filename = filename
        self.targets = {}
        with open(self.filename, 'r') as file:
            values = {item['NAME']: item
                      for item in yaml.load_all(stream=file,
                                                Loader=yaml.Loader)
                      if item}
        # Load targets
        for name, value in values.items():
            if value.get('STATUS', True):
                self.targets[name] = Target(
                    name=name,
                    url=value['URL'],
                    parser=value.get('PARSER', 'html.parser'),
                    type=value.get('TYPE', 'links'),
                    use_absolute_urls=value.get('ABSOLUTE_URLS', False),
                    filters=value.get('FILTERS', []) or [])

    def get_targets(self) -> list[Target]:
        """
        Return the configuration targets

        :return: targets list
        """
        return list(self.targets.values())
