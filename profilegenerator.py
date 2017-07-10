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
    


import random, csv, io, os, sys

import profilegentools

import config

print("Profilegenerator 1.1\n")
print("Copyright (C) 2017 Gerwin Hoogsteen")
print("This program comes with ABSOLUTELY NO WARRANTY.")
print("This is free software, and you are welcome to redistribute it under certain conditions.")
print("See the acompanying license for more information.\n")

print("Writing output file to: "+config.folder)
print("The current config will create and simulate "+str(len(config.householdList))+" households\n")

#import neighbourhood
import neighbourhood
neighbourhood.neighbourhood()

configFile = []

#more preamble
if not os.path.exists(config.folder):
    os.makedirs(config.folder)



#addhouse function
configFile.append('control = False')
configFile.append('def addHouse(node, coordx, coordy, phase, houseNum):')

hnum = 0

householdList = config.householdList
numOfHouseholds = len(householdList)



if not os.path.exists(config.folder):
	os.makedirs(config.folder)
			

while len(householdList) > 0:
	#Apparently, the seed is brokin in the while loop...:
	#random.seed(config.seed+hnum)
	
	print("Household "+str(hnum+1)+" of "+str(numOfHouseholds))
	householdList[0].simulate()
	
	#Warning: On my PC the random number is still the same at this point, but after calling scaleProfile() it isn't!!!
	householdList[0].scaleProfile()
	householdList[0].reactivePowerProfile()

	
	if config.intervalLength != 1:
		householdList[0].Consumption['Total'] = profilegentools.resample(householdList[0].Consumption['Total'], config.intervalLength)
		householdList[0].ReactiveConsumption['Total'] = profilegentools.resample(householdList[0].ReactiveConsumption['Total'], config.intervalLength)

	config.writer.writeHousehold(householdList[0], hnum)
	config.writer.writeNeighbourhood(hnum)
	
	householdList[0].Consumption = None
	householdList[0].Occupancy = None
	for p in householdList[0].Persons:
		del(p)
	del(householdList[0])
	
	hnum = hnum + 1
