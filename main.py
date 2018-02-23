from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from get_json2 import make_json
import json
from plot_graph2 import plot_only
import sys
import re

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(Ui_MainWindow,self).__init__(parent=parent)
        self.setupUi(self)

#function for showmap and graph
    def show_table(self):
#get start stop from textinput
        start = self.rest.text()
        stop = self.end.text()
#plot graph all the time
        print(self.filename)
        plot_only.plot_graph(plot_only,start,stop,self.filename)
        self.graph_2.setPixmap(QtGui.QPixmap('{}.png'.format(self.filename)))
        self.map.setPixmap(QtGui.QPixmap('{}_map.png'.format(self.filename)))
#just gui
    def setupUi(self, graph):
        graph.setObjectName("graph")
        graph.resize(985, 693)
        self.centralwidget = QtWidgets.QWidget(graph)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.rest = QtWidgets.QLineEdit(self.centralwidget)
        self.rest.setObjectName("rest")
        self.gridLayout.addWidget(self.rest, 0, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)
        self.end = QtWidgets.QLineEdit(self.centralwidget)
        self.end.setObjectName("end")
        self.gridLayout.addWidget(self.end, 0, 4, 1, 1)
        self.submit = QtWidgets.QPushButton(self.centralwidget)
        self.submit.setObjectName("submit")
        self.gridLayout.addWidget(self.submit, 0, 5, 1, 1)
        self.map = QtWidgets.QLabel(self.centralwidget)
        self.map.setText("")
        self.map.setObjectName("map")
        self.map.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.gridLayout.addWidget(self.map, 2, 4, 1, 2)
        self.graph_2 = QtWidgets.QLabel(self.centralwidget)
        self.graph_2.setText("")
        self.graph_2.setObjectName("graph_2")
        self.graph_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.gridLayout.addWidget(self.graph_2, 2, 1, 1, 2)
        graph.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(graph)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 985, 31))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        graph.setMenuBar(self.menubar)
        self.actionOpen = QtWidgets.QAction(graph)
        self.actionOpen.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionOpen)
        self.menubar.addAction(self.menuFile.menuAction())
        self.actionOpen.triggered.connect(self.file_open)
        self.submit.clicked.connect(self.show_table)
        self.retranslateUi(graph)
        QtCore.QMetaObject.connectSlotsByName(graph)

    def retranslateUi(self, graph):
        _translate = QtCore.QCoreApplication.translate
        graph.setWindowTitle(_translate("graph", "MainWindow"))
        self.label_3.setText(_translate("graph", "START-STOP"))
        self.submit.setText(_translate("graph", "submit"))
        self.menuFile.setTitle(_translate("graph", "file"))
        self.actionOpen.setText(_translate("graph", "open"))
#for action oren when open file
    def file_open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
#means dont tag condition render only file and directory
        fileName,_ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()","","All File(*);;Text Files (*.txt)",options=options)
        self.filename = make_json.append_file(make_json,fileName)
        file =  open("{}.json".format(self.filename),"r")
        data = file.read()
        document = json.loads(data)
        normal = re.compile(r'(?P<origin>\d+\-\d+\-\d+)')
        rest = document[0]['timestamp']
        end = document[len(document)-1]['timestamp']
        rest = re.findall(normal,rest)
        end = re.findall(normal,end)
        print(rest)
        print(end)
        self.end.setText(end[0])
        self.rest.setText(rest[0])

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

