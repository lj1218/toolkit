#!/bin/sh
# Function: generate empty files.
# Author: lj1218
# Create: 2019-03-31
# Update: 2019-03-31

file_dirs="file_dirs"
srcdir=$1
outdir=$2

function usage()
{
    echo "Usage: $0 srcdir outdir"
    exit 1
}

function check()
{
    [ "$srcdir" = "$outdir" ] && {
        echo "srcdir and outdir should not the same"
        exit 1
    }

    [ ! -d $srcdir ] && {
        echo "$srcdir is not directory"
        exit 1
    }

    [ ! -d $outdir ] && {
        echo "$outdir is not directory"
        exit 1
    }

    local curdir=$(pwd)
    cd $outdir
    rm -rf *
    outdir=$(pwd)
    cd $curdir
}

function gen_files()
{
    local dir file
    local curdir=$1

    cd $curdir
    ls >$file_dirs
    while read line
    do
        echo $line
        if [ -d "$line" ]; then
            dir="$line"
            gen_files "$dir"
        else
            line=$(echo $line | grep -v "^~" | grep -v ".DS_Store" | grep -v "$file_dirs")
            [ -z "$line" ] && continue
            file="$line"
            echo "touch $outdir/\"$file\""
            touch $outdir/"$file"
        fi
    done <$file_dirs
    rm -f $file_dirs
    cd ..
}


[ $# -lt 2 ] && usage
check
gen_files $srcdir
