#!/usr/bin/env python

import datetime
import os
import re
from decimal import Decimal
import argparse
import sys

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
JAVATSFMT = '%Y-%m-%dT%H:%M:%S.%f+0000'
PAUSETIMERE = re.compile('\d+.\d+: Total time for which application threads were stopped: (\d+.\d+) seconds$')
TEMPLATE='JAVAGC {status}: {message} | {perfdata}'
DEFAULTLOG='/var/log/tomcat7/catalina.out'

parser = argparse.ArgumentParser(description="Check the java log for world pauses.")
parser.add_argument('-l',
                    dest='logfile',
                    action='store',
                    default=DEFAULTLOG,
                    help="Logfile to process.")
parser.add_argument('-p',
                    dest='period',
                    action='store',
                    default='5',
                    type=int,
                    help="Number of minutes to look back in the file.")
parser.add_argument('-c',
                   dest='critical',
                   action='store',
                   default='10.0',
                   type=Decimal,
                   help='The number of seconds to produce a critical condition (based on total time during period).')
parser.add_argument('-w',
                   dest='warning',
                   action='store',
                   default='5.0',
                   type=Decimal,
                   help='The number of seconds to produce a warning condition (based on total time during period).')
args = parser.parse_args()
target_timestamp = datetime.datetime.now() - datetime.timedelta(minutes=args.period)

pausetime_total = Decimal('0.0000000')
pausetime_mean = Decimal('0.0000000')
pausetime_median = Decimal('0.0000000')
pausetime_max = Decimal('0.0000000')
pausetime_min = Decimal('0.0000000')

pausetimes = []

if not os.access(args.logfile, os.F_OK):
    print TEMPLATE.format(status='CRITICAL',
                          message='Logfile "'+args.logfile+'" could not be opened.',
                          perfdata='')
    sys.exit(STATUS_CRITICAL)

with os.popen('tac '+args.logfile) as inlog:
    for line in inlog:
        if ':' in line:
            ts, rest = line.strip().split(' ', 1)
            ts = ts[:-1]
            try:
                timestamp = datetime.datetime.strptime(ts, JAVATSFMT)
            except ValueError:
                continue
            if timestamp > target_timestamp:
                result = PAUSETIMERE.match(rest)
                if result:
                    pausetime = Decimal(result.group(1))
                    pausetimes.append(pausetime)
            else:
                break


pausetimes.sort()
if pausetimes:
    pausetime_min = pausetimes[0]
    pausetime_max = pausetimes[-1]
    pausetime_median = pausetimes[len(pausetimes) / 2]
    pausetime_total = sum(pausetimes)
    pausetime_mean = pausetime_total / len(pausetimes)

outperf = 'min={min} max={max} mean={mean} median={median} total={total} count={count}'.format(min=pausetime_min, max=pausetime_max, mean=pausetime_mean, median=pausetime_median, total=pausetime_total, count=len(pausetimes))
outstatus = 'OK'
outexit = STATUS_OK
outmessage = ''

if pausetime_total > args.critical:
    outstatus = 'CRITICAL'
    outexit = STATUS_CRITICAL
    outmessage = 'Total pause time is {total} secs during the period of {period} mins which is greater than critical threshold!'.format(total=pausetime_total, period=args.period)
elif pausetime_total > args.warning:
    outstatus = 'WARNING'
    outexit = STATUS_WARNING
    outmessage = 'Total pause time is {total} secs during the period of {period} mins which is greater than warning threshold!'.format(total=pausetime_total, period=args.period)
else:
    outmessage = 'Total pause time is {total} seconds during a period of {period} minutes.'.format(total=pausetime_total, period=args.period)

print TEMPLATE.format(status=outstatus,
                      message=outmessage,
                      perfdata=outperf)
sys.exit(outexit)
