import hashlib
import sqlite3
import sys

from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtWidgets import QFileDialog,QScrollBar
import pandas as pd

from define_cat import data
from plotcanvas import PlotCanvas

from listwid import TableWidgetDragRows
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np



class Ui_MainWindow(QtWidgets.QMainWindow,data):
    def __init__(self,parent=None):
        super(Ui_MainWindow,self).__init__(parent=parent)
        self.setupUi(self)
    # Gui
    def setupUi(self, graph):
        graph.setObjectName("graph")
        graph.resize(985, 693)
        self.centralwidget = QtWidgets.QWidget(graph)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.win = PlotCanvas(self.centralwidget)
        self.gridLayout.addWidget(self.win, 3, 0, 4, 3)
        self.gridLayout.addWidget(self.win.scroll, 5,0,6,3)
        self.gridLayout.addWidget(self.win.scroll2, 3,0,4,3)
        #self.gridLayout.addWidget(self.win.scroll3, 3,0,4,3)
        self.toolBarArea = NavigationToolbar(self.win,self.centralwidget,coordinates=True)

        self.win.mpl_connect('pick_event', self.onpick1)
        self.listcol = QtWidgets.QLineEdit(self.centralwidget)
        self.gridLayout.addWidget(self.listcol, 0, 1, 1, 2)

        self.listrows = QtWidgets.QLineEdit(self.centralwidget)
        self.gridLayout.addWidget(self.listrows, 1, 1, 1, 2)

        self.hafe = QtWidgets.QHBoxLayout(self.centralwidget)
        self.submit = QtWidgets.QPushButton(self.centralwidget)
        self.hafe.addWidget(self.submit)
        self.filterlist = QtWidgets.QLineEdit(self.centralwidget)
        self.hafe.addWidget(self.filterlist)

        self.submit.clicked.connect(self.filter)
        self.gridLayout.addItem(self.hafe, 2, 1, 1, 2)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.gridLayout.addItem(self.verticalLayout,0,3,3,1)
        self.getgraph_b()
        self.verticalLayout2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.gridLayout.addItem(self.verticalLayout2,3,3,1,0)
        self.getlist()

        graph.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(graph)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 985, 31))
        self.menuFile = QtWidgets.QMenu(self.menubar)
        graph.setMenuBar(self.menubar)
        self.actionOpen = QtWidgets.QAction(graph)
        self.menuFile.addAction(self.actionOpen)
        self.menubar.addAction(self.menuFile.menuAction())
        self.actionOpen.triggered.connect(self.file_open)
        saveFile = QtWidgets.QAction("&Save File", self)
        saveFile.triggered.connect(self.file_save)
        self.menuFile.addAction(saveFile)

        self.retranslateUi(graph)
        self.creatdateselect()
        self.comboBox3.setVisible(False)
        QtCore.QMetaObject.connectSlotsByName(graph)


    # Savefile is csv and xlxs
    def file_save(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',"", "xlsx(*.xlsx);;csv(*.csv)")
        file = open(name,'w')
        text = self.textEdit.toPlainText()
        file.write(text)
        file.close()

    #   Edit try
    def file_open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName,_ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()","","xlsx(*.xlsx);;csv(*.csv)",options=options)
        self.clearlist()
        hasher = hashlib.md5()
        f = open(self.fileName,'rb')
        for chunk in iter (lambda :f.read(4096),b""):
            hasher.update(chunk)
        self.read = hasher.hexdigest()
        try:
            self.check_sum(self.read)
            self.getitemlist()
            self.dataset = pd.read_excel(self.fileName)
        except:
            self.check_non(self.read)
            self.getitemlist()
            self.dataset = pd.read_excel(self.fileName)

    # Filter use to choose date.
    def filter(self):
        self.x = self.listcol.text()
        self.y = self.listrows.text()
        self.listx = self.x.split(',')
        self.listy = self.y.split(',')
        self.dimentionplotlist = []
        self.valuesplotlist = []
        self.dateplotlist = []
        self.in_key_di = []
        self.in_key_val = []
        self.in_key_date = []
        self.genlist(self.listx)
        self.genlist(self.listy)

        for i in range(len(self.key)):
            if self.key[i] in self.dimentionplotlist:
                self.in_key_di.append(i)
            elif self.key[i] in self.valuesplotlist:
                self.in_key_val.append(i)
            elif self.key[i] in self.dateplotlist:
                self.in_key_date.append(i)

        if len(self.in_key_date) == 1 and len(self.in_key_di) == 0 and len(self.in_key_val) != 0:
            self.getdataform = self.getinfo(self.in_key_date,self.in_key_val,self.dataset)
            self.tellaxisplot(self.dateplotlist)
            self.comboBox3.setVisible(True)
        elif len(self.in_key_date) == 1 and len(self.in_key_di) >= 1:
            for i in self.in_key_date:
                self.in_key_di.append(i)
            self.getdataform = self.getinfo(self.in_key_di,self.in_key_val,self.dataset)
            self.tellaxisplot(self.dimentionplotlist)
            self.comboBox3.setVisible(True)
        else:
            self.getdataform = self.getinfo(self.in_key_di,self.in_key_val,self.dataset)
            self.tellaxisplot(self.dimentionplotlist)



        #   For plot
        if 'y' not in self.findaxis:
            return self.win.plotbar(self.getdataform,self.listx,self.listy)
        if 'x' not in self.findaxis:
            return self.win.plotbary(self.getdataform,self.listy,self.listx)
        #   Not now
        if 'x' in self.findaxis and 'y' in self.findaxis:
            print('multitable')
        #   If not value then it not work
        if len(self.dimentionplotlist) == 0 or len(self.valuesplotlist) == 0:
            return  self.warning()

    #   Seperate data in x,y and use data to another plot graph
    def tellaxisplot(self,daidate):
        self.findaxis=[]
        for a in daidate:
            if a in self.listx:
               self.findaxis.append('x')
            if a in self.listy:
               self.findaxis.append('y')
    #   Seperate data and use data for another plot graph
    def genlist(self,inaxis):
        for i in inaxis:
            if i in self.catagories:
                self.dimentionplotlist.append(i)
            elif i in self.values:
                self.valuesplotlist.append(i)
            elif i in self.date:
                self.dateplotlist.append(i)
    # Select false
    def warning(self):
        self.error_dialog = QtWidgets.QErrorMessage()
        self.error_dialog.showMessage('Not acceptable for dimention3')
        self.error_dialog.exec_()

    # Choose date
    def creatdateselect(self):
        self.comboBox3 = QtWidgets.QComboBox(self.centralwidget)
        self.gridLayout.addWidget(self.comboBox3, 2, 0, 1, 1)
        datedata = ['all','years','months','dates']
        self.comboBox3.addItems(datedata)
        self.comboBox3.currentIndexChanged.connect(self.dateagain)
    # Try and except to check
    def dateagain(self):
        try:
            formatdmy = str(self.comboBox3.currentText())
            xy = self.selectdate(self.getdataform,formatdmy)
            if  'y' not in self.findaxis:
                return self.win.plotbar(xy,self.listx,self.listy)
            elif 'x' not in self.findaxis:
                return self.win.plotbary(xy,self.listy,self.listx)
        except:
            print('sorry')

    # Gui show Text and button to submit
    def retranslateUi(self, graph):
         _translate = QtCore.QCoreApplication.translate
         graph.setWindowTitle(_translate("graph", "MainWindow"))
         self.label_3.setText(_translate("graph", "COLUMNS"))
         self.label.setText(_translate("graph", "ROWS"))
         self.submit.setText(_translate("graph", "submit"))
         self.menuFile.setTitle(_translate("graph", "file"))
         self.actionOpen.setText(_translate("graph", "open"))

    # Read file and connect
    def check_sum(self,read):
        connection = sqlite3.connect('database.db')
        cur = connection.cursor()
        cur.execute("SELECT * FROM check_sum where md5=?",(read,))
        list_do = []
        for i in cur.fetchone():
            list_do.append(i)
        self.date = list_do[1].split(',')
        self.catagories = list_do[2].split(',')
        self.values = list_do[3].split(',')
        self.key = list_do[4].split(',')
        cur.close()
        connection.close()

    # Check data in database
    def check_non(self,read):
        connection = sqlite3.connect('database.db')
        cur = connection.cursor()
        self.data = self.getdf(self.fileName)
        self.date = self.data[0]
        self.catagories = self.data[1]
        self.values = self.data[2]
        self.key = list(self.data[3])
        date = ','.join(self.date)
        catagories = ','.join(self.catagories)
        values = ','.join(self.values)
        key = ','.join(self.key)
        cur.execute("insert into check_sum values(?,?,?,?,?)",(read,date,catagories,values,key))
        connection.commit()
        cur.close()
        connection.close()
    # Choose button on Gui
    def getgraph_b(self):
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setText("Pie Chart")
        self.pushButton_4.clicked.connect(self.pie)
        self.verticalLayout.addWidget(self.pushButton_4)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setText("Line graph")
        self.pushButton.clicked.connect(self.line)
        self.verticalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setText("Bubble")
        self.pushButton_2.clicked.connect(self.Bubbel)
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.verticalLayout.addWidget(self.pushButton_5)
        self.pushButton_5.setText("Table")
        self.pushButton_5.clicked.connect(self.table)
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.verticalLayout.addWidget(self.pushButton_6)
        self.pushButton_6.setText("Bar Graph")
        self.pushButton_6.clicked.connect(self.bar)
    # Show value of dimension , value and Date
    def getitemlist(self):
        self.cat.setFixedSize(470, 189)
        self.setitem(self.cat,self.catagories)
        self.cat.setHorizontalHeaderLabels(['Dimension'])
        self.verticalLayout2.addWidget(self.cat)
        self.valueslist.setFixedSize(470,189 )
        self.setitem(self.valueslist,self.values)
        self.valueslist.setHorizontalHeaderLabels(['Values'])
        self.verticalLayout2.addWidget(self.valueslist)
        self.datelist.setFixedSize(470,189 )
        self.setitem(self.datelist,self.date)
        self.datelist.setHorizontalHeaderLabels(['Date'])
        self.verticalLayout2.addWidget(self.datelist)
        self.addbutcol.setFixedSize(470,50)
        self.verticalLayout2.addWidget(self.addbutcol)
        self.addbutrows.setFixedSize(470,50)
        self.verticalLayout2.addWidget(self.addbutrows)
        self.setvalueforcheck()
    # Change data in database
    def changedata_cat(self):
        try:
            self.checking(self.catagories,self.itemnow)
            self.itemnow = self.cat.currentItem().text()
        except:
            self.itemnow = self.cat.currentItem().text()
            self.checking(self.catagories,self.itemnow)
    # Change data is a value in database
    def changedata_val(self):
        try:
            self.checking(self.values,self.itemnow)
            self.itemnow = self.valueslist.currentItem().text()
        except:
            self.itemnow = self.valueslist.currentItem().text()
            self.checking(self.values,self.itemnow)
    # Change data is a date in database
    def changedata_date(self):
        try:
            self.checking(self.date,self.itemnow)
            self.itemnow = self.datelist.currentItem().text()
        except:
            self.itemnow = self.datelist.currentItem().text()
            self.checking(self.date,self.itemnow)
    # Check data
    def checking(self,typechange,item):
        a = self.cat.rowCount()
        b = self.valueslist.rowCount()
        c = self.datelist.rowCount()
        if self.forcheck != [a,b,c]:
            typechange.remove(item)
            if self.forcheck[0] < a:
                self.catagories.append(item)
            if self.forcheck[1] < b:
                self.values.append(item)
            if self.forcheck[2] < c:
                self.date.append(item)
            self.setvalueforcheck()
            self.newinform()
    # Update data in database
    def newinform(self):
        dai = ','.join(self.catagories)
        val = ','.join(self.values)
        day = ','.join(self.date)
        key = ','.join(self.key)
        connection = sqlite3.connect('database.db')
        cur = connection.cursor()
        read = self.read
        cur.execute("DELETE FROM check_sum WHERE md5 = ? ",(read,))
        cur.execute("insert into check_sum values(?,?,?,?,?)",(read,day,dai,val,key))
        connection.commit()
        cur.close()
        connection.close()
    # Set value for check
    def setvalueforcheck(self):
        a = len(self.catagories)
        b = len(self.values)
        c = len(self.date)
        self.forcheck = [a,b,c]
        print(self.forcheck)
    #
    def addplaincol(self):
        if self.listcol.text() == '':
            self.x = []
            self.x.append(self.itemnow)
            text = ','.join(self.x)
            self.listcol.setText(text)
        else:
            a = self.listcol.text()
            a = a.split(',')
            self.x = a
            self.x.append(self.itemnow)
            text = ','.join(self.x)
            self.listcol.setText(text)
    # Add value in row
    def addplainrow(self):
        if self.listrows.text() == '':
            self.y=[]
            self.y.append(self.itemnow)
            text = ','.join(self.y)
            self.listrows.setText(text)
        else:
            a = self.listrows.text()
            a = a.split(',')
            self.y = a
            self.y.append(self.itemnow)
            text = ','.join(self.y)
            self.listrows.setText(text)
    #
    def getlist(self):
        self.cat = TableWidgetDragRows(self.centralwidget)
        self.verticalLayout2.addWidget(self.cat)
        self.valueslist = TableWidgetDragRows(self.centralwidget)
        self.verticalLayout2.addWidget(self.valueslist)
        self.datelist = TableWidgetDragRows(self.centralwidget)
        self.verticalLayout2.addWidget(self.datelist)
        self.addbutcol = QtWidgets.QPushButton(self.centralwidget)
        self.addbutcol.setText('Add To Colums')
        self.verticalLayout2.addWidget(self.addbutcol)
        self.addbutrows = QtWidgets.QPushButton(self.centralwidget)
        self.addbutrows.setText('Add To Rows')
        #  For filter

        self.verticalLayout2.addWidget(self.addbutrows)
        self.cat.currentItemChanged.connect(self.changedata_cat)
        self.valueslist.currentItemChanged.connect(self.changedata_val)
        self.datelist.currentItemChanged.connect(self.changedata_date)
        self.addbutcol.clicked.connect(self.addplaincol)
        self.addbutrows.clicked.connect(self.addplainrow)
    # Clear value in list
    def clearlist(self):
        self.x = []
        self.y = []
        try:
            self.cat.clear()
            self.datelist.clear()
            self.valueslist.clear()

        except:
            pass
    #
    def setitem(self,typelistwid,typeitemwid):
        typelistwid.setColumnCount(1)
        filled_widget = typelistwid
        for i, itemone in enumerate(typeitemwid):
            c = QtWidgets.QTableWidgetItem(itemone)
            filled_widget.insertRow(filled_widget.rowCount())
            filled_widget.setItem(i,0,c)
        header = typelistwid.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        #typelistwid.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    # Show plot graph
    def bar(self):
        self.win.plotbar(self.getdataform,self.in_key_di,self.in_key_val)
    def pie(self):
        self.win.plot_pie(self.getdataform)
    def Bubbel(self):
        self.win.plot_bubble(self.getdataform)
    def line(self):
        self.win.plot_line(self.getdataform,self.in_key_di,self.in_key_val)
    def table(self):
        self.win.table(self.getdataform,self.in_key_di,self.in_key_val)
    # Check label
    def onpick1(self,event):
        if isinstance(event.artist, Line2D):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            print('onpick1 line:', zip(np.take(xdata, ind), np.take(ydata, ind)))
        elif isinstance(event.artist, Rectangle):
            patch = event.artist
            print('onpick1 patch:', patch.get_path())
        elif isinstance(event.artist, Text):
            text = event.artist
            print('onpick1 text:', text.get_text())
            if self.filterlist.text() == '':
                self.flist = []
                self.flist.append(text.get_text())
                self.filterlist.setText('{}'.format(self.flist))
            else:
                self.flist.append(text.get_text())
                self.filterlist.setText('{}'.format(self.flist))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
