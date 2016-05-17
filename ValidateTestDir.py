#!/usr/bin/python

# Copyright 2016 Marcin Polaczyk All Rights Reserved.

import UEBuildValidator as bv
import os

enginedir = os.getcwd() + '\TestDir'

print '\n########\n'
engine = bv.EngineApp("UE4Editor", enginedir)
print '\n########\n'
frontend = bv.EngineApp("UnrealFrontend", enginedir)
print '\n########\n'
game = bv.GameApp("ExampleGame", enginedir)

print '\n########\n'
bv.Validate_App_BuildId(engine)
print '\n########\n'
bv.Validate_App_BuildId(frontend)
print '\n########\n'
bv.Validate_App_BuildId(game)
