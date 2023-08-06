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

import datetime
import pathlib

from watchpage.command_line_options import CommandLineOptions
from watchpage.configuration import Configuration


def main():
    # Get command-line options
    command_line = CommandLineOptions()
    command_line.add_configuration_arguments()
    options = command_line.parse_options()
    results_dir = pathlib.Path(options.results)
    if not results_dir.exists():
        # Create results directory
        results_dir.mkdir(parents=True)
    configuration = Configuration(options.config)
    for target in configuration.get_targets():
        # Get results
        new_results = target.get_results()
        results_file = results_dir / f'{target.name}.txt'
        if results_file.exists():
            # Compare previous results
            with open(results_file, 'r') as file:
                previous_results = [line.strip('\n')
                                    for line in file.readlines()]
        else:
            previous_results = []
        # Compare previous results
        if differences := set(new_results).difference(previous_results):
            print(f'Target: {target.name}')
            print(f'URL: {target.url}')
            print(f'Date: {datetime.datetime.now():%Y-%m-%d %H:%M.%S}')
            print()
            print('\n'.join(sorted(differences)))
            print('-' * 79)
        # Save new results
        if not options.dump:
            with open(results_file, 'w') as file:
                file.writelines(line + '\n' for line in new_results)


if __name__ == '__main__':
    main()
