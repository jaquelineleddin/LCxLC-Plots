from PyQt5 import QtWidgets as Qw
from PyQt5 import QtCore as Qc

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages

import matplotlib.pyplot as plt
import numpy as np

from GUI.dataTab import MessageWindow
from GUI.functions import intensity_matrix, shift_intensity_matrix, calc_axis, plot2d, create_animation


class PlotTab(Qw.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dadDf = None
        self.colorDict = dict({'Blue Red': 'RdBu_r',
                                'Rainbow': 'jet',
                                'Magma': 'magma',
                                'Viridis': 'viridis',
                                'Grayscale': 'binary'})
        self.currentPlot = None
        self.plot2D.ax = None
        self.matrix = None
        self.matrixModified = None

    def initUI(self):
        self.setStyleSheet('font-size: 9pt')

        self.modTime = Qw.QLineEdit('0.5')
        self.modTime.setFixedWidth(60)

        self.sampleRate = Qw.QLineEdit('40')
        self.sampleRate.setFixedWidth(60)

        self.wavelengthList = Qw.QListWidget()
        self.wavelengthList.setFixedWidth(100)
        self.wavelengthList.itemClicked.connect(self.newWavelengthClicked)

        self.figSizeX = Qw.QSpinBox()
        self.figSizeX.setValue(10)
        self.figSizeX.setRange(1, 20)
        self.figSizeX.setSingleStep(1)
        self.figSizeX.setFixedWidth(50)

        self.figSizeY = Qw.QSpinBox()
        self.figSizeY.setValue(5)
        self.figSizeY.setRange(1, 20)
        self.figSizeY.setSingleStep(1)
        self.figSizeY.setFixedWidth(50)

        self.shift = Qw.QLineEdit('0.0')
        self.shift.setFixedWidth(60)
        self.shift.editingFinished.connect(self.draw2DPlot)

        self.showTitle = Qw.QCheckBox()
        self.showTitle.setChecked(True)
        self.showTitle.stateChanged.connect(self.draw2DPlot)

        self.plotMode = Qw.QComboBox()
        self.plotMode.addItems(['Contour plot', 'Pixmap'])
        self.plotMode.setCurrentIndex(0)
        self.plotMode.setFixedWidth(100)
        self.plotMode.currentTextChanged.connect(self.draw2DPlot)

        self.minCutoff = Qw.QLineEdit()
        self.minCutoff.setFixedWidth(80)
        self.minCutoff.editingFinished.connect(self.draw2DPlot)

        self.maxCutoff = Qw.QLineEdit()
        self.maxCutoff.setFixedWidth(80)
        self.maxCutoff.editingFinished.connect(self.draw2DPlot)

        self.setColorbarFixed = Qw.QCheckBox()

        self.colormap = Qw.QComboBox()
        self.colormap.addItems(['Blue Red', 'Rainbow', 'Magma', 'Viridis', 'Grayscale'])  # Rainbow = Jet in colormaps
        self.colormap.setCurrentText('Blue Red')
        self.colormap.setFixedWidth(100)
        self.colormap.currentTextChanged.connect(self.draw2DPlot)

        self.intyScale = Qw.QComboBox()
        self.intyScale.addItems(['absolute', 'relative'])
        self.intyScale.setCurrentIndex(0)
        self.intyScale.setFixedWidth(100)
        self.intyScale.currentTextChanged.connect(self.newWavelengthClicked)

        self.showColorbar = Qw.QCheckBox()
        self.showColorbar.setChecked(True)
        self.showColorbar.stateChanged.connect(self.draw2DPlot)

        self.datapointsInfo = Qw.QLabel()
        self.plot2D = FigureCanvas()

        self.exportBtn = Qw.QPushButton('Current plot')
        self.exportBtn.setFixedWidth(100)
        self.exportBtn.clicked.connect(self.saveCurrentPlot)

        self.exportAllBtn = Qw.QPushButton('All plots')
        self.exportAllBtn.setFixedWidth(100)
        self.exportAllBtn.clicked.connect(self.saveAllPlots)

        self.createGifBtn = Qw.QPushButton('Create GIF')
        self.createGifBtn.setFixedWidth(100)
        self.createGifBtn.clicked.connect(self.createGif)
        self.gifHelptext = Qw.QLabel("For GIF: first export all plots, then open the directory with 'Create GIF' Button.")

        self.drawPlotBtn = Qw.QPushButton('Draw plot')
        self.drawPlotBtn.setFixedWidth(100)
        self.drawPlotBtn.clicked.connect(self.draw2DPlot)
        self.drawPlotBtn.setEnabled(False)

        # Layouts
        # Figure Layout
        fig_1 = Qw.QFormLayout()
        fig_1.addRow(self.tr("&Width:"), self.figSizeX)
        fig_1.addRow(self.tr("&Height:"), self.figSizeY)

        fig_2 = Qw.QFormLayout()
        fig_2.addRow(self.tr("&Shift [s]"), self.shift)
        fig_2.addRow(self.tr("&Plot:"), self.plotMode)

        fig_3 = Qw.QFormLayout()
        fig_3.addRow(self.tr("&Show title:"), self.showTitle)

        self.figLayout = Qw.QGroupBox("Figure")
        figure = Qw.QHBoxLayout()
        figure.addLayout(fig_1)
        figure.addSpacing(20)
        figure.addLayout(fig_2)
        figure.addSpacing(20)
        figure.addLayout(fig_3)
        self.figLayout.setLayout(figure)
        self.figLayout.setEnabled(False)

        # Colorbar
        color_1 = Qw.QFormLayout()
        color_1.addRow(self.tr("&Minimum:"), self.minCutoff)
        color_1.addRow(self.tr("&Maximum:"), self.maxCutoff)

        color_2 = Qw.QFormLayout()
        color_2.addRow(self.tr("&Color map:"), self.colormap)
        color_2.addRow(self.tr("&Set fixed"), self.setColorbarFixed)

        color_3 = Qw.QFormLayout()
        color_3.addRow(self.tr("&Intensity:"), self.intyScale)
        color_3.addRow(self.tr("&Show colorbar:"), self.showColorbar)

        self.colorLayout = Qw.QGroupBox("Colorbar")
        color = Qw.QHBoxLayout()
        color.addLayout(color_1)
        color.addSpacing(20)
        color.addLayout(color_2)
        color.addSpacing(20)
        color.addLayout(color_3)
        self.colorLayout.setLayout(color)
        self.colorLayout.setEnabled(False)

        # Parameters
        param = Qw.QFormLayout()
        param.addRow(self.tr("&Sample rate [Hz]:"), self.sampleRate)
        param.addRow(self.tr("&Modulation time [min]:"), self.modTime)

        self.parameterLayout = Qw.QGroupBox("Parameters")
        self.parameterLayout.setLayout(param)
        self.parameterLayout.setEnabled(False)

        # Save
        save = Qw.QHBoxLayout()
        save.addWidget(self.exportBtn)
        save.addWidget(self.exportAllBtn)
        save.addWidget(self.createGifBtn)
        save.addWidget(self.gifHelptext)

        self.saveLayout = Qw.QGroupBox("Save")
        self.saveLayout.setLayout(save)
        self.saveLayout.setEnabled(False)

        self.plotLayout = Qw.QGridLayout()
        self.plotLayout.setSpacing(20)
        self.plotLayout.setColumnMinimumWidth(0, 100)
        self.plotLayout.addWidget(self.drawPlotBtn, 0, 0)
        self.plotLayout.addWidget(self.parameterLayout, 0, 1)
        self.plotLayout.addWidget(self.figLayout, 0, 2)
        self.plotLayout.addWidget(self.colorLayout, 0, 3)

        self.plotLayout.addWidget(Qw.QLabel("Wavelength"), 1, 0)
        self.plotLayout.addWidget(self.wavelengthList, 2, 0, 1, 2)

        self.plotLayout.addWidget(self.datapointsInfo, 1, 1, 1, 3)
        self.plotLayout.addWidget(self.plot2D, 2, 1, 1, 3)

        self.plotLayout.addWidget(self.saveLayout, 3, 1, 1, 3)

        self.setLayout(self.plotLayout)

    def newWavelengthClicked(self):

        if not self.setColorbarFixed.isChecked():
            self.minCutoff.clear()
            self.maxCutoff.clear()
        self.draw2DPlot()

    def getPlotParameters(self):

        shift_time = float(self.shift.text()) / 60  # in textbox time of shifting y-axis is given in seconds
        wavelength = int(self.wavelengthList.currentItem().text())
        time = float(self.modTime.text())
        srate = int(self.sampleRate.text()) * 60

        width = self.figSizeX.value()
        height = self.figSizeY.value()

        cmap = self.colorDict[self.colormap.currentText()]

        rt_array = self.dadDf['RT.min'].values

        return shift_time, wavelength, time, srate, width, height, cmap, rt_array

    def draw2DPlot(self):

        if self.plot2D.ax is not None:
            plt.close()

        shift_time, wavelength, mod_time, sample_rate, width, height, colormap, time_array = self.getPlotParameters()

        # reshape intensity array from data frame and get dimension of x and y-axis
        self.matrix, dim_x, dim_y = intensity_matrix(self.dadDf, wavelength, mod_time, sample_rate)

        # calculate relative intensities
        if self.intyScale.currentText() == 'relative':
            self.matrixModified = self.matrix - np.min(self.matrix)
            self.matrixModified = np.round(self.matrixModified * 100 / np.max(self.matrixModified), decimals=2)

        else:
            self.matrixModified = self.matrix

        # shift of y-axis
        if shift_time != 0:
            self.matrixModified = shift_intensity_matrix(self.matrixModified, shift_time, sample_rate)

        # get minimum and maximum of colorbar
        if self.minCutoff.text() == '':
            bar_min = np.min(self.matrixModified)
            self.minCutoff.setText(str(round(bar_min, ndigits=2)))
        else:
            bar_min = float(self.minCutoff.text())

        if self.maxCutoff.text() == '':
            bar_max = np.max(self.matrixModified)
            self.maxCutoff.setText(str(round(bar_max, ndigits=2)))
        else:
            bar_max = float(self.maxCutoff.text())

        run_time = np.round(time_array[-1], decimals=0)

        # create plot
        self.plot2D.figure, self.plot2D.ax = plt.subplots(1, figsize=(width, height))

        if self.plotMode.currentText() == 'Contour plot':
            y, x = np.meshgrid(time_array[0:dim_y] * 60, np.linspace(0, run_time, num=dim_x))
            self.currentPlot = self.plot2D.ax.contourf(x, y, self.matrixModified,
                                                       cmap=colormap, vmin= bar_min, vmax= bar_max,
                                                       levels=500)
        else:
            y, x = np.meshgrid(time_array[0:dim_y+1] * 60, np.linspace(0, run_time, num=dim_x+1))
            self.currentPlot = self.plot2D.ax.pcolormesh(x, y, self.matrixModified,
                                                         cmap=colormap, vmin=bar_min, vmax=bar_max)

        # set limits of axis
        self.plot2D.ax.axis([x.min(), x.max(), y.min(), y.max()])

        if self.showTitle.isChecked():
            self.plot2D.ax.set_title(str(wavelength) + " nm")

        if self.showColorbar.isChecked():
            cbar = self.plot2D.figure.colorbar(self.currentPlot, ax=self.plot2D.ax)
            if self.intyScale.currentText() == 'relative':
                cbar.set_ticks([10, 20, 30, 40, 50, 60, 70, 80, 90])

        self.plot2D.ax.set_xlabel("1D time [min]")
        self.plot2D.ax.set_ylabel("2D time [s]")
        self.plot2D.draw()

        # print dim x, dim y and number of points, so user can check, if sample rate and modulation time fit together
        num_all_points = len(time_array)
        num_plot_points = dim_x * dim_y
        diff = np.abs(num_plot_points - num_all_points)
        info_text = (("data points:     1st dim: %i" % dim_x) + ("      2nd dim: %i" % dim_y) +
                     ("     plotted: %i" % num_plot_points) + ("       all: %i" % num_all_points) +
                     ("     difference: %i" % diff))

        self.datapointsInfo.setText(info_text)

        if self.currentPlot is not None:
            self.exportBtn.setEnabled(True)

    def saveCurrentPlot(self):

        file_filter = 'Portable Network Graphic (*.png);;JPEG (*.jpg);; Portable Document Format (*.pdf)'

        path = Qw.QFileDialog.getSaveFileName(parent=self,
                                              caption='Save current plot',
                                              filter=file_filter)

        fname = path[0]

        if fname != '':
            if fname.endswith('.pdf'):
                pdf_save = SavePlotThread(fname)
                pdf_save.run()

            else:
                plt.savefig(fname,  bbox_inches='tight')

    def saveAllPlots(self):

        dir_path = Qw.QFileDialog.getExistingDirectory(parent=self,
                                                       caption='Select existing directory')

        if dir_path != '':

            shift_time, wavelength, mod_time, sample_rate, width, height, colormap, time_array = self.getPlotParameters()

            if self.setColorbarFixed.isChecked():
                bar_min = float(self.minCutoff.text())
                bar_max = float(self.maxCutoff.text())
            else:
                bar_min = None
                bar_max = None

            # retentionTime = np.append(0.0, retentionTime)

            self.thread = CreatingAllPlotsThread(self.dadDf, dir_path, mod_time, sample_rate, time_array, shift_time,
                                                 colormap, width, height, bar_min, bar_max, self.intyScale.currentText())
            self.msgWindow = MessageWindow('Saving all plots...Please wait until this window closes.')
            self.thread.finished.connect(self.msgWindow.close)
            self.msgWindow.show()
            self.thread.start()

    def createGif(self):

        dir_path = Qw.QFileDialog.getExistingDirectory(parent=self,
                                                       caption='Select directory with all plots')

        width = self.figSizeX.value()
        height = self.figSizeY.value()

        if dir_path != '':

            self.gifThread = CreateGIFThread(dir_path, width, height)
            self.msgWindow_gif = MessageWindow('Creating GIF...Please wait until this window closes.')
            self.gifThread.finished.connect(self.msgWindow_gif.close)
            self.msgWindow_gif.show()
            self.gifThread.start()


class CreatingAllPlotsThread(Qc.QThread):
    def __init__(self, dad_df, dir_out, mod_time, sample_rate, rt_array, shift_time,
                 colormap, width, height, bar_min, bar_max, inty_mode):
        super().__init__()
        self.dadDf = dad_df
        self.dirPath = dir_out
        self.modTime = mod_time
        self.sampleRate = sample_rate
        self.retentionTime = rt_array
        self.shiftTime = shift_time
        self.colormap = colormap
        self.width = width
        self.height = height
        self.barMin = bar_min
        self.barMax = bar_max
        self.intyScale = inty_mode

    def run(self):
        for wavelength in self.dadDf.columns[1:]:

            fp = self.dirPath + '/' + str(wavelength) + ".png"

            title = str(wavelength) + ' nm'

            matrix, dim_x, dim_y = intensity_matrix(self.dadDf, wavelength, self.modTime, self.sampleRate)
            x, y = calc_axis(self.retentionTime, dim_x, dim_y)

            # relative intensities
            if self.intyScale == 'relative':
                matrix = matrix - np.min(matrix)
                matrix = np.round(matrix * 100 / np.max(matrix), decimals=2)

            if self.shiftTime != 0:
                matrix = shift_intensity_matrix(matrix, self.shiftTime, self.sampleRate)

            plot2d(matrix, x, y, title, self.colormap, self.width, self.height, fp, self.intyScale, self.barMin,
                   self.barMax)
            plt.close()


class CreateGIFThread(Qc.QThread):
    def __init__(self, dir_path, width, height):
        super().__init__()
        self.dirPath = dir_path
        self.width = width
        self.height = height

    def run(self):
        create_animation(self.dirPath, self.width, self.height)


# if plot mode is set to Pixmap, plot can be saved as pdf file. If contour plot, the pdf size will be too big to save
class SavePlotThread(Qc.QThread):
    def __init__(self, fn):
        super().__init__()
        self.filepath = fn

    def run(self):
        with PdfPages(self.filepath) as pp:
            pp.savefig()



