#!/bin/bash


OUT=fykos.txt
FKS=/home/michal/Documents/Work/Fykos
STRIP=../src/python/learning/stripTex.py


$STRIP $FKS/fyk-2012/problems/*.tex \
 $FKS/fyk-2012/batch*/serial*.tex \
 $FKS/fyk-2012/batch*/uvod*.tex \
 $FKS/vyf-2012/problems/*.tex \
 $FKS/vyf-2012/batch*/serial*.tex \
 $FKS/vyf-2012/batch*/uvod*.tex \
 > $OUT


