#!/usr/bin/python3    

    #Copyright (C) 2023 University of Twente

    #This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    

    
#This is an example configuration file!

# Select the output writer
import writer as writer

#Random seed
seed = 42

#input files:
weather_irradiation = 'input/weather/solarirradiation_twenthe.csv'
weather_timebaseDataset = 3600 #in seconds per interval


#Simulation:
#number of days to simulate and skipping of initial days. Simulation starts at Sunday January 1.
numDays = 365			# number of days
startDay = 0			# Initial day


#Select the geographic location. Refer to the Astral plugin to see available locations (or give a lon+lat)
# Use e.g. https://www.latlong.net/
from astral import Location

location = Location()
location.solar_depression = 'civil'
location.latitude = 52.239095
location.longitude = 6.857018
location.timezone = 'Europe/Amsterdam'
location.elevation = 0

#Select the devices in the neighbourhood

#Devices
#Scale overall consumption:
consumptionFactor = 1.0 #consumption was a bit too high

# Penetration of emerging technology in percentages
# all values must be between 0-100
# These indicate what percentage of the houses has a certain device

# Electric mobility, restriction that the sum <= 100
# Note, households with larger driving distances will receive EVs first
penetrationEV 				= 25
penetrationPHEV 			= 25

# PV and storage, restriction that Battery <= PV
# Note PV and battery size depend on the annual household consumption
# This emulates the Dutch "nul-op-the-meter regime (net zero annual electricity usage)
penetrationPV				= 50
penetrationBattery 			= 10	#Note only houses with PV will receive a battery!

# Heating systems, with restriction that the sum <= 100
penetrationHeatPump 		= 25
penetrationCHP				= 5		# Combined heat and power

penetrationInductioncooking = 25


#Device parameters:
#EV
capacityEV = 	50000	#Wh
powerEV = 		11000	#W
capacityPHEV = 	10000	#Wh
powerPHEV = 	3700	#W

#PV
PVProductionPerYear = 	220		#average kWh per m2 solar panel on annual basis
PVAngleMean = 			35 		#degrees, 0 is horizontal to earth surface
PVAngleSigma = 			10		#degrees
PVAzimuthMean = 		180 	#degrees, 0 is north, 90 is east
PVAzimuthSigma = 		90 		#degrees
PVEfficiencyMin = 		18		#% of theoretical max
PVEfficiencyMax = 		22		#% of theoretical max

#Driving distances
commuteDistanceMean = 	25		#km
commuteDistanceSigma = 	10		#km


#Battery
capacityBatteryLarge = 	5000 	#Wh
capacityBatteryMedium = 4000  	#Wh
capacityBatterySmall = 	2000 	#Wh
powerBatteryLarge = 	3700 	#W
powerBatteryMedium = 	3700  	#W
powerBatterySmall = 	3700 	#W


#Kitchen
#Consumption of devices
ConsumptionOven = 				2000	#W
ConsumptionMicroWave = 			800		#W
ConsumptionStoveVentilation = 	120 	#W #But this is maximum, usually set lower!
ConsumptionInductionStove = 	2200 	#W #http://homeguides.sfgate.com/many-watts-induction-stove-85380.html

ConsumptionFridgeBigMin = 		80		#W
ConsumptionFridgeBigMax = 		120		#W
ConsumptionFridgeSmallMin = 	50		#W
ConsumptionFridgeSmallMax = 	80		#W

ConsumptionKettle = 			2000	#W

#White goods
ConsumptionIron = 				2000	#W
ConsumptionVacuumcleaner = 		1500	#W

#House
ConsumptionHouseVentilation = 	50 		#W


#Household randomization
#all values must be between 0-1000
familyOutingChanceMin = 			10 	#percentage
familyOutingChanceMax = 			20 	#percentage
personWeekdayActivityChanceMin = 	20 	#percentage
personWeekdayActivityChanceMax = 	30 	#percentage
personWeekendActivityChanceMin = 	20 	#percentage
personWeekendActivityChanceMax = 	30 	#percentage



householdList = []

#Select the types of households
import households

for i in range(0,1):
	householdList.append(households.HouseholdSingleWorker())

for i in range(0,2):
	householdList.append(households.HouseholdSingleRetired())

for i in range(0,1):
	householdList.append(households.HouseholdDualWorker(True))

for i in range(0,1):
	householdList.append(households.HouseholdDualWorker(False))

for i in range(0,2):
	householdList.append(households.HouseholdDualRetired())

for i in range(0,2):
	householdList.append(households.HouseholdFamilyDualWorker(True))

for i in range(0,1):
	householdList.append(households.HouseholdFamilyDualWorker(False))
