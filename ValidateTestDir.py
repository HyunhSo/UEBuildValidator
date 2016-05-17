#!/usr/bin/python

# Copyright 2016 Marcin Polaczyk All Rights Reserved.

import UEBuildValidator as bv
import os

enginedir = os.getcwd() + '\TestDir'
engine = bv.EditorApp(enginedir)
game = bv.GameApp("ExampleGame", enginedir)




