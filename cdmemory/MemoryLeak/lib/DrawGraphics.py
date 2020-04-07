from reportlab.graphics.shapes import Drawing, Group
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib import colors
from reportlab.graphics.widgets.grids import DoubleGrid, Grid
from time import strftime, localtime

class CLinePlot(LinePlot):
    def __init__(self):
        LinePlot.__init__(self)
    
    def draw(self):
        xva, yva = self.xValueAxis, self.yValueAxis
        if xva: xva.joinAxis = yva
        if yva: yva.joinAxis = xva

        yva.setPosition(self.x, self.y, self.height)
        yva.configure(self.data)

        # if zero is in chart, put x axis there, otherwise
        # use bottom.
        xAxisCrossesAt = yva.scale(0)
        if ((xAxisCrossesAt > self.y + self.height) or (xAxisCrossesAt < self.y)):
            y = self.y
        else:
            y = xAxisCrossesAt

        xva.setPosition(self.x, y, self.width)
        xva.configure(self.data)

        back = self.background
        if isinstance(back, Grid):
            if back.orientation == 'vertical' and xva._tickValues:
                xpos = list(map(xva.scale, [xva._valueMin] + xva._tickValues))
                steps = []
                for i in range(len(xpos)-1):
                    steps.append(xpos[i+1] - xpos[i])
                back.deltaSteps = steps
            elif back.orientation == 'horizontal' and yva._tickValues:
                ypos = list(map(yva.scale, [yva._valueMin] + yva._tickValues))
                steps = []
                for i in range(len(ypos)-1):
                    steps.append(ypos[i+1] - ypos[i])
                back.deltaSteps = steps
        elif isinstance(back, DoubleGrid):
            # Ideally, these lines would not be needed...
            back.grid0.x = self.x
            back.grid0.y = self.y
            back.grid0.width = self.width
            back.grid0.height = self.height
            back.grid1.x = self.x
            back.grid1.y = self.y
            back.grid1.width = self.width
            back.grid1.height = self.height

            # some room left for optimization...
            if back.grid0.orientation == 'vertical' and xva._tickValues:
                xpos = list(map(xva.scale, [xva._valueMin] + xva._tickValues))
                steps = []
                for i in range(len(xpos)-1):
                    steps.append(xpos[i+1] - xpos[i])
                back.grid0.deltaSteps = steps
            elif back.grid0.orientation == 'horizontal' and yva._tickValues:
                ypos = list(map(yva.scale, [yva._valueMin] + yva._tickValues))
                steps = []
                for i in range(len(ypos)-1):
                    steps.append(ypos[i+1] - ypos[i])
                back.grid0.deltaSteps = steps
            if back.grid1.orientation == 'vertical' and xva._tickValues:
                xpos = list(map(xva.scale, [xva._valueMin] + xva._tickValues))
                steps = []
                for i in range(len(xpos)-1):
                    steps.append(xpos[i+1] - xpos[i])
                back.grid1.deltaSteps = steps
            elif back.grid1.orientation == 'horizontal' and yva._tickValues:
                ypos = list(map(yva.scale, [yva._valueMin] + yva._tickValues))
                steps = []
                for i in range(len(ypos)-1):
                    steps.append(ypos[i+1] - ypos[i])
                back.grid1.deltaSteps = steps

        self.calcPositions()

        #width, height, scaleFactor = self.width, self.height, self.scaleFactor
        g = Group()

        g.add(self.makeBackground())
        g.add(self.xValueAxis)
        g.add(self.yValueAxis)
        g.add(self.makeLines())

        return g

class DrawGraphics(object):
    def __init__(self, data, name=None, fileName="", sampleRate=3):
        self._h = 500
        self._x = 40
        self._y = 40
        self._step = 60
        self._w = len(data[0])*sampleRate/2+0.1
        if self._w < 600:
            self._w = 600
        self.drawing = Drawing(self._w, self._h)
        self.data = data
        self.lp = self.initLinePlot()
        self.fn = fileName
        self.setLabels("Time", (self._w-self._x+20, self._y))
        self.setLabels("PSS(KB)", (self._x, self._h-self._y+20))
        if name:
            self.setLabels(name, (self._w/2-10, self._h-self._y+30), fontsize=18)
        self.drawLines()
    
    def initLinePlot(self):
        lp = CLinePlot()
        lp.x = self._x
        lp.y = self._y
        lp.height = self._h - self._y*2
        lp.width = self._w - self._x*2
        lp.joinedLines = 1
        lp.data = self.data
        lp.gridFirst = True
        lp.background = DoubleGrid()
        lp.background.grid0.strokeColor=colors.lightgrey
        lp.background.grid1.strokeColor=colors.lightgrey
        lp.background.grid0.x = lp.x
        lp.background.grid0.y = lp.y
        lp.background.grid0.width = lp.width
        lp.background.grid0.height = lp.height
        lp.background.grid1.x = lp.x
        lp.background.grid1.y = lp.y
        lp.background.grid1.width = lp.width
        lp.background.grid1.height = lp.height
        lp.xValueAxis.labelTextFormat = self.seconds2str
        lp.xValueAxis.valueStep = self._step
        lp.yValueAxis.valueMin = 0
        lp.yValueAxis.valueStep = 50000
        lp.yValueAxis.valueMax = 400000
        return lp
    
    def seconds2str(self, seconds):
        return strftime('%H:%M', localtime(seconds))
    
    def setLabels(self, text, pos, fontsize=14):
        label = Label()
        label.setText(text)
        label.x = pos[0]
        label.y = pos[1]
        label.fontSize = fontsize
        label.fillColor = colors.red
        self.drawing.add(label)
        
    def drawLines(self):
        import os
        self.drawing.add(self.lp)
        try:
            self.drawing.save(formats=['jpg'],outDir=os.path.dirname(self.fn),fnRoot=os.path.basename(self.fn))
        except Exception as e:
            print(e)

if __name__ == "__main__":
    f = open(r"G:\cdmemory\MemoryLeak\report\source_data\Camera_case_testSwitchScenario_2020-03-31-19-55-15_com.tcl.camera.txt")
    d = [eval(line.strip()) for line in f]
    print(d)
    f.close()
    #_monthlyIndexData = [[(1444444686, 145559), (1444444689, 141443), (1444444691, 141427), (1444444694, 132675), (1444444697, 142765), (1444444700, 170040), (1444444702, 147904), (1444444705, 155508), (1444444708, 172720), (1444444711, 172744), (1444444714, 152244), (1444444717, 172638), (1444444720, 178550), (1444444723, 176662), (1444444726, 153268), (1444444729, 164388), (1444444732, 148078), (1444444735, 146835), (1444444738, 176143), (1444444741, 151623), (1444444744, 169903), (1444444747, 173585), (1444444750, 170377), (1444444752, 138143), (1444444755, 174081), (1444444758, 166445), (1444444761, 150127), (1444444764, 150305), (1444444767, 171551), (1444444770, 174533), (1444444772, 152525), (1444444775, 180587), (1444444778, 178391), (1444444781, 165683), (1444444784, 148005), (1444444787, 172009), (1444444789, 175299), (1444444792, 140659), (1444444795, 164873), (1444444798, 177213), (1444444801, 169485), (1444444804, 151817), (1444444807, 184449), (1444444810, 180849), (1444444813, 163481), (1444444815, 154245), (1444444818, 176433), (1444444821, 173565), (1444444824, 149409), (1444444827, 190189), (1444444830, 174189), (1444444833, 149977), (1444444836, 167425), (1444444839, 178313), (1444444841, 167217), (1444444844, 152065), (1444444847, 174137), (1444444850, 174617), (1444444853, 142693), (1444444856, 161161), (1444444859, 174565), (1444444861, 174537), (1444444864, 148289), (1444444867, 178065), (1444444870, 177349), (1444444873, 154217), (1444444876, 167279), (1444444878, 174591), (1444444881, 179259), (1444444884, 154169), (1444444887, 169755), (1444444890, 179919), (1444444893, 157863), (1444444896, 167811), (1444444899, 163259), (1444444902, 148025), (1444444905, 186577), (1444444907, 174389), (1444444910, 173377), (1444444913, 149505), (1444444916, 184467), (1444444919, 173317), (1444444922, 173461), (1444444924, 150153), (1444444927, 114676)]]
    _data=[]
    _data.append(d)
    DrawGraphics(_data, "case", "report\\test")
    
