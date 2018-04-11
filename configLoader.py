
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


import sys, getopt, importlib, random

# Default write into a new folder
folder = 'output/output/'

cfgOutputDir = 'output/output/'
outputFolder = cfgOutputDir
cfgFile = None

#Parse arguments
opts, args = getopt.getopt(sys.argv[1:],"c:o:f",["config=","output=", "force"])
for opt, arg in opts:
	if opt in ("-c", "--config"):
		cfgFile = arg
	elif opt in ("-o", "--output"):
		cfgOutputDir = 'output/'+arg+'/'

outputFolder = cfgOutputDir		
sys.path.insert(0, 'configs')
