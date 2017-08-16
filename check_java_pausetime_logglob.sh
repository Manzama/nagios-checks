#!/bin/sh

/usr/bin/python /opt/manzama-nagios-checks/check_java_pausetime "$@" -l "$(ls /var/solr/logs/solr_gc.log.*.current)"
