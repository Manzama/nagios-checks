#!/usr/bin/env python
# Written by chaomodus 2017-06-12

import redis
import argparse
import sys
import timeit

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3

parser = argparse.ArgumentParser(description="Check a REDIS instance and return latency.")

parser.add_argument('-t', action='store', nargs=1, default=30, type=int, metavar='S', dest='timeout')
parser.add_argument('-H', action='store', nargs=1, default='localhost', type=str, metavar='H', dest='host')
parser.add_argument('-p', action='store', nargs=1, default=6379, type=int, metavar='P', dest='port')
parser.add_argument('--password', action='store', nargs=1, default=None, type=str, metavar='P', dest='password')
parser.add_argument('-s', action='store', nargs=1, default=5, type=int, metavar='S', dest='samples')
parser.add_argument('-c', action='store', nargs=1, default=200, type=int, metavar='C', dest='crit')
parser.add_argument('-w', action='store', nargs=1, default=100, type=int, metavar='W', dest='warn')

args = parser.parse_args()

try:
    redisclient = redis.client.StrictRedis(host=args.host, port=args.port, password=args.password, socket_timeout=args.timeout, socket_connect_timeout=args.timeout)
except Exception, instance:
    print('CRITICAL REDIS Exception when Redis client {}'.format(repr(instance)))
    sys.exit(STATUS_CRITICAL)


def sample():
    try:
        ping = redisclient.ping()
    except Exception, instance:
        print('CRITICAL REDIS Exception when connecting to Redis during sampling {}'.format(repr(instance)))
        sys.exit(STATUS_CRITICAL)


totaltime = (timeit.timeit(sample, number=args.samples)) * 1000
averagetime = totaltime / args.samples

perfdata="samples={}, totaltime={:.4}, averagetime={:.4}".format(args.samples, totaltime, averagetime)

if averagetime >= args.crit:
    print('CRITICAL REDIS ping time | {}'.format(perfdata))
    sys.exit(STATUS_CRITICAL)

if averagetime >= args.warn:
    print('WARNING REDIS ping time | {}'.format(perfdata))
    sys.exit(STATUS_WARNING)

print('OK REDIS | {}'.format(perfdata))
sys.exit(STATUS_OK)
