# SQUID Advanced Background Substraction 

This python script takes raw data from SQUID magnetometers (for now only the MPMS3 is supported) and subtracts a raw background.

## Features

- Almost complete error propagation thanks to the great [`uncertainties`](https://pythonhosted.org/uncertainties) package
- Fitting using Orthogonl Distance Regression (ODRPACK 77) 
- Easy per scan inspection of the fit quality.
- Rudimenrtary support for the rotator option.


## Dependencies

- [`python > 3.9`](https://www.python.org/downloads/)
- [`scipy`](https://scipy.org/install/)
- [`numpy`](https://numpy.org/install/)
- [`uncertainties`](https://uncertainties.readthedocs.io/en/latest/#installation-and-download)
- [`matplotlib`](https://matplotlib.org/stable/#installation)

### Special Notes for Windows users

See the [Windows Guide](INSTALL-win.md).

## Usage

### Measurement

When thinking about using SABS there are a few things to consider before you start measuring. First of all you should 
know that SABS is only for the DC mesuring mode. In most situations where you can use the VSM mode, you should do so. 
For VSM mode the background can be subtracted more easily by just subtracting the resulting data directly.
If your measurement needs DC mode you can use SABS. 

You will need two separate measurements one for background and one with the sample. You should use the same sequence for both measurements. Make sure to enable RAW file recording. To get the most accurate results make sure to change as little as possible between measurements. The sampleposition is determined by touching down (As far as we know). So make sure the sampleholder has the same length between measurements. If you are using a protective straw. Use the same straw at the same possition.

Further take care to output each measurement into its own file. If you are for example sweeping temperature at different fields, use one file for each field.

### Software

Type `python sabs.py -h` to show the help message. Use `-s [sampledata]` and `-b [background]` to point to the sampledata or 
background raw file (`*.rw.dat`) respectively. Since there is no information about the rotation angle stored in the `*.rw.dat` file, it is necessary to also read the `*.dat` file. Make sure the `*.dat`  file is present in the same folder and has the same name before the file extension.  
Specify your outputfile with `-o [outfile]`. With `-p` plotting can be turned on. This is recommended to check the validity of the fit.
There are two modes for subtraction:
- _dirty mode_ `-m dirty`
  - Even when using the same sequence there is no guarantee, that all points in your measurement are recorded. 
    This leads to a different number of scans between background and sampledata. Using *dirty mode* the arrays 
    of scans are cut to fit in length.
- _nearest mode_ `-m nearest` (default)
  - _dirty mode_ can lead to problems, when a scan or multiple scans in the middle of your sequence were not recorded. 
    Look out for larger errorbars in your variable.
  - _nearest mode_ looks for the nearest scan in background to each scan in sampledata. 
    Only the distance in your variable is regarded. Which observable was your variable is determined automatically.
    
#### Example

```bash
python sabs.py -p \
-s sampledata/2021-11-08_Fe5Ge2Te5_SE5749_grease-quartz-brass_MvT_1000Oe.rw.dat \
-b sampledata/2021-11-04_Test_background_grease-quartz-brass_MvT_1000Oe.rw.dat \
-o sampledata/2021-12-17_Fe5Ge2Te5_SE5749_grease-quartz-brass_MvT_1000Oe.sabs.dat 
```


In case of problems or if you need help, please write me an E-Mail: `b.mehlhorn at ifw-dresden.de` and open an issue in the issue tracker.
