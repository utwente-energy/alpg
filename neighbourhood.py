#!/usr/bin/python3

import random

import config
import profilegentools
import houses

import sys

class neighbourhood:
	print("Creating Neighbourhood")
	houseList = []
	pvList = [0] * config.numHouses
	batteryList = [0] * config.numHouses
	inductioncookingList = [0] * config.numHouses

	for i in range(0, config.numHouses):
		houseList.append(houses.House())
	
	#Add PV to houses:
	for i in range(0, config.numHouses):
		if i < (round(config.numHouses*(config.penetrationPV/100))):
			pvList[i] = 1
					
	#And randomize:
	random.shuffle(pvList)

	#Add induction cooking
	for i in range(0, config.numHouses):
		if i < (round(config.numHouses*(config.penetrationInductioncooking/100))):
			inductioncookingList[i] = 1
	random.shuffle(inductioncookingList)
	for i in range(0, len(config.householdList)):
		if inductioncookingList[i] == 1:
			config.householdList[i].hasInductionCooking = True

	#Now add batteries
	i = 0
	while i < (round(config.numHouses*(config.penetrationBattery/100))):
		j = random.randint(0,config.numHouses-1)
		if pvList[j] == 1 and batteryList[j] == 0:
			batteryList[j] = 1
			i = i + 1

	
	drivingDistance = [0] * config.numHouses	
	
	# Add EVs		
	for i in range(0, len(config.householdList)):
		drivingDistance[i] = config.householdList[i].Persons[0].DistanceToWork
		drivingDistance = sorted(drivingDistance, reverse=True)
	for i in range(0, len(drivingDistance)):
		if i < (round(config.numHouses*(config.penetrationEV/100))+round(config.numHouses*(config.penetrationPHEV/100))):
			#We can still add an EV
			added = False
			j = 0
			while added == False:
				if config.householdList[j].Persons[0].DistanceToWork == drivingDistance[i]:
					if config.householdList[j].hasEV == False:
						if i < (round(config.numHouses*(config.penetrationEV/100))):
							config.householdList[j].Devices["ElectricalVehicle"].BufferCapacity = config.capacityEV
							config.householdList[j].Devices["ElectricalVehicle"].Consumption = config.powerEV
						else:
							config.householdList[j].Devices["ElectricalVehicle"].BufferCapacity = config.capacityPHEV
							config.householdList[j].Devices["ElectricalVehicle"].Consumption = config.powerPHEV
						config.householdList[j].hasEV = True
						added = True
				j = j + 1
	
	#Shuffle
	random.shuffle(config.householdList)
		
	#And then map households to houses
	for i in range(0,config.numHouses):
		config.householdList[i].setHouse(houseList[i])
		#add solar panels according to the size of the annual consumption:
		if pvList[i] == 1:
			# Do something fancy
			# A solar panel will produce approx 875kWh per kWp on annual basis in the Netherlands:
			# https://www.consumentenbond.nl/energie/extra/wat-zijn-zonnepanelen/
			# Furthermore, the size of a single solar panel is somewhere around 1.6m2 (various sources)
			# Hence, if a household is to be more or less energy neutral we have:
			area = round( (config.householdList[i].ConsumptionYearly / config.PVProductionPerYear) * 1.6) #average panel is 1.6m2
			config.householdList[i].House.addPV(area)
			
		if batteryList[i] == 1:
			# Do something based on the household size and whether the house has an EV:
			if config.householdList[i].hasEV:
				#House has an EV as well!
				config.householdList[i].House.addBattery(config.capacityBatteryLarge, config.powerBatteryLarge) #Let's give it a nice battery!
			else:
				#NO EV, just some peak shaving:
				if(config.householdList[i].ConsumptionYearly > 2500):
					config.householdList[i].House.addBattery(config.capacityBatteryMedium, config.powerBatteryMedium)
				else:
					config.householdList[i].House.addBattery(config.capacityBatterySmall, config.powerBatterySmall)
