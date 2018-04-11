
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
import math, datetime
import profilegentools
import linecache

class Device:
	def __init__(self, consumption = 0):
		self.generate(consumption)
		
	def generate(self, consumption = 0):
		self.State = 0
		self.Consumption = consumption
		
	def writeDevice(self, hnum):
		pass

class TimeShiftableDevice(Device):
	def __init__(self, consumption = 0):
		self.generate(consumption)
		self.StartTimes = []
		self.EndTimes = []
		
	def generate(self, consumption = 0):
		self.State = 0
		self.Consumption = consumption		

class BufferTimeshiftableDevice(TimeShiftableDevice):
	def __init__(self, consumption = 0):
		self.generate(consumption)
		self.BufferCapacity = 0
		self.Consumption = consumption
		self.Setpoint = []
		self.EnergyLoss = []
		self.StartTimes = []
		self.EndTimes = []
		TimeShiftableDevice
		
	def generate(self, consumption = 0):
		self.State = 0
		self.Consumption = consumption


		
class DeviceFridge(Device):
	def generate(self, consumption):
		self.Runtime = profilegentools.gaussMinMax(15, 5)
		self.Offtime = profilegentools.gaussMinMax(40, 10)
		self.Consumption = consumption
		self.State = 0
		
		self.RuntimeCycle = self.Runtime
		self.OfftimeCycle = self.Offtime
		self.CycleProgress = random.randint(0,self.Runtime+self.Offtime)
		if(self.CycleProgress < (self.Runtime+self.Offtime)):
			self.State = 1
	
	def __init__(self, consumption):
		self.generate(consumption)
		
	def simulate(self, timeintervals):
		DeviceProfile = [0] * timeintervals
		for t in range(0, timeintervals):
			#simulate this thing
			self.CycleProgress = self.CycleProgress + 1
			if self.CycleProgress == (self.Runtime+self.Offtime):
				self.State = 1
				self.RuntimeCycle = random.randint(self.Runtime-2, self.Runtime+2)
				self.OfftimeCycle = random.randint(self.Runtime-2, self.Runtime+2)
				self.CycleProgress = 0
			elif(self.CycleProgress == self.Runtime):
				#Turn it Off
				self.State = 0
			DeviceProfile[t] = self.State * self.Consumption
		return DeviceProfile
		
		
		
class DeviceKettle(Device):
	def simulate(self, timeintervals, occupancy):
		DeviceProfile = [0] * timeintervals
		
		m = 0
		while occupancy[m] == 0:
			m += 1
		m = m + random.randint(10,20)
		if(random.randint(1,10)<7):
			for i in range(m, m+occupancy[m]):
				DeviceProfile[i] = self.Consumption
			
		#12:00
		m = random.randint(12*60, 14*60)
		if occupancy[m] > 0 and (random.randint(1,10)<7):
			for i in range(m, m+occupancy[m]):
				DeviceProfile[i] = self.Consumption
				
		#afternoon
		m = random.randint(14*60, 17*60)
		if occupancy[m] > 0 and (random.randint(1,10)<7):
			for i in range(m, m+occupancy[m]):
				DeviceProfile[i] = self.Consumption		
		
		#evening
		m = random.randint(20*60, 21*60)
		if occupancy[m] > 0 and (random.randint(1,10)<7):
			for i in range(m, m+occupancy[m]):
				DeviceProfile[i] = self.Consumption
				
		return DeviceProfile
	
	
class DeviceLighting(Device):
	def simulate(self, timeintervals, occupancy, timestamp):
		sun = config.location.sun(date=datetime.date.fromtimestamp(timestamp), local=True)
		LightingOnProfile = [1] * 1440
		LightingProfile = [0] * 1440
		for m in range((sun['sunrise'].hour*60+sun['sunrise'].minute)+random.randint(-10,40), \
			(sun['sunset'].hour*60+sun['sunset'].minute)-random.randint(-10,40)):					# Lighting quite well does match sunrise and sunset. Cloud data can enhance this. based on own experiences :)
			LightingOnProfile[m] = 0
				
		for m in range(0, 1440):
			if (occupancy[m] == 0 or LightingOnProfile[m] == 0):
				LightingProfile[m] = 0
			else:
				LightingProfile[m] = LightingOnProfile[m] + ((occupancy[m] - 1)*0.2)
		return LightingProfile		
	
	
class DeviceElectronics(Device):
	def simulate(self, timeintervals, occupancy, occupancyPerson):
		ElectronicsProfile = [0] * 1440
		for p in range(0, len(occupancyPerson)):
			consuming = 0
			for m in range(1,1440):
				if(occupancyPerson[p][m] == 1 and occupancyPerson[p][m-1] == 0):
					#Person is activated, do something with it
					#treat the morning differently:
					if m < 13*60:
						if(random.random() < 0.8-(0.2*(occupancy[m]-1))):
							consuming = (random.randint(7,10) / 10)
							ElectronicsProfile[m] = ElectronicsProfile[m] + consuming
					else:	
						if(random.random() < 0.8-(0.125*(occupancy[m]-1))):
							consuming = (random.randint(8,12) / 10)
							ElectronicsProfile[m] = ElectronicsProfile[m] + consuming
				elif(occupancyPerson[p][m] == 0 and occupancyPerson[p][m-1] == 1 and consuming > 0):
					consuming = 0
				ElectronicsProfile[m] = ElectronicsProfile[m] + consuming		
				
		return ElectronicsProfile


class DeviceCooking(Device):
	def simulate(self, timeintervals, occupancy, persons, startCooking, cookingDuration, hasInductionCooking, ventilation):
		CookingProfile = [0] * 1440
		cookingDuration = random.randint(20,40)
		
		
		#Now see what well cook: Microwave, Oven or Stove (or Stove and Oven). Lets considder that the fryer will use approx the same amount of energy
		#Depends on the size of the family, a math.single person household will faster opt for the microwave ;-)
		CookingType = random.randint(0,10)
		if CookingType == 10:			
			cookingDuration = random.randint(25,40)
			randomCycle = random.randint(4,8)
			for m in range(startCooking, startCooking+cookingDuration):
				if m < 10+startCooking:
					CookingProfile[m] += config.ConsumptionOven
				elif m%(randomCycle*2) < randomCycle:
					CookingProfile[m] += config.ConsumptionOven
					
			cookingDuration = random.randint(35,45)
			for m in range(startCooking, startCooking+cookingDuration):
				ventilation.VentilationProfile[m] += ventilation.CookingAirFlow
				ventilation.VentilationProfile[m] = min(ventilation.VentilationProfile[m], ventilation.MaxAirflow)
				# CookingProfile[m] += config.ConsumptionStoveVentilation
				
			if(hasInductionCooking):
				inductionRatio = random.randint(3,6)
				for m in range(startCooking, startCooking+cookingDuration):
					if m < 6+startCooking:
						CookingProfile[m] += config.ConsumptionInductionStove
					else:
						CookingProfile[m] += round(config.ConsumptionInductionStove*(inductionRatio/10))
		
		elif CookingType == 9:
			#Oven 
			randomCycle = random.randint(4,8)
			cookingDuration = random.randint(25,40)
			for m in range(startCooking, startCooking+cookingDuration):
				if m < 10+startCooking:
					CookingProfile[m] += config.ConsumptionOven
				elif m%(randomCycle*2) < randomCycle:
					CookingProfile[m] += config.ConsumptionOven
			
			if random.random()<0.2:
				cookingDuration = random.randint(4,6)
				randomOffset = random.randint(5,15)
				for m in range(startCooking+randomOffset, startCooking+cookingDuration):
					CookingProfile[m] += config.ConsumptionMicroWave
		
		elif((CookingType == 8) or (len(persons) == 2 and CookingType > 6) or (len(persons) == 1 and CookingType > 5)):
			#Microwave
			cookingDuration = random.randint(4,6)
			for m in range(startCooking, startCooking+cookingDuration):
				CookingProfile[m] += config.ConsumptionMicroWave
		
		else:
		#Stove
			cookingDuration = random.randint(35,45)
			for m in range(startCooking, startCooking+cookingDuration):
				ventilation.VentilationProfile[m] += ventilation.CookingAirFlow
				ventilation.VentilationProfile[m] = min(ventilation.VentilationProfile[m], ventilation.MaxAirflow)
				# CookingProfile[m] += config.ConsumptionStoveVentilation
			
			if random.random()<0.3:
				cookingDuration = random.randint(4,6)
				randomOffset = random.randint(5,15)
				for m in range(startCooking+randomOffset, startCooking+cookingDuration):
					CookingProfile[m] += config.ConsumptionMicroWave
					
			if(hasInductionCooking):
				inductionRatio = random.randint(3,6)
				
				for m in range(startCooking, startCooking+cookingDuration):
					if m < 6+startCooking:
						CookingProfile[m] += config.ConsumptionInductionStove
					else:
						CookingProfile[m] += round(config.ConsumptionInductionStove*(inductionRatio/10))
				
			if random.random() < 0.2:
				inductionRatio = random.randint(3,6)
				for m in range(startCooking+random.randint(6,12), startCooking+cookingDuration):
					if m < 18+startCooking:
						CookingProfile[m] += config.ConsumptionInductionStove
					else:
						CookingProfile[m] += round(config.ConsumptionInductionStove*(inductionRatio/10))	
		
		return CookingProfile



class DeviceVentilation(Device):
	# Determine the power consumption of the ventilationsystem baased on the requested air ventilation. NOTE using pointers here
	def simulate(self, timeintervals, ventilation):
		VentilationProfile = []
		for i in range(0, len(ventilation.VentilationProfile)):
			VentilationProfile.append(int((ventilation.VentilationProfile[i]/ventilation.MaxAirflow) * self.Consumption))

		return VentilationProfile


class DeviceIroning(Device):
	def simulate(self, timeintervals, occupancy, numPersons):
		IroningProfile = [0] * 1440
		ironingDuration = random.randint(10,15) + numPersons*7
		startIroning = 0
		count = 0
		while occupancy[startIroning] == 0 and count != 50:
			count += 1
			if(occupancy[16*60] > 0):
				startIroning = random.randint(10*60, 17*60)
			else:
				startIroning = random.randint(20*60, 22*60)
		if count != 50:
			for m in range(startIroning, startIroning+ironingDuration):
				if m < 6+startIroning:
					IroningProfile[m] += self.Consumption
				elif m%4 < 2:
					IroningProfile[m] += self.Consumption
		return IroningProfile
		
class DeviceVacuumcleaner(Device):
	def simulate(self, timeintervals, occupancy, numPersons):
		VacuumProfile = [0] * 1440
		vacuumDuration = random.randint(12,20) + numPersons*2
		startVacuum = 0
		count = 0
		while occupancy[startVacuum] == 0 and count != 50:
			count += 1
			if(occupancy[16*60] > 0):
				startVacuum = random.randint(10*60, 17*60)
			else:
				startVacuum = random.randint(20*60, 22*60)
		if count != 50:
			for m in range(startVacuum, startVacuum+vacuumDuration):
				VacuumProfile[m] += self.Consumption
		return VacuumProfile
	
	
class DeviceSolarPanel(Device):	
	def simulate(self, startday, timeintervals, pvArea, pvEfficiency, pvAzimuth, pvElevation):
		pvProfile = []

		time = startday*24*60*60
		while(time < (startday*24*60*60)+timeintervals*60):
			modeltime = int(time - (time % config.weather_timebaseDataset) + int(config.weather_timebaseDataset / 2))

			d = datetime.datetime.utcfromtimestamp(1388534400 + modeltime)
			elevation = config.location.solar_elevation(d)
			azimuth = config.location.solar_azimuth(d)
			zenith = config.location.solar_zenith(d)

			index = int(math.floor(modeltime/config.weather_timebaseDataset))
			index = max(index, 0)
			try:
				irradiation = float(linecache.getline(config.weather_irradiation, index+1))
			except:
				print("An error occurred reading the solar irradiation file. Make sure that the file is correct (e.g. only contains numbers), is long enough (make sure that it has a bit more data than the actual simulation. And, make sure that the file exists!")
				exit()

			GHI = ( irradiation * 10000 ) / float(config.weather_timebaseDataset)

			# Calculate diffused light

			# Adapted from:
			# https://github.com/jgoizueta/solar/blob/master/lib/solar/radiation.rb
			Gmax = 1367 * math.sin(math.radians(elevation))

			# Determine the clearness index
			clearnessIndex = 0.0
			if Gmax > 0.0:
				clearnessIndex = GHI / Gmax

			# Calculate the diffuse fraction
			# Depends on clearness index and elevation
			# Calculated using this method:
			# 1982 Erbs, Klein, Duffie
			diffuseFraction = 0.165
			if clearnessIndex <= 0.0001:
				diffuseFraction = 0.0
			elif clearnessIndex <= 0.22:
				diffuseFraction = (1.0-0.09*clearnessIndex)
			elif clearnessIndex<= 0.8:
				diffuseFraction = ( 0.9511-0.1604*clearnessIndex + \
							   4.388 * math.pow(clearnessIndex, 2) - \
							   16.638 * math.pow(clearnessIndex, 3) + \
							   12.336 * (math.pow(clearnessIndex, 4)) )

			# irradiance based on this fraction
			DHI =  diffuseFraction * GHI # Diffuse Horizontal Irradiance

			# Beam radiation
			irradiationBeam = GHI - DHI

			# And now calculate DNI based on the elevation of the sun
			# Using this relation:	GHI = DHI + DNI*cos(solar zenith)
			if elevation > 1 and math.sin(math.radians(elevation)) > 0.25:
				DNI = min(1367.0, ( irradiationBeam * 1 / math.sin(math.radians(elevation)) ) )
				# Avoid gigantic overshoots using the minimum here.
			elif elevation > 0 and math.sin(math.radians(elevation)) <= 0.2:
				# Avoiding weir corner case behaviour
				DNI = min(2*irradiationBeam, ( irradiationBeam * 1 / math.sin(math.radians(elevation)) ) )
			else:
				DNI = 0.0

			# Now calculate the energy falling on a plane
			# Based on the research by Marius Groen at Liandon
			# Improvement of the Liandon EC Cablepooling Model (Public Version)
			# Marius Groen

			if GHI < 0.001 or elevation <= 1:
				pvProfile.append(0)	# No power (significant) irradiation, avoid division by 0.
			else:
				# Calculate Incidence Angle (2.3) (theta_i)
				planeIncidence = math.degrees( math.acos( \
											math.cos(math.radians(zenith)) * math.cos(math.radians(pvElevation)) + \
											( math.sin(math.radians(zenith)) * math.sin(math.radians(pvElevation)) * \
											  math.cos(math.radians(azimuth - pvAzimuth))	) \
											) )

				# Calculate Gdir (2.2)
				Gdir = DNI * math.cos(math.radians(planeIncidence))

				# Calculate the diffuse irradiance (Gdfs)
				# First (2.5)
				factorF = 1 - math.pow( (DHI / GHI) , 2)

				# Now (2.4)
				Gdfs = DHI * 	( \
								( ( 1 + math.cos(math.radians(pvElevation))) / 2.0 ) * \
								( 1 + factorF * math.pow(math.sin(math.radians(pvElevation / 2.0)), 3) ) * \
								( 1 + factorF * math.pow(math.cos(math.radians(planeIncidence)), 2) * math.pow(math.sin(math.radians(zenith)), 3) ) \
								)

				# Ground reflected Irradiance Gref ( 2.6)
				Gref = GHI * 0.2 * ( (1 - math.cos(math.radians(pvElevation))) / 2.0 )

				# Now according to 2.1 we can add these and return out results
				total = max(0.0, Gdir + Gdfs + Gref)

				pvProfile.append(-1 * total * (pvEfficiency/100.0) * pvArea)
			# Increment time
			time = time + 60

		return pvProfile
		
	
class DeviceWashingMachine(TimeShiftableDevice):
	def simulate(self, timeintervals, day, occupancy, washingMoment):
		washingtimeintervals = washingMoment-30 + random.randint(0,59)
		if(washingMoment < 0):
			washingMoment = random.randint(20*60,(22*60-1))
		if((washingtimeintervals < (22*60)) or (occupancy[washingtimeintervals] < 1)):
			for i in range(washingtimeintervals, 1440):
				#Nobody is home, use the next possible moment
				if occupancy[i] > 0:
					washingtimeintervals = i
					break
			
		#Starttimeintervals:
		if(len(self.EndTimes) > 0):
			if((washingtimeintervals + 1440*(day)) > self.EndTimes[len(self.EndTimes)-1]):
				self.StartTimes.append(washingtimeintervals + (1440*(day)))
			else:
				self.StartTimes.append(self.EndTimes[len(self.EndTimes)-1]+60)
				washingtimeintervals = (self.EndTimes[len(self.EndTimes)-1]%1440)+60
		else:
			self.StartTimes.append(washingtimeintervals + (1440*(day)))
			
		if washingtimeintervals < 4*60:
			self.EndTimes.append(1440*(day) + random.randint(6.5*60,7.5*60))
		elif washingtimeintervals < 11*60:
			self.EndTimes.append(1440*(day) + random.randint(14*60,17*60))
		elif washingtimeintervals < 17*60:
			self.EndTimes.append(1440*(day) + random.randint(20*60,22*60))
		elif washingtimeintervals < 20*60:
			self.EndTimes.append(1440*(day) + random.randint(22*60,23*60))
		else:
			self.EndTimes.append(1440*(day+1) + random.randint(6.5*60,7.5*60))

		#check for overlap on endTimes:
		if self.EndTimes[len(self.EndTimes)-1] < self.StartTimes[len(self.StartTimes)-1] + 90:
			self.EndTimes.pop()
			self.StartTimes.pop()	
			
	def generate(self, consumption = 0):
		self.LongProfile = 'complex(66.229735, 77.4311402954),complex(119.35574, 409.21968),complex(162.44595, 516.545199388),complex(154.744551, 510.671236335),complex(177.089979, 584.413201848),complex(150.90621, 479.851164854),complex(170.08704, 540.84231703),complex(134.23536, 460.23552),complex(331.837935, 783.490514121),complex(2013.922272, 587.393996),complex(2032.267584, 592.744712),complex(2004.263808, 584.576944),complex(2023.32672, 590.13696),complex(2041.49376, 595.43568),complex(2012.8128, 587.0704),complex(2040.140352, 595.040936),complex(1998.124032, 582.786176),complex(2023.459776, 590.175768),complex(1995.309312, 581.965216),complex(2028.096576, 591.528168),complex(1996.161024, 582.213632),complex(552.525687, 931.898925115),complex(147.718924, 487.486021715),complex(137.541888, 490.4949133),complex(155.996288, 534.844416),complex(130.246299, 464.477753392),complex(168.173568, 497.908089133),complex(106.77933, 380.79103735),complex(94.445568, 323.813376),complex(130.56572, 317.819806804),complex(121.9515, 211.226194059),complex(161.905679, 360.175184866),complex(176.990625, 584.085324519),complex(146.33332, 501.71424),complex(173.06086, 593.35152),complex(145.07046, 517.342925379),complex(188.764668, 522.114985698),complex(88.4058, 342.394191108),complex(117.010432, 346.43042482),complex(173.787341, 326.374998375),complex(135.315969, 185.177207573),complex(164.55528, 413.181298415),complex(150.382568, 515.597376),complex(151.517898, 540.335452156),complex(154.275128, 509.122097304),complex(142.072704, 506.652479794),complex(171.58086, 490.815333752),complex(99.13293, 368.167736052),complex(94.5507, 366.193286472),complex(106.020684, 378.085592416),complex(194.79336, 356.012659157),complex(239.327564, 302.865870739),complex(152.75808, 209.046388964),complex(218.58576, 486.26562702),complex(207.109793, 683.481346289),complex(169.5456, 581.2992),complex(215.87571, 712.409677807),complex(186.858018, 573.073382584),complex(199.81808, 534.79864699),complex(108.676568, 403.611655607),complex(99.930348, 356.366544701),complex(151.759998, 358.315027653),complex(286.652289, 300.697988258),complex(292.921008, 266.244164873),complex(300.5829, 265.089200586),complex(296.20425, 261.22759426),complex(195.74251, 216.883021899),complex(100.34136, 260.038063655),complex(312.36975, 275.4842252),complex(287.90921, 261.688800332),complex(85.442292, 140.349851956),complex(44.8647, 109.208529515)'
		self.name = "WashingMachine"
			
	def writeDevice(self, hnum):
		config.writer.writeDeviceTimeshiftable(self, hnum)
		
			
class DeviceDishwasher(TimeShiftableDevice):
	def simulate(self, timeintervals, day, occupancy, washingMoment):
		dishwashtimeintervals = washingMoment-30 + random.randint(0,59)
		if(washingMoment < 0):
			dishwashtimeintervals = random.randint(20*60,23*60)
		if((dishwashtimeintervals < (22*60)) or (occupancy[dishwashtimeintervals] < 1)):
			for i in range(dishwashtimeintervals, 1440):
				#Nobody is home, use the next possible moment
				if occupancy[i] > 0:
					dishwashtimeintervals = i
					break
						
		#Starttimeintervals:
		if(len(self.EndTimes) > 0):
			if((dishwashtimeintervals + (1440*(day))) > self.EndTimes[len(self.EndTimes)-1]):
				self.StartTimes.append(dishwashtimeintervals + (1440*(day)))
			else:
				self.StartTimes.append(self.EndTimes[len(self.EndTimes)-1]+60)
				dishwashtimeintervals = (self.EndTimes[len(self.EndTimes)-1]%1440)+60
		else:
			self.StartTimes.append(dishwashtimeintervals + (1440*(day)))
	
		if dishwashtimeintervals < 4*60:
			self.EndTimes.append(1440*(day) + random.randint(6*60,7.60))
		elif dishwashtimeintervals < 13*60:
			self.EndTimes.append(1440*(day) + random.randint(17*60,18*60))
		elif dishwashtimeintervals < 19.5*60:
			self.EndTimes.append(1440*(day) + random.randint(22*60,23*60))
		else:
			self.EndTimes.append(1440*(day+1) + random.randint(6*60,7*60))
			
		#check for overlap on endTimes:
		if self.EndTimes[len(self.EndTimes)-1] < self.StartTimes[len(self.StartTimes)-1] + 2*60:
			self.EndTimes.pop()
			self.StartTimes.pop()
			
	def generate(self, consumption = 0):
		self.LongProfile = 'complex(2.343792, 9.91720178381),complex(0.705584, 8.79153133754),complex(0.078676, 7.86720661017),complex(0.078744, 7.87400627016),complex(0.078948, 7.89440525013),complex(0.079152, 7.91480423011),complex(0.079016, 7.90120491012),complex(0.078812, 7.88080593015),complex(0.941108, 3.10574286964),complex(10.449, 18.0981988883),complex(4.523148, 1.78766247656),complex(34.157214, 15.5624864632),complex(155.116416, 70.6731270362),complex(158.38641, 72.1629803176),complex(158.790988, 67.6446776265),complex(158.318433, 72.1320090814),complex(158.654276, 67.5864385584),complex(131.583375, 109.033724507),complex(13.91745, 13.0299198193),complex(4.489968, 1.91271835851),complex(1693.082112, 669.148867416),complex(3137.819256, 447.115028245),complex(3107.713851, 442.825240368),complex(3120.197256, 444.604029241),complex(3123.464652, 445.069607955),complex(3114.653256, 443.814052026),complex(3121.27497, 444.757595169),complex(3116.305863, 444.04953577),complex(3106.801566, 442.695246796),complex(3117.703743, 444.248722882),complex(3118.851648, 444.412290486),complex(3110.016195, 443.15330662),complex(3104.806122, 442.410911425),complex(1148.154728, 416.724520071),complex(166.342624, 70.8616610914),complex(161.205252, 68.6731497838),complex(160.049824, 68.1809395169),complex(158.772588, 67.6368392593),complex(158.208076, 67.3963581543),complex(157.926096, 67.2762351774),complex(157.01364, 66.8875305491),complex(112.30272, 108.243298437),complex(11.65632, 9.35164905552),complex(17.569056, 18.4299236306),complex(4.947208, 2.10750178285),complex(4.724016, 2.012422389),complex(143.12025, 65.2075123351),complex(161.129536, 68.6408949029),complex(160.671915, 63.501604078),complex(23.764224, 12.8265693277),complex(136.853808, 62.352437012),complex(159.11184, 62.8850229849),complex(159.464682, 63.0244750664),complex(159.04302, 62.8578235805),complex(36.68544, 55.7061505818),complex(9.767628, 7.07164059421),complex(4.902772, 2.08857212612),complex(2239.315008, 885.033921728),complex(3116.846106, 444.126516228),complex(3111.034014, 443.298337972),complex(3118.112712, 444.306997808),complex(3111.809778, 443.408878355),complex(3113.442189, 443.641484325),complex(3110.529708, 443.226478259),complex(3104.676432, 442.392431601),complex(3101.093424, 441.881880613),complex(3121.076178, 444.729268843),complex(1221.232208, 443.248103556),complex(159.964185, 63.2218912841),complex(2663.07828, 966.568347525),complex(272.524675, 436.038267268),complex(7.76832, 5.82624),complex(3.258112, 1.75854256572),complex(3.299408, 1.69033685682),complex(3.295136, 1.68814824631),complex(3.256704, 1.75778260783),complex(3.258112, 1.75854256572),complex(3.262336, 1.7608224394),complex(2224.648744, 807.439674778),complex(367.142872, 587.426961418),complex(4.711025, 11.8288968082)'
		self.name = "Dishwasher"
			
	def writeDevice(self, hnum):
		config.writer.writeDeviceTimeshiftable(self, hnum)	
			
class DeviceElectricalVehicle(BufferTimeshiftableDevice):
	def simulate(self, day, person, eventStart, eventDuration):
		dayOfWeek = day%7
		if dayOfWeek in person.Workdays:		
			self.Setpoint.append(self.BufferCapacity)
			energyLoss = round(person.DistanceToWork / (5+(random.randint(0,100)/100))) * 1000 * 2 #Round trip
		
			if(random.randint(1,10) < 3):
				#add a random trip:
				self.StartTimes.append(1440*day + person.WorkdayArrival_Avg + random.randint(150,210))
				energyLoss = energyLoss + round(random.randint(5,20) / (5+(random.randint(0,100)/100))) * 1000 * 2
			else:
				self.StartTimes.append(1440*day + person.WorkdayArrival_Avg + random.randint(0,30))

			energyLoss = round(energyLoss + (energyLoss * 0.166 * ((math.cos((day/365) * 2 * math.pi ))))) #approx 25% less range in winter! Not considering heating here
						
			#print(person.DistanceToWork)
			if(energyLoss > self.BufferCapacity):
				energyLoss = self.BufferCapacity
			self.EnergyLoss.append(energyLoss) #Approx 5.5km/kWh for current (PH)EVs, positive ;-)
				
			self.EndTimes.append(1440*(day+1) + person.WorkdayLeave_Avg - 30)
						
					
		elif eventDuration > 0 and eventStart > 8*60 and random.randint(1,10)<8:
			#Family event, lets use it!
				
			#first make sure the car is filled:
			if(len(self.EndTimes) > 0):
				self.EndTimes.pop() #remove the dummy entry
				self.EndTimes.append(1440*(day) + eventStart - random.randint(30,60))
			
			self.Setpoint.append(self.BufferCapacity)
			energyLoss = round(random.randint(20,150) / (5+(random.randint(0,100)/100))) * 1000 * 2 #Round trip
			energyLoss = round(energyLoss + (energyLoss * 0.166 * ((math.cos((day/365) * 2 * math.pi ))))) #approx 25% less range in winter! Not considering heating here
			
			self.StartTimes.append(1440*day + eventStart+eventDuration + random.randint(0,60))
			
			#print(person.DistanceToWork)
			if(energyLoss > self.BufferCapacity):
				energyLoss = self.BufferCapacity
			self.EnergyLoss.append(energyLoss) #Approx 5.5km/kWh for current (PH)EVs
			
			self.EndTimes.append(1440*(day+1) + person.WorkdayLeave_Avg - 30)
				
		if len(self.EndTimes) > 0 and len(self.StartTimes) > 0:		
			assert(self.EndTimes[-1] > 	(self.StartTimes[-1]))
				
	def writeDevice(self, hnum):
		config.writer.writeDeviceBufferTimeshiftable(self, hnum)	
		

