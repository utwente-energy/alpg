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

def writeNeighbourhood(num):
	configFile = []
	configFile.append('\tif houseNum == '+str(num)+':')
	configFile.append('\t\timport out.House'+str(num))
	configFile.append('\t\tout.House'+str(num)+'.addHouse(node, coordx, coordy, phase, houseNum, control, masterController, cfg)')

	if num == 0: 
		#overwrite
		f = open(config.folder+'/neighbourhood.py', 'w')
	else:
		#append
		f = open(config.folder+'/neighbourhood.py', 'a')
	for line in range(0, len(configFile)):
		f.write(configFile[line] + '\n')
	f.close()

def writeHousehold(house, num):
	#Save the profile:
	
	#Only saving total power now, could be replaced by others
	if num == 0:
		with open(config.folder+'/electricity_profile.csv', 'w') as f:
			for l in range(0, len(house.Consumption['Total'])):
				f.write(str(round(house.Consumption['Total'][l])) + '\n')
		with open(config.folder+'/electricity_reactive_profile.csv', 'w') as fr:
			for l in range(0, len(house.ReactiveConsumption['Total'])):
				fr.write(str(round(house.ReactiveConsumption['Total'][l])) + '\n')
	else:
		with open(config.folder+'/electricity_profile.csv', 'r+') as f:
			lines = f.readlines()
			f.seek(0)
			f.truncate()
			j = 0
			for line in lines:
				line = line.rstrip()
				line = line + ';' + str(round(house.Consumption['Total'][j])) + '\n'
				f.write(line)
				j = j + 1	
		with open(config.folder+'/electricity_reactive_profile.csv', 'r+') as fr:
			lines = fr.readlines()
			fr.seek(0)
			fr.truncate()
			j = 0
			for line in lines:
				line = line.rstrip()
				line = line + ';' + str(round(house.ReactiveConsumption['Total'][j])) + '\n'
				fr.write(line)
				j = j + 1	
	
	text = []
	text.append('def addHouse(node, coordx, coordy, phase, houseNum, control, masterController, cfg):')
	text.append('\timport triana')
	text.append('\tnode.setPosition(coordx, coordy)')

	text.append('\texchanger = node.newElement("TrianaThreephaseExchanger", "Exchanger"+str(houseNum))')
	text.append('\texchanger.set("PowerLimit", 230*60)')
	text.append('\texchanger.setPosition(coordx+75, coordy)')
	text.append('\ttriana.newConnection("TrianaEnergyStream", exchanger.Sum, node.ExchangerPort)')

	text.append('\tpool = node.newElement("TrianaPool", "Pool"+str(houseNum))')
	text.append('\tpool.setPosition(coordx+150, coordy)')

	text.append('\tif(phase == 1):')
	text.append('\t\ttriana.newConnection("TrianaEnergyStream", pool.Sum, exchanger.StreamPortL1)')
	text.append('\tif(phase == 2):')
	text.append('\t\ttriana.newConnection("TrianaEnergyStream", pool.Sum, exchanger.StreamPortL2)')
	text.append('\tif(phase == 3):')
	text.append('\t\ttriana.newConnection("TrianaEnergyStream", pool.Sum, exchanger.StreamPortL3)')

	text.append('\tload = node.newElement("TrianaUncontrollable", "Load"+str(houseNum))')
	text.append('\tload.set("ActivePowerProfile", "csv:../../'+config.trianaModelPath+config.folder+'/electricity_profile.csv,"+str(houseNum))') 		
	text.append('\tload.set("ReactivePowerProfile", "csv:../../'+config.trianaModelPath+config.folder+'/electricity_reactive_profile.csv,"+str(houseNum))') 
	text.append('\tload.set("LoadType", "Power")')
	text.append('\tload.set("TimeBase", '+str(config.timeBase)+')')
	text.append('\tload.setPosition(coordx+225, coordy)')
	text.append('\ttriana.newConnection("TrianaEnergyStream", load.Stream, pool.Stream)')

	text.append('\tif control:')
	text.append('\t\thouseController = node.newElement("TrianaGroupController", "HouseController"+str(houseNum))')
	text.append('\t\thouseController.set("PlanningHorizon", '+str(config.TrianaPlanning_Horizon)+')')
	text.append('\t\thouseController.set("PlanningInterval", '+str(config.TrianaPlanning_ReplanningInterval)+')')
	text.append('\t\thouseController.setPosition(coordx+75, coordy-75)')
	text.append('\t\thouseController.set("MaxPlanningIterations", cfg[\'HC_iters\'])')
	text.append('\t\thouseController.set("MinPlanningImprovement", cfg[\'HC_improvement\'])')
	if config.TrianaPlanning_LocalFlat:
		text.append('\t\thouseController.set("InitialPlanningStep", True)')
	else:
		text.append('\t\thouseController.set("InitialPlanningStep", False)')
		text.append('\t\thouseController.set("MinPlanningImprovement", '+ str(config.TrianaPlanning_MinImprovement)+')')
	text.append('\t\thouseController.set("TimeBase", '+str(config.timeBase)+')')
	text.append('\t\ttriana.newConnection("TrianaControlConnection", houseController.Parent, masterController[phase].Children)')

	text.append('\t\tucc = node.newElement("TrianaUncontrollableController", "LoadController"+str(houseNum))')
	text.append('\t\tucc.setPosition(coordx+300, coordy)')
	text.append('\t\tucc.set("TimeBase", '+str(config.timeBase)+')')
	text.append('\t\ttriana.newConnection("TrianaControlConnection", load.Control, ucc.Children)')
	text.append('\t\ttriana.newConnection("TrianaControlConnection", ucc.Parent, houseController.Children)')

	f = open(config.folder+'/House'+str(num)+'.py', 'w')
	for line in range(0, len(text)):
		f.write(text[line] + '\n')
	f.close()
	
	
	#Write all devices:
	for k, v, in house.Devices.items():
		house.Devices[k].writeDevice(num)
		
	
	
	#House devices	
	text = [] 
	if house.House.hasPV:
		text.append('\tpv = node.newElement("TrianaSolarPanel", "PV"+str(houseNum))')
		text.append('\tpv.set("IrradiationProfile", "csv:'+config.weather_irradiation+',0")')
		text.append('\tpv.set("TemperatureProfile", "csv:'+config.weather_temperature+',0")')
		text.append('\tpv.set("Area", '+str(house.House.pvArea)+')')
		text.append('\tpv.set("Longitude", 6.48)')
		text.append('\tpv.set("Latitude", 52.72)')
		text.append('\tpv.set("Elevation", '+str(house.House.pvElevation)+')')
		text.append('\tpv.set("Efficiency", '+str(house.House.pvEfficiency)+')')
		text.append('\tpv.set("TemperatureEfficiency", 0.3)')
		text.append('\tpv.set("TimeBaseDataset", 3600)')
		text.append('\tpv.set("LoadType", "Power")')
		text.append('\tpv.set("TimeBase", '+str(config.timeBase)+')')
		text.append('\tpv.set("TimeOffset", 0)')
		text.append('\tpv.setPosition(coordx+225, coordy+75)')
		text.append('\tpv.set("Azimuth",'+str(house.House.pvAzimuth)+')')
		text.append('\ttriana.newConnection("TrianaEnergyStream", pv.Stream, pool.Stream)')
		
		text.append('\tif control:')
		text.append('\t\tPVC=node.newElement("TrianaScalableController","PVController"+str(houseNum))')
		text.append('\t\tPVC.setPosition(coordx+225,coordy+150)')
		text.append('\t\tPVC.set("TimeBase", '+str(config.timeBase)+')')
		text.append('\t\ttriana.newConnection("TrianaControlConnection",pv.Control , PVC.Children)')
		text.append('\t\ttriana.newConnection("TrianaControlConnection",PVC.Parent,houseController.Children)')	
		
	if house.House.hasBattery:
		text.append('\tbattery=node.newElement("TrianaBuffer","Battery"+str(houseNum))')
		text.append('\tbattery.setPosition(coordx+75,coordy+75)')
		text.append('\tbattery.set("Capacity", '+str(house.House.batteryCapacity)+')')
		text.append('\tbattery.set("InitialSoC", '+str(round(house.House.batteryCapacity/2))+')')
		text.append('\tbattery.set("MaxPower", 3700)')
		text.append('\tbattery.set("MinPower", -3700)')
		text.append('\tbattery.set("TimeBase", '+str(config.timeBase)+')')
		text.append('\ttriana.newConnection("TrianaEnergyStream", battery.Stream, pool.Slack)')

		text.append('\tif control:')
		text.append('\t\tbatteryC=node.newElement("TrianaBufferController","BatteryController"+str(houseNum))')
		text.append('\t\tbatteryC.setPosition(coordx+75,coordy+150)')
		text.append('\t\tbatteryC.set("TimeBase", '+str(config.timeBase)+')')
		text.append('\t\tbatteryC.set("CostPrice", cfg[\'BAT_cost\'])')
		text.append('\t\tbatteryC.set("MinPlanningImprovement", cfg[\'BAT_improvement\'])')
		text.append('\t\tif cfg[\'BAT_readonly\'].count(houseNum) > 0:')
		text.append('\t\t\tbatteryC.set("ReadOnly", True)')
		text.append('\t\ttriana.newConnection("TrianaControlConnection",battery.Control,batteryC.Children)')
		text.append('\t\ttriana.newConnection("TrianaControlConnection",batteryC.Parent,houseController.Children)')
	
	f = open(config.folder+'/House'+str(num)+'.py', 'a')
	for line in range(0, len(text)):
		f.write(text[line] + '\n')
	f.close()
	
def writeDeviceBufferTimeshiftable(machine, hnum):
	text = []
	
	if machine.BufferCapacity > 0 and len(machine.StartTimes) > 0:
		text.append('\tmachine = node.newElement("TrianaBufferTimeShiftable", "ElectricalVehicle"+str(houseNum))')
		text.append('\tmachine.setPosition(coordx+150, coordy-75)')
		text.append('\tmachine.set("StartTimes", ['+profilegentools.createStringList(machine.StartTimes, None, 60)+'])')
		text.append('\tmachine.set("EndTimes", ['+profilegentools.createStringList(machine.EndTimes, machine.StartTimes, 60)+'])')
		text.append('\tmachine.set("PredictedStartTimes", ['+profilegentools.createStringList(machine.StartTimes, None, 60)+'])')
		text.append('\tmachine.set("PredictedEndTimes", ['+profilegentools.createStringList(machine.EndTimes, machine.StartTimes, 60)+'])')
		text.append('\tmachine.set("Capacity", '+ str(machine.BufferCapacity) +')')
		text.append('\tmachine.set("InitialSoC", '+ str(machine.BufferCapacity) +')')
		text.append('\tmachine.set("MinPower", 1380.0)')
		if machine.Consumption == 3700:
			machine.Consumption = 3680.0
			text.append('\tmachine.set("MaxPower", '+ str(machine.Consumption) +')')
			text.append('\tmachine.set("ChargingPowers", [1380.0, 1610.0, 1840.0, 2070.0, 2300.0, 2530.0, 2760.0, 2990.0, 3220.0, 3450.0, 3680.0] )')
		else:
			machine.Consumption = 7360.0
			text.append('\tmachine.set("MaxPower", '+ str(machine.Consumption) +')')
			text.append('\tmachine.set("ChargingPowers", [1380.0, 1610.0, 1840.0, 2070.0, 2300.0, 2530.0, 2760.0, 2990.0, 3220.0, 3450.0, 3680.0, 3910, 4140, 4370, 4600, 4830, 5060, 5290, 5520, 5750, 5980, 6210, 6440, 6670, 6900, 7130, 7360] )')
		text.append('\tmachine.set("SoCSetpoints", ['+profilegentools.createStringList(machine.Setpoint, None, 1, False)+'])')
		text.append('\tmachine.set("EnergyLoss", ['+profilegentools.createStringList(machine.EnergyLoss, None, 1, False)+'])')
		text.append('\tmachine.set("PredictedSoCSetpoints", ['+profilegentools.createStringList(machine.Setpoint, None, 1, False)+'])')
		text.append('\tmachine.set("PredictedEnergyLoss", ['+profilegentools.createStringList(machine.EnergyLoss, None, 1, False)+'])')
		text.append('\tmachine.set("Efficiency", 1.0)')
		text.append('\tmachine.set("TimeBase", '+str(config.timeBase)+')')
		text.append('\tmachine.set("LoadType", "Power")')
		text.append('\ttriana.newConnection("TrianaEnergyStream", pool.Stream, machine.Stream)')
		
		text.append('\tif control:')
		text.append('\t\tmachinec = node.newElement("TrianaBufferTimeShiftableController", "EVController"+str(houseNum))')
		text.append('\t\tmachinec.setPosition(coordx+150, coordy-150)')
		text.append('\t\tmachinec.set("TimeBase", '+str(config.timeBase)+')')
		text.append('\t\tmachinec.set("CostPrice", cfg[\'EV_cost\'])')
		text.append('\t\tmachinec.set("MinPlanningImprovement", cfg[\'EV_improvement\'])')
		text.append('\t\tif cfg[\'EV_readonly\'].count(houseNum) > 0:')
		text.append('\t\t\tmachinec.set("ReadOnly", True)')
		text.append('\t\ttriana.newConnection("TrianaControlConnection", machine.Control, machinec.Children)')
		text.append('\t\ttriana.newConnection("TrianaControlConnection", machinec.Parent, houseController.Children)')
		
		f = open(config.folder+'/House'+str(hnum)+'.py', 'a')
		for line in range(0, len(text)):
			f.write(text[line] + '\n')
		f.close()
		

def writeDeviceTimeshiftable(machine, hnum):
	text = []
	
	if len(machine.StartTimes) > 0:
		text.append('\tmachine = node.newElement("TrianaTimeShiftable")')
		text.append('\tmachine.setPosition(coordx+150, coordy+75)')
		if config.intervalLength  == 1:
			text.append('\tmachine.set("DemandProfile", ['+machine.LongProfile+'])')
		else:
			text.append('\tmachine.set("DemandProfile", ['+machine.ShortProfile+'])')
		text.append('\tmachine.set("StartTimes",  ['+profilegentools.createStringList(machine.StartTimes, None, 60)+'])')
		text.append('\tmachine.set("EndTimes",  ['+profilegentools.createStringList(machine.EndTimes, machine.StartTimes, 60)+'])')
		text.append('\tmachine.set("PredictedStartTimes",  ['+profilegentools.createStringList(machine.StartTimes, None, 60)+'])')
		text.append('\tmachine.set("PredictedEndTimes",  ['+profilegentools.createStringList(machine.EndTimes, machine.StartTimes, 60)+'])')
		text.append('\tmachine.set("LoadType", "Power")')
		text.append('\tmachine.set("Name", "'+machine.name+'"+str(houseNum))')
		text.append('\tmachine.set("TimeBase", '+str(config.timeBase)+')')
		text.append('\ttriana.newConnection("TrianaEnergyStream", pool.Stream, machine.Stream)')

		text.append('\tif control:')
		text.append('\t\ttsc = node.newElement("TrianaTimeShiftableController", "'+machine.name+'Controller"+str(houseNum))')
		text.append('\t\ttsc.setPosition(coordx+150, coordy+150)')
		text.append('\t\ttsc.set("TimeBase", '+str(config.timeBase)+')')
		if machine.name == "WashingMachine":
			text.append('\t\ttsc.set("CostPrice", cfg[\'WM_cost\'])')
			text.append('\t\ttsc.set("MinPlanningImprovement", cfg[\'WM_improvement\'])')
			text.append('\t\tif cfg[\'WM_readonly\'].count(houseNum) > 0:')
			text.append('\t\t\ttsc.set("ReadOnly", True)')
		else:
			text.append('\t\ttsc.set("CostPrice", cfg[\'DW_cost\'])')
			text.append('\t\ttsc.set("MinPlanningImprovement", cfg[\'DW_improvement\'])')
			text.append('\t\tif cfg[\'DW_readonly\'].count(houseNum) > 0:')
			text.append('\t\t\ttsc.set("ReadOnly", True)')
		text.append('\t\ttriana.newConnection("TrianaControlConnection", machine.Control, tsc.Children)')
		text.append('\t\ttriana.newConnection("TrianaControlConnection", tsc.Parent, houseController.Children)')

		f = open(config.folder+'/House'+str(hnum)+'.py', 'a')
		for line in range(0, len(text)):
			f.write(text[line] + '\n')
		f.close()
