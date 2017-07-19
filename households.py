#!/usr/bin/python3
	
	#Artifical load profile generator v1.0, generation of artificial load profiles to benchmark demand side management approaches
    #Copyright (C) 2016 Gerwin Hoogsteen

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
    


import random, math, copy, datetime

import profilegentools
import config
import persons
import devices
		
class Household:
	#Note to self, must simulate whole household at once!
	
	#Statistics can be found here:
	#http://www.nibud.nl/uitgaven/huishouden/gas-elektriciteit-en-water.html
	#http://www.energie-nederland.nl/wp-content/uploads/2013/04/EnergieTrends2014.pdf
	
	def __init__(self):
		self.generate()
		
	def generate(self):
		#The Yearly consumption is the normal consumption of domestic appliances as found for years in households. This excludes: 
		#																										   (PH)EV, Heat Pump, PV
		self.ConsumptionYearly		= profilegentools.gaussMinMax(3500,500) #kWh
		
		#According to http://www.energie-nederland.nl/wp-content/uploads/2013/04/EnergieTrends2014.pdf, this is the distribution for devices we are interested in:					
		self.ConsumptionShare = {	"Electronics"	: profilegentools.gaussMinMax(17,3), \
									"Lighting"		: profilegentools.gaussMinMax(6,2), \
									"Standby"		: profilegentools.gaussMinMax(35,6) }


		self.Persons = []
		
		self.Consumption 	= {		"Total"			: [], \
									"Other"			: [], \
									"Inductive"		: [], \
									"Fridges"		: [], \
									"Electronics"	: [], \
									"Lighting"		: [], \
									"Standby"		: [] }
		
		self.consumptionFactor = {	"Other"			: [], \
									"Inductive"		: [], \
									"Fridges"		: [], \
									"Electronics"	: [], \
									"Lighting"		: [], \
									"Standby"		: [] }
		
		self.ReactiveConsumption = {"Total"			: [], \
									"Other"			: [], \
									"Inductive"		: [], \
									"Fridges"		: [], \
									"Electronics"	: [], \
									"Lighting"		: [], \
									"Standby"		: [] }
		
		self.ReactiveFactor = {	"Other"			: 1, \
								"Inductive"		: (random.randint(70,90)/100), \
								"Fridges"		: (random.randint(50,65)/100), \
								"Electronics"	: -(random.randint(99,100)/100), \
								"Lighting"		: -(random.randint(99,100)/100), \
								"Standby"		: -(random.randint(75,85)/100) }
		
		self.PVProfile = []
		
		self.Occupancy = []
		
		
		
		self.hasDishwasher = False
		self.hasInductionCooking = random.randint(1,10)<4
		self.hasEV= False
		
		self.numOfWashes = 0		#weekly
		self.numOfDishwashes = 0 	#Weekly
		
		self.WashingDays = []
		self.washingMoment = [-1] * 7
		self.DishwashDays = []
		self.DishwashMoment = [-1] * 7
		
		#devices
		self.Fridges = []
		self.Devices = { 	"Kettle": devices.DeviceKettle(config.ConsumptionKettle),\
							"Lighting": devices.DeviceLighting(),\
							"Electronics": devices.DeviceElectronics(),\
							"Cooking":	devices.DeviceCooking(),\
							"Ventilation": devices.DeviceVentilation(config.ConsumptionHouseVentilation),\
							"Ironing": devices.DeviceIroning(config.ConsumptionIron),\
							"Vacuumcleaner": devices.DeviceVacuumcleaner(config.ConsumptionVacuumcleaner),\
							"WashingMachine": devices.DeviceWashingMachine(),\
							"DishwashMachine": devices.DeviceDishwasher(),\
							"ElectricalVehicle": devices.DeviceElectricalVehicle(),\
							"PVPanel" : devices.DeviceSolarPanel()}
		
		self.familyActivites = random.randint(config.familyOutingChanceMin, config.familyOutingChanceMax) / 100
	
	def setHouse(self, house):
		self.House = house
		
	def scaleProfile(self):
		totalShare = 0
		self.Consumption['Other'] = self.consumptionFactor['Other']
		self.Consumption['Inductive'] = self.consumptionFactor['Inductive']
		self.Consumption['Fridges'] = self.consumptionFactor['Fridges']
		
		self.Consumption['Total'] = self.consumptionFactor['Other']
		self.Consumption['Total'] = [sum(x) for x in zip(self.Consumption['Total'], self.Consumption['Inductive'])]
		self.Consumption['Total'] = [sum(x) for x in zip(self.Consumption['Total'], self.Consumption['Fridges'])]
		
		
		for k, v, in self.ConsumptionShare.items():
			sumDevice = sum(self.consumptionFactor[k])
			multiplier = ((self.ConsumptionShare[k]/100) * (((self.ConsumptionYearly/365) * config.numDays) * 1000) * 60) / sumDevice #joules
			self.Consumption[k] = [x * multiplier for x in self.consumptionFactor[k]]
			
			self.Consumption[k] = [round(x) for x in self.Consumption[k]]
			
			##NOTE: The following code breaks the random seed somehow, hence it is commented
			##add a bit of noise to the signal:
			#for x in range(0, len(self.Consumption[k])):
				#self.Consumption[k][x] = round(random.randint(int(round(0.93*self.Consumption[k][x])), int(round(1.07*self.Consumption[k][x]))))
			
			##add a sine wave
			#sinePeriod = random.randint(120, 180)
			#sineOffset = random.randint(0, sinePeriod)
			#for i in range(0, len(self.Consumption[k])):
				#self.Consumption[k][x] = int(round(self.Consumption[k][i]+ (math.sin(((i+sineOffset)/sinePeriod)*(2*3.14)))*self.Consumption[k][i]*0.05))
			#for i in range(0,1440):
				#self.Consumption[k][i] = round(self.Consumption[k][i]+ (math.sin(((i+sineOffset)/sinePeriod)*(2*3.14)))*self.Consumption[k][i]*0.05)
				
			
			self.Consumption['Total'] = [sum(x) for x in zip(self.Consumption['Total'], self.Consumption[k])]
		
		
	def reactivePowerProfile(self):
		self.ReactiveConsumption['Total'] = [0] * len(self.Consumption['Total'])
		
		for k, v, in self.ReactiveFactor.items():
			reactive = math.sqrt(1 - (self.ReactiveFactor[k]*self.ReactiveFactor[k]))
			if self.ReactiveFactor[k] < 0:
				reactive = -1*reactive
			
			self.ReactiveConsumption[k] = [x * reactive for x in self.Consumption[k]]
			
			#add some noise
			#self.ReactiveConsumption[k] = [(x+round(x*(-0.5+random.random())/(10))) for x in self.ReactiveConsumption[k]]
			
			self.ReactiveConsumption[k] = [round(x) for x in self.ReactiveConsumption[k]]			
			self.ReactiveConsumption['Total'] = [sum(x) for x in zip(self.ReactiveConsumption['Total'], self.ReactiveConsumption[k])]
		
		
	def generateWashingdays(self, days):
		self.WashingDays = random.sample(range(0, 7), days)
		for i in range(0,7):
			if i in self.WashingDays:
				notWorking = False
				for p in self.Persons:
					if p.Age > 25 and i not in p.Workdays:
						notWorking = True
				
				if notWorking and random.random() < 0.8:
					self.washingMoment[i] = random.randint((10*60), (17*60))
				
				else:
					moment = random.random()
					if(moment < 0.2):
						#Washing in the morning
						self.washingMoment[i] = self.Persons[0].WorkdayWakeUp_Avg + self.Persons[0].WorkdayWakeUp_Variate + 20
					elif(moment < 0.8):
						#Evening
						self.washingMoment[i] = random.randint((18*60), (21*60))
					else:
						#Later in the night
						self.washingMoment[i] = random.randint((21*60), (23*60))
			
			
			
	def generateDishwashdays(self, days):
		self.DishwashDays = random.sample(range(0, 7), days)
		for i in range(0,7):
			if i in self.DishwashDays:
				moment = random.random()
				if(moment < 0.2):
					#Washing in the morning
					self.DishwashMoment[i] = self.Persons[0].WorkdayWakeUp_Avg + self.Persons[0].WorkdayWakeUp_Variate + 20
				elif(moment < 0.7):
					#Evening
					self.DishwashMoment[i] = random.randint((19*60), (20*60))
				else:
					#Later in the night
					self.DishwashMoment[i] = random.randint((22*60), (23.5*60))
	
	def simulate(self):		
		for day in range(config.startDay, config.numDays+config.startDay):	
			dayOfWeek = day%7
			
			#Select occupancy profiles for each person
			self.OccupancyPersonsDay = [0] * 1440
			self.OccupancyAdultsDay = [0] * 1440
			self.OccupancyPerson = [[] for x in range(0, len(self.Persons))]
			for p in range(0, len(self.Persons)):
				schedulePerson = self.Persons[p].simulate(day)
				#print(schedulePerson)
				self.OccupancyPersonsDay = [sum(x) for x in zip(self.OccupancyPersonsDay, schedulePerson)]
				if(self.Persons[p].Age > 25):
					#This one may be useful to use for trips by EV in events (e.g. grocery shopping) and also scheduling of devices such as washing machines :)
					self.OccupancyAdultsDay = [sum(x) for x in zip(self.OccupancyAdultsDay, schedulePerson)]
				self.OccupancyPerson[p] = schedulePerson
			
			#Activities for the whole family
			eventDuration = 0;
			eventStart = 0;
			if (day%7==0 or day%7==6) and random.random() < self.familyActivites:
				#Only on Sundays we will have outings
				#see whether it takes whole day or just a visit to other family members
				#Notice that for now there is no relation between the individual family members and this outing!
				eventDuration = 0;
				if(random.random() < 0.2):
					#Long event
					eventDuration = random.randint(6*60,9*60)
					eventStart = random.randint(10*60,12*60)
				else:
					#short event, family visit or shopping.
					eventDuration = random.randint(3*60,4*60)
					if(day%7==0):
						eventStart = random.randint(15*60,16*60)
					else:
						eventStart = random.randint(13*60,14*60)	
			
				#Make these entries empty, no-one is home!
				for t in range(eventStart, eventStart+eventDuration):
					self.OccupancyPersonsDay[t] = 0
					self.OccupancyAdultsDay[t] = 0
					for p in range(0, len(self.Persons)):
						self.OccupancyPerson[p][t] = 0
						
			#Select cooking time
			cookingTime = random.randint(17*60,19.5*60)
			startCooking = cookingTime;
			cookingDuration = 0
			count = 0;
			while self.OccupancyPersonsDay[startCooking] == 0 and count != 100:
				startCooking = random.randint(17*60,19.5*60)
				count += 1
				if count == 99:
					startCooking = -1
					cookingConsumption = 0
					cookingDuration = 0
					break
		
			#Empty consumption patterns
			ElectronicsProfile = [0] * 1440
			LightingProfile = [0] * 1440
			OtherProfile = [0] * 1440
			InductiveProfile = [0] * 1440
			StandbyProfile = [1] * 1440 # Standby is fixed load, but will be scaled!
			
			#Simulate individual devices
			LightingProfile = self.Devices["Lighting"].simulate(1440, self.OccupancyPersonsDay, 1388534400+(3600*24*day))		
			ElectronicsProfile = self.Devices["Electronics"].simulate(1440, self.OccupancyPersonsDay, self.OccupancyPerson)		
			InductiveProfile = self.Devices["Ventilation"].simulate(1440, self.OccupancyPersonsDay)
			
			#Kitchen
			if startCooking != -1:
				OtherProfile = self.Devices["Cooking"].simulate(1440, self.OccupancyAdultsDay, self.Persons, startCooking, cookingDuration, self.hasInductionCooking)
			OtherProfile = [sum(x) for x in zip(OtherProfile, self.Devices['Kettle'].simulate(1440, self.OccupancyPersonsDay))]

			FridgeProfile = [0] * 1440
			for f in range(0, len(self.Fridges)):
				profile = self.Fridges[f].simulate(1440)
				FridgeProfile = [sum(x) for x in zip(FridgeProfile, profile)]	
			
			#Household and whitegoods
			#ironing
			if random.randint(1,7) == 1:
				OtherProfile = [sum(x) for x in zip(OtherProfile, self.Devices["Ironing"].simulate(1440, self.OccupancyAdultsDay, len(self.Persons)))]	
		
			#Vacuumcleaning
			if random.randint(1,7) == 1:
				OtherProfile = [sum(x) for x in zip(OtherProfile, self.Devices["Vacuumcleaner"].simulate(1440, self.OccupancyAdultsDay, len(self.Persons)))]	
							
			#Smart devices
			if day-config.startDay < config.numDays - 1:
				#Making sure that we dont run out of the simulation time
				
				#Whats for EV?					
				if self.hasEV > 0:
					self.Devices["ElectricalVehicle"].simulate(day, self.Persons[0], eventStart, eventDuration)
				
				if (((dayOfWeek in self.WashingDays) and (random.random()  < 0.9)) or (random.random()  < 0.1)):
					self.Devices["WashingMachine"].simulate(1440, day, self.OccupancyAdultsDay, self.washingMoment[dayOfWeek])
				
				#check if household has a dishwashmachine!
				if(self.hasDishwasher == True):
					if (((dayOfWeek in self.DishwashDays) and (random.random()  < 0.9)) or (random.random()  < 0.1)):
						self.Devices["DishwashMachine"].simulate(1440, day, self.OccupancyAdultsDay, self.DishwashMoment[dayOfWeek])

			self.consumptionFactor['Electronics'].extend(ElectronicsProfile)
			self.consumptionFactor['Lighting'].extend(LightingProfile)
			self.consumptionFactor['Standby'].extend(StandbyProfile)
			self.consumptionFactor['Other'].extend(OtherProfile)
			self.consumptionFactor['Inductive'].extend(InductiveProfile)
			self.consumptionFactor['Fridges'].extend(FridgeProfile)
			
			self.Occupancy.extend(self.OccupancyPersonsDay)

		#Now simulate the PV Profile
		if self.House.hasPV:
			#simulate(startday, timeintervals, pvArea, pvEfficiency, pvAzimuth, pvElevation)
			self.PVProfile = self.Devices['PVPanel'].simulate(config.startDay, config.numDays*((3600*24)/config.timeBase), self.House.pvArea, self.House.pvEfficiency, self.House.pvAzimuth, self.House.pvElevation)
		else:
			self.PVProfile = [0] * config.numDays * int(24*3600/config.timeBase)


	def saveToFile(self, num):
		text = []
		config.writer.writeHousehold(self, num)
		
		
		
		

class HouseholdSingleWorker(Household):
	def __init__(self):
		self.generate()
		self.ConsumptionYearly		= profilegentools.gaussMinMax(2010,400)*config.consumptionFactor #kWh http://www.nibud.nl/uitgaven/huishouden/gas-elektriciteit-en-water.html
		
		self.Persons = [ persons.PersonWorker(random.randint(26,65))]
		
		#For information about commuters, see this:
		#http://www.kimnet.nl/publicatie/mobiliteitsbalans-2013
		#Approx 50% uses the car to commute, which is our interrest as this part can be replaced by (PH)EV
		#http://www.cbs.nl/NR/rdonlyres/13516DAC-36E1-47B7-9918-2364EF7D0B48/0/2011k2v4p34art.pdf
		#3 out of 5 working people don't work in town. Fair to assume that these people commute by car
		#Average commute distance is not too clear from multiple sources, such as the once above. Something around 20km seems to be average in most sources
		#However 30 is also mentioned: http://www.nederlandheeftwerk.nl/index.php/cms_categorie/58707/bb/1/id/58707
		#Depends also on the region and work in vicinity.
		
		self.Persons[0].setDistanceToWork(round(max(0, random.gauss(config.commuteDistanceMean, config.commuteDistanceSigma))))	
			
		if(random.randint(1,2) == 1):
			self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeBigMin,config.ConsumptionFridgeBigMax)) ]
		else:
			self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)), devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)) ]
			
		#We synchronize the dishwasher and dryer based on the annual consumption. Furthermore, this also influences the number of washes.		
		self.hasDishwasher = random.randint(0,5) == 0 	#20%
		
		#Determine washing days
		self.generateWashingdays(random.randint(2,3))
		
		
		#Dermine Dishwasher times
		if self.hasDishwasher:
			self.generateDishwashdays(3)

		

class HouseholdDualWorker(Household):
	def __init__(self, parttime):
		self.generate()
		self.ConsumptionYearly		= profilegentools.gaussMinMax(3360,700)*config.consumptionFactor #kWh http://www.nibud.nl/uitgaven/huishouden/gas-elektriciteit-en-water.html
		
		age = random.randint(26,65)
		if parttime == True:
			self.Persons = [ persons.PersonWorker(age), persons.PersonParttimeWorker(age)]
		else:
			self.Persons = [ persons.PersonWorker(age), persons.PersonWorker(age)]
		
		#To make life easy, only one persons.Person will use the electric vehicle, so only the main persons.Person will receive a driving distance
		self.Persons[0].setDistanceToWork(round(max(0, random.gauss(config.commuteDistanceMean, config.commuteDistanceSigma))))		
		
		if(random.randint(1,2) == 1):
			self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeBigMin,config.ConsumptionFridgeBigMax)) ]
		else:
			self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)), devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)) ]
			
			
		self.hasDishwasher = random.randint(0,5) < 2 	#40%
		
		#Determine washing days
		self.generateWashingdays(random.randint(3,4))
		
		#Dermine Dishwasher times
		if self.hasDishwasher:
			self.generateDishwashdays(3)
	
	
class HouseholdFamilyDualWorker(Household):		
	def __init__(self, parttime):
		self.generate()
		numKids = round(max(min(4, random.gauss(1.7, 0.4)), 1))	# http://www.cbs.nl/nl-NL/menu/themas/bevolking/faq/specifiek/faq-hoeveel-kinderen.htm

		self.ConsumptionYearly		= profilegentools.gaussMinMax(2010+(700*numKids),500+(numKids*100))*config.consumptionFactor #kWh http://www.nibud.nl/uitgaven/huishouden/gas-elektriciteit-en-water.html
		
		ageParents = random.randint(40,55)
		self.Persons = [ persons.PersonWorker(ageParents)]
		
		self.Persons.append(copy.deepcopy(self.Persons[0]))  #Make a copy, we expect a household to be rather synchronized!
		if parttime == True:
			self.Persons[1].generateWorkdays(random.randint(2,3))
		
		#To make life easy, only one persons.Person will use the electric vehicle, so only the main persons.Person will receive a driving distance
		self.Persons[0].setDistanceToWork(round(max(0, random.gauss(config.commuteDistanceMean, config.commuteDistanceSigma))))	
				
		#now add the kids
		for i in range(0,numKids):
			self.Persons.append(persons.PersonStudent(random.randint(ageParents-3,ageParents+3)-30))
		
		self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)), devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)) ]
		
		self.hasDishwasher = random.randint(0,5) < 4 #60%	
		
		#Determine washing days
		self.generateWashingdays(min(5+numKids, 7))
		
		#Dermine Dishwasher times
		if self.hasDishwasher:
			self.generateDishwashdays(min(5+numKids, 7))
		
	
class HouseholdFamilySingleWorker(Household):		
	def __init__(self, parttime):
		self.generate()
		numKids = round(max(min(4, random.gauss(1.7, 0.4)), 1))	# http://www.cbs.nl/nl-NL/menu/themas/bevolking/faq/specifiek/faq-hoeveel-kinderen.htm
	
		self.ConsumptionYearly		= profilegentools.gaussMinMax(3360+(700*numKids),500+(numKids*100))*config.consumptionFactor #kWh http://www.nibud.nl/uitgaven/huishouden/gas-elektriciteit-en-water.html
		
		ageParents = random.randint(40,55)
		self.Persons = [ persons.PersonWorker(ageParents)]
		
		self.Persons.append(copy.deepcopy(self.Persons[0]))  #Make a copy, we expect a household to be rather synchronized!
		if parttime == True:
			self.Persons[1].generateWorkdays(random.randint(2,3))
		
		#To make life easy, only one persons.Person will use the electric vehicle, so only the main persons.Person will receive a driving distance
		self.Persons[0].setDistanceToWork(round(max(0, random.gauss(config.commuteDistanceMean, config.commuteDistanceSigma))))	
				
		#now add the kids
		for i in range(0,numKids):
			self.Persons.append(persons.PersonStudent(random.randint(ageParents-3,ageParents+3)-30))
			
		self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)), devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)) ]
		
		self.hasDishwasher = random.randint(0,5) < 4 #60%
		
		#Determine washing days
		self.generateWashingdays(min(5+numKids, 7))
		
		#Dermine Dishwasher times
		if self.hasDishwasher:
			self.generateDishwashdays(min(5+numKids, 7))
		
	
class HouseholdFamilySingleParent(Household):
	def __init__(self, parttime):
		self.generate()
		numKids = round(max(min(4, random.gauss(1.7, 0.4)), 1))	# http://www.cbs.nl/nl-NL/menu/themas/bevolking/faq/specifiek/faq-hoeveel-kinderen.htm
	
		self.ConsumptionYearly		= profilegentools.gaussMinMax(2500+(700*numKids),500+(numKids*100))*config.consumptionFactor #kWh http://www.nibud.nl/uitgaven/huishouden/gas-elektriciteit-en-water.html
		
		ageParents = random.randint(40,55)
		self.Persons = [ persons.PersonWorker(ageParents)]
		
		#To make life easy, only one persons.Person will use the electric vehicle, so only the main persons.Person will receive a driving distance
		self.Persons[0].setDistanceToWork(round(max(0, random.gauss(config.commuteDistanceMean, config.commuteDistanceSigma))))	
				
		#now add the kids
		for i in range(0,numKids):
			self.Persons.append(persons.PersonStudent(random.randint(ageParents-3,ageParents+3)-30))

		self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)), devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)) ]
		self.hasDishwasher = random.randint(0,5) < 4 #60%
		
		#Determine washing days
		self.generateWashingdays(min(5+numKids, 7))
		
		#Dermine Dishwasher times
		if self.hasDishwasher:
			self.generateDishwashdays(min(5+numKids, 7))
			
	
class HouseholdDualRetired(Household):	
	def __init__(self):
		self.generate()
		self.ConsumptionYearly		= profilegentools.gaussMinMax(3360,600)*config.consumptionFactor #kWh http://www.nibud.nl/uitgaven/huishouden/gas-elektriciteit-en-water.html
		
		age = random.triangular(65, 85, 70)
		self.Persons = [ persons.PersonRetired(age), persons.PersonRetired(age)]
		
		if(random.randint(1,2) == 1):
			self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeBigMin,config.ConsumptionFridgeBigMax)) ]
		else:
			self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)), devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)) ]
			
	
		self.hasDishwasher = random.randint(0,5) < 3 #40%
		
		#Determine washing days
		self.generateWashingdays(random.randint(3,4))
		
		#Dermine Dishwasher times
		if self.hasDishwasher:
			self.generateDishwashdays(3)

	
class HouseholdSingleRetired(Household):	
	def __init__(self):
		self.generate()
		self.ConsumptionYearly		= profilegentools.gaussMinMax(2010,400)*config.consumptionFactor #kWh http://www.nibud.nl/uitgaven/huishouden/gas-elektriciteit-en-water.html
		
		age = random.triangular(65, 85, 70)
		self.Persons = [ persons.PersonRetired(age)]
		
		if(random.randint(1,2) == 1):
			self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeBigMin,config.ConsumptionFridgeBigMax)) ]
		else:
			self.Fridges = [ devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)), devices.DeviceFridge(random.randint(config.ConsumptionFridgeSmallMin,config.ConsumptionFridgeSmallMax)) ]
			
		
		self.hasDishwasher = random.randint(0,5) < 3 #40%
		
		#Determine washing days
		self.generateWashingdays(random.randint(2, 3))
		
		#Dermine Dishwasher times
		if self.hasDishwasher:
			self.generateDishwashdays(3)
		
		
