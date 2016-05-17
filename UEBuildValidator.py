#!/usr/bin/python

# MIT License
# Copyright (C)  2016  Marcin Polaczyk (me@mpolaczyk.pl)
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import os as os
from glob import glob
import json
import re

#######  DATA CLASSES + DATA GATHERING

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
    def __init__(self, name, engineDir, pluginsUseEditorAppName=False):
        Binary.__init__(self, name, engineDir)
        self.PluginsUseEditorAppName = pluginsUseEditorAppName
        
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
        appName = ''
        if self.PluginsUseEditorAppName:
            appName = 'UE4Editor'
        else:
            appName = self.Name
        pluginNamePattern = re.compile("Plugins(.*)\\\\([a-zA-Z]+)\\\\Binaries\\\\Win64\\\\" + appName + "\.modules")
        pluginList = []
        for modulePath in modulePaths:
            match = pluginNamePattern.search(modulePath)
            if match:
                additionalPath = match.group(1)
                pluginName = match.group(2)
                if len(pluginName) > 1:
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
    def __init__(self, name, engineDir, additionalPath, appName):
        self.AdditionalPath = additionalPath
        self.AppName = appName
        Binary.__init__(self, name, engineDir)
        
    def GetModulesFilePath(self):
        return self.EngineDir + '\Engine\Plugins' + self.AdditionalPath + '\\' + self.Name + '\Binaries\Win64\\' + self.AppName + '.modules'

class GamePlugin(Binary):
    def __init__(self, name, engineDir, gameName):
        self.GameName = gameName
        Binary.__init__(self, name, engineDir)
        
    def GetModulesFilePath(self):
        return self.EngineDir + '\\' + self.GameName + '\Plugins\\' + self.Name + '\Binaries\Win64\UE4Editor.modules'


            
class EngineApp(App):
    def __init__(self, name, engineDir):
        App.__init__(self, name, engineDir)

    def GetModulesFilePath(self):
        return self.EngineDir + '\Engine\Binaries\Win64\\' + self.Name + '.modules'

    def GetPluginsDir(self):
        return self.EngineDir + '\Engine\Plugins\\'

    def AddPlugin(self, modulePath, additionalPath, pluginName):
        self.Plugins.append(EnginePlugin(pluginName, self.EngineDir, additionalPath, self.Name))
    
    
class GameApp(App):
    def __init__(self, name, engineDir):
        App.__init__(self, name, engineDir, True)

    def GetModulesFilePath(self):
        return self.EngineDir + '\\' + self.Name + '\Binaries\Win64\UE4Editor.modules'
        
    def GetPluginsDir(self):
        return self.EngineDir + '\\' + self.Name + '\Plugins\\'

    def AddPlugin(self, modulePath, additionalPath, pluginName):
        self.Plugins.append(GamePlugin(pluginName, self.EngineDir, self.Name))


#######  DATA ANALYSIS


def Validate_App_BuildId(app):
    print 'Validating BuildId\'s in: ' + app.Name
    print 'BuildId: ' + app.BuildId
    score = 0
    for plugin in app.Plugins:
        if plugin.BuildId != app.BuildId:
            score = score + 1
            print '  Mismatch plugin: ' + plugin.BuildId + ' ' + plugin.Name
    print 'Errors found: ' + str(score)
        
