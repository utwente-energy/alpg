
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

import os
import profilegentools

def writeCsvLine(fname, hnum, line):
	if not os.path.exists(outputFolder+'/'+fname): 
		#overwrite
		f = open(outputFolder+'/'+fname, 'w')
	else:
		#append
		f = open(outputFolder+'/'+fname, 'a')
	f.write(line + '\n')
	f.close()
	
def writeCsvRow(fname, hnum, data):
	if hnum == 0:
		with open(outputFolder+'/'+fname, 'w') as f:
			for l in range(0, len(data)):
				f.write(str(round(data[l])) + '\n')
	else:
		with open(outputFolder+'/'+fname, 'r+') as f:
			lines = f.readlines()
			f.seek(0)
			f.truncate()
			j = 0
			for line in lines:
				line = line.rstrip()
				line = line + ';' + str(round(data[j])) + '\n'
				f.write(line)
				j = j + 1	


def createFile(fname):
    if os.path.exists(fname):
        os.utime(outputFolder+'/'+fname, None)
    else:
        open(outputFolder+'/'+fname, 'a').close()

# Function to create empty files to ensure that certain software doesn't crash for lack of files
def createEmptyFiles():
	createFile('Electricity_Profile.csv')
	createFile('Electricity_Profile_GroupOther.csv')
	createFile('Electricity_Profile_GroupInductive.csv')
	createFile('Electricity_Profile_GroupFridges.csv')
	createFile('Electricity_Profile_GroupElectronics.csv')
	createFile('Electricity_Profile_GroupLighting.csv')
	createFile('Electricity_Profile_GroupStandby.csv')
	
	createFile('Reactive_Electricity_Profile.csv')
	createFile('Reactive_Electricity_Profile_GroupOther.csv')
	createFile('Reactive_Electricity_Profile_GroupInductive.csv')
	createFile('Reactive_Electricity_Profile_GroupFridges.csv')
	createFile('Reactive_Electricity_Profile_GroupElectronics.csv')
	createFile('Reactive_Electricity_Profile_GroupLighting.csv')
	createFile('Reactive_Electricity_Profile_GroupStandby.csv')

	createFile('Electricity_Profile_PVProduction.csv')
	createFile('PhotovoltaicSettings.txt')
	createFile('Electricity_Profile_PVProduction.csv')
	createFile('BatterySettings.txt')
	createFile('HeatingSettings.txt')
		
	createFile('ElectricVehicle_Starttimes.txt')
	createFile('ElectricVehicle_Endtimes.txt')
	createFile('ElectricVehicle_RequiredCharge.txt')	
	createFile('ElectricVehicle_Specs.txt')

	createFile('WashingMachine_Starttimes.txt')
	createFile('WashingMachine_Endtimes.txt')
	createFile('WashingMachine_Profile.txt')
		
	createFile('Dishwasher_Starttimes.txt')
	createFile('Dishwasher_Endtimes.txt')
	createFile('Dishwasher_Profile.txt')

	createFile('Thermostat_Starttimes.txt')
	createFile('Thermostat_Setpoints.txt')
	
	# Save HeatGain profiles
	createFile('Heatgain_Profile.csv')
	createFile('Heatgain_Profile_Persons.csv')
	createFile('Heatgain_Profile_Devices.csv')

	# Safe TapWater profiles
	createFile('Heatdemand_Profile.csv')
	createFile('Heatdemand_Profile_DHWTap.csv')

	createFile('Airflow_Profile_Ventilation.csv')

def writeNeighbourhood(num):
	pass

def writeHousehold(house, num):
	#Save the profile:
	writeCsvRow('Electricity_Profile.csv', num, house.Consumption['Total'])
	writeCsvRow('Electricity_Profile_GroupOther.csv', num, house.Consumption['Other'])
	writeCsvRow('Electricity_Profile_GroupInductive.csv', num, house.Consumption['Inductive'])
	writeCsvRow('Electricity_Profile_GroupFridges.csv', num, house.Consumption['Fridges'])
	writeCsvRow('Electricity_Profile_GroupElectronics.csv', num, house.Consumption['Electronics'])
	writeCsvRow('Electricity_Profile_GroupLighting.csv', num, house.Consumption['Lighting'])
	writeCsvRow('Electricity_Profile_GroupStandby.csv', num, house.Consumption['Standby'])
	
	writeCsvRow('Reactive_Electricity_Profile.csv', num, house.ReactiveConsumption['Total'])
	writeCsvRow('Reactive_Electricity_Profile_GroupOther.csv', num, house.ReactiveConsumption['Other'])
	writeCsvRow('Reactive_Electricity_Profile_GroupInductive.csv', num, house.ReactiveConsumption['Inductive'])
	writeCsvRow('Reactive_Electricity_Profile_GroupFridges.csv', num, house.ReactiveConsumption['Fridges'])
	writeCsvRow('Reactive_Electricity_Profile_GroupElectronics.csv', num, house.ReactiveConsumption['Electronics'])
	writeCsvRow('Reactive_Electricity_Profile_GroupLighting.csv', num, house.ReactiveConsumption['Lighting'])
	writeCsvRow('Reactive_Electricity_Profile_GroupStandby.csv', num, house.ReactiveConsumption['Standby'])

	# Save HeatGain profiles
	writeCsvRow('Heatgain_Profile.csv', num, house.HeatGain['Total'])
	writeCsvRow('Heatgain_Profile_Persons.csv', num, house.HeatGain['PersonGain'])
	writeCsvRow('Heatgain_Profile_Devices.csv', num, house.HeatGain['DeviceGain'])

	# Safe TapWater profiles
	writeCsvRow('Heatdemand_Profile.csv', num, house.HeatDemand['Total'])
	writeCsvRow('Heatdemand_Profile_DHWTap.csv', num, house.HeatDemand['DHWDemand'])

	# Airflow, kind of hacky
	writeCsvRow('Airflow_Profile_Ventilation.csv', num, house.HeatGain['VentFlow'])

	# writeCsvRow('Heatgain_Profile_Solar.csv', num, house.HeatGain['SolarGain'])

	# FIXME Add DHW Profile

	#Write all devices:
	for k, v, in house.Devices.items():
		house.Devices[k].writeDevice(num)

	#Write all heatdevices:
	for k, v, in house.HeatingDevices.items():
		house.HeatingDevices[k].writeDevice(num)
	
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

	# Write what type of heating device is used
	if house.hasHP:
		text = str(num)+':HP'			# Heat pump
		writeCsvLine('HeatingSettings.txt', num, text)
	elif house.hasCHP:
		text = str(num)+':CHP'			# Combined Heat Power
		writeCsvLine('HeatingSettings.txt', num, text)
	else:
		text = str(num)+':CONVENTIONAL'	# Conventional heating device, e.g. natural gas boiler
		writeCsvLine('HeatingSettings.txt', num, text)
	
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

def writeDeviceThermostat(machine, hnum):
	text = str(hnum)+':'
	text += profilegentools.createStringList(machine.StartTimes, None, 60)
	writeCsvLine('Thermostat_Starttimes.txt', hnum, text)

	text = str(hnum)+':'
	text += profilegentools.createStringList(machine.Setpoints)
	writeCsvLine('Thermostat_Setpoints.txt', hnum, text)
