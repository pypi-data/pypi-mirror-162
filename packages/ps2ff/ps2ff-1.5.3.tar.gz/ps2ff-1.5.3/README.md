ps2ff
=====

<img align="left" height="70" src="doc_source/_static/ps2ff_wide.png">
Produce approximated finite fault distances and variance corrections given
point source information, for example Repi (epcentral distance) to Rjb
(Joyner-Boore distance) or Rrup (closest distance to rupture).

<br><br>

Using the results (the API)
---------------------------

The command line programs (described below) can be used to generate new
distance adjustments. This package also includes a set of correction factors
for some common conditions (e.g., typical active crustal regions). These
can most easily be used with the `interpolate` module that contains the `PS2FF`
class, which enables the use of the tables for arbitrary magnitudes and
epicentral distance values. See the `ps2ff.interpolate` section of this
package.

Installation
------------------------------
In the base of this repository, run
```
conda create --name ps2ff pip
conda activate ps2ff
pip install -r requirements.txt .
```
You can omit the conda commands if you do not wish to use a conda virtual environment.

To run the tests
```
pip install pytest
pytest .
```

Background
----------
This code implements the methods descibed by:
- Thompson, E. M., and C. B. Worden (2017). Estimating rupture distances without
  a rupture, *Bulletin of the Seismological Society of America*. 
DOI: https://doi.org/10.1785/0120170174.


Running the Programs
--------------------
The primary program is `run_ps2ff`, which must be given a configuraiton file
```
ps2ff -w Rjb config_file.ini
```
where '-w Rjb' is the 'what' command line argument for `run_ps2ff`.
There are example configuration files in the `ps2ff/config` directory.

Output Tables
-------------
The `ps2ff/tables` directory contains example results for some generic seismological
assumptions. The output file name convension is easiest to describe with an
example:
```
Rjb_S14_mechA_ar1p0_seis0_15_Ratios.csv
```
where:
 - "Rjb" is the the `what` command line argument.
 - "S14" is the selected `rup_dim_model`.
 - "mechA" specifies the rupture mechanism parameter `mech`, where "A" can
   be one of "A", "SS", "N", or "R".
 - "ar1p0" is the aspect ratio specified with the `AR` parameter, where the
   decimal point is replaced with the letter 'p'.
 - "seis0_15" is the range min/max seismogenic depths (in this case 0 to 15
   km).
 - "Ratios" is either "Ratios" or "Var" specifying whether the file contains
   Rjb- or Rrup-to-Repi ratios, or variances.

Each output table starts with six header lines (each beginning with `#`)
specifying the processing parameters. This is followed by a line
(comma-separated) providing the column headers. The first column, "Repi_km",
is the epicentral distance. The following columns "R(magnitude)" ("R" for
"ratio") or "V(magnitude)" ("V" for "variance) provide the values for a given
Repi and magnitude. The table is intended for bi-variate interpolation, linear
in magnitude and logarithmic in distance. The ratios are Rjb (or Rrup) to Repi.


Program Details
---------------

`run_ps2ff` produces tables of Rjb-to-Repi or Rrup-to-Repi ratios and
variances. Example configuration files may be found in ps2ff/config.

`run_ps2ff_single_event` produces tables of Rrup-to-Repi and Rjb-to-Repi
ratios and variances for a single event. This means that the magnitdue and
hypocentral depth are available, simplifying the integration. It optionally
tabulates the adjustment factors as a function of backazimuth. An example
configuration file for this program is given in
`tests/config/test_single.ini`.

