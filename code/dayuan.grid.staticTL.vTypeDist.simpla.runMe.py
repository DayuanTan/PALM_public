
# @file    dayuan.grid.staticTL.runMe.py
# @author  Dayuan Tan
# @date    2020 05 24
# @version $Id$

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import xml.etree.ElementTree as ET


# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

    dayuanSUMOpath = os.path.join("/usr","local","Cellar","sumo","1.3.1","share","sumo","tools")
    sys.path.append(dayuanSUMOpath)
    print("PATH:",sys.path)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from datetime import datetime
from sumolib import checkBinary  
import traci  
import traci.constants as tc # used for subscription

import simpla # this is for platoon. 

def run():
    """execute the TraCI control loop"""
    step = 0
    
    #traci.trafficlight.setPhase("0", 2). N W S E are "0 1 2 3".

    #context subscription, get variables around a junction
    traci.junction.subscribeContext("C3", tc.CMD_GET_VEHICLE_VARIABLE, 50, [tc.VAR_SPEED, tc.VAR_WAITING_TIME, tc.VAR_LANE_ID, tc.VAR_SIGNALS])
    #Q: don't have a list of all varibales which can be subscribed.   

    #while traci.simulation.getTime() <209:#unit is s. Set a short time for testing
    while traci.simulation.getMinExpectedNumber() > 0:# run until all v have arrived
        traci.simulationStep() # forward one step

        allTLid = traci.trafficlight.getIDList() #all traffic lights id
        #print("len of allTLid:", len(allTLid)) #=30

        """
        for i_TLids in range(len(allTLid)):#py3 don't have xrange
            if (12 < i_TLids < 14) & (200 < traci.simulation.getTime() < 210.0):# just show partial since too many
                print("TL id:", allTLid[i_TLids])
                print("Phase:", traci.trafficlight.getPhase(allTLid[i_TLids]))
                #print(traci.trafficlight.getPhaseDuration(allTLid[i_TLids]))
                #print(traci.trafficlight.getPhaseName(allTLid[i_TLids]))
                #print(traci.trafficlight.getProgram(allTLid[i_TLids]))

                # show partial context subscription results
                contextSubscriptionResults = traci.junction.getContextSubscriptionResults("C3")
                print("contextSubscriptionResults:",contextSubscriptionResults)
                print("\n ------------ \n")
        """

        step += 1
    print("step: ", step)
    traci.close()
    sys.stdout.flush()

def calAvgWaitTime(tripinfo_output_filename):
    tree = ET.parse(tripinfo_output_filename) # get the file
    root = tree.getroot() # loc the root

    vCount = 0
    vWaitingTimeTotal = 0
    for tripinfo in root.findall('tripinfo'):
        vCount += 1
        vID = tripinfo.get('id')
        vType = tripinfo.get('vType')
        vDuration = tripinfo.get('duration')
        vRouteLength = tripinfo.get('routeLength')
        vWaitingTime = tripinfo.get('waitingTime')
        vWaitingCount = tripinfo.get('waitingCount')
        vWaitingTimeTotal += float(vWaitingTime)
        #print(vID)
        #print(vType)
        #print(vWaitingTime)

    CO_all = 0
    CO2_all = 0
    HC_all = 0
    PMx_all = 0
    NOx_all = 0
    fuel_all = 0
    eletricity_all = 0
    # for tripinfo in root.findall('tripinfo'):
    #     CO_all += float( tripinfo.find('emissions').get('CO_abs'))
    #     CO2_all += float( tripinfo.find('emissions').get('CO2_abs'))
    #     HC_all += float( tripinfo.find('emissions').get('HC_abs'))
    #     PMx_all += float( tripinfo.find('emissions').get('PMx_abs'))
    #     NOx_all += float( tripinfo.find('emissions').get('NOx_abs'))
    #     fuel_all += float( tripinfo.find('emissions').get('fuel_abs'))
    #     eletricity_all += float( tripinfo.find('emissions').get('electricity_abs'))


    vWaitingTimeAvg = vWaitingTimeTotal / vCount
    print("vWaitingTimeTotal:", vWaitingTimeTotal)
    print("vCount:", vCount)
    print("CO_all: ", CO_all )
    print("CO2_all: ", CO2_all )
    print("HC_all: ", HC_all )
    print("PMx_all: ", PMx_all )
    print("NOx_all: ", NOx_all )
    print("total_car_exhausts: ", CO_all+CO2_all+HC_all+PMx_all+NOx_all )
    print("fuel_all: ", fuel_all )
    print("eletricity_all: ", eletricity_all )
    return vWaitingTimeAvg
         


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    

    # datetime object containing current date and time
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")
    print("date and time =", dt_string)	


    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    tripinfo_output_filename = "output/tripinfo.grid.staticTL.vTypeDist.simpla" +dt_string+".xml"
    emission_output_filename = "output/emission.staticTL." +dt_string+".xml"
    traci.start([sumoBinary, "-c", "sumocfg_dayuan.grid.staticTL.vTypeDist.simpla.sumocfg",
                             "--tripinfo-output", tripinfo_output_filename,
                             "--emission-output", emission_output_filename])
    
    # import my platoon cfg after traci start
    simpla.load("simpla_configure/dayuan.platoon.cfg.xml")

    # implement my alg
    run()

    # calculate avg waiting time
    vWaitingTimeAvg = calAvgWaitTime(tripinfo_output_filename)
    print("vWaitingTimeAvg:", vWaitingTimeAvg)
    