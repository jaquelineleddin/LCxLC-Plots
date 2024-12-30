from PyQt5 import QtWidgets as Qw
from PyQt5 import QtCore as Qc
from PyQt5.QtGui import QIcon

from functions import create_dad_dataframe, export_wavelength


class DataTab(Qw.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dadDf = None

    def initUI(self):
        self.setStyleSheet('font-size: 9pt')

        self.DADuvFilepath = Qw.QLabel()

        self.openBtn = Qw.QPushButton('Open DAD.uv')
        self.openBtn.setFixedWidth(110)
        self.openBtn.clicked.connect(self.getUVPath)

        self.loadDataBtn = Qw.QPushButton('Load data')
        self.loadDataBtn.setFixedWidth(110)
        self.loadDataBtn.setEnabled(False)
        self.loadDataBtn.clicked.connect(self.loadData)

        self.dfTableTitle = Qw.QLabel('Data:')
        self.dfTable = Qw.QTableWidget()


        self.wavelengths = Qw.QListWidget(parent=self)
        self.wavelengths.setFixedWidth(100)

        self.exportBtn = Qw.QPushButton('Export wavelength')
        self.exportBtn.setFixedWidth(150)
        self.exportBtn.clicked.connect(self.exportTSV)

        self.exportAllBtn = Qw.QPushButton('Export all')
        self.exportAllBtn.setFixedWidth(150)
        self.exportAllBtn.clicked.connect(self.exportAll)

        # Layouts

        # Data
        data = Qw.QHBoxLayout()
        data.addWidget(self.openBtn)
        data.addWidget(Qw.QLabel("UV File:"))
        data.addWidget(self.DADuvFilepath, Qc.Qt.AlignLeft)
        data.addWidget(self.loadDataBtn)
        data.setSpacing(20)

        data_frame = Qw.QGroupBox("Data")
        data_frame.setLayout(data)

        self.dataLayout = Qw.QGridLayout()
        self.dataLayout.setSpacing(20)

        self.dataLayout.addWidget(data_frame, 0, 0, 1, 3)

        self.dataLayout.addWidget(Qw.QLabel("Wavelength:"), 1, 0)
        self.dataLayout.addWidget(self.wavelengths, 2, 0)

        self.dataLayout.addWidget(self.dfTableTitle, 1, 1)
        self.dataLayout.addWidget(self.dfTable, 2, 1, 1, 2)
        self.dataLayout.addWidget(self.exportBtn, 3, 0)
        self.dataLayout.addWidget(self.exportAllBtn, 3, 1)

        self.setLayout(self.dataLayout)

    def getUVPath(self):

        self.uvPath = Qw.QFileDialog.getOpenFileName(parent=self,
                                                     caption='Select a dad uv file',
                                                     filter='Agilent DAD (*.UV)')

        if self.uvPath[0] != '':
            self.DADuvFilepath.setText(self.uvPath[0])
            self.updateBtns()

    def loadData(self):

        self.msgWindow = MessageWindow('Loading data...Please wait until this window closes.')
        self.loadingThread = LoadingThread(self.uvPath[0])
        self.loadingThread.finished.connect(self.showData)
        self.msgWindow.show()
        self.loadingThread.start()

    def showData(self):
        self.msgWindow.close()
        self.showOverview()

    def updateBtns(self):
        if self.DADuvFilepath.text() == '':
            self.exportBtn.setEnabled(False)
            self.loadDataBtn.setEnabled(False)

        else:
            self.exportBtn.setEnabled(True)
            self.loadDataBtn.setEnabled(True)

    def showOverview(self):

        self.dadDf = self.loadingThread.dadDf
        col_num = len(self.dadDf.columns)
        row_num = len(self.dadDf)

        if row_num > 500:
            row_num = 500

        self.dfTable.setColumnCount(col_num)
        self.dfTable.setRowCount(row_num)
        self.colNames = [str(num) for num in self.dadDf.columns]
        self.dfTable.setHorizontalHeaderLabels(self.colNames)

        for i in range(row_num):
            self.dfTable.setItem(i, 0, Qw.QTableWidgetItem(str(round(self.dadDf.iat[i, 0], ndigits=4))))

            for j in range(1, col_num):
                self.dfTable.setItem(i, j, Qw.QTableWidgetItem(str(round(self.dadDf.iat[i, j], ndigits=1))))

        self.dfTable.resizeColumnsToContents()

        # add wavelength to list
        self.wavelengths.clear()
        self.wavelengths.addItems(self.colNames[1:])

        # select first item
        self.wavelengths.setCurrentItem(self.wavelengths.item(0))

    def exportTSV(self):

        fp = Qw.QFileDialog.getSaveFileName(parent=self,
                                            caption='Channel Export',
                                            filter='tab-separated values (*.tsv)')

        selected_wavelength = self.wavelengths.currentItem().text()

        if fp[0] != '':
            export_wavelength(self.dadDf, int(selected_wavelength), fp[0])

    def exportAll(self):

        fp = Qw.QFileDialog.getSaveFileName(parent=self,
                                            caption='UV Export',
                                            filter='tab-separated values (*.tsv)')

        if (fp[0] != '') and (self.dadDf is not None):

            self.dadDf.to_csv(fp[0], sep='\t', index=False)


class LoadingThread(Qc.QThread):
    def __init__(self, fpath):
        super().__init__()
        self.fp = fpath
        self.dadDf = None

    def run(self):
        self.dadDf = create_dad_dataframe(self.fp)


class MessageWindow(Qw.QWidget):
    def __init__(self, msg_text):
        super().__init__()
        self.setStyleSheet('font-size: 9pt')
        self.setFixedSize(400, 150)
        self.setWindowTitle('Info')
        dir_path = Qw.QApplication.applicationDirPath()
        self.setWindowIcon(QIcon(dir_path + '/icon.png'))
        self.setWindowIcon(QIcon('icon.png'))
        self.message = Qw.QLabel(msg_text)
        self.message.setAlignment(Qc.Qt.AlignHCenter | Qc.Qt.AlignVCenter)

        self.messageLayout = Qw.QHBoxLayout()
        self.messageLayout.addWidget(self.message)

        self.setLayout(self.messageLayout)

        # enable close 'x' button on top right side, so window cannot be closed before process is finished
        self.setWindowFlags(self.windowFlags() | Qc.Qt.CustomizeWindowHint)
        self.setWindowFlag(Qc.Qt.WindowCloseButtonHint, False)
