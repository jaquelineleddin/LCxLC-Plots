import sys

from PyQt5 import QtWidgets as Qw
from PyQt5.QtGui import QIcon

from GUI.dataTab import DataTab
from GUI.plotTab import PlotTab


class AppWindow(Qw.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet('font-size: 9pt')

        self.setFixedSize(1500, 900)
        self.setWindowTitle('LCxLC Plots')
        self.setWindowIcon(QIcon('icon.png'))

        self.mainWidget = Qw.QWidget()
        self.setCentralWidget(self.mainWidget)

        self.mainLayout = Qw.QVBoxLayout()

        self.dataTab = DataTab()
        self.plotTab = PlotTab()

        self.tabWidget = Qw.QTabWidget()
        self.tabWidget.addTab(self.dataTab, 'Data')
        self.tabWidget.addTab(self.plotTab, 'Plots')

        self.mainLayout.addWidget(self.tabWidget)
        self.mainWidget.setLayout(self.mainLayout)

        wavelengthList_model = self.dataTab.wavelengths.model()
        wavelengthList_model.rowsInserted.connect(self.copyData)

    def copyData(self):

        # copy dataframe to plot tab
        self.plotTab.dadDf = self.dataTab.dadDf

        self.plotTab.wavelengthList.clear()

        # copy wavelength from data tab to plot tab
        for i in range(self.dataTab.wavelengths.count()):
            clone_it = self.dataTab.wavelengths.item(i).clone()
            self.plotTab.wavelengthList.addItem(clone_it)

        self.plotTab.wavelengthList.setCurrentItem(self.plotTab.wavelengthList.item(0))

        objects = [self.plotTab.figLayout, self.plotTab.parameterLayout,
                   self.plotTab.colorLayout, self.plotTab.saveLayout,
                   self.plotTab.drawPlotBtn]

        for obj in objects:
            obj.setEnabled(True)


if __name__ == '__main__':

    app = Qw.QApplication(sys.argv)
    main_window = AppWindow()
    main_window.show()

    sys.exit(app.exec_())
