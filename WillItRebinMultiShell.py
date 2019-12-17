#!/usr/bin/env python

##     Will It Rebin?     ##
##                        ##
##    Copyright 2013,     ##
## Martin Cramer Pedersen ##
##      mcpe@nbi.dk       ##

## This file is part of WillItRebin.                                    ##
##                                                                      ##
## WillItRebin is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by ##
## the Free Software Foundation, either version 3 of the License, or    ##
## (at your option) any later version.                                  ##
##                                                                      ##
## WillItRebin is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of       ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        ##
## GNU General Public License for more details.                         ##
##                                                                      ##
## You should have received a copy of the GNU General Public License    ##
## along with WillItRebin  If not, see <http://www.gnu.org/licenses/>.  ##

## If you use this software in        ##
## your work, please cite:            ##
##                                    ##
## Pedersen et al.,                   ##
## Journal of Applied Crystallography ##
## Etc                                ##

## Libraries
import re
import os
import sys
import math
import getopt
import argparse

# Examples
#
# help:
# python WillItRebinMultiShell.py -h
#
# start with GUI:
# python WillItRebinMultiShell.py
#
# run without GUI:
# python WillItRebinMultiShell.py -nox -f testdata/[5-8]*_NTJ_phy*x.dat -n 0 -q ang -r log 1.04 -s 1.0
# python WillItRebinMultiShell.py -nox -f testdata/[5-8]*_NTJ_phy*x.dat -n 5 -q ang -r lin 8 -s 1.5
# python WillItRebinMultiShell.py -nox -f testdata/[5-8]*_NTJ_phy*x.dat -r log 1.06 

# TODO
# -integrate argparsing into a class member, remigrate global RebinFncs as class members
# -add option to create log file
# -write call arguments and some stats into each RB* file; add a columns header

try:
    import wx
except:
    print ""
    print "*************************************************************************"
    print "* WillItRebin failed to import wxPython - is it correctly installed...? *"
    print "*************************************************************************"
    print ""
    sys.exit(1)

import wx.lib.scrolledpanel


## Plotting libraries
import matplotlib
matplotlib.interactive(True)
matplotlib.use('WXAgg')
import pylab

## Define main class and text
class MainCls(wx.Frame):
    def __init__(self, parent, id):
        self.cwd = os.getcwd()
        print("self.cwd = {}".format(self.cwd))
        
        # Initial widgets
        wx.Frame.__init__(self, parent, id, 'Will It Rebin?', style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        
        BoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.Panel = wx.lib.scrolledpanel.ScrolledPanel(self, -1)
        self.Panel.SetupScrolling(False, True)
        
        # Widgets for data-file
        BoxSizer.AddSpacer(10)        
        
        DataTextSizer = wx.BoxSizer(wx.HORIZONTAL)
        DataTextSizer.AddSpacer(10)
        
        DataText = wx.StaticText(self.Panel, -1, 'Location of data:', size = (330, -1))
        DataTextSizer.Add(DataText)
        
        BoxSizer.Add(DataTextSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(10)
        
        DataPathSizer = wx.BoxSizer(wx.HORIZONTAL)
        DataPathSizer.AddSpacer(10)
        
        self.DataPathTxt = wx.StaticText(self.Panel, -1, 'N/A')
        self.DataPathStr = 'N/A'
        DataPathSizer.Add(self.DataPathTxt)
        
        BoxSizer.Add(DataPathSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(130)
        
        DataBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        DataBtnSizer.AddSpacer(10)
        
        BrowseDataBtn = wx.Button(self.Panel, label = 'Browse')
        self.Bind(wx.EVT_BUTTON, self.BrowseDataFnc, BrowseDataBtn)
        DataBtnSizer.Add(BrowseDataBtn, 1, wx.EXPAND)
        DataBtnSizer.AddSpacer(10)
        
        BoxSizer.Add(DataBtnSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(10)
        
        LineData = wx.StaticLine(self.Panel, -1)
        BoxSizer.Add(LineData, 0, wx.EXPAND|wx.HORIZONTAL)
        
        # Widgets used to set rebinning factor
        BoxSizer.AddSpacer(10)
        
        LogRebinSizer = wx.BoxSizer(wx.HORIZONTAL)
        LogRebinSizer.AddSpacer(10)        
        
        self.RBLog = wx.RadioButton(self.Panel, -1, 'Logarithmic rebinning - coefficient:')
        LogRebinSizer.Add(self.RBLog)  
        
        BoxSizer.Add(LogRebinSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(10)
        
        LogRebinCtrlSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.LogRebinCtrl = wx.TextCtrl(self.Panel, -1, '', size = (150, -1))
        self.LogRebinCtrl.SetValue('1.04')
        LogRebinCtrlSizer.Add(self.LogRebinCtrl)
        
        BoxSizer.Add(LogRebinCtrlSizer, 0, wx.ALIGN_CENTER, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(10)
        
        LinRebinSizer = wx.BoxSizer(wx.HORIZONTAL)
        LinRebinSizer.AddSpacer(10)        
        
        self.RBLin = wx.RadioButton(self.Panel, -1, 'Linear rebinning - coefficient:')
        LinRebinSizer.Add(self.RBLin)  
        
        BoxSizer.Add(LinRebinSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(10)
        
        LinRebinCtrlSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.LinRebinCtrl = wx.SpinCtrl(self.Panel, -1, "", size = (100, -1), min = 0, max = 100000, initial = 2)
        LinRebinCtrlSizer.Add(self.LinRebinCtrl)
        
        BoxSizer.Add(LinRebinCtrlSizer, 0, wx.ALIGN_CENTER, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(10)
        
        LineRebin = wx.StaticLine(self.Panel, -1)
        BoxSizer.Add(LineRebin, 0, wx.EXPAND|wx.HORIZONTAL)
        
        # Widgets used to set scaling factor
        BoxSizer.AddSpacer(10)
        
        ScaleSizer = wx.BoxSizer(wx.HORIZONTAL)
        ScaleSizer.AddSpacer(10) 
        
        ScaleText = wx.StaticText(self.Panel, -1, 'Scaling factor:')
        ScaleSizer.Add(ScaleText)
        
        BoxSizer.Add(ScaleSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(1)
        
        ScaleCtrlSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.ScaleCtrl = wx.TextCtrl(self.Panel, -1, '', (150, -1))
        self.ScaleCtrl.SetValue('1.0')
        ScaleCtrlSizer.Add(self.ScaleCtrl)
        
        BoxSizer.Add(ScaleCtrlSizer, 0, wx.ALIGN_CENTER, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(1)
        
        LineScale = wx.StaticLine(self.Panel, -1)
        BoxSizer.Add(LineScale, 0, wx.EXPAND|wx.HORIZONTAL)
        
        # Widget used to set number of skipped points
        BoxSizer.AddSpacer(10)
        
        SkipSizer = wx.BoxSizer(wx.HORIZONTAL)
        SkipSizer.AddSpacer(10)
        
        SkipText = wx.StaticText(self.Panel, -1, 'Number of skipped points:')
        SkipSizer.Add(SkipText)
        
        BoxSizer.Add(SkipSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(1)
        
        SkipCtrlSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.SkipSpn = wx.SpinCtrl(self.Panel, -1, '', (150, -1))
        self.SkipSpn.SetRange(0, 10000)
        self.SkipSpn.SetValue(0)
        SkipCtrlSizer.Add(self.SkipSpn)
        
        BoxSizer.Add(SkipCtrlSizer, 0, wx.ALIGN_CENTER, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(1)
        
        SkipLine = wx.StaticLine(self.Panel, -1)
        BoxSizer.Add(SkipLine, 0, wx.EXPAND|wx.HORIZONTAL)
        
        # Widget used for rescaling q from nm^-1 to AA^-1
        BoxSizer.AddSpacer(10)
        
        AngstromSizer = wx.BoxSizer(wx.HORIZONTAL)
        AngstromSizer.AddSpacer(10)
        
        AngstromText = wx.StaticText(self.Panel, -1, 'Rescale q from inverse nm to inverse angstrom:')
        AngstromSizer.Add(AngstromText)
        
        BoxSizer.Add(AngstromSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(1)
        
        AngstromCheckboxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.AngstromCheckbox = wx.CheckBox(self.Panel, -1, '', size = (30, -1))
        AngstromCheckboxSizer.Add(self.AngstromCheckbox)
        
        BoxSizer.Add(AngstromCheckboxSizer, 0, wx.ALIGN_CENTER, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(1)
        
        AngstromLine = wx.StaticLine(self.Panel, -1)
        BoxSizer.Add(AngstromLine, 0, wx.EXPAND|wx.HORIZONTAL)
        
        # Widgets creating buttons
        BoxSizer.AddSpacer(1)
        
        RebinBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        RebinBtnSizer.AddSpacer(10)
        
        self.RebinBtn = wx.Button(self.Panel, label = 'Rebin')
        self.Bind(wx.EVT_BUTTON, self.RebinFnc, self.RebinBtn)
        self.RebinBtn.Disable()
        
        RebinBtnSizer.Add(self.RebinBtn, 1, wx.EXPAND)
        RebinBtnSizer.AddSpacer(10)
        
        BoxSizer.Add(RebinBtnSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(1)        
        
        PlotBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        PlotBtnSizer.AddSpacer(10)
        
        self.PlotDataBtn = wx.Button(self.Panel, label = 'Plot original data')
        self.Bind(wx.EVT_BUTTON, self.PlotDataFnc, self.PlotDataBtn)
        self.PlotDataBtn.Disable()
        
        PlotBtnSizer.Add(self.PlotDataBtn, 1, wx.EXPAND)
        PlotBtnSizer.AddSpacer(10)
        
        BoxSizer.Add(PlotBtnSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(1)
        
        RebinBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        RebinBtnSizer.AddSpacer(10) 
        
        self.PlotRebinBtn = wx.Button(self.Panel, label = 'Plot rebinned data')
        self.Bind(wx.EVT_BUTTON, self.PlotRebinFnc, self.PlotRebinBtn)
        self.PlotRebinBtn.Disable()
        
        RebinBtnSizer.Add(self.PlotRebinBtn, 1, wx.EXPAND)
        RebinBtnSizer.AddSpacer(10)
        
        BoxSizer.Add(RebinBtnSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        BoxSizer.AddSpacer(1)
        
        QuitBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        QuitBtnSizer.AddSpacer(10)
        
        QuitBtn = wx.Button(self.Panel, label = 'Quit')
        self.Bind(wx.EVT_BUTTON, self.CloseWindowFnc, QuitBtn)
        self.Bind(wx.EVT_CLOSE, self.CloseWindowFnc)
        
        QuitBtnSizer.Add(QuitBtn, 1, wx.EXPAND)
        QuitBtnSizer.AddSpacer(10)
        
        BoxSizer.Add(QuitBtnSizer, 0, wx.EXPAND|wx.HORIZONTAL)
        
        # Store initial directory upon initialization
        InitialDirectoryStr = os.path.abspath(os.path.dirname(sys.argv[0]))
        os.chdir(InitialDirectoryStr)
        
        # Conclusion of init-function
        self.Panel.SetSizerAndFit(BoxSizer)
        self.SetSizerAndFit(BoxSizer)
        self.SetAutoLayout(True)
        self.Panel.Layout()
        self.Layout()

## Define rebinning function
    def RebinFnc(self, event):
        if self.RBLog.GetValue():
            self.LogRebinFnc()
        else:
            self.LinRebinFnc()

    def LinRebinFnc(self):
        DataPathStr = self.DataPathStr
        SkippedPoints = int(self.SkipSpn.GetValue())
        RebinningFactor = int(self.LinRebinCtrl.GetValue())
        ScaleFactor = float(self.ScaleCtrl.GetValue())
        if self.AngstromCheckbox.GetValue():
            QScaling = 0.1
        else:
            QScaling = 1.0
            
        self.RebinnedDataPath, DispMessage = LinRebinFncExt(DataPathStr, SkippedPoints, RebinningFactor, ScaleFactor, QScaling)
        
        wx.MessageBox(DispMessage, "Did it rebin...?", wx.OK | wx.ICON_INFORMATION)
        
        self.PlotRebinBtn.Enable()

    def LogRebinFnc(self):
        DataPathStr = self.DataPathStr
        SkippedPoints = int(self.SkipSpn.GetValue())
        RebinningFactor = float(self.LogRebinCtrl.GetValue())
        ScaleFactor = float(self.ScaleCtrl.GetValue())
        if self.AngstromCheckbox.GetValue():
            QScaling = 0.1
        else:
            QScaling = 1.0
            
        self.RebinnedDataPath, DispMessage = LogRebinFncExt(DataPathStr, SkippedPoints, RebinningFactor, ScaleFactor, QScaling)
        
        wx.MessageBox(DispMessage, "Did it rebin...?", wx.OK | wx.ICON_INFORMATION)
        
        self.PlotRebinBtn.Enable()

## Define plotting functions
    def PlotDataFnc(self, event):
        try:
            self.Figure1.clf()
        except:
            pass
        
        LowestYValue = 100000000000000
        fmtvec=['r.', 'gd', 'b^', 'mv', 'ks', 'cx']
        
        self.Figure1 = pylab.figure(1)
        Subplot = pylab.subplot(111)
        
        # loop over all files
        for k in range(len(self.DataPathStr)):
            Data = GetData(self.DataPathStr[k])
            
            xDataArr = Data[0]
            yDataArr = Data[1]
            wDataArr = Data[2]
            
            xData = []
            yData = []
            wData = []
            
            NumberOfPoints = len(xDataArr)
            
            for i in range(NumberOfPoints):
                if yDataArr[i] > 0:
                    xData.append(xDataArr[i])
                    yData.append(yDataArr[i])
                    wData.append(wDataArr[i])
            
            Subplot.errorbar(xData, yData, yerr = wData, fmt = fmtvec[k%len(fmtvec)], label=os.path.basename(self.RebinnedDataPath[k]))
            
            for y in yData:
                if y < LowestYValue:
                    LowestYValue = y
            
        Subplot.set_xscale('log', nonposx = 'clip')
        Subplot.set_yscale('log', nonposy = 'clip')
        Subplot.set_ylim(ymin = LowestYValue / 10.0)
        
        Subplot.set_xlabel('q')
        Subplot.set_ylabel('I')
        
        Subplot.legend(loc='best', shadow=True, fontsize='small')
        
        pylab.show()
        
    def PlotRebinFnc(self, event):
        try:
            self.Figure2.clf()
        except:
            pass
            
        LowestYValue = 100000000000000
        fmtvec=['r.', 'gd', 'b^', 'mv', 'ks', 'cx']
        
        self.Figure2 = pylab.figure(2)
        Subplot = pylab.subplot(111)
        
        # loop over all files
        for k in range(len(self.RebinnedDataPath)):
            Data = GetData(self.RebinnedDataPath[k])
            
            xDataArr = Data[0]
            yDataArr = Data[1]
            wDataArr = Data[2]
            
            xData = []
            yData = []
            wData = []
            
            NumberOfPoints = len(xDataArr)
            
            for i in range(NumberOfPoints):
                if yDataArr[i] > 0:
                    xData.append(xDataArr[i])
                    yData.append(yDataArr[i])
                    wData.append(wDataArr[i])
            
            Subplot.errorbar(xData, yData, yerr = wData, fmt = fmtvec[k%len(fmtvec)], label=os.path.basename(self.RebinnedDataPath[k]))
            
            for y in yData:
                if y < LowestYValue:
                    LowestYValue = y
        
        Subplot.set_xscale('log', nonposx = 'clip')
        Subplot.set_yscale('log', nonposy = 'clip')
        Subplot.set_ylim(ymin = LowestYValue / 10.0)
        
        Subplot.set_xlabel('q')
        Subplot.set_ylabel('I')
        
        Subplot.legend(loc='best', shadow=True, fontsize='small')
        
        pylab.show()

## Define function for filebrowsing for data
    def BrowseDataFnc(self, event):
        
        # do not use os.getcwd(), points always to $HOME
        FileDialogWindow = wx.FileDialog(None, 'Please select data-file(s)...', defaultDir=self.cwd, defaultFile = '', style = wx.OPEN | wx.MULTIPLE)
        
        if FileDialogWindow.ShowModal() == wx.ID_OK:
#            self.DataPathStr = FileDialogWindow.GetPath()
            self.DataPathStr = FileDialogWindow.GetPaths()
            
            print(self.DataPathStr)
            
            DataPathDisplayStr = ''
            
            for k in range(len(self.DataPathStr)):
                print self.DataPathStr[k]
            
            # print only info about first 6 files in list
            for k in range(min(6,len(self.DataPathStr))):
                DummyStr = str(self.DataPathStr[k])
                
                if len(DummyStr) > 40:
                    DummyStr = '...' + DummyStr[-40:]
                
                DataPathDisplayStr += DummyStr + '\n'
            
            if len(self.DataPathStr) > 6:
               DataPathDisplayStr = DataPathDisplayStr + '( plus ' + str( len(self.DataPathStr) - 6 ) + ' further file(s) )'
            
            self.DataPathTxt.SetLabel(DataPathDisplayStr)
            
            # use 1st file for directory change
            DirectoryStr = os.path.dirname(self.DataPathStr[0])
            os.chdir(DirectoryStr)
            
            # setup the array for rebinned files as a deep copy of the native 
            self.RebinnedDataPath=self.DataPathStr[:]
            
            self.RebinBtn.Enable()
            self.PlotDataBtn.Enable()
            self.PlotRebinBtn.Disable()
        
        FileDialogWindow.Destroy()

## Define exit functions
    def CloseWindowFnc(self, event):
        try:
            pylab.close()
        except:
            pass
        
        sys.exit(0)

## Read data files
def GetData(filename):
    file = open(filename, 'rU')
    data = file.readlines()
    file.close()
    
    DataStrArr = []

    for line in data:
        DataStrArr.append(line)

    xDataStr = []
    yDataStr = []
    wDataStr = []
    
    xDataFlt = []
    yDataFlt = []
    wDataFlt = []
    
    # Look for optional sign, a decimal number and an optional exponential
    RegularExpression = r"\W*[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?"
    Pattern = re.compile(RegularExpression, re.VERBOSE)

    for i in range(len(DataStrArr)):
        if DataStrArr[i][0] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ', '\t'):
            if len(Pattern.findall(DataStrArr[i])) in (3, 4):
                xDataStr.append(Pattern.findall(DataStrArr[i])[0])
                yDataStr.append(Pattern.findall(DataStrArr[i])[1])
                wDataStr.append(Pattern.findall(DataStrArr[i])[2])

    for item in xDataStr:
        xDataFlt.append(float(item))
    
    for item in yDataStr:
        yDataFlt.append(float(item))
        
    for item in wDataStr:
        wDataFlt.append(float(item))
    
    return xDataFlt, yDataFlt, wDataFlt


def LinRebinFncExt(DataPathStr, SkippedPoints, RebinningFactor, ScaleFactor, QScaling):
    DispMessage = ''
    RebinnedDataPath = DataPathStr[:]
    
    # loop over all files
    for k in range(len(DataPathStr)):
    
        RebinnedDataPath[k] = os.path.abspath(os.path.dirname(DataPathStr[k])) + '/RB' + os.path.basename(DataPathStr[k])
        
        Data = GetData(DataPathStr[k])
        xDataArr = Data[0]
        yDataArr = Data[1]
        wDataArr = Data[2]
        
        NumberOfOriginalDatapoints = len(xDataArr)
        
        TotalNumberOfPointsBinned = 0
        BinNumber = 0
        
        xRebinned = []
        yRebinned = []
        wRebinned = []
        
        while TotalNumberOfPointsBinned < NumberOfOriginalDatapoints - SkippedPoints:
            PointsInCurrentBin = RebinningFactor
            
            if PointsInCurrentBin + TotalNumberOfPointsBinned > NumberOfOriginalDatapoints - SkippedPoints:
                PointsInCurrentBin = NumberOfOriginalDatapoints - SkippedPoints - TotalNumberOfPointsBinned
            
            SumX = 0.0
            SumY = 0.0
            SumW = 0.0
            
            for i in range(PointsInCurrentBin):
                SumX += xDataArr[i + TotalNumberOfPointsBinned + SkippedPoints]
                SumY += yDataArr[i + TotalNumberOfPointsBinned + SkippedPoints]
                SumW += wDataArr[i + TotalNumberOfPointsBinned + SkippedPoints]**2
            
            AverageX = SumX / PointsInCurrentBin * QScaling
            AverageY = SumY / PointsInCurrentBin * ScaleFactor
            AverageW = SumW**0.5 / PointsInCurrentBin * ScaleFactor
            
            xRebinned.append(AverageX)
            yRebinned.append(AverageY)
            wRebinned.append(AverageW)
            
            BinNumber += 1
            TotalNumberOfPointsBinned += PointsInCurrentBin
        
        if DataPathStr[k] != 'N/A':
            file = open(RebinnedDataPath[k], 'w')
            file.write('### Datafile rebinned by Will It Rebin...? \n')
            file.write('### Original datafile = ' + DataPathStr[k] + '\n')
            file.write('### Number of datapoints = ' + str(BinNumber) + '\n')
            
            for i in range(BinNumber):
                file.write('   ' + '{0:.10e}'.format(xRebinned[i]) + '   ' + '{0:.10e}'.format(yRebinned[i]) + '   ' + '{0:.10e}'.format(wRebinned[i]) + '   0.0\n')
            
            file.close()
        
        Message = 'The algorithm found ' + str(NumberOfOriginalDatapoints) + ' points, which were rebinned into ' + str(BinNumber) + ' points. The rebinned data can be found in ' + RebinnedDataPath[k] + '\n'
        print(Message)
        
        # accumulate messages for first 6 files
        if k < 6:
            DispMessage += Message + '\n'
    
    if len(DataPathStr) > 6:
        DispMessage += '( information for ' + str( len(DataPathStr) - 6 ) + ' further file(s) truncated )'
    
    return RebinnedDataPath, DispMessage


def LogRebinFncExt(DataPathStr, SkippedPoints, RebinningFactor, ScaleFactor, QScaling):
    DispMessage = ''
    RebinnedDataPath = DataPathStr[:]
    
    # loop over all files
    for k in range(len(DataPathStr)):
    
        RebinnedDataPath[k] = os.path.abspath(os.path.dirname(DataPathStr[k])) + '/RB' + os.path.basename(DataPathStr[k])
        
        Data = GetData(DataPathStr[k])
        xDataArr = Data[0]
        yDataArr = Data[1]
        wDataArr = Data[2]
        
        NumberOfOriginalDatapoints = len(xDataArr)
        
        TotalNumberOfPointsBinned = 0
        
        BinNumber = 0
        
        xRebinned = []
        yRebinned = []
        wRebinned = []
        
        while TotalNumberOfPointsBinned < NumberOfOriginalDatapoints - SkippedPoints:
            BinNumber += 1
            
            PointsInCurrentBin = int(RebinningFactor**BinNumber)
            
            if PointsInCurrentBin + TotalNumberOfPointsBinned > NumberOfOriginalDatapoints - SkippedPoints:
                PointsInCurrentBin = NumberOfOriginalDatapoints - SkippedPoints - TotalNumberOfPointsBinned
            
            SumX = 0.0
            SumY = 0.0
            SumW = 0.0
            
            for i in range(PointsInCurrentBin):
                SumX += xDataArr[i + TotalNumberOfPointsBinned + SkippedPoints]
                SumY += yDataArr[i + TotalNumberOfPointsBinned + SkippedPoints]
                SumW += wDataArr[i + TotalNumberOfPointsBinned + SkippedPoints]**2
            
            AverageX = SumX / PointsInCurrentBin * QScaling
            AverageY = SumY / PointsInCurrentBin * ScaleFactor
            AverageW = SumW**0.5 / PointsInCurrentBin * ScaleFactor
            
            xRebinned.append(AverageX)
            yRebinned.append(AverageY)
            wRebinned.append(AverageW)
            
            TotalNumberOfPointsBinned += PointsInCurrentBin
        
        if DataPathStr[k] != 'N/A':
            file = open(RebinnedDataPath[k], 'w')
            file.write('### Datafile rebinned by Will It Rebin...? \n')
            file.write('### Original datafile = ' + DataPathStr[k] + '\n')
            file.write('### Number of datapoints = ' + str(BinNumber) + '\n')
            
            for i in range(BinNumber):
                file.write('   ' + '{0:.10e}'.format(xRebinned[i]) + '   ' + '{0:.10e}'.format(yRebinned[i]) + '   ' + '{0:.10e}'.format(wRebinned[i]) + '   0.0\n')
            
            file.close()
        
        Message = 'The algorithm found ' + str(NumberOfOriginalDatapoints) + ' points, which were rebinned into ' + str(BinNumber) + ' points. The rebinned data can be found in ' + RebinnedDataPath[k] + '\n'
        print(Message)
        
        # accumulate messages for first 6 files
        if k < 6:
            DispMessage += Message + '\n'
    
    if len(DataPathStr) > 6:
        DispMessage += '( information for ' + str( len(DataPathStr) - 6 ) + ' further file(s) truncated )'
    
    return RebinnedDataPath, DispMessage



def check_nonnegative_integer(arg):
    if int(arg) < 0:
        raise argparse.ArgumentTypeError("Argument %s for -n option must be a non-negative integer" % arg)

def check_nonnegative_float(arg):
    if float(arg) < 0:
        raise argparse.ArgumentTypeError("Argument {} for -s option must be non-negative".format(arg))

def check_rebinopts(arg):
    if arg[0] != 'log' and arg[0] != 'lin':
        raise argparse.ArgumentTypeError("First argument %s for -r option is neither lin or log" % arg[0])
    
    if arg[0] == 'log' and float(arg[1]) < 1.0:
        raise argparse.ArgumentTypeError("Second argument {} for -r option must be a float number >=1.0 for {} rebinning".format(arg[1], arg[0]))
    
    if arg[0] == 'lin' and ( float(arg[1]).is_integer() == False or float(arg[1]) < 1):
        raise argparse.ArgumentTypeError("Second argument {} for -r option must be a int number >=1 for {} rebinning".format(arg[1], arg[0]))


def check_qscale(arg):
    if arg != 'nm' and arg != 'ang':
        raise argparse.ArgumentTypeError("Q-scale argument %s for -q option is neither nm or ang" % arg)




## Boilerplate code linking program and widgets
if __name__ == '__main__':
    
    if len(sys.argv) == 1:
        # if options' length is 0 start GUI
        # cwd = os.getcwd()
        # print(cwd)
        App = wx.App()
        frame = MainCls(parent = None, id = -1)
        frame.Show()
        App.MainLoop()
    else:
        # Iterate the options and get the corresponding values
        
        # Construct the argument parser
        ap = argparse.ArgumentParser()

        try:
            # Add the arguments to the parser
            # -h automatically generated
            ap.add_argument('-nox', action='store_true', default=False, required=True, help='Required, if you wanna run it without GUI')
            ap.add_argument('-f', '--files', action='store', dest='filelist', default=[], required=True, nargs='+', help='Required, a list of files (relative paths)')
            ap.add_argument('-r', '--rebinning-type-coeff', action='store', dest='rebinopts', default=['log', '1.04'], required=False, nargs=2, help='lin/log and rebin factor (integer for lin), e.g. log 1.04 or lin 8, default log 1.04')
            ap.add_argument('-s', '--scale-factor', action='store', dest='scf', default=[1.0], required=False, nargs=1, help='Scaling factor for intensities, e.g. 2.4, default 1.0')
            ap.add_argument('-n', '--number-skipped-points', action='store', dest='nsp', default=[0], required=False, nargs=1, type=int, help='Number of skipped points at low Q, e.g. 5, default 0')
            ap.add_argument('-q', '--q-scale', action='store', dest='qsc', default=['ang'], required=False, nargs=1, help='Q-units: ang for [$\AA^{-1}$] and nm for [nm$^{-1}$], default ang')
            ap.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')

#            args = vars(ap.parse_args())
#            print args
#            print args['filelist']
#            print args['rebinopts']
#            print args['qscale']

            # parse
            args = ap.parse_args()
            print args
#            print args.filelist
#            print args.rebinopts
#            print args.scf
#            print args.qsc

            # check input
            check_nonnegative_integer(args.nsp[0])
            check_nonnegative_float(args.scf[0])
            check_rebinopts(args.rebinopts)
            check_qscale(args.qsc[0])

        except argparse.ArgumentTypeError:
            print('An error occured in your commandline arguments:')
            raise

        try:
            for file in args.filelist:
                if os.path.isfile(file) == False :
                    raise os.error("File %s does not exist" % file)

        except os.error:
            raise
        
        
        DataPathStr = args.filelist[:]
        # int + float conversion necessary 
        SkippedPoints = int(args.nsp[0])
        ScaleFactor = float(args.scf[0])
        if args.rebinopts[0] == 'lin':
            RebinningFactor = int(args.rebinopts[1])
        else:
            RebinningFactor = float(args.rebinopts[1])
        
        if args.qsc[0] == 'nm':
            QScaling = 0.1
        else:
            QScaling = 1.0
        
        print("DataPathStr = {}".format(DataPathStr))
        print("SkippedPoints = {}".format(SkippedPoints))
        print("RebinningType = {}".format(args.rebinopts[0]))
        print("RebinningFactor = {}".format(RebinningFactor))
        print("ScaleFactor = {}".format(ScaleFactor))
        print("QScaling = {}".format(QScaling))

        if args.rebinopts[0] == 'log':
            LogRebinFncExt(DataPathStr, SkippedPoints, RebinningFactor, ScaleFactor, QScaling)
        else:
            LinRebinFncExt(DataPathStr, SkippedPoints, RebinningFactor, ScaleFactor, QScaling)

