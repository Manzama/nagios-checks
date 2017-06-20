#!/bin/sh

/usr/bin/python /opt/manzama-nagios-checks/check_java_pausetime -c 60 -w 45 -l "$(ls /var/solr/logs/solr_gc.log.*.current)"
