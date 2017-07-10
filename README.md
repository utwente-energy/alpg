Artifical load profile generator
==============

This tool is an Artifical Load Profile Generator (ALPG) with the purpose to stimulate research and benchmarking of different Demand Side Management (DSM) approaches. The main contribution of this generator is the addition of flexibility information of flexible devices. This input, next to static profiles, can be used to evaluate and benchmark the performance of DSM approches. 

As such, the tool is free to use and modify under the GPL v3.0 license to stimulate expansion and improvement of the used models. 

The work is presented in the paper: G. Hoogsteen, A. Molderink, J.L. Hurink and G.J.M. Smit, "Generation of Flexible Domestic Load Profiles to Evaluate Demand Side Management Approaches", IEEE EnergyCon 2016 conference, Leuven, Belgium.

For more information, please see http://utwente.nl/energy

Running
--------------

Running the ALPG is done by executing "profilegenerator.py"

The tool is written in the Python3 language and should work on all major platforms. Furthermore, the tool depends on the Astral package, which can be installed using pip:
https://pypi.python.org/pypi/astral


Configuration
--------------

The configuration is specified in the file "config.py". The comments in the file should guide the setup process and the provided example works out of the box. The following input can be specified:
- Output folder
- Number of days to produce
- Geographical location
- Input files for solar irradiation data
- Penetration of emerging technologies
- Power consumption of certain devices
- Predictability of people
- Type of households in the neighbourhood.

**Household types**

- HouseholdSingleWorker
- HouseholdSingleRetired
- HouseholdDualWorker(Parttime)
- HouseholdDualRetired
- HouseholdFamilyDualWorker(Parttime)
- HouseholdFamilySingleWorker(Parttime)

Where (Parttime) is an argument that specifies if one of the workers has a part-time job instead of a full-time job.	
	
**Solar irradiation file**

This must be a single column CSV file with one value on each row for the corresponding interval. The timebase can be given (default 3600 seconds) to specify the interval length of the dataset. Information must be provided in J/cm2 (joules per square centimeter). Dutch weather data can be found and downloaded from the KNMI website: http://projects.knmi.nl/klimatologie/uurgegevens/selectie.cgi. The provided data contains the 2014 measurements of weather station Twenthe, Netherlands.

Generation
--------------

The comments in the code give some hints on how the simulation is executed and used sources where applicable. 


Output
--------------

The resulting profile data is stored in the specified output folder. All static profiles are given in minute intervals. All flexibility times are specified in seconds since the simulation start. The content of the files with the default writer is as follows:

**CSV files***

All CSV files contain the static profiles and use a semicolon (;) as delimiter. The format of each CSV-file is as follows: 
- Each row represents an interval in order. Hence row 1 is interval 1, row 2 interval 2, etc.
- Each column represents a household in order. Hence colunmn 1 is the consumption for household 1, row 2 for household 2, etc.
- Each value is the average power consumption durin gthat interval in Watts

Note that the solar profile is flexible in the sense that it can be curtailed. Negative consumption is production. For reactive power profiles, the value represents the reactive power in var.

**Text files**

The format of text files is as follows for each line:

**Start and endtime text files:**

Specifies availability times for each device in two files (starttimes and endtimes):
```
<houseID>: <startTime1 in seconds>, <starttime 2 in seconds>, ..., <starttime n in seconds>
```

**Profiles**

Specifies the consumption profile for Timeshiftable devices (washing machines, dishwashers, etc) for each interval of 60 seconds:
```
<houseID>: <interval 1>, <interval 2>, <interval 3>, ..., <interval n>
```
The profile is given in Python Complex values where the real part represents the active power consumption in Watts and the imaginary part the reactive power in var.

**Device specific**

BatterySettings.txt:
```
<houseID>: <maximum power in W>, <capacity in Wh>, <initial SoC in Wh>
```

ElectricVehicle_RequiredCharge.txt:
```
<houseID>: <required charge for job 1 in Wh>, <required charge for job 2 in Wh>, ...,<required charge for job n in Wh>
```
The jobs correspond to the start- and endtimes as specified in ElectricVehicle_Starttimes.txt and ElectricVehicle_Endtimes.txt

ElectricVehicle_Specs.txt:
```
<houseID>: <battery capacity in Wh>, <maximum charging power in W>
```

PhotovoltaicSettings.txt:
```
<houseID>: <angle in degrees>, <aimuth in degrees>, <efficiency in percent>, <size in m2 (square meter)>
```


Changelog
--------------

**Version 1.1**
- Fixed retired people to have no driving distance to work
- Fixed dishwasher profile
- More rounded timeshiftable times to avoid synchronisation with auctions pushing towards the runtime deadlines
- Fixed a bug resulting in overlapping start + endtimes for EVs

