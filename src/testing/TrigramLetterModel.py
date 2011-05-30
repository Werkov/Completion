#!/usr/bin/python
#coding=utf-8

import string
import re
from AbstractNgramLetterModel import AbstractNgramLetterModel

class LetterModel (AbstractNgramLetterModel):
   order = 3
   lCoeff = 0.9