#!/bin/sh

export PYTHONPATH="./"
export DJANGO_SETTINGS_MODULE="settings"

if [ `which django-admin.py` ] ; then
    export DJANGO_ADMIN=django-admin.py
else
    export DJANGO_ADMIN=django-admin
fi

export args="$@"

# run only django_auxilium tests if not arguments are provided
if [ -z "$args" ] ; then
    export args="django_auxilium"
fi

$DJANGO_ADMIN test --settings=$DJANGO_SETTINGS_MODULE --pythonpath="../" "$args"
