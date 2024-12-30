# LCxLC-Plots

App to parse Agilent *DAD.uv* files of comprehensive two-dimensional liquid chromatography measurements with a diode array detector.
* Retention time and absorptions of all measured wavelengths can be exported as text files.
* Plot and save 2D chromatograms
* Create gif video with all measured wavelength

  ![app](https://github.com/user-attachments/assets/ca1a78ce-a579-4d60-8259-6fce9f15012e)


## Getting started
Use *Anaconda* and *pyinstaller* to convert code to standalone app:
1. Start Anaconda Powershell
2. Activate Anaconda environment with *pyinstaller* installed.
3. In the shell go to directory **GUI** with **main.py** file in it.
4. Use the following command:

```
pyinstaller --onedir --windowed --icon directoryPath\icon.png --name LCxLCPlots main.py
```
   
