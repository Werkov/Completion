#!/bin/bash

LOG_DIR=$HOME/.kde/share/apps/kopete/logs
XSL_FILE=tr.xsl
OUT_FILE=kopete.txt

[ "$1x" != "x" ] && OUT_FILE=$1

echo -n "" > $OUT_FILE

find $LOG_DIR -name "*.xml" | while read file ; do
	xsltproc $XSL_FILE $file >> $OUT_FILE
done
