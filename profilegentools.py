
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

    


import random

def gaussMinMax(mu, deviation):
	assert(deviation > 0)
	n = random.gauss(mu, round(deviation/3))
	return round(max(min((mu+deviation), n), mu-deviation))

def roundToTimeBase(time, timeBase=60):
	return round(time/timeBase) * timeBase

def roundList(listIn, rate):
	result = []
	for i in range(0, len(listIn)):
		if(listIn[i]%rate == 0): 
			result.append(listIn[i])
		else:
			result.append(listIn[i]+(rate-(listIn[i]%rate)))
	return result


def createStringList(listIn, compare=None, multiplier=1, rescale=True):
	if compare == None:
		out = str(listIn[0]*multiplier)
		for i in range(1, len(listIn)):
			out = out + ',' + str(listIn[i]*multiplier)
		return out
	
	#Check if the deadline is before the next time
	else:
		first = True
		out = ''
		assert(len(listIn) == len(compare))
		for i in range(0, len(listIn)-1):
			if(listIn[i] < (compare[i+1]*multiplier-60)):
				if first:
					out = str(listIn[i]*multiplier)
					first = False
				else:
					out = out + ',' + str(listIn[i]*multiplier)
			else:
				if first:
					out = str(compare[i+1]*multiplier-60)
					first = False
				else:
					out = out + ',' + str(compare[i+1]*multiplier-60)
		if first:
			out = str(listIn[len(listIn)-1]*multiplier)
		else:
			out = out + ',' + str(listIn[len(listIn)-1]*multiplier)
		return out

	
def resample(listIn, rate):
	sample = 0
	idx = 0
	result = []
	total = 0
	while(idx < len(listIn)):
		if(idx % rate == (rate - 1)):
			#reset
			result.append(round(total/rate))
			total = 0			
		total = total + listIn[idx]	
		idx += 1
	return result
