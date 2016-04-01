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
    


import random, math

import profilegentools
import config

class Person:		
	def __init__(self, age):
		generate(age)
		
	def generate(self, age):	
		#Variates could also use a gauss distribution, some persons are more predictable than others ;)
		self.Age = age
		
		self.WorkdayWakeUp_Avg				= profilegentools.gaussMinMax(7*60, 1.5*60)
		self.WorkdayWakeUp_Variate 			= 10
		self.WorkdayLeave_Avg				= self.WorkdayWakeUp_Avg + profilegentools.gaussMinMax(45, 15)
		self.WorkdayLeave_Variate 			= 10
		self.WorkdayArrival_Avg				= self.WorkdayLeave_Avg + profilegentools.gaussMinMax(8.5*60, 30) 
		self.WorkdayArrival_Variate			= 15
		self.WorkdaySport_Avg				= self.WorkdayArrival_Avg + profilegentools.gaussMinMax(2.5*60, 2*60)
		self.WorkdaySport_Variate			= 15
		self.WorkdaySportDuration_Avg			= profilegentools.gaussMinMax(1.5*60, 30)
		self.WorkdaySportDuration_Variate 		= 10
		self.WorkdayBedTime_Avg				= self.WorkdayWakeUp_Avg + profilegentools.gaussMinMax(15.5*60,30) 
		self.WorkdayBedTime_Variate			= 15
		self.WorkdayActivities 				= random.randint(config.personWeekdayActivityChanceMin, config.personWeekdayActivityChanceMax) / 100 #Chance to conduct random activities			
		
		self.WeekendWakeUp_Avg 				= profilegentools.gaussMinMax(9*60, 2*60)
		self.WeekendWakeUp_Variate 			= 20
		self.WeekendSport_Avg				= profilegentools.gaussMinMax(14*60, 5*60)
		self.WeekendSport_Variate			= 60
		self.WeekendSportDuration_Avg			= profilegentools.gaussMinMax(1.5*60, 30)
		self.WeekendSportDuration_Variate 		= 30
		self.WeekendBedTime_Avg				= profilegentools.gaussMinMax(23*60, 30) 
		self.WeekendBedTime_Variate			= 10
		self.WeekendActivities				= random.randint(config.personWeekendActivityChanceMin, config.personWeekendActivityChanceMax) / 100
		
		#For a new deepcopy, the following values should be regenerated
		self.WorkdaySportday = 1 + random.randint(1,5)
		self.WeekendSportday = 6*random.randint(0,1)
		self.Workdays = range(1,6)
		self.DistanceToWork  = 0
			
		
		self.CookingTime = self.WorkdayArrival_Avg + 30




		
	def generateActivity(self):
		self.WorkdaySportday = 1 + random.randint(1,5)
		self.WeekendSportday = 6 + randon.randint(0,1)

	def generateWorkdays(self, days):
		self.Workdays = random.sample(range(1, 6), days)
		
	def setActivities(self, workday, weekend):
		self.WorkdayActivities 				= workday
		self.WeekendActivities				= weekend
	
	def setDistanceToWork(self, distance):
		if distance > 5: 	#Only distance of 5 or more is interesting, the rest is not really of interrest tbh. Bicycle will be used for example
			self.DistanceToWork = distance
	
	def simulateWorkday(self, day):
		#select variables
		eventList = []
		self.WorkdayWakeUp = random.randint((self.WorkdayWakeUp_Avg - self.WorkdayWakeUp_Variate), (self.WorkdayWakeUp_Avg + self.WorkdayWakeUp_Variate))
		eventList.append(self.WorkdayWakeUp)
		self.WorkdayLeave = random.randint((self.WorkdayLeave_Avg - self.WorkdayLeave_Variate), (self.WorkdayLeave_Avg + self.WorkdayLeave_Variate))
		eventList.append(self.WorkdayLeave)
		self.WorkdayArrival = random.randint((self.WorkdayArrival_Avg - self.WorkdayArrival_Variate), (self.WorkdayArrival_Avg + self.WorkdayArrival_Variate))
		eventList.append(self.WorkdayArrival)
		
		if ((day%7) == self.WorkdaySportday):
			#Today this person will go to sport or have an activity. Times are synchronized to keep it easy
			self.WorkdayActivity = random.randint((self.WorkdaySport_Avg - self.WorkdaySport_Variate), (self.WorkdaySport_Avg + self.WorkdaySport_Variate))
			eventList.append(self.WorkdayActivity)
			self.WorkdayActivityEnd = self.WorkdayActivity + random.randint((self.WorkdaySportDuration_Avg - self.WorkdaySportDuration_Variate), (self.WorkdaySportDuration_Avg + self.WorkdaySportDuration_Variate))
			eventList.append(self.WorkdayActivityEnd)
		elif (random.random() < self.WorkdayActivities):
			self.WorkdayActivity = random.randint((self.WorkdaySport_Avg - self.WorkdaySport_Variate), (self.WorkdaySport_Avg + self.WorkdaySport_Variate))
			eventList.append(self.WorkdayActivity)
			self.WorkdayActivityEnd = self.WorkdayActivity + random.randint((self.WorkdaySportDuration_Avg - self.WorkdaySportDuration_Variate), (self.WorkdaySportDuration_Avg + self.WorkdaySportDuration_Variate))
			eventList.append(self.WorkdayActivityEnd)
			
		self.WorkdayBedTime = min(1439, random.randint((self.WorkdayBedTime_Avg - self.WorkdayBedTime_Variate), (self.WorkdayBedTime_Avg + self.WorkdayBedTime_Variate)))
		eventList.append(self.WorkdayBedTime)
		
		active = 0 #start asleep
		activeList = []
		for minute in range(0,1440):
			if minute in eventList:
				active = 1 - active
			activeList.append(active)
		assert((len(eventList)%2)==0)
		assert(self.WorkdayBedTime<1440)
		
		return activeList
		
		
	def simulateWeekend(self, day):
		#select variables
		eventList = []
		
		#basically this simulates a free day. On normal days one will wake up more early
		if((day%7)==0 or (day%7)==6):
			self.WeekendWakeUp = random.randint((self.WeekendWakeUp_Avg - self.WeekendWakeUp_Variate), (self.WeekendWakeUp_Avg + self.WeekendWakeUp_Variate))
		else:
			#Day off, get out of bed earlier
			self.WeekendWakeUp = random.randint((self.WeekendWakeUp_Avg - self.WeekendWakeUp_Variate - 60), (self.WeekendWakeUp_Avg + self.WeekendWakeUp_Variate - 60))
		eventList.append(self.WeekendWakeUp)
		
		if (((day%7) == self.WeekendSportday)):
			#Today this person will go to sport or have an activity. Times are synchronized to keep it easy
			self.WeekendActivity = random.randint((self.WeekendSport_Avg - self.WeekendSport_Variate), (self.WeekendSport_Avg + self.WeekendSport_Variate))
			eventList.append(self.WeekendActivity)
			self.WeekendActivityEnd = self.WeekendActivity + random.randint((self.WeekendSportDuration_Avg - self.WeekendSportDuration_Variate), (self.WeekendSportDuration_Avg + self.WeekendSportDuration_Variate))
			eventList.append(self.WeekendActivityEnd)
		elif ((day%7) == self.WorkdaySportday):
			#Today this person will go to sport or have an activity. Times are synchronized to keep it easy
			self.WorkdayActivity = random.randint((self.WorkdaySport_Avg - self.WorkdaySport_Variate), (self.WorkdaySport_Avg + self.WorkdaySport_Variate))
			eventList.append(self.WorkdayActivity)
			self.WorkdayActivityEnd = self.WorkdayActivity + random.randint((self.WorkdaySportDuration_Avg - self.WorkdaySportDuration_Variate), (self.WorkdaySportDuration_Avg + self.WorkdaySportDuration_Variate))
			eventList.append(self.WorkdayActivityEnd)
		elif (random.random() < self.WeekendActivities):
			duration = random.randint(90,8*60)
			startOffset = profilegentools.gaussMinMax(9*60, 1*60)
			if duration > 6*60:
				#all-day event
				if random.randint(0,1) == 0: #Note: For retired people we might need to add a restriction here
					self.WeekendActivity = self.WeekendWakeUp + random.randint(60,90)
				else:
					self.WeekendActivity = random.randint(13*60,15*60)
			elif duration > 3*60:
				#Afternoon activity
				self.WeekendActivity = random.randint(14*60,15*60)
			elif random.randint(0,1) == 0:
				#Morning event
				self.WeekendActivity = self.WeekendWakeUp + random.randint(60,90)
			else:
				#night event
				self.WeekendActivity = random.randint(20*60,21*60)
			eventList.append(self.WeekendActivity)
			self.WeekendActivityEnd = self.WeekendActivity + duration
			eventList.append(self.WeekendActivityEnd)
			
		self.WeekendBedTime = random.randint((self.WeekendBedTime_Avg - self.WeekendBedTime_Variate), (self.WeekendBedTime_Avg + self.WeekendBedTime_Variate))
		eventList.append(self.WeekendBedTime)
		
		active = 0 #start asleep
		activeList = []
		for minute in range(0,1440):
			if minute in eventList:
				active = 1 - active
			activeList.append(active)
		assert((len(eventList)%2)==0)
		
		assert(self.WeekendBedTime<1440)
		
		return activeList

		
	def simulate(self, day):
		if (day%7) in self.Workdays:
			if((day%7)==0 or (day%7)==6 or random.randint(0,(100-len(self.Workdays)*10))==0):
				return self.simulateWeekend(day)
			else:
				return self.simulateWorkday(day)
		else:
			return self.simulateWeekend(day)
		
		
		
		
class PersonWorker(Person):
	def __init__(self, age):
		self.generate(age)
		if age>55 or random.randint(0,2)==0: #Older people can get a day off sometimes, such as BAPO in the education. Furthermore 33% has a home working day: http://www.kamer033.nl/nieuws/in-8-tips-een-productieve-thuiswerkdag/
			self.generateWorkdays(4)
		else:
			self.generateWorkdays(5)
		
class PersonParttimeWorker(Person):
	def __init__(self, age):
		self.generate(age)
		self.generateWorkdays(random.randint(2,3))
			
			
class PersonStudent(Person):
	def __init__(self, age):
		self.generate(age)
		self.WorkdayArrival_Avg			= self.WorkdayLeave_Avg + profilegentools.gaussMinMax(7*60, 30)
		if(age < 16):
			self.WorkdayBedTime_Avg		= profilegentools.gaussMinMax((23-(16-age)*0.25)*60, 30) 
			self.WeekendBedTime_Avg		= profilegentools.gaussMinMax((23-(16-age)*0.25)*60, 30) 
		self.WorkdaySport_Avg			= profilegentools.gaussMinMax(19*60, 1*60)

class PersonJobless(Person):
	def __init__(self, age):
		self.generate(age)
		self.generateWorkdays(0)
			
		
class PersonRetired(Person):
	def __init__(self, age):
		self.generate(age)
		self.generateWorkdays(0)
		self.WeekendWakeUp_Avg 			= profilegentools.gaussMinMax(8.5*60, 1*60)
		self.WeekendActivities 			= 0.7 - (0.03*(age-65))
		self.WorkdayBedTime_Avg			= profilegentools.gaussMinMax((23-(age-65)*0.15)*60, 30) 
		self.WeekendBedTime_Avg			= profilegentools.gaussMinMax((23-(age-65)*0.15)*60, 30) 
		
		
		
		