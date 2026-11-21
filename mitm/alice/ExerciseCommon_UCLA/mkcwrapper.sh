#!/bin/sh

if [ $# -ne 2 ]
then
    echo "mkcwrapper.sh is a really simple script that generates compiled C wrappers for scripts."
    echo
    echo "Usage: mkcwrapper.sh <script location> <wrapper output location>"
    exit 1
fi

SCRIPT=$1
WRAPPERNAME=$2

cc -xc -o ${WRAPPERNAME} - << EOF
#define REAL_PATH "$SCRIPT"

   main(ac, av)
       char **av;
   {
       execv(REAL_PATH, av);
   }
EOF
