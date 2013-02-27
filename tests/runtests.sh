#!/bin/sh

export DJANGO_MANAGE=manage.py
export args="$@"

# run only django_auxilium tests if not arguments are provided
if [ -z "$args" ] ; then
    export args="django_auxilium"
fi

python $DJANGO_MANAGE test "$args"
