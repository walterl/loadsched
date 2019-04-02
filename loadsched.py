#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError
from collections import defaultdict
from datetime import date
from urllib.request import urlopen

LOAD_SHEDDING_LEVEL_URL = \
    'http://loadshedding.eskom.co.za/LoadShedding/GetStatus'


class DataUnavailableError(Exception):
    pass


def fetch_stage():
    status_id = int(urlopen(LOAD_SHEDDING_LEVEL_URL).read().decode())
    if status_id >= 99:
        raise DataUnavailableError
    return status_id - 1


class Schedule:
    def __init__(self, data=None):
        if data is None:
            self.data = defaultdict(
                lambda: defaultdict(lambda: defaultdict(set)),
            )
        else:
            self.data = data

    def load(self, fname):
        with open(fname) as sched_file:
            for line in sched_file.readlines():
                if line.startswith('#'):
                    continue

                fields = [
                    f.strip() for f in line.strip().split('|') if f.strip()
                ]

                if not fields:
                    continue

                if len(fields) == 2:
                    # Times line
                    start_time, end_time = fields
                elif len(fields) == 32:
                    # Stage line
                    stage = int(fields.pop(0).replace('Stage', ''))
                    for i, group_num in enumerate(fields):
                        day_of_month = i+1
                        timeslot = \
                            self.data[day_of_month][start_time, end_time]
                        timeslot[stage].add(int(group_num))
                        if stage > 1:
                            timeslot[stage].update(timeslot[stage-1])

        return self.data

    def filter_by_day(self, day_of_month):
        filtered = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
        filtered[day_of_month] = self.data[day_of_month]
        return Schedule(data=filtered)

    def filter_by_groups(self, groups):
        filtered = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

        for day_of_month, timeslots in self.data.items():
            for timeslot, stages in timeslots.items():
                for stage, stage_groups in stages.items():
                    filtered[day_of_month][timeslot][stage] = [
                        g for g in stage_groups if g in groups
                    ]

        return Schedule(data=filtered)

    def filter_by_stage(self, stage):
        filtered = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

        for day_of_month, timeslots in self.data.items():
            for timeslot, stages in timeslots.items():
                filtered[day_of_month][timeslot][stage] = stages[stage]

        return Schedule(data=filtered)

    def dump(self, write_fn=print):
        for day_of_month, timeslots in self.data.items():
            for timeslot, stages in timeslots.items():
                start, end = timeslot
                for stage in stages:
                    s_groups = ', '.join(str(g) for g in sorted(stages[stage]))
                    if not s_groups:
                        continue

                    write_fn(
                        f'{day_of_month} {stage} {start:>5} - {end:>5}: '
                        f'{s_groups}'
                    )


def int_arg(name, min_val, max_val):
    def arg_number_validator(s):
        try:
            i = int(s)
        except ValueError:
            raise ArgumentTypeError(
                f'Invalid {name} number: {repr(s)}. Not a number.',
            )

        if not (min_val <= i <= max_val):
            raise ArgumentTypeError(
                f'Invalid {name} number: {repr(i)}. '
                f'Must be between {min_val} and {max_val}.',
            )

        return i
    return arg_number_validator


def create_arg_parser():
    parser = ArgumentParser(description='Load shedding schedule tool.')

    parser.add_argument(
        '--day', '-d', default=None, type=int_arg('day', 1, 31),
        help=(
            'Day of month to show schedule for. 1 to 31, inclusive. '
            'Default: today'
        ),
    )
    parser.add_argument(
        '--filename', '-f', dest='schedule_filename', default='schedule.txt',
        help='File to read schedule from. Default: schedule.txt',
    )
    parser.add_argument(
        '--group', '-g', dest='groups', action='append', default=[],
        type=int_arg('group', 1, 16),
        help='Filter on specified groups. 1 to 16, inclusive. Default: all',
    )
    parser.add_argument(
        '--stage', '-s', default=None, type=int, help=(
            'Filter schedule for this stage number only. '
            'Default: current load shedding stage, queried from Eskom.'
        ),
    )
    parser.add_argument(
        '--print-schedule', action='store_true', default=False,
        help='Print entire schedule.',
    )
    parser.add_argument('--verbose', '-v', action='store_true', default=False)

    return parser


def main():
    options = create_arg_parser().parse_args()
    log = id
    if options.verbose:
        log = print

    try:
        schedule = Schedule()
        schedule.load(options.schedule_filename)

        if not options.print_schedule:
            stage = options.stage or fetch_stage()
            if stage == 0:
                log('# No load shedding in progress! \\o/')
                return

            schedule = schedule.filter_by_stage(stage)
            log(f'# LOAD SHEDDING STAGE: {stage}')

            day = options.day or date.today().day
            schedule = schedule.filter_by_day(day)
            log(f'# DAY OF MONTH: {day}')

            if options.groups:
                schedule = schedule.filter_by_groups(options.groups)
                log('# GROUPS: {}'.format(
                    ', '.join(str(i) for i in sorted(options.groups)),
                ))

            log('# TIMESLOTS:')

        schedule.dump()
    except DataUnavailableError:
        log('! Failed to lookup current load shedding stage.')
        exit(1)


if __name__ == "__main__":
    main()
