# `loadsched.py`

A simple command-line utility for querying a [load shedding](#what-is-load-shedding) schedule.

```
$ ./loadsched.py --help
usage: loadsched.py [-h] [--day DAY] [--filename SCHEDULE_FILENAME]
                    [--group GROUPS] [--stage STAGE] [--print-schedule]
                    [--verbose]

Load shedding schedule tool.

optional arguments:
  -h, --help            show this help message and exit
  --day DAY, -d DAY     Day of month to show schedule for. 1 to 31, inclusive.
                        Default: today
  --filename SCHEDULE_FILENAME, -f SCHEDULE_FILENAME
                        File to read schedule from.
  --group GROUPS, -g GROUPS
                        Filter on specified groups. 1 to 16, inclusive.
                        Default: all
  --stage STAGE, -s STAGE
                        Filter schedule for this stage number only. Default:
                        current load shedding stage, queried from Eskom.
  --print-schedule      Print entire schedule.
  --verbose, -v

$ ./loadsched.py -s 4 -g 6 -g 9 -g 10 -d 20
20 4  1:00 -  3:30: 9
20 4  3:00 -  5:30: 6, 10
20 4  9:00 - 11:30: 9
20 4 11:00 - 13:30: 6, 10
20 4 17:00 - 19:30: 9
20 4 19:00 - 21:30: 6, 10
```

If no command-line arguments are given, the current load shedding level is
queried from Eskom, and the schedule entries for the current day of the month
and all groups are printed.

Output is formatted for easy grepping, and follows the format
`<day> <stage> <start time> - <end time>: <groups>`.

See ["Schedule file format"](#schedule-file-format) below for details about the expected format of
`SCHEDULE_FILENAME`.

## Schedule file format

Schedule files are parsed according to the following rules:
* It is a plain text file.
* Lines starting with `#` are ignored.
* Lines are split into fields on `|` characters.
* Leading/trailing whitespace is stripped from fields.
* Empty fields are discarded.
* Lines with 2 fields contain the start- and end times of the timeslot for the following lines.
* Lines with 32 fields contain the stage number and 31 group numbers.
  * The stage number for stage `N` is formatted as `StageN`.
  * The 31 group numbers represent the group (of towns/suburbs) affected by load shedding on the corresponding day of the month.
* All other lines are ignored.

[**NOTE**](http://www.eskom.co.za/Pages/LS_schedules.aspx):

> Schedules are cumulative, i.e. stage 3 will include the times as scheduled
> for the preceding stages 1 and 2.

See [`schedule.txt`](https://github.com/walterl/loadsched/blob/master/schedule.txt) as an example. It was manually transformed into text from [this schedule](http://www.tshwane.gov.za/sites/Departments/Public-works-and-infrastructure/Pages/Load-Shedding.aspx). (Yay [nvim](https://neovim.io)!)

## What is Load Shedding?

It is what ["rolling blackouts"](https://en.wikipedia.org/wiki/Rolling_blackout) are called by [Eskom](http://loadshedding.eskom.co.za/LoadShedding/Description), the sole, state
owned electrical power producer in South Africa:

> Load shedding, or load reduction, is done countrywide as a controlled option
> to respond to unplanned events to protect the electricity power system from a
> total blackout.
