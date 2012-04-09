#!/usr/bin/python
#coding=utf-8

import string
import re
from AbstractNgramLetterModel import AbstractNgramLetterModel

class LetterModel (AbstractNgramLetterModel):
   order = 2
   lCoeff = 0.9