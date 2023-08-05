import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import os
import time
from scipy import signal
from collections import OrderedDict


class PeakTrackingToTemp():
    """
    This class is used to track temperature changes from XRD data.
    """

    def __init__(self, calFile, dataDirectory, xVals, yVals, tol=2, roomTemp=23, showText=False):
        self.calFile = pd.read_csv(calFile)
        self.calibR, self.calibF = self.line_chunker(self.calFile[xVals], self.calFile[yVals], tol=tol)
        self.dataDirectory = dataDirectory
        self.roomTemp = roomTemp
        self.showText = showText
        return

    def line_chunker(self, x, y, tol=2):
        """
        Description: Takes any arbitrary x y data and fits lines through it.
        """
        range_dict = OrderedDict()
        mini_y = []
        for i, val in enumerate(y):
            if len(mini_y) == 0:
                saved_i = i
            mini_y.append(val)
            if len(mini_y) > 1:
                fit = np.polyfit(x[saved_i:i + 1], mini_y, 1)
                curve = [np.polyval(fit, n) for n in x[saved_i:i + 1]]
                for i2, mini_val in enumerate(mini_y):
                    diff = np.absolute(((curve[i2] - mini_val) / mini_val) * 100)
                    if diff > tol:
                        range_dict[str(x[saved_i]) + '_' + str(x[i])] = np.polyfit(x[saved_i:i], mini_y[0:-1], 1)
                        mini_y = [val]
                        saved_i = i
                        break
        range_dict[str(x[saved_i]) + '_' + str(x[i])] = np.polyfit(x[saved_i:i + 1], mini_y, 1)
        range_dict2 = OrderedDict()
        count = 1
        for i, key in enumerate(range_dict.keys()):
            try:
                r = (range_dict[list(range_dict.keys())[i + 1]][1] - range_dict[key][1]) / (range_dict[key][0] - range_dict[list(range_dict.keys())[i + 1]][0])
            except:
                r2_keys = []
                for key2 in range_dict2.keys():
                    r2_keys.append(key2)
                new_key = r2_keys[i - 1].split('_')[1] + '_' + key.split('_')[1]
                range_dict2[new_key] = range_dict[key]
            if count == 1:
                new_key = key.split('_')[0] + '_' + str(r)
                range_dict2[new_key] = range_dict[key]
                count += 1
            else:
                r2_keys = []
                for key2 in range_dict2.keys():
                    r2_keys.append(key2)
                new_key = r2_keys[i - 1].split('_')[1] + '_' + str(r)
                range_dict2[new_key] = range_dict[key]

        def solve(t):
            for key in range_dict2.keys():
                if float(key.split('_')[0]) <= t < float(key.split('_')[1]):
                    result = np.polyval(range_dict2[key], t)
                    return result
            if t < float(list(range_dict2.keys())[0].split('_')[0]):
                result = np.polyval(range_dict2[list(range_dict2.keys())[0]], t)
                return result
            else:
                result = np.polyval(range_dict2[list(range_dict2.keys())[-1]], t)
                return result
        return range_dict2, solve

    def calculatePeakPosition(self, pattern):
        peaksInd = signal.find_peaks(pattern['y'], distance=10, prominence=100)
        peaksInd = list(peaksInd[0])
        plotablePeaksx = []
        plotablePeaksy = []
        for i in peaksInd:
            plotablePeaksx.append(list(pattern['x'])[i])
            plotablePeaksy.append(list(pattern['y'])[i])
        top5x = []
        for ind, i2 in enumerate(plotablePeaksx):
            if 5.5 < i2 < 6.2:
                top5x.append(plotablePeaksx[ind])
        return np.average(top5x)

    def calculatePeakPosition2(self, pattern):
        peaksInd = signal.find_peaks(pattern['y'], distance=10, prominence=100)
        peaksInd = list(peaksInd[0])
        plotablePeaksx = []
        plotablePeaksy = []
        for i in peaksInd:
            plotablePeaksx.append(list(pattern['x'])[i])
            plotablePeaksy.append(list(pattern['y'])[i])
        topx = plotablePeaksx[plotablePeaksy.index(max(plotablePeaksy))]
        return topx

    def posFromFile(self, file):
        fileNameList = file.split('_')
        xString = fileNameList[-4]
        yString = fileNameList[-7]
        x = float(xString.replace(',', '.').replace('mm', ''))
        y = float(yString.replace(',', '.').replace('mm', ''))
        return x, y

    def run(self, startInd=0):
        runQChiFiles = []
        plt.ion()
        xyList = []
        tList = []
        corList = []
        fig, ax = plt.subplots()
        tPlot = ax.scatter(1, 1, c=20)
        cb = fig.colorbar(tPlot, ax=ax)
        if self.showText:
            textList = []
        count = 0
        while True:
            totalQChiFiles = [i for i in os.listdir(self.dataDirectory) if i.endswith('q.chi')]
            totalQChiFiles = sorted(totalQChiFiles)
            for file in totalQChiFiles[startInd:]:
                if file in runQChiFiles:
                    continue
                print(file)
                runQChiFiles.append(file)
                x, y = self.posFromFile(file)
                if (x, y) not in xyList:
                    xyList.append((x, y))
                    pat = pd.read_csv(self.dataDirectory + '\\' + file, header=0, names=['x', 'y'], skiprows=1, delimiter=' ')
                    peakPos = self.calculatePeakPosition(pat)
                    temp = self.calibF(peakPos)
                    diff = self.roomTemp - temp
                    corList.append(diff)
                    temp = self.roomTemp
                    tList.append(temp)
                else:
                    xyInd = xyList.index((x, y))
                    pat = pd.read_csv(self.dataDirectory + '\\' + file, header=0, names=['x', 'y'], skiprows=1, delimiter=' ')
                    peakPos = self.calculatePeakPosition(pat)
                    temp = self.calibF(peakPos)
                    temp = temp + corList[xyInd]
                    if temp > 2500:
                        temp = np.nan
                    tList[xyInd] = temp
                print((temp, peakPos))
                xS = [i[0] for i in xyList]
                yS = [i[1] for i in xyList]
                if self.showText:
                    for i in textList:
                        i.remove()
                        textList.remove(i)
                cb.remove()
                tPlot.remove()
                tPlot = ax.scatter(xS, yS, c=tList)
                cb = fig.colorbar(tPlot, ax=ax)
                if self.showText:
                    for ind, i in enumerate(xS):
                        textList.append(plt.text(i, yS[ind], round(tList[ind],1)))
                tPlot.figure.canvas.draw_idle()
                tPlot.figure.canvas.flush_events()
                plt.pause(0.1)
