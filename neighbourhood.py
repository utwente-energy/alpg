
	#Artifical load profile generator v1.2, generation of artificial load profiles to benchmark demand side management approaches
    #Copyright (C) 2018 Gerwin Hoogsteen

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



from configLoader import *
config = importlib.import_module(cfgFile)

import houses

class neighbourhood:
	print("Creating Neighbourhood")
	houseList = []
	pvList = [0] * len(config.householdList)
	batteryList = [0] * len(config.householdList)
	inductioncookingList = [0] * len(config.householdList)

	for i in range(0, len(config.householdList)):
		houseList.append(houses.House())
	
	#Add PV to houses:
	for i in range(0, len(config.householdList)):
		if i < (round(len(config.householdList)*(config.penetrationPV/100))):
			pvList[i] = 1
	
	#And randomize:
	random.shuffle(pvList)

	#Add induction cooking
	for i in range(0, len(config.householdList)):
		if i < (round(len(config.householdList)*(config.penetrationInductioncooking/100))):
			inductioncookingList[i] = 1
	random.shuffle(inductioncookingList)
	for i in range(0, len(config.householdList)):
		if inductioncookingList[i] == 1:
			config.householdList[i].hasInductionCooking = True
	
	# Add Combined Heat Power
	i = 0
	while i < (round(len(config.householdList)*(config.penetrationCHP/100))) - (round(len(config.householdList)*(config.penetrationPV/100))):
		j = random.randint(0,len(config.householdList)-1)
		if config.householdList[j].hasCHP == False and pvList[j] == 0: # First supply houses without PV
			config.householdList[j].hasCHP = True
			i = i + 1
	if (round(len(config.householdList)*(config.penetrationPV/100))) > (round(len(config.householdList)*(config.penetrationCHP/100))): # If there are too much CHPs compared to PV, add some more CHPS
		while i < (round(len(config.householdList)*(config.penetrationCHP/100))):
			j = random.randint(0,len(config.householdList)-1)
			if config.householdList[j].hasCHP == False: # First supply houses without PV
				config.householdList[j].hasCHP = True
				i = i + 1
			
	# Add heat pumps
	i = 0
	while i < (round(len(config.householdList)*(config.penetrationHeatPump/100))):
		j = random.randint(0,len(config.householdList)-1)
		if config.householdList[j].hasHP == False and config.householdList[j].hasCHP == False:
			config.householdList[j].hasHP = True
			i = i + 1

	#Now add batteries
	i = 0
	while i < (round(len(config.householdList)*(config.penetrationBattery/100))):
		j = random.randint(0,len(config.householdList)-1)
		if (pvList[j] == 1 or config.householdList[j].hasCHP) and batteryList[j] == 0:
			batteryList[j] = 1
			i = i + 1
	
	# Add EVs
	drivingDistance = [0] * len(config.householdList)
	for i in range(0, len(config.householdList)):
		drivingDistance[i] = config.householdList[i].Persons[0].DistanceToWork
		drivingDistance = sorted(drivingDistance, reverse=True)
	for i in range(0, len(drivingDistance)):
		if i < (round(len(config.householdList)*(config.penetrationEV/100))+round(len(config.householdList)*(config.penetrationPHEV/100))):
			#We can still add an EV
			added = False
			j = 0
			while added == False:
				if config.householdList[j].Persons[0].DistanceToWork == drivingDistance[i]:
					if config.householdList[j].hasEV == False:
						if i < (round(len(config.householdList)*(config.penetrationEV/100))):
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
	for i in range(0,len(config.householdList)):
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
