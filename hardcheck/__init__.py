#-------------------------------------------------------------------------------
# HardCheck: Checkpointing/Restore Framework for Reconfigurable Systems
# 
# Copyright (C) 2016, Shinya Takamaeda-Yamazaki
# License: Apache 2.0
#-------------------------------------------------------------------------------
from __future__ import absolute_import
from __future__ import print_function

# convert: convert an orignal RTL into a checkpoint-able RTL
from .convert import convert, convert_from_file

# generate: generate and add peripheral components to the checkpoint-able RTL

# pack: create an IP-core package by IPgen
