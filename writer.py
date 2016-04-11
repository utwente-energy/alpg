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
    


import random, math, copy, datetime, os

import profilegentools
import config

def writeCsvLine(fname, hnum, line):
	if not os.path.exists(config.folder+'/'+fname): 
		#overwrite
		f = open(config.folder+'/'+fname, 'w')
	else:
		#append
		f = open(config.folder+'/'+fname, 'a')
	f.write(line + '\n')
	f.close()
	
def writeCsvRow(fname, hnum, data):
	if hnum == 0:
		with open(config.folder+'/'+fname, 'w') as f:
			for l in range(0, len(data)):
				f.write(str(round(data[l])) + '\n')
	else:
		with open(config.folder+'/'+fname, 'r+') as f:
			lines = f.readlines()
			f.seek(0)
			f.truncate()
			j = 0
			for line in lines:
				line = line.rstrip()
				line = line + ';' + str(round(data[j])) + '\n'
				f.write(line)
				j = j + 1	

def writeNeighbourhood(num):
	pass
	#Write specific neighbourhood data if required, see the Triana example:
	#configFile = []
	#configFile.append('\tif houseNum == '+str(num)+':')
	#configFile.append('\t\timport out.House'+str(num))
	#configFile.append('\t\tout.House'+str(num)+'.addHouse(node, coordx, coordy, phase, houseNum, control, masterController, cfg)')

	#if num == 0: 
		##overwrite
		#f = open(config.folder+'/neighbourhood.py', 'w')
	#else:
		##append
		#f = open(config.folder+'/neighbourhood.py', 'a')
	#for line in range(0, len(configFile)):
		#f.write(configFile[line] + '\n')
	#f.close()




def writeHousehold(house, num):
	#Save the profile:
	writeCsvRow('Electricity_Profile.csv', num, house.Consumption['Total'])
	writeCsvRow('Electricity_Profile_Groupother.csv', num, house.Consumption['Other'])
	writeCsvRow('Electricity_Profile_GroupInductive.csv', num, house.Consumption['Inductive'])
	writeCsvRow('Electricity_Profile_GroupFridges.csv', num, house.Consumption['Fridges'])
	writeCsvRow('Electricity_Profile_GroupElectronics.csv', num, house.Consumption['Electronics'])
	writeCsvRow('Electricity_Profile_GroupLighting.csv', num, house.Consumption['Lighting'])
	writeCsvRow('Electricity_Profile_GroupStandby.csv', num, house.Consumption['Standby'])
	
	writeCsvRow('Reactive_Electricity_Profile.csv', num, house.ReactiveConsumption['Total'])
	writeCsvRow('Reactive_Electricity_Profile_Groupother.csv', num, house.ReactiveConsumption['Other'])
	writeCsvRow('Reactive_Electricity_Profile_GroupInductive.csv', num, house.ReactiveConsumption['Inductive'])
	writeCsvRow('Reactive_Electricity_Profile_GroupFridges.csv', num, house.ReactiveConsumption['Fridges'])
	writeCsvRow('Reactive_Electricity_Profile_GroupElectronics.csv', num, house.ReactiveConsumption['Electronics'])
	writeCsvRow('Reactive_Electricity_Profile_GroupLighting.csv', num, house.ReactiveConsumption['Lighting'])
	writeCsvRow('Reactive_Electricity_Profile_GroupStandby.csv', num, house.ReactiveConsumption['Standby'])
	
	#Write all devices:
	for k, v, in house.Devices.items():
		house.Devices[k].writeDevice(num)
	
	#House specific devices	
	if house.House.hasPV:
		text = str(num)+':'
		text += str(house.House.pvElevation)+','+str(house.House.pvAzimuth)+','+str(house.House.pvEfficiency)+','+str(house.House.pvArea)
		writeCsvLine('PhotovoltaicSettings.txt', num, text)
		
	writeCsvRow('Electricity_Profile_PVProduction.csv', num, house.PVProfile)
		
	if house.House.hasBattery:
		text = str(num)+':'
		text += str(house.House.batteryPower)+','+str(house.House.batteryCapacity)+','+str(round(house.House.batteryCapacity/2))
		writeCsvLine('BatterySettings.txt', num, text)	

	
def writeDeviceBufferTimeshiftable(machine, hnum):
	if machine.BufferCapacity > 0 and len(machine.StartTimes) > 0:
		text = str(hnum)+':'
		text += profilegentools.createStringList(machine.StartTimes, None, 60)
		writeCsvLine('ElectricVehicle_Starttimes.txt', hnum, text)
		
		text = str(hnum)+':'
		text += profilegentools.createStringList(machine.EndTimes, None, 60)
		writeCsvLine('ElectricVehicle_Endtimes.txt', hnum, text)
			
		text = str(hnum)+':'
		text += profilegentools.createStringList(machine.EnergyLoss, None, 1, False)
		writeCsvLine('ElectricVehicle_RequiredCharge.txt', hnum, text)	
			
		text = str(hnum)+':'
		text += str(machine.BufferCapacity)+','+str(machine.Consumption)
		writeCsvLine('ElectricVehicle_Specs.txt', hnum, text)
		

def writeDeviceTimeshiftable(machine, hnum):
	if machine.name == "WashingMachine" and len(machine.StartTimes) > 0:
		text = str(hnum)+':'
		text += profilegentools.createStringList(machine.StartTimes, None, 60)
		writeCsvLine('WashingMachine_Starttimes.txt', hnum, text)
		
		text = str(hnum)+':'
		text += profilegentools.createStringList(machine.EndTimes, None, 60)
		writeCsvLine('WashingMachine_Endtimes.txt', hnum, text)
		
		text = str(hnum)+':'
		text += machine.LongProfile
		writeCsvLine('WashingMachine_Profile.txt', hnum, text)
		
	elif len(machine.StartTimes) > 0:
		#In our case it is a dishwasher
		text = str(hnum)+':'
		text += profilegentools.createStringList(machine.StartTimes, None, 60)
		writeCsvLine('Dishwasher_Starttimes.txt', hnum, text)
		
		text = str(hnum)+':'
		text += profilegentools.createStringList(machine.EndTimes, None, 60)
		writeCsvLine('Dishwasher_Endtimes.txt', hnum, text)
		
		text = str(hnum)+':'
		text += machine.LongProfile
		writeCsvLine('Dishwasher_Profile.txt', hnum, text)