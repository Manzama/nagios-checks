#!/usr/bin/env python
# Written by chaomodus 2017-03-09

import redis
import argparse
import sys

STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3

parser = argparse.ArgumentParser(description="Check a REDIS instance and return statistics.")

parser.add_argument('-t', action='store', nargs=1, default=5, type=int, metavar='S', dest='timeout')
parser.add_argument('-H', action='store', nargs=1, default='localhost', type=str, metavar='H', dest='host')
parser.add_argument('-p', action='store', nargs=1, default=6379, type=int, metavar='P', dest='port')
parser.add_argument('--password', action='store', nargs=1, default=None, type=str, metavar='P', dest='password')

args = parser.parse_args()

try:
    redisclient = redis.client.StrictRedis(host=args.host, port=args.port, password=args.password, socket_timeout=args.timeout, socket_connect_timeout=args.timeout)
except Exception, instance:
    print('CRITICAL Exception when Redis client {}'.format(repr(instance)))
    sys.exit(STATUS_CRITICAL)

try:
    info = redisclient.info('all')
except Exception, instance:
    print('CRITICAL Exception when connecting to Redis {}'.format(repr(instance)))
    sys.exit(STATUS_CRITICAL)

# Sets the defaults. Nones result in WARNING status.
perfdata = {
    'used_memory_rss': None,
    'used_memory': None,
    'used_memory_peak': 0,
    'uptime_in_seconds': None,
    'connected_clients': None,
    'blocked_clients': 0,
    'total_commands_processed': 0,
    'total_connections_received': 0,
    'total_net_input_bytes': 0,
    'total_net_output_bytes': 0,
    'evicted_keys': 0,
    'expired_keys': 0,
    'total_commands_processed': 0,
    'total_connections_received': 0,
    'used_cpu_sys': 0.0,
    'used_cpu_sys_children': 0.0,
    'used_cpu_user': 0.0,
    'used_cpu_user_children': 0.0,
}
perf_keys = list(perfdata.keys())

perfdata.update(info)

status = STATUS_OK
status_message = ''
for key in perf_keys:
    if perfdata[key] is None:
        status = STATUS_WARNING
        status_message += ' missing stats key: {}'.format(key)

totalkeys = 0
ttls = []
additional = {}
for key in perfdata:
    if key[0:2] == 'db':
        dbperfs = perfdata[key]
        additional[key+'.average_ttl'] = dbperfs['avg_ttl']
        perf_keys.append(key+'.average_ttl')
        ttls.append(dbperfs['avg_ttl'])
        additional[key+'.keys'] = dbperfs['keys']
        perf_keys.append(key+'.keys')
        totalkeys += dbperfs['keys']
perfdata.update(additional)
# backwards compatibility perfdata
perfdata['clients'] = perfdata['connected_clients']
perf_keys.append('clients')
perfdata['dbkeys'] = totalkeys
perf_keys.append('dbkeys')
perfdata['memory'] = perfdata['used_memory']
perf_keys.append('memory')


if status_message == '':
    status_message = 'REDIS OK'
else:
    status_message = 'REDIS WARNING' + status_message

outperf = ' '.join([x+'='+str(perfdata[x]) for x in perf_keys])

print("{} | {}".format(status_message, outperf))
sys.exit(status)
