#!/usr/bin/python

# Copyright 2016 Marcin Polaczyk All Rights Reserved.

import os as os
from glob import glob
import json
import re


class Module():
    def __init__(self, name, fileName):
        self.Name = name
        self.FileName = fileName
        
class Binary():
    def __init__(self, name, engineDir):
        self.Name = name
        self.EngineDir = engineDir
        print self.__class__.__name__ + ': ' + self.Name
        print '  Engine dir: ' + self.EngineDir
        
        # Binary can have modules
        self.BuildId = 0            # guid
        self.ModulesFilePath = ''   # absolute path to file
        self.Modules = []           # list of Module
        self.ReadModulesFile()

    @staticmethod
    def OpenModulesFile(filePath):
        with open(filePath, 'r') as r:
            data = json.load(r)
            r.close()
            return [data["BuildId"], data["Modules"]]
    
    def ReadModulesFile(self):
        path = self.GetModulesFilePath()
        if not os.path.isfile(path):
            print 'ERROR: Unable to locate ' + path
        [buildId, modulesDict] = Binary.OpenModulesFile(path)
        self.BuildId = buildId
        self.Modules = []
        self.ModulesFilePath = path
        for key in modulesDict.keys():
                self.Modules.append(Module(key, modulesDict[key]))
        print '  Modules file: ' + self.ModulesFilePath
        print '  Build id: ' +str(self.BuildId)
        print '  Modules: ' + str(len(self.Modules))
        return

    def GetModulesFilePath(self):
        return 'override this'

class App(Binary):
    def __init__(self, name, engineDir):
        Binary.__init__(self, name, engineDir)

        # Application can have plugins
        self.Plugins = []
        self.DiscoverPlugins()

    def GetPluginsDir(self):
        return 'override this'

    def IsPluginEnabled(self, pluginName):
        return True #override this
    
    def AddPlugin(self, modulePath, additionalPath, pluginName):
        return # override this
    
    def DiscoverPlugins(self):
        path = self.GetPluginsDir()
        # find all module files in plugin directory
        modulePaths = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.modules'))]
        # cut plugin names from module file paths
        pluginNamePattern = re.compile("Plugins(.*)\\\\([a-zA-Z]+)\\\\Binaries\\\\Win64\\\\UE4Editor\.modules")
        pluginList = []
        for modulePath in modulePaths:
            match = pluginNamePattern.search(modulePath)
            if match:
                additionalPath = match.group(1)
                pluginName = match.group(2)
                if len(pluginName) > 1 and len(additionalPath) > 1:
                    pluginList.append([modulePath, additionalPath, pluginName])
        # remove plugins that are disabled for an app
        for p in pluginList:
            if not self.IsPluginEnabled(p[2]):
                pluginList.remove(p)
        print '  Plugins: ' + str(len(pluginList))
        # add plugins
        for p in pluginList:
            self.AddPlugin(p[0], p[1], p[2])
        
        
class EnginePlugin(Binary):
    def __init__(self, name, engineDir, additionalPath):
        self.AdditionalPath = additionalPath
        Binary.__init__(self, name, engineDir)
        
    def GetModulesFilePath(self):
        return self.EngineDir + '\Engine\Plugins' + self.AdditionalPath + '\\' + self.Name + '\Binaries\Win64\UE4Editor.modules'

class GamePlugin(Binary):
    def __init__(self, name, engineDir, gameName):
        self.GameName = gameName
        Binary.__init__(self, name, engineDir)
        
    def GetModulesFilePath(self):
        return self.EngineDir + '\\' + self.GameName + '\Plugins\\' + self.Name + '\Binaries\Win64\UE4Editor.modules'
            
class EditorApp(App):
    def __init__(self, engineDir):
        App.__init__(self, "UE4Editor", engineDir)

    def GetModulesFilePath(self):
        return self.EngineDir + '\Engine\Binaries\Win64\UE4Editor.modules'

    def GetPluginsDir(self):
        return self.EngineDir + '\Engine\Plugins\\'

    def AddPlugin(self, modulePath, additionalPath, pluginName):
        self.Plugins.append(EnginePlugin(pluginName, self.EngineDir, additionalPath))
    
    
class GameApp(App):
    def __init__(self, name, engineDir):
        App.__init__(self, name, engineDir)

    def GetModulesFilePath(self):
        return self.EngineDir + '\\' + self.Name + '\Binaries\Win64\UE4Editor.modules'
        


