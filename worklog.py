#!/usr/bin/python
from optparse import OptionParser
from datetime import datetime
import sys
import os


# Configuration
config = {}
config['date_format']      = '%Y-%m-%d'
config['time_format']      = '%H:%M:%S'
config['full_date_format'] = config['date_format'] + ' ' + config['time_format']

config['directory']        = os.path.expanduser('~') + '/Worklog/'
config['filename']         = '%Y/Week %U/' + config['date_format'] + '.log' # Be careful, a slash will create a new directory

config['start_char']       = 'S'
config['continue_char']    = '|'
config['stop_char']        = 'F'

class WorkLog:
    """ Small script to start and stop logging work with optional commenting. """

    __config   = None
    __filename = None
    __options  = None
    __largs    = None

    def __init__(self, config):
        # Prepare configuration
        self.__config                  = config
        self.__filename                = config['directory'] + datetime.strftime(datetime.now(), config['filename'])
        (self.__options, self.__largs) = self.__get_cli_arguments()
        
        # Determine (last)times
        self.__touch_file()

        (last_line, last_time, last_is_end) = self.__get_last_breakpoint()
        total_worktime = self.__get_total_worktime(last_time, last_is_end)

        # Dump log file and exit
        if self.__options.dump:
            for line in open(self.__filename):
                sys.stdout.write(line)
            print(total_worktime)
            return

        # Output current status and exit
        if self.__options.status:
            print(last_line.strip())
            print(total_worktime)
            return

        # Determine command and comment
        command = self.__determine_command(last_line)
        comment = ' '.join(self.__largs).strip().replace('\t', ' ')

        # Output log record
        self.__write_line(command, comment, total_worktime)
        self.__log_status(command, comment, total_worktime)

    def __get_cli_arguments(self):
        # CLI options
        parser = OptionParser()

        parser.add_option('-d', '--dump',
                          action="store_true", dest="dump", default=False,
                          help="Dump log file.")

        parser.add_option('-s', '--status',
                          action="store_true", dest="status", default=False,
                          help="Print working status and total time.")

        parser.add_option('-f', '--finish',
                          action="store_true", dest="stop", default=False,
                          help="Finish working.")

        (options, args) = parser.parse_args()

        return (options, parser.largs)

    def __touch_file(self):
        directory = os.path.dirname(self.__filename)

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(self.__filename, 'a') as log_file:
            log_file.close()

    def __get_last_breakpoint(self):
        line        = ''
        last_time   = ''
        last_is_end = False

        for line in open(self.__filename):
            try:
                pos = line.index('\t' + self.__config['start_char'])
                if pos > 0:
                    last_time = line[0:pos]
                    last_is_end = False
            except ValueError:
                pass
            try:
                pos = line.index('\t' + self.__config['stop_char'])
                if pos > 0:
                    last_time = line[0:pos]
                    last_is_end = True
            except ValueError:
                pass

        return (line, last_time, last_is_end)

    def __get_total_worktime(self, last_time, get_mtbw):
        total = 'Error calculating working time.'

        if len(last_time) > 0:
            try:
                total = str(datetime.now()-datetime.strptime(last_time, config['full_date_format']))
                total = total[0:total.index('.')]
                total = ('MTBW ' if get_mtbw else 'Total of ') + total + '.'
            except ValueError:
                pass

        return total

    def __determine_command(self, last_line):
        if self.__options.stop:
            return self.__config['stop_char']
        
        command = self.__config['start_char']

        try:
            (self.__config['start_char'] + self.__config['continue_char']).index(last_line[last_line.index('\t')+1])
            command = self.__config['continue_char']
        except ValueError:
            pass

        return command

    def __write_line(self, command, comment, total):
        # Write to file
        with open(self.__filename, 'a') as log_file:
            log_file.write(datetime.now().strftime(self.__config['full_date_format']) +
                           '\t' + command +
                           '\t' + comment)
            if command == self.__config['stop_char']:
                log_file.write(' ' + total)
            log_file.write('\n')

    def __log_status(self, command, comment, total):
        # Write to console
        if command == self.__config['start_char']:
            print('Started.')
        elif command == self.__config['continue_char']:
            print('Continuing. ' + total)
        elif command == self.__config['stop_char']:
            print('Stopped. ' + total)
        # else:
        #     print('Invalid command: ' + command + '.')

if __name__ == '__main__':
    log = WorkLog(config)