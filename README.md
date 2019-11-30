Artifical load profile generator
==============

This tool is an Artifical Load Profile Generator (ALPG) with the purpose to stimulate research and benchmarking of different Demand Side Management (DSM) approaches. The main contribution of this generator is the addition of flexibility information of flexible devices. This input, next to static profiles, can be used to evaluate and benchmark the performance of DSM approches. 

Note that, because of this purpose, the output of the ALPG should only be used as an input for another smart grid simulation and optimization tool. This is due to the fact that only static load profiles are written in CSV files, which do not include the power consumption of flexibile devices, such as washing machines, dishwashers, electric vehicles or heating devices! It is up to the smart grid / DSM optimization software to schedule (and simualate) the usage and power consumption of these devices.

As such, the tool is free to use and modify under the GPL v3.0 license to stimulate expansion and improvement of the used models. 

The work is presented in the paper: G. Hoogsteen, A. Molderink, J.L. Hurink and G.J.M. Smit, "Generation of Flexible Domestic Load Profiles to Evaluate Demand Side Management Approaches", IEEE EnergyCon 2016 conference, Leuven, Belgium.

An updated version is presented in the G. Hoogsteen, "A Cyber-Physical Systems Perspective on Decentralized Energy Management", PhD Thesis, University of Twente, Enschede, the Netherlands. Available: 
https://research.utwente.nl/en/publications/a-cyber-physical-systems-perspective-on-decentralized-energy-mana (Chapter 6 covers the ALPG).

For more information, please see http://utwente.nl/ctit/energy

Contact me at: g.hoogsteen [at] utwente.nl

Running
--------------

Running the ALPG is done by executing "profilegenerator.py -c <configuration> [-o <output_folder> --force]"

Here, the parameters are:
```
-c	--config=	Configuration file within the configs/ directory. Note ".py" must be excluded!
-o	--output=	Output directory of the generated configuration data within the output/ folder.
-f	--force		Force the output directory to be cleared
```

So, to run the configs/example.py configuration and write results into output/results/, a command (depending on your operating system) like this should be issued on the commandline:
```
python3 profilegenerator.py -c example -o results
```

The tool is written in the Python3 language and should work on all major platforms. 

Furthermore, the tool depends on the Astral package, which can be installed using pip:
https://pypi.python.org/pypi/astral
E.g. use a command like
```
pip3 install astral
```

Note that the simulation is quite heavy and is barely optimized. Generation of output therefore takes a long time. So, be patient and don't generate too much households as the tool is aimed at small groups of houses (~100 households max).

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

This must be a single column CSV file with one value on each row for the corresponding interval. The timebase can be given (default 3600 seconds) to specify the interval length of the dataset. The required informaiton is the global horizontal irradiation (GHI) and must be provided in J/cm2 (joules per square centimeter). Dutch weather data can be found and downloaded from the KNMI website: http://projects.knmi.nl/klimatologie/uurgegevens/selectie.cgi. The provided data contains the 2014 measurements of weather station Twenthe, Netherlands.

Generation
--------------

The comments in the code give some hints on how the simulation is executed and used sources where applicable. 


Output
--------------

The resulting profile data is stored in the specified output folder. All static profiles are given in minute intervals. All flexibility times are specified in seconds since the simulation start. The content of the files with the default writer is as follows:

**CSV files***

All CSV files contain the static profiles and use a semicolon (;) as delimiter. The format of each CSV-file is as follows: 
- Each row represents an interval in order. Hence row 1 is time interval 1, row 2 time interval 2, etc.
- Each column represents a household in order. Hence colunmn 1 is the consumption for household 0, row 2 for household 1, etc.
- Each value is the average power consumption during that interval in Watts
- Negative values indicate production
- Note that we index all IDs starting at 0 instead of 1!

Note that the solar profile is flexible in the sense that it can be curtailed. Negative consumption is production. For reactive power profiles, the value represents the reactive power in var.

**Text files**

The format of text files is as follows for each line:

**Start and endtime text files:**

Specifies availability times for each device in two files (starttimes and endtimes):
```
<houseID>: <startTime1 in seconds>, <starttime 2 in seconds>, ..., <starttime n in seconds>
```

Note that for the thermostat only starttimes are given. The temperature setpoint is changed at each starttime.

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
<houseID>: <angle (elevation) in degrees>, <aimuth in degrees, north = 0, east = 90>, <efficiency in percent>, <size in m2 (square meter)>
```

Thermostat_Setpoints.txt:
```
<houseID>: <temperature setpoint in degrees Celsius for starttime 1>, <temperature setpoint for starttime 2>, ..., <temperature setpoint for starttime n>
```
The starttimes correspond to the starttimes as specified in Thermostat_Starttimes.txt, and last until the next starttime.


HeatingSettings.txt:
```
<houseID>: <type of heating>
```
Here, the type of heating is either HP (heatpump), CHP (combined heat power) or CONVENTIONAL (conventional heating used in the area, e.g. gas boilers (Netherlands)).



**Heat profiles**
For heating, the heatgains are also provided in Watts. The output matches with models by R.P. van Leeuwen. References in this section of the readme refer to chapters and pages of:
R.P. van Leeuwen, "Towards 100% renewable energy supply for urban areas and the role of smart control", PhD Thesis, University of Twente, Enschede, the Netherlands. Available: 
https://research.utwente.nl/en/publications/towards-100-renewable-energy-supply-for-urban-areas-and-the-role-


Heatgain_Profile.csv:
This file contains all zone heat gains for each house (columns) in each interval (rows), excluding solar gain. Matches with the gains in the 2R2C model, R.P. van Leeuwen Chapter 2.5, pp. 27-28

Airflow_Profile_Ventilation.csv:
This file contains the airflow of the ventilation system given in m3/h. The actual heat loss depends on the temperature difference between the ambient an indoor temperature. See  R.P. van Leeuwen Chapter 3.3, pp. 48 formula 3.1

Heatdemand_Profile.csv:
This file contains domestic hot tap water usage and falls outside the thermal models. However, a heat sourece must still provide the heating energy to heat up the water.

**Notes**
- HouseID starts at 0


Using the output
--------------

As stated in the introduction, the output should be used as input for energy management tools. An example of such a tool is DEMKit, developped at the University of Twente. For more information on DEMKit, smart grid optimization and the ALPG+DEMKit toolchain, please refer to:
G. Hoogsteen, "A Cyber-Physical Systems Perspective on Decentralized Energy Management", PhD Thesis, University of Twente, Enschede, the Netherlands. Available: 
https://research.utwente.nl/en/publications/a-cyber-physical-systems-perspective-on-decentralized-energy-mana

Device specific optimization algorithms, as implemented in DEMKit, are presented by T. van der Klauw:
T. van der Klauw, "Decentralized Energy Management with Profile Steering: Resource Allocation Problems in Energy Management", PhD Thesis, University of Twente, Enschede, the Netherlands. Available:
https://research.utwente.nl/en/publications/decentralized-energy-management-with-profile-steering-resource-al

Furthermore, the heating information generated as of v1.2 requires heat models for zones, ventilation calculations and implementation of thermostats. The ALPG output for heating and ventilation systems match the requirements for heat models as presented by R.P. van Leeuwen, which are also implemented in DEMKit. For more information on these models and control refer to:
R.P. van Leeuwen, "Towards 100% renewable energy supply for urban areas and the role of smart control", PhD Thesis, University of Twente, Enschede, the Netherlands. Available: 
https://research.utwente.nl/en/publications/towards-100-renewable-energy-supply-for-urban-areas-and-the-role-

Changelog
--------------

**Version 1.3**
- Creation of empty files on start
- Added new household types, including jobless persons

**Version 1.2**
- Improved the PV panel model
- Additional checks to prevent overwriting on the output folder
- Added parameters for configurage configs and output directory
- Improved folder structure
- Improved documentation and comments here and there
- Added heatdemand models
- ALPG now also generates thermostat setpoints
- ALPG now also generates internal heatgains
- ALPG now also generates active ventilation schedules (ventilation electricity usage updated accordingly)
- ALPG now also generates domestic hot water usage profiles
- Added penetrations for heating devices: Heatpumps and combined heat power (CHP)
- Removed the old config.py module, contents split up in configLoader.py and configs/example.py and the rest of the code
- Timebases now hardcode to 60 seconds as resampling was not working
- Usage of latitude and longitude with astral instead of city name for more flexibility
- Azimuth for PV panels shifted by 180 degrees!!!


**Version 1.1**
- Fixed retired people to have no driving distance to work
- Fixed dishwasher profile
- More rounded timeshiftable times to avoid synchronisation with auctions pushing towards the runtime deadlines
- Fixed a bug resulting in overlapping start + endtimes for EVs

