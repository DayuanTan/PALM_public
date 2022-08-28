
# @file    dayuan.grid.myTL.runMe.py
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
import operator  # get max value of a dict
import math # sqrt()

# Log System:
# Choose keywords from following to customize the log printing.
# { core, 2connectedEdges, 3throughput, 3throughputAll, 3throughputC2, 4prepareFlowSouTgtDataStructure, 4prepareNxVDataStructure, 4NPV_vehivleInOutEdges, 4NPVresult, 5NDV, 6AWT, 7getTLneighborTLs, 7flowSouTgt_ofAllTLs, 7getNEV, 8fourRatios, newTL, helper , halfcycle}
comments = {}
# comments = {"core", "halfcycle"}#, "helper2", "helper"}
# comments = {"core", "newTL", "halfcycle", "greenLightEndsDivider", "helper4"}
# comments = {"core", "2connectedEdges", "3throughput", "3throughputAll", "3throughputC2", "4prepareFlowSouTgtDataStructure", "4prepareNxVDataStructure", "4NPV_vehivleInOutEdges", "4NPVresult", "5NDV", "6AWT", "7getNEV", "8fourRatios", "newTL", "helper", "halfcycle"}

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

from sumolib import net # get junction's nearby edges, Step 2
net_xml = net.readNet('netfiles/dayuan.grid.1.net.xml')

# LANE_NUMBERS_PER_EDGE = 2
NS_EDGE_LENGTH = 129.2
WE_EDGE_LENGTH = 179.2
MARGIN_EDGE_LENGTH = 9.6
TL_WIDTH = 20.8 #150-129.2=200-179.2=20.8  
TL_WIDTH_HALF = 10.4
AVG_V_LENGTH_PROBABILITY = 5.513 #(4.5*0.4+14.63*0.05+4.5*0.045)*2+4.5*0.01 = 5.513


# to delete 
# Solve the SUMO's original Edges and Routes data structure conflict problem.
# Should only need for my grid road network. 
def helper_nearbyEdgesGetIDs(incoming, outgoing, edges):
    #Routes example: The vehicle  1 's whole route (all edges):  ('bottom5F0', 'F0F1', 'F0F1.480.00', 'F1F2', 'F1F2.480.00', 'F2E2', 'F2E2.580.00', 'E2D2', 'E2D2.580.00', 'D2C2', 'D2C2.580.00', 'C2B2', 'C2B2.580.00', 'B2A2', 'B2A2.580.00', 'A2left2')
    #Edges example:  outgoingEdges: [<edge id="F0E0" from="F0" to="F0E0.580.00"/>, <edge id="F0F1" from="F0" to="F0F1.480.00"/>, <edge id="F0bottom5" from="F0" to="bottom5"/>, <edge id="F0right0" from="F0" to="right0"/>]
    #Edges example: incomingEdges: [<edge id="E0F0.580.00" from="E0F0.580.00" to="F0"/>, <edge id="F1F0.480.00" from="F1F0.480.00" to="F0"/>, <edge id="bottom5F0" from="bottom5" to="F0"/>, <edge id="right0F0" from="right0" to="F0"/>]
    #So for incomding edge "edge id="bottom5F0" from="bottom5" to="F0"" we want bottom5F0 as ID. (incomding edge)
    #for outgoing edge "edge id="F0bottom5" from="F0" to="bottom5"" we want F0bottom5 as ID. (outgoing edge)
    if incoming:
        inEdgeID = edges.getFromNode().getID()
        if ("bottom" in inEdgeID) | ("top" in inEdgeID) | ("left" in inEdgeID) | ("right" in inEdgeID):
            inEdgeID = edges.getID()
            return inEdgeID
        else: 
            return inEdgeID
    elif outgoing:
        outEdgeID = edges.getToNode().getID()
        if ("bottom" in outEdgeID) | ("top" in outEdgeID) | ("left" in outEdgeID) | ("right" in outEdgeID):
            outEdgeID = edges.getID()
            return outEdgeID
        else:
            return outEdgeID

#getControlledLinks:  [[('C3C2_0', 'C2B2_0', ':C2_0_0')], [('C3C2_0', 'C2C1_0', ':C2_1_0')], [('C3C2_1', 'C2C1_1', ':C2_1_1')], [('C3C2_1', 'C2D2_1', ':C2_3_0')], [('C3C2_1', 'C2C3_1', ':C2_4_0')], [('D2C2_0', 'C2C3_0', ':C2_5_0')], [('D2C2_0', 'C2B2_0', ':C2_6_0')], [('D2C2_1', 'C2B2_1', ':C2_6_1')], [('D2C2_1', 'C2C1_1', ':C2_8_0')], [('D2C2_1', 'C2D2_1', ':C2_9_0')], [('C1C2_0', 'C2D2_0', ':C2_10_0')], [('C1C2_0', 'C2C3_0', ':C2_11_0')], [('C1C2_1', 'C2C3_1', ':C2_11_1')], [('C1C2_1', 'C2B2_1', ':C2_13_0')], [('C1C2_1', 'C2C1_1', ':C2_14_0')], [('B2C2_0', 'C2C1_0', ':C2_15_0')], [('B2C2_0', 'C2D2_0', ':C2_16_0')], [('B2C2_1', 'C2D2_1', ':C2_16_1')], [('B2C2_1', 'C2C3_1', ':C2_18_0')], [('B2C2_1', 'C2B2_1', ':C2_19_0')]]
def helper_getOrderedIncomingOutgoingSeg(allLinks): # ordered by N,E,S,W
    incomingSeg = list()
    outgoingSeg = list()
    for link in allLinks:
        incomingSeg.append(link[0][0].split('_')[0]) # get 'C3C2'
        outgoingSeg.append(link[0][1].split('_')[0]) # get 'C2B2'
    if "helper" in comments: print("\n helper_getOrderedIncomingOutgoingSeg splited incomingSeg: ",incomingSeg, " outgoingSeg: ", outgoingSeg)

    #de-duplication
    pure_incomgingSeg = list()
    pure_outgoingSeg = list()
    for seg in incomingSeg:
        if seg not in pure_incomgingSeg:
            pure_incomgingSeg.append(seg)
    for seg in outgoingSeg:
        if seg not in pure_outgoingSeg:
            pure_outgoingSeg.append(seg)
    pure_outgoingSeg.reverse()
    if "helper" in comments: print("helper_getOrderedIncomingOutgoingSeg pure_incomgingSeg: ",pure_incomgingSeg, " pure_outgoingSeg: ", pure_outgoingSeg)
    return pure_incomgingSeg, pure_outgoingSeg
        
def helper_my_sum(*args):
    return sum(args)

def helper_my_avg(*args):
    return sum(args)/len(args)

def helper_is_margin_edge(edge_id):
    if "top" in edge_id or "bottom" in edge_id or "left" in edge_id or "right" in edge_id :
        return True
    
def helper_getVehicleNextSegment(v_id, curr_seg_id): 
    thisVehicleWholeRoute = traci.vehicle.getRoute(v_id)
    if "helper2" in comments: print("\nhelper helper_getVehicleNextSegment thisVehicleWholeRoute: ",thisVehicleWholeRoute)
    if "helper2" in comments: print("\nhelper helper_getVehicleNextSegment curr_seg_id: ",curr_seg_id)
    for edge_i in thisVehicleWholeRoute:
        if edge_i == curr_seg_id: # (Assuming v pass this seg only once)
            index = thisVehicleWholeRoute.index(edge_i)
            if len(thisVehicleWholeRoute) > index +1: # Now it is "+1" after change road net TL area. It was "+2" to avoid out of range bug
                outgoingEdgeID = thisVehicleWholeRoute[ index + 1 ]
                if "helper2" in comments: print("\nhelper helper_getVehicleNextSegment outgoingEdgeID: ",outgoingEdgeID)
                return outgoingEdgeID

def helper_calcDistanceViaXY(x1, y1, x2, y2):
    return math.sqrt( (float(x1)-float(x2))**2 + (float(y1)-float(y2))**2 )

def helper_getNearestFarthestVehToIntersectionOnEachLane(intersection_id, lane_id1):
    if "helper3" in comments: print("\n allIntersectionsXY ", intersection_id, " : ", allIntersectionsXY[intersection_id])
    inte_x, inte_y = allIntersectionsXY[intersection_id]
    all_v = traci.lane.getLastStepVehicleIDs(lane_id1)

    max_dist, min_dist, farthest_v_id, nearest_v_id = 0, 10086000, 0, 0

    for v_id in all_v:
        v_x, v_y = traci.vehicle.getPosition(v_id)
        dist = helper_calcDistanceViaXY(inte_x, inte_y, v_x, v_y)
        if "helper3" in comments: print("v_x: ", v_x, " v_y: ", v_y, " dist: ", dist)
        if dist > max_dist:
            max_dist = dist 
            farthest_v_id = v_id
        if dist < min_dist:
            min_dist = dist 
            nearest_v_id = v_id
        if "helper3" in comments: print("max_dist: ", max_dist, " min_dist: ", min_dist, " farthest_v_id: ", farthest_v_id, " nearest_v_id: ", nearest_v_id)
    
    return max_dist, min_dist

def helper_getAllVehiclesIDsFromPlatoonClass(platoonClassInstance):
    allPVehicleClassInstances = platoonClassInstance.getVehicles() #Returns the platoon members as an ordered list. The leader is at index 0.
    allVIds = list()
    for PV_i in allPVehicleClassInstances:   
        #PV_i._ID, PV_i._vTypes
        if PV_i not in allVIds:
            allVIds.append(PV_i._ID)
    return allVIds

def helper_generateVIdAndEdgeId2PlatoonIdDict():
    # print("platoon_i: ", platoon_i[0], platoon_i[1], platoon_i[1].getVehicles())
    # platoon_i:  2261 <simpla._platoon.Platoon object at 0x7fa6d36c5da0> [<simpla._pvehicle.PVehicle object at 0x7fa6d36fa2e8>, <simpla._pvehicle.PVehicle object at 0x7fa6d36d5550>]

    platoonId2VidsDict = dict()
    # VId2PlatoonIdDict = dict()
    edgeId2PlatoonIdsDict = dict()
    # allVIdsInAllPlatoons = list()
    for platoon_i in simpla._mgr._platoons.items(): #simpla._mgr._platoons is a dict()
        platoonID = platoon_i[0]
        allVIdsInThisPlatoon = helper_getAllVehiclesIDsFromPlatoonClass(platoon_i[1])
        if len(allVIdsInThisPlatoon) >= 2:
            platoonId2VidsDict[platoonID] = allVIdsInThisPlatoon
        # allVIdsInAllPlatoons = allVIdsInAllPlatoons + allVIdsInThisPlatoon
        # for vid in allVIdsInThisPlatoon:
        #     VId2PlatoonIdDict[vid] = platoonID
        # get the edge id where current platoon's leader is in
        edgeIdTheVehicleIsIn = traci.vehicle.getRoadID(platoon_i[1].getLeader().getID())
        if (edgeIdTheVehicleIsIn not in  edgeId2PlatoonIdsDict.keys()):
            edgeId2PlatoonIdsDict[edgeIdTheVehicleIsIn] = list()           
        edgeId2PlatoonIdsDict[edgeIdTheVehicleIsIn].append(platoonID)
    return platoonId2VidsDict, edgeId2PlatoonIdsDict

def helper_findMathSetIntersection(oneDict):
    SetIntersectionLeft = 0
    SetIntersectionRight = 10086
    for key_i in oneDict.keys():
        SetIntersectionLeft = oneDict[key_i][0]
        SetIntersectionRight = oneDict[key_i][1]
        break #randomly pick one element of dict to set initial value
    for key_i in oneDict.keys():#only four cases, only three of them can form intersection/overlap
        if oneDict[key_i][0] <= SetIntersectionLeft and oneDict[key_i][1] >= SetIntersectionLeft and oneDict[key_i][1] <= SetIntersectionRight:
            SetIntersectionLeft = oneDict[key_i][0]
        elif oneDict[key_i][0] >= SetIntersectionLeft and oneDict[key_i][0] <= SetIntersectionRight and oneDict[key_i][1] >= SetIntersectionRight:
            SetIntersectionRight = oneDict[key_i][1]
        elif oneDict[key_i][0] <= SetIntersectionLeft and oneDict[key_i][1] >= SetIntersectionRight:
            SetIntersectionLeft = oneDict[key_i][0]
            SetIntersectionRight = oneDict[key_i][1]
    return SetIntersectionLeft, SetIntersectionRight


    

def helper_getPlatoonIntersectionLeaderEnderTimeOnThisEdge(edgeid1, tlid):
    if "helper4" in comments: print("\n intersectionsXY ", tlid, " : ", allIntersectionsXY[tlid])
    tl_x, tl_y = allIntersectionsXY[tlid]
    platoonId2VidsDict, edgeId2PlatoonIdsDict = helper_generateVIdAndEdgeId2PlatoonIdDict()

    noPlatoonFlag = 0
    platoonId2TimeDict = dict()

    #get how long leader/ender of all platoons on edge 1 can go to TL
    if (edgeid1 not in edgeId2PlatoonIdsDict.keys()):
        if "helper4" in comments: print("no platoon in ", edgeid1)
        noPlatoonFlag = 1
        return noPlatoonFlag, 0, 0
    else:
        platoonIdsListInThisEdge = edgeId2PlatoonIdsDict[edgeid1]
        if "helper4" in comments: print("edgeid1: ", edgeid1, " platoonIdsListInThisEdge ", platoonIdsListInThisEdge)
        for platoonIds_i in platoonIdsListInThisEdge:
            if platoonIds_i not in  platoonId2VidsDict.keys():
                continue
            allVIdsInThisPlatoon = platoonId2VidsDict[platoonIds_i]
            if "helper4" in comments: print("allVIdsInThisPlatoon: ", allVIdsInThisPlatoon)

            if (len(allVIdsInThisPlatoon) <= 1):
                continue        
            vLeaderId = allVIdsInThisPlatoon[0]
            vEnderId = allVIdsInThisPlatoon[len(allVIdsInThisPlatoon)-1]

            if "helper4" in comments: print("\n getPosition vLeaderId", traci.vehicle.getPosition(vLeaderId))
            v_x, v_y = traci.vehicle.getPosition(vLeaderId)
            speedlimit = traci.lane.getMaxSpeed(edgeid1 + "_0")
            vLeader_time_toTL = helper_calcDistanceViaXY(tl_x, tl_y, v_x, v_y) / float(speedlimit)

            if "helper4" in comments: print("\n getPosition vEnderId", traci.vehicle.getPosition(vEnderId))
            v_x, v_y = traci.vehicle.getPosition(vEnderId)
            vEnder_time_toTL = helper_calcDistanceViaXY(tl_x, tl_y, v_x, v_y) / float(speedlimit)

            platoonId2TimeDict[platoonIds_i] = [vLeader_time_toTL, vEnder_time_toTL]
        # find intersection of set (commong range) (Math, not traffic lights)    
        veryFirst, veryLast = helper_findMathSetIntersection(platoonId2TimeDict)
        noPlatoonFlag = 0
        return noPlatoonFlag, veryFirst, veryLast

# def helper_decideCutPlatoonTime

        


    # for platoon_i in simpla._mgr._platoons.items(): #simpla._mgr._platoons is a dict()
    #     allVIdsInThisPlatoon = helper_getAllVehiclesIDsFromPlatoonClass(platoon_i[1])
    #     print("platoon_i: ", platoon_i[0], platoon_i[1], platoon_i[1].getVehicles())
    #     for vid in allVIdsInThisPlatoon:
    #         print("vid : ", vid, " type: ", traci.vehicle.getTypeID(vid))
    #         if traci.vehicle.getTypeID(vid) not in {"myvTypeCar_platoon", "myvTypeBus_platoon", "myvTypeTaxi_platoon"}:
    #             print("not in three platoon vtype!")

    # allVIds = traci.edge.getLastStepVehicleIDs(edgeid1)
    # if "helper4" in comments: print("allVIds: ", allVIds)

    # vInPlatoonOnEdge1 = list()
    # platoonIDsOnEdge1 = list()
    # for vid in allVIds:
    #     # 7 vtype ids: myvTypeCar_platoon, myvTypeBus_platoon, myvTypeTaxi_platoon, myvTypeCar_human_nojoinP, myvTypeBus_human_nojoinP, myvTypeTaxi_human_nojoinP, myvTypeEmergency_human_nojoinP
    #     if traci.vehicle.getTypeID(vid) in {"myvTypeCar_platoon", "myvTypeBus_platoon", "myvTypeTaxi_platoon"}:
    #         vInPlatoonOnEdge1.append(vid)
    #         if "helper4" in comments: print("helper_getPlatoonOnEdge: vid: ", vid, " vtype: ", traci.vehicle.getTypeID(vid), " follower: ", traci.vehicle.getFollower(vid, 5), " leader: ", traci.vehicle.getLeader(vid, 5) )
    #         # print(simpla.test_dayuan())

    #         for platoon_i in simpla._mgr._platoons.items(): #simpla._mgr._platoons is a dict()
    #             # print("platoon_i: ", platoon_i[0], platoon_i[1], platoon_i[1].getVehicles())
    #             allVIdsInThisPlatoon = helper_getAllVehiclesIDsFromPlatoonClass(platoon_i[1])
    #             if vid in allVIdsInThisPlatoon:
    #                 platoonIDsOnEdge1.append(platoon_i[0])
    #                 if "helper4" in comments: print("helper_getPlatoonOnEdge, the platoon id this vid is in: ", platoon_i[0], " all v in this platoon: ", allVIds)
    #                 break

    #         # print("1: ", simpla._mgr.getPlatoonLeaders())
    #         # print("2: ", simpla._mgr._platoons.items())
    #         #2:  dict_items([(0, <simpla._platoon.Platoon object at 0x7f84396a5ac8>), (1, <simpla._platoon.Platoon object at 0x7f84396a50b8>), (2, <simpla._platoon.Platoon object at 0x7f84396affd0>), (3, <simpla._platoon.Platoon object at 0x7f8439690da0>), (4, <simpla._platoon.Platoon object at 0x7f8439690cc0>), (6, <simpla._platoon.Platoon object at 0x7f84396aa748>), (7, <simpla._platoon.Platoon object at 0x7f8439690400>), (8, <simpla._platoon.Platoon object at 0x7f84396906d8>), (9, <simpla._platoon.Platoon object at 0x7f8439690c50>), (10, <simpla._platoon.Platoon object at 0x7f84396aa048>), (11, <simpla._platoon.Platoon object at 0x7f8439690048>), (12, <simpla._platoon.Platoon object at 0x7f843967eda0>), (13, <simpla._platoon.Platoon object at 0x7f84396afe80>), (14, <simpla._platoon.Platoon object at 0x7f843967e550>), (15, <simpla._platoon.Platoon object at 0x7f843967e208>), (16, <simpla._platoon.Platoon object at 0x7f843967e0b8>)])
    #         # print("3: ", simpla._mgr._platoons.values())
         



def helper_hasVehiclesWithIn3sToTLOrNot(orthogonal_direction_edge1, orthogonal_direction_edge2, TL_id):
    _, min_dist0 = helper_getNearestFarthestVehToIntersectionOnEachLane(TL_id, orthogonal_direction_edge1 + "_0")
    speedlimit = traci.lane.getMaxSpeed(orthogonal_direction_edge1 + "_0")
    min_time0 = min_dist0 / speedlimit

    _, min_dist1 = helper_getNearestFarthestVehToIntersectionOnEachLane(TL_id, orthogonal_direction_edge1 + "_1")
    speedlimit = traci.lane.getMaxSpeed(orthogonal_direction_edge1 + "_1")
    min_time1 = min_dist1 / speedlimit

    _, min_dist2 = helper_getNearestFarthestVehToIntersectionOnEachLane(TL_id, orthogonal_direction_edge2 + "_0")
    speedlimit = traci.lane.getMaxSpeed(orthogonal_direction_edge2 + "_0")
    min_time2 = min_dist2 / speedlimit

    _, min_dist3 = helper_getNearestFarthestVehToIntersectionOnEachLane(TL_id, orthogonal_direction_edge2 + "_1")
    speedlimit = traci.lane.getMaxSpeed(orthogonal_direction_edge2 + "_1")
    min_time3 = min_dist3 / speedlimit

    min_time = min(min_time0, min_time1, min_time2, min_time3)
    if min_time <= 3:
        return True
    return False
        




def helper_getMaxFourRatios(seg1, seg2, i_TLids):
    curr_incoming_seg = seg1
    if "newTL" in comments: print("\n\n\ncurr_incoming_seg ", curr_incoming_seg)
    if "newTL" in comments: print("NPV_ratio", " allTLid[i_TLids]: ", NPV_ratio[allTLid[i_TLids]][curr_incoming_seg])
    if "newTL" in comments: print("AWT_ratio", " allTLid[i_TLids]: ", AWT_ratio[allTLid[i_TLids]][curr_incoming_seg])
    if "newTL" in comments: print("NDV_ratio", " allTLid[i_TLids]: ", NDV_ratio[allTLid[i_TLids]][curr_incoming_seg])
    if "newTL" in comments: print("NEV_ratio", " allTLid[i_TLids]: ", NEV_ratio[allTLid[i_TLids]][curr_incoming_seg])
    max_npv_r_E = max(NPV_ratio[allTLid[i_TLids]][curr_incoming_seg].items(), key=operator.itemgetter(1))[1] # get max value of dict
    max_awt_r_E = max(AWT_ratio[allTLid[i_TLids]][curr_incoming_seg].items(), key=operator.itemgetter(1))[1] 
    max_ndv_r_E = max(NDV_ratio[allTLid[i_TLids]][curr_incoming_seg].items(), key=operator.itemgetter(1))[1] 
    max_nev_r_E = max(NEV_ratio[allTLid[i_TLids]][curr_incoming_seg].items(), key=operator.itemgetter(1))[1] 

    curr_incoming_seg = seg2
    if "newTL" in comments: print("\n\n\ncurr_incoming_seg ", curr_incoming_seg)
    if "newTL" in comments: print("NPV_ratio", " allTLid[i_TLids]: ", NPV_ratio[allTLid[i_TLids]][curr_incoming_seg])
    if "newTL" in comments: print("AWT_ratio", " allTLid[i_TLids]: ", AWT_ratio[allTLid[i_TLids]][curr_incoming_seg])
    if "newTL" in comments: print("NDV_ratio", " allTLid[i_TLids]: ", NDV_ratio[allTLid[i_TLids]][curr_incoming_seg])
    if "newTL" in comments: print("NEV_ratio", " allTLid[i_TLids]: ", NEV_ratio[allTLid[i_TLids]][curr_incoming_seg])
    max_npv_r_W = max(NPV_ratio[allTLid[i_TLids]][curr_incoming_seg].items(), key=operator.itemgetter(1))[1]
    max_awt_r_W = max(AWT_ratio[allTLid[i_TLids]][curr_incoming_seg].items(), key=operator.itemgetter(1))[1]
    max_ndv_r_W = max(NDV_ratio[allTLid[i_TLids]][curr_incoming_seg].items(), key=operator.itemgetter(1))[1]
    max_nev_r_W = max(NEV_ratio[allTLid[i_TLids]][curr_incoming_seg].items(), key=operator.itemgetter(1))[1]

    max_npv_r = max(max_npv_r_E, max_npv_r_W)
    max_awt_r = max(max_awt_r_E, max_awt_r_W)
    max_ndv_r = max(max_ndv_r_E, max_ndv_r_W)
    max_nev_r = max(max_nev_r_E, max_nev_r_W)

    return max_npv_r, max_awt_r, max_ndv_r, max_nev_r


    

def run():
    if "core" in comments: print("\nexecute the TraCI control loop.\n")
    step = 0
    
    #traci.trafficlight.setPhase("0", 2). N W S E are "0 1 2 3".

    ###################################################
    ###### Prepare varibales used for all cycles ######
    ###################################################

    # Step 1: get all TLs
    global allTLid
    allTLid = traci.trafficlight.getIDList() #all traffic lights id
    if "core" in comments: print("\n\nProgram starts. \n\nLen of allTLid:", len(allTLid)) #=30
    # Step 2: get TL's nearby edges
    outgoingEdgesOfEachTL = {} # dict
    incomingEdgesOfEachTL = {}
    # Step 3: initial throughput of each TL, Step 3
    throughput = {} 
    allVehiclesAtIncomingEdges_previousAllSteps = {} # used for recording throughput
    allVehiclesAtOutgoingEdges_previous1Step = {} # used to exclude vehicles who begins at outgoing edge
    # Step 4.0: initial throughput of each TL each flow: NPV_t(F(sou,tgt)) # Step 4
    NPV_eachTLeachFlow_currentCycle = {}
    NPV_eachTLeachFlow_previousCycle = {}
    NPV_eachTLeachFlow_allCycles = {}
    # Step 4.0: each vehilce's in and out (source and target) edges when pass each TL. 
    #vehivleInOutEdges = {} # Step 4 # Move it down, Temporary for current TL current Step only.
    initialOnlyOnce = {} # Step 4 
    phasePreviousStep = {} # Step 4 
    cycleDivider =  {} # Step 4 
    cycleNo = {} # Step 4 
    # Step 5.0
    NDV_eachTLeachFlow_currentCycle = {}
    NDV_eachTLeachFlow_previousCycle = {}
    # Step 6.0
    AWT_eachTLeachFlow_currentCycle = {}
    AWT_eachTLeachFlow_previousCycle = {}
    # Step 7.0 NEV
    neighborTLsSetOfEachTL = {}
    NEV_eachTLeachFlow_currentCycle = {}
    NEV_eachTLeachFlow_previousCycle = {}
    flowSouTgt_ofAllTLs = {} # step 7.1
    # Step 8.0: four ratios
    global NPV_ratio 
    global NDV_ratio 
    global AWT_ratio 
    global NEV_ratio 
    NPV_ratio = {}
    NDV_ratio = {}
    AWT_ratio = {}
    NEV_ratio = {}
    # Step 9.0: re-schedule for next cycle
    stepCounter_inLastPhase = {}
    # Step 11.2.0 
    halfCycleDivider =  {} 
    stepCounter_forHalfCycle = {}
    # Step 11.3.Temp check point 4
    greenLightEndsDivider =  {} 
    stepCounter_forGreenLight = {}

    for i_TLids in range(len(allTLid)):
        # Step 2: get TL's ID before to get its nearby edges
        nodeTL_i= net_xml.getNode(allTLid[i_TLids]) # get TL's corresponding node data structure, e.g. C2: <sumolib.net.node.Node object at 0x7f904dbd5f98>
        # Step 2: TL's connected edges
        outgoingEdgesOfEachTL[allTLid[i_TLids]] = nodeTL_i.getOutgoing() 
        incomingEdgesOfEachTL[allTLid[i_TLids]] = nodeTL_i.getIncoming()  
        #allEdgesOfTL = outgoingEdges + incomingEdges
        # Step 3.0
        throughput[allTLid[i_TLids]] = 0  
        allVehiclesAtIncomingEdges_previousAllSteps[allTLid[i_TLids]] = [] 
        allVehiclesAtOutgoingEdges_previous1Step[allTLid[i_TLids]] = []
        # Step 4.0
        NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] = 0 
        NPV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = 0
        NPV_eachTLeachFlow_allCycles[allTLid[i_TLids]] = {} 
        initialOnlyOnce[allTLid[i_TLids]] = 0
        phasePreviousStep[allTLid[i_TLids]] = 10086 # set a huge number for first cycle
        cycleDivider[allTLid[i_TLids]] = False 
        cycleNo[allTLid[i_TLids]] = 0
        # Step 5.0
        NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] = 0
        NDV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = 0
        # Step 6.0
        AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]] = 0
        AWT_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = 0
        # Step 7.0
        # Step 7.0: get TL's neighbor node TLs
        # Only incoming is needed since we want incoming expected vehicles (but they also should be same).
        #neighboringNodesEdges_outgoing = nodeTL_i.getNeighboringNodes(1, 0)# outgoing 
        neighboringNodesEdges_incoming = nodeTL_i.getNeighboringNodes(0, 1)# incoming 
        neighborTLsSetOfEachTL[allTLid[i_TLids]] = set() # declare a set data structure
        # Tricky: Connection is the DS connecting Node DS TL and edge.
        # neighboringNodesEdges_incoming.getConnections().getFrom() is the incoming edges: <edge id="B2C2" from="B2" to="B2C2.580.00"/>.
        for nodeEdge_i in neighboringNodesEdges_incoming:
            if "7getTLneighborTLs" in comments: print("\n TL", allTLid[i_TLids], "'s neighboringNodesEdges_incoming:", nodeEdge_i.getID(), "\n getConnections:", nodeEdge_i.getConnections() )
            # for connection_i in nodeEdge_i.getConnections():
            #     if "7getTLneighborTLs" in comments: print("Connection:",connection_i,"\n",
            #         "getFrom:",connection_i.getFrom(),"\n",
            #         "getFrom().getFromNode():",connection_i.getFrom().getFromNode().getID() )
            #     # neighborTLsSetOfEachTL[allTLid[i_TLids]].add(connection_i.getFrom().getFromNode().getID())
            neighborTLsSetOfEachTL[allTLid[i_TLids]].add( nodeEdge_i.getID() )
        NEV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] = 0 
        NEV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = 0 
        # Step 7.0 ends.
        # Step 7.1
        # do it only once when program starts 
        # prepare data structure for NEV bc it needs flowSouTgt_ofAllTLs
        outgoingEdges = outgoingEdgesOfEachTL[allTLid[i_TLids]]
        incomingEdges = incomingEdgesOfEachTL[allTLid[i_TLids]]
        if ( initialOnlyOnce[allTLid[i_TLids]] == 0 ) :
            if "7flowSouTgt_ofAllTLs" in comments: print("\n -----\nPrepare NEV flowSouTgt_ofAllTLs Data Structure Section:\n")
            # flowSouTgt = {}
            for inEdge in incomingEdges:
                # Below 2 are old when has reduntant connecting turning area
                # sourceEdge = helper_nearbyEdgesGetIDs(True, False, inEdge) # True for incoming edge
                #sourceEdge = inEdge.getFromNode().getID() # incomingEdges: [<edge id="A1A0.480.00" from="A1A0.480.00" to="A0"/>, <edge id="B0A0.580.00" from="B0A0.580.00" to="A0"/>, <edge id="bottom0A0" from="bottom0" to="A0"/>, <edge id="left0A0" from="left0" to="A0"/>]
                # Below 1 are NEW after fix the reduntant connecting turning area issue
                sourceEdge = inEdge.getID() # TL C2 's incomingEdges: [<edge id="B2C2" from="B2" to="C2"/>, <edge id="C1C2" from="C1" to="C2"/>, <edge id="C3C2" from="C3" to="C2"/>, <edge id="D2C2" from="D2" to="C2"/>]                      
                targetEdgeAll = {}
                for outEdge in outgoingEdges:
                    # Below 2 are old when has reduntant connecting turning area
                    # targetEdge = helper_nearbyEdgesGetIDs(False, True, outEdge) # True for outgoing edge
                    #targetEdge = outEdge.getToNode().getID()
                    # Below 1 are NEW after fix the reduntant connecting turning area issue
                    targetEdge = outEdge.getID()
                    targetEdgeAll[targetEdge] = 0
                if "7flowSouTgt_ofAllTLs" in comments: print("\n targetEdgeAll:", targetEdgeAll)
                flowSouTgt_ofAllTLs[sourceEdge] = targetEdgeAll
                if "7flowSouTgt_ofAllTLs" in comments: print("\n flowSouTgt_ofAllTLs:", flowSouTgt_ofAllTLs)  
            # Step 8.1: four ratios prepare data structure
            NPV_ratio[allTLid[i_TLids]] = flowSouTgt_ofAllTLs
            NDV_ratio[allTLid[i_TLids]] = flowSouTgt_ofAllTLs
            AWT_ratio[allTLid[i_TLids]] = flowSouTgt_ofAllTLs
            NEV_ratio[allTLid[i_TLids]] = flowSouTgt_ofAllTLs
            # Step 9.1: re-schedule for next cycle, prepare data structure
            stepCounter_inLastPhase[allTLid[i_TLids]] = 0
            # Step 11.2.1 
            halfCycleDivider[allTLid[i_TLids]] = False
            stepCounter_forHalfCycle[allTLid[i_TLids]] = 0
            # Step 11.3.Temp check point 4
            greenLightEndsDivider[allTLid[i_TLids]] = False
            stepCounter_forGreenLight[allTLid[i_TLids]] = 0

        # Step 7.1 ends
        
    if "core" in comments: print("\n Throughput:", throughput) # Step 3.0 
    if "core" in comments: print("\n NeighborTLsSetOfEachTL:", neighborTLsSetOfEachTL) # Step 7.0 
    if "core" in comments: print("\n flowSouTgt_ofAllTLs:", flowSouTgt_ofAllTLs) # Step 7.1
    


    ###################################################
    ######        Proceed forward each step      ######
    ###################################################

    cycle_ctr_totally = 0 
    re_schedule_when_enough_counter_totally = 0
    re_schedule_when_NOT_enough_counter_totally = 0
    # while traci.simulation.getTime() <640:# The unit is s. Set a short time for testing 
    while traci.simulation.getMinExpectedNumber() > 0:# run until all v have arrived
        traci.simulationStep() # forward one step

        

        # iterate each TL
        for i_TLids in range(len(allTLid)):#py3 don't have xrange
            #Comment this 'if' to run for all TLs.
            # if ( i_TLids == 17): #& ( traci.simulation.getTime() < 210.0):# id12 is C2. 17 is D2. # just show partial since too many
                
                if "core" in comments: print("\n\n\n\n----------------------------------\n\nSimulation time:", traci.simulation.getTime())
                if "core" in comments: print("[TL id]:", allTLid[i_TLids])
                phaseCurrentStep = traci.trafficlight.getPhase(allTLid[i_TLids])
                if "core" in comments: print("[Phase]:", phaseCurrentStep)
                phaseDuration_currPhase = traci.trafficlight.getPhaseDuration(allTLid[i_TLids])
                if "core" in comments: print("[Phase duration]:", phaseDuration_currPhase)
                if "core" in comments: print("[Phase Name]:", traci.trafficlight.getPhaseName(allTLid[i_TLids]))
                if "core" in comments: print("[Program]:", traci.trafficlight.getProgram(allTLid[i_TLids]))
                if "core" in comments: print("[getRedYellowGreenState]:", traci.trafficlight.getRedYellowGreenState(allTLid[i_TLids]))
                
                allProgramLogicInThisTL = traci.trafficlight.getCompleteRedYellowGreenDefinition(allTLid[i_TLids])
                if "core" in comments: print("[getAllProgramLogics]:", allProgramLogicInThisTL) # output is 'logic' data structure
                allPhasesOfThisProgramLogicInThisTL = allProgramLogicInThisTL[0].getPhases() # get content
                if "core" in comments: print("[phases all]:", allPhasesOfThisProgramLogicInThisTL)
                phasesTotalAmount = len(allPhasesOfThisProgramLogicInThisTL)
                if "core" in comments: print("[phasesTotalAmount]:", phasesTotalAmount) # the length is how much phases this TL program logic has in one cycle
                
                allLinks = traci.trafficlight.getControlledLinks(allTLid[i_TLids])
                if "core" in comments: print("[All Links]:", allLinks)
                orderedIncomingSeg, orderedOutgoingSeg = helper_getOrderedIncomingOutgoingSeg(allLinks)
                if "core" in comments: print("[ordered Incoming Seg]:", orderedIncomingSeg) # ordered by N,E,S,W
                if "core" in comments: print("[ordered Outgoing Seg]:", orderedOutgoingSeg) # ordered by N,E,S,W




                ###################################################
                #########           cycle divider         #########
                ###################################################
                # Step 4: cycle divider for each TL 
                # if cycles begin or program just begins 
                """OLD:
                if (phaseCurrentStep == 0) & ( (phasePreviousStep[allTLid[i_TLids]] == phasesTotalAmount - 1) | (phasePreviousStep[allTLid[i_TLids]] == 10086) ): 
                    cycleDivider[allTLid[i_TLids]] = True 
                    phasePreviousStep[allTLid[i_TLids]] =  0 
                    if "core" in comments: print("cycleDivider ", allTLid[i_TLids], " is set true. ",  cycleDivider, " phasePreviousStep[", allTLid[i_TLids], "] is set to 0.")
                """

                # if cycles begin (change to "last step in the last phase in curr cycle") or program just begins 
                if (phaseCurrentStep== phasesTotalAmount - 1) and (phasePreviousStep[allTLid[i_TLids]] == phasesTotalAmount - 2): # the moment from last_but_one phase to last phase
                    stepCounter_inLastPhase[allTLid[i_TLids]] = 0
                if (phaseCurrentStep == phasesTotalAmount - 1): # is last phase in curr cycle
                    stepCounter_inLastPhase[allTLid[i_TLids]] += 1
                    if "core" in comments: print("stepCounter_inLastPhase[", allTLid[i_TLids], "]: ",  stepCounter_inLastPhase[allTLid[i_TLids]])
                    if "core" in comments: print("phaseDuration_currPhase: ",  phaseDuration_currPhase)
                    if (stepCounter_inLastPhase[allTLid[i_TLids]] == phaseDuration_currPhase): # is last step in the last phase in curr cycle
                        cycleDivider[allTLid[i_TLids]] = True 
                        if "core" in comments: print("cycleDivider ", allTLid[i_TLids], " is set true. ",  cycleDivider)
                elif (phaseCurrentStep == 0) & (phasePreviousStep[allTLid[i_TLids]] == 10086): # program just begins
                    cycleDivider[allTLid[i_TLids]] = True 
                    phasePreviousStep[allTLid[i_TLids]] =  -1 
                    if "core" in comments: print("cycleDivider ", allTLid[i_TLids], " is set true. ",  cycleDivider, "\n phasePreviousStep[", allTLid[i_TLids], "] is set to -1.")
                
                # Step 11.2.2 
                # phase: 0 1 2 3
                if (phaseCurrentStep == 1 ) and (phasePreviousStep[allTLid[i_TLids]] == 0): 
                    stepCounter_forHalfCycle[allTLid[i_TLids]] = 0
                elif cycleDivider[allTLid[i_TLids]] == True: 
                    halfCycleDivider[allTLid[i_TLids]] = True
                    if "core" in comments: print("halfCycleDivider ", allTLid[i_TLids], " is set true bc cycleDivider. ",  halfCycleDivider)
                if (phaseCurrentStep == 1): # is last phase in curr cycle
                    stepCounter_forHalfCycle[allTLid[i_TLids]] += 1
                    if "core" in comments: print("stepCounter_forHalfCycle[", allTLid[i_TLids], "]: ",  stepCounter_forHalfCycle[allTLid[i_TLids]])
                    if "core" in comments: print("phaseDuration_currPhase: ",  phaseDuration_currPhase)
                    if (stepCounter_forHalfCycle[allTLid[i_TLids]] == phaseDuration_currPhase): # is last step in the last phase in curr cycle
                        halfCycleDivider[allTLid[i_TLids]] = True 
                        if "core" in comments: print("halfCycleDivider ", allTLid[i_TLids], " is set true. ",  halfCycleDivider)

                # Step 11.3.Temp check point 4
                # add to determine when green light ends (phase 0 and 1 ends)
                if ((phaseCurrentStep == 0 ) and (phasePreviousStep[allTLid[i_TLids]] == phasesTotalAmount - 1) ) or ( (phaseCurrentStep == 2 ) and (phasePreviousStep[allTLid[i_TLids]] == 1) ):
                    stepCounter_forGreenLight[allTLid[i_TLids]] = 0
                if (phaseCurrentStep == 0 or phaseCurrentStep == 2): # is phase 0 in curr cycle
                    stepCounter_forGreenLight[allTLid[i_TLids]] += 1
                    if "core" in comments: print("stepCounter_forGreenLight[", allTLid[i_TLids], "]: ",  stepCounter_forGreenLight[allTLid[i_TLids]])
                    if "core" in comments: print("phaseDuration_currPhase: ",  phaseDuration_currPhase)
                    if (stepCounter_forGreenLight[allTLid[i_TLids]] == phaseDuration_currPhase): # is last step in the phase 0 in curr cycle
                        greenLightEndsDivider[allTLid[i_TLids]] = True 
                        if "core" in comments: print("greenLightEndsDivider ", allTLid[i_TLids], " is set true. ",  greenLightEndsDivider)


                # Step 7.2: NEV. Only once for each cycle. 
                # Before the beginning of new cycle (except program begins bc datastruture is not initialized at that time)
                if "core" in comments: print("\n cycleDivider[allTLid[i_TLids]] ", cycleDivider[allTLid[i_TLids]], " halfCycleDivider[allTLid[i_TLids]]  ", halfCycleDivider[allTLid[i_TLids]])
                # if  (cycleDivider[allTLid[i_TLids]] == True) & (initialOnlyOnce[allTLid[i_TLids]] >= 1):
                if (halfCycleDivider[allTLid[i_TLids]] == True) & (initialOnlyOnce[allTLid[i_TLids]] >= 1):
                    # Step 7.3: get TL's neighbor node TLs and their incoming Edges
                    if "7getNEV" in comments: print("\n ------------------------ Before the beginning of new Cycle, NEV ------------------------")
                    if "7getNEV" in comments: print("\n TL", allTLid[i_TLids], "'s neighboring TLs : ", neighborTLsSetOfEachTL[allTLid[i_TLids]] )
                    for neighborTLsSet_i in neighborTLsSetOfEachTL[allTLid[i_TLids]]:
                        neighborTLsSet_i_neighborEdges = []
                        if neighborTLsSet_i in incomingEdgesOfEachTL: # if exists as key in dict, since "bottom0" not exists in it.
                            neighborTLsSet_i_neighborEdges = incomingEdgesOfEachTL[neighborTLsSet_i]
                        if "7getNEV" in comments: print("\n ------\n TL", allTLid[i_TLids], "'s neighboring TL", neighborTLsSet_i, "'s incoming Edges:",  neighborTLsSet_i_neighborEdges)
                        for neighborTLsSet_i__neighborEdges_i in neighborTLsSet_i_neighborEdges:
                            if "7getNEV" in comments: print("\nEdges IDs:", neighborTLsSet_i__neighborEdges_i.getID() )
                            if allTLid[i_TLids] in neighborTLsSet_i__neighborEdges_i.getID():
                                if "7getNEV" in comments: print("    skip." )
                                continue # only keep three incomings, skip the one from current TL, e.g. C2's neighbor B2, only keep A2B2, B1B2, B3B2, not C2B2.
                            # Step 7.4: collect all vehicles in the incoming edges of TL's neighbor node TLs                                                       
                            neighborTLsSet_i__neighborEdges_i_allVehiclesAtEdge = traci.edge.getLastStepVehicleIDs(neighborTLsSet_i__neighborEdges_i.getID() ) # get vehilces IDs in this edge
                            if "7getNEV" in comments: print("    All Vehicles IDs in this Edge:", neighborTLsSet_i__neighborEdges_i_allVehiclesAtEdge )
                            for v_IDs_i in neighborTLsSet_i__neighborEdges_i_allVehiclesAtEdge:
                                # Step 7.5: determine whether this vehicle is going to current TL. By judging next next TL is current TL or not. 
                                nextTLs = traci.vehicle.getNextTLS(v_IDs_i)
                                if "7getNEV" in comments: print("v ", v_IDs_i, " info, next TLs:", nextTLs,
                                                                "\n routes:", traci.vehicle.getRoute(v_IDs_i))
                                if len(nextTLs) >=2:
                                    if "7getNEV" in comments: print("next TL:", nextTLs[0][0])
                                    if "7getNEV" in comments: print("next next TL:", nextTLs[1][0])
                                    if (nextTLs[0][0] == neighborTLsSet_i) & (nextTLs[1][0] == allTLid[i_TLids]): 
                                        if "7getNEV" in comments: print("hooray!! add into NEV")
                                        # Step 7.6 confirmed! add into NEV
                                        incomingEdgeID_of_current_neighbor = neighborTLsSet_i__neighborEdges_i.getID()
                                        outgoingEdgeID_of_current_neighbor = neighborTLsSet_i + allTLid[i_TLids]
                                        if "7getNEV" in comments: print("incomingEdgeID_of_current_neighbor: ", incomingEdgeID_of_current_neighbor, "outgoingEdgeID_of_current_neighbor: ", outgoingEdgeID_of_current_neighbor)
                                        NEV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_of_current_neighbor][outgoingEdgeID_of_current_neighbor] += 1


                    if "7getNEV" in comments: print("\n ------------------------ End the beginning of new Cycle, NEV ------------------------")



                #############################################################################################################  
                # Section to get 4 main parameters ratios, preping for updating the next Cycle Traffic Lights System    #####
                ############################################################################################################# 

                # Step 8.2 calculate four ratios
                # do it when each cycle begins except program begins
                # if  (cycleDivider[allTLid[i_TLids]] == True) & (initialOnlyOnce[allTLid[i_TLids]] >= 1):
                if (halfCycleDivider[allTLid[i_TLids]] == True) & (initialOnlyOnce[allTLid[i_TLids]] >= 1):
                    # At this moment the NPV_eachTLeachFlow_currentCycle is the NPV value of previous cycle 
                    # and the NPV_eachTLeachFlow_previousCycle is the NPV value of previous previous cycle 
                    # bc the new value assignment has not began
                    if "8fourRatios" in comments: print("\n\n\n ------------------------  BEGIN of Section to get 4 main parameters ratios ------------------------")
                    if "8fourRatios" in comments: print("NPV_ratio  NPV_eachTLeachFlow_previousCycle ", allTLid[i_TLids], NPV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] )
                    if "8fourRatios" in comments: print("NPV_ratio  NPV_eachTLeachFlow_currentCycle ", allTLid[i_TLids], NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] )
                    for flow_sou in NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]]:
                        for flow_tgt in NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][flow_sou]:
                            if NPV_eachTLeachFlow_previousCycle[allTLid[i_TLids]][flow_sou][flow_tgt] != 0:
                                NPV_ratio[allTLid[i_TLids]][flow_sou][flow_tgt] = float(NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][flow_sou][flow_tgt]) / NPV_eachTLeachFlow_previousCycle[allTLid[i_TLids]][flow_sou][flow_tgt]
                            else:
                                NPV_ratio[allTLid[i_TLids]][flow_sou][flow_tgt] = 0 
                            if "8fourRatios" in comments: print("NPV_ratio ", allTLid[i_TLids], " ", flow_sou, " ", flow_tgt, ": ", NPV_ratio[allTLid[i_TLids]][flow_sou][flow_tgt]  )
                    
                    if "8fourRatios" in comments: print("NDV_ratio  NDV_eachTLeachFlow_previousCycle ", allTLid[i_TLids], NDV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] )
                    if "8fourRatios" in comments: print("NDV_ratio  NDV_eachTLeachFlow_currentCycle ", allTLid[i_TLids], NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] )
                    for flow_sou in NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]]:
                        for flow_tgt in NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][flow_sou]:
                            if len(NDV_eachTLeachFlow_previousCycle[allTLid[i_TLids]][flow_sou][flow_tgt]) != 0:
                                NDV_ratio[allTLid[i_TLids]][flow_sou][flow_tgt] = float(len(NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][flow_sou][flow_tgt])) / len(NDV_eachTLeachFlow_previousCycle[allTLid[i_TLids]][flow_sou][flow_tgt])
                            else:
                                NDV_ratio[allTLid[i_TLids]][flow_sou][flow_tgt] = 0 
                            if "8fourRatios" in comments: print("NDV_ratio ", allTLid[i_TLids], " ", flow_sou, " ", flow_tgt, ": ", NDV_ratio[allTLid[i_TLids]][flow_sou][flow_tgt]  )
                    
                    if "8fourRatios" in comments: print("AWT_ratio  AWT_eachTLeachFlow_previousCycle ", allTLid[i_TLids], AWT_eachTLeachFlow_previousCycle[allTLid[i_TLids]] )
                    if "8fourRatios" in comments: print("AWT_ratio  AWT_eachTLeachFlow_currentCycle ", allTLid[i_TLids], AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]] )
                    for flow_sou in AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]]:
                        for flow_tgt in AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]][flow_sou]:
                            if len(AWT_eachTLeachFlow_previousCycle[allTLid[i_TLids]][flow_sou][flow_tgt]) != 0:
                                AWT_ratio[allTLid[i_TLids]][flow_sou][flow_tgt] = float(len(AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]][flow_sou][flow_tgt])) / len(AWT_eachTLeachFlow_previousCycle[allTLid[i_TLids]][flow_sou][flow_tgt])
                            else:
                                AWT_ratio[allTLid[i_TLids]][flow_sou][flow_tgt] = 0 
                            if "8fourRatios" in comments: print("AWT_ratio ", allTLid[i_TLids], " ", flow_sou, " ", flow_tgt, ": ", AWT_ratio[allTLid[i_TLids]][flow_sou][flow_tgt]  )
                    
                    if "8fourRatios" in comments: print("NEV_ratio  NEV_eachTLeachFlow_previousCycle ", allTLid[i_TLids], NEV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] )
                    if "8fourRatios" in comments: print("NEV_ratio  NEV_eachTLeachFlow_currentCycle ", allTLid[i_TLids], NEV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] )                    
                    for flow_sou in NEV_eachTLeachFlow_currentCycle[allTLid[i_TLids]]:
                        for flow_tgt in NEV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][flow_sou]:
                            if NEV_eachTLeachFlow_previousCycle[allTLid[i_TLids]][flow_sou][flow_tgt] != 0:
                                NEV_ratio[allTLid[i_TLids]][flow_sou][flow_tgt] = float(NEV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][flow_sou][flow_tgt]) / NEV_eachTLeachFlow_previousCycle[allTLid[i_TLids]][flow_sou][flow_tgt]
                            else:
                                NEV_ratio[allTLid[i_TLids]][flow_sou][flow_tgt] = 0 
                            if "8fourRatios" in comments: print("NEV_ratio ", allTLid[i_TLids], " ", flow_sou, " ", flow_tgt, ": ", NEV_ratio[allTLid[i_TLids]][flow_sou][flow_tgt]  )
                                    
                # if "8fourRatios" in comments: print("\nAll NPV_ratio ",  NPV_ratio  )
                # if "8fourRatios" in comments: print("\nAll NDV_ratio ",  NDV_ratio  )
                # if "8fourRatios" in comments: print("\nAll AWT_ratio ",  AWT_ratio  )
                # if "8fourRatios" in comments: print("\nAll NEV_ratio ",  NEV_ratio  )

                if "8fourRatios" in comments: print("\n", allTLid[i_TLids], " NPV_ratio ",  NPV_ratio[allTLid[i_TLids]]  )
                if "8fourRatios" in comments: print("\n", allTLid[i_TLids], " NDV_ratio ",  NDV_ratio[allTLid[i_TLids]]  )
                if "8fourRatios" in comments: print("\n", allTLid[i_TLids], " AWT_ratio ",  AWT_ratio[allTLid[i_TLids]]  )
                if "8fourRatios" in comments: print("\n", allTLid[i_TLids], " NEV_ratio ",  NEV_ratio[allTLid[i_TLids]]  )
                if "8fourRatios" in comments: print("\n------------------------  END of Section to get 4 main parameters ratios ------------------------")
                
                # Section of 4 ratios END.
                    
                #################################################################################
                #################################################################################
                ### Section to schedule the next (new current) Cycle Traffic Lights System   ####
                #################################################################################
                #################################################################################
                #
                # show TL change, 17 is D2
                if (  i_TLids == 17 ) : print("\n", allTLid[i_TLids], " allPhasesOfThisProgramLogicInThisTL: ", allPhasesOfThisProgramLogicInThisTL)
                
                
                
                # Step 11.2.4
                if halfCycleDivider[allTLid[i_TLids]] == True:
                    if "halfcycle" in comments: print("\n\n\n ------------------------  BEGIN of Section to schedule the next Green Light Session  Traffic Lights System ------------------------")
                    goto_seg_N, goto_seg_E, goto_seg_S, goto_seg_W = 0, 0, 0, 0
                    halfCycle_isFisrtHalf = False
                    if phaseCurrentStep == 1: 
                        halfCycle_isFisrtHalf = True
                        if "halfcycle" in comments: print("half cycle, curr phase: 1 \n")
                        
                        allVehicles_inIncomingEdge_N = traci.edge.getLastStepVehicleIDs(orderedIncomingSeg[0])
                        for v_i in allVehicles_inIncomingEdge_N:
                            next_seg = helper_getVehicleNextSegment(v_i, orderedIncomingSeg[0])
                            if next_seg == orderedOutgoingSeg[1]: #turn left
                                goto_seg_E += 1
                            elif next_seg == orderedOutgoingSeg[2]: #go straight
                                goto_seg_S += 1
                            elif next_seg == orderedOutgoingSeg[2]: #turn right
                                goto_seg_W += 1

                        allVehicles_inIncomingEdge_S = traci.edge.getLastStepVehicleIDs(orderedIncomingSeg[2])
                        for v_i in allVehicles_inIncomingEdge_S:
                            next_seg = helper_getVehicleNextSegment(v_i, orderedIncomingSeg[2])
                            if next_seg == orderedOutgoingSeg[3]: #turn left
                                goto_seg_W += 1
                            elif next_seg == orderedOutgoingSeg[0]: #go straight
                                goto_seg_N += 1
                            elif next_seg == orderedOutgoingSeg[1]: #turn right
                                goto_seg_E += 1

                    elif phaseCurrentStep == 3:
                        if "halfcycle" in comments: print("half cycle, curr phase: 3 \n")

                        allVehicles_inIncomingEdge_E = traci.edge.getLastStepVehicleIDs(orderedIncomingSeg[1])
                        for v_i in allVehicles_inIncomingEdge_E:
                            next_seg = helper_getVehicleNextSegment(v_i, orderedIncomingSeg[1])
                            if next_seg == orderedOutgoingSeg[2]: #turn left
                                goto_seg_S += 1
                            elif next_seg == orderedOutgoingSeg[3]: #go straight
                                goto_seg_W += 1
                            elif next_seg == orderedOutgoingSeg[0]: #turn right
                                goto_seg_N += 1

                        allVehicles_inIncomingEdge_W = traci.edge.getLastStepVehicleIDs(orderedIncomingSeg[3])
                        for v_i in allVehicles_inIncomingEdge_W:
                            next_seg = helper_getVehicleNextSegment(v_i, orderedIncomingSeg[3])
                            if next_seg == orderedOutgoingSeg[0]: #turn left
                                goto_seg_N += 1
                            elif next_seg == orderedOutgoingSeg[1]: #go straight
                                goto_seg_E += 1
                            elif next_seg == orderedOutgoingSeg[2]: #turn right
                                goto_seg_S += 1

                    #################################################################################
                    # remaining capacity enough ?
                    remian_cap_enough_seg = list()
                    
                    # margin edge leng is 9.6 m # WE 200m actually has only 179.2m # NS 150m actually has only 129.2m
                    avg_v_len = traci.edge.getLastStepLength(orderedIncomingSeg[0]) if traci.edge.getLastStepLength(orderedIncomingSeg[0]) > 0 else AVG_V_LENGTH_PROBABILITY # getLastStepLength returns the mean vehicle length in m; AVG_V_LENGTH_PROBABILITY is avg v length in my v_type
                    seg_len = MARGIN_EDGE_LENGTH if helper_is_margin_edge(orderedIncomingSeg[0]) else NS_EDGE_LENGTH 
                    remain_seg_cap_N  = ( ( 1 - traci.edge.getLastStepOccupancy(orderedIncomingSeg[0]) ) * seg_len  ) / avg_v_len 
                    
                    avg_v_len = traci.edge.getLastStepLength(orderedIncomingSeg[1]) if traci.edge.getLastStepLength(orderedIncomingSeg[1]) > 0 else AVG_V_LENGTH_PROBABILITY
                    seg_len = MARGIN_EDGE_LENGTH if helper_is_margin_edge(orderedIncomingSeg[1]) else WE_EDGE_LENGTH
                    remain_seg_cap_E  = ( ( 1 - traci.edge.getLastStepOccupancy(orderedIncomingSeg[1]) ) * seg_len  ) / avg_v_len 
                    
                    avg_v_len = traci.edge.getLastStepLength(orderedIncomingSeg[2]) if traci.edge.getLastStepLength(orderedIncomingSeg[2]) > 0 else AVG_V_LENGTH_PROBABILITY
                    seg_len = MARGIN_EDGE_LENGTH if helper_is_margin_edge(orderedIncomingSeg[2]) else NS_EDGE_LENGTH
                    remain_seg_cap_S  = ( ( 1 - traci.edge.getLastStepOccupancy(orderedIncomingSeg[2]) ) * seg_len  ) / avg_v_len
                    
                    avg_v_len = traci.edge.getLastStepLength(orderedIncomingSeg[3]) if traci.edge.getLastStepLength(orderedIncomingSeg[3]) > 0 else AVG_V_LENGTH_PROBABILITY
                    seg_len = MARGIN_EDGE_LENGTH if helper_is_margin_edge(orderedIncomingSeg[3]) else WE_EDGE_LENGTH
                    remain_seg_cap_W  = ( ( 1 - traci.edge.getLastStepOccupancy(orderedIncomingSeg[3]) ) * seg_len  ) / avg_v_len
                    
                    if "halfcycle" in comments: print("getLastStepOccupancy 0: ", traci.edge.getLastStepOccupancy(orderedIncomingSeg[0]), )
                    if "halfcycle" in comments: print("getLastStepOccupancy 1: ", traci.edge.getLastStepOccupancy(orderedIncomingSeg[1]), )
                    if "halfcycle" in comments: print("getLastStepOccupancy 2: ", traci.edge.getLastStepOccupancy(orderedIncomingSeg[2]), )
                    if "halfcycle" in comments: print("getLastStepOccupancy 3: ", traci.edge.getLastStepOccupancy(orderedIncomingSeg[3]), " \n")

                    

                    if remain_seg_cap_N >= goto_seg_N :
                        remian_cap_enough_seg.append(orderedIncomingSeg[0])
                    if remain_seg_cap_E >= goto_seg_E :
                        remian_cap_enough_seg.append(orderedIncomingSeg[1])
                    if remain_seg_cap_S >= goto_seg_S :
                        remian_cap_enough_seg.append(orderedIncomingSeg[2])
                    if remain_seg_cap_W >= goto_seg_W :
                        remian_cap_enough_seg.append(orderedIncomingSeg[3])
                    if "halfcycle" in comments: print("remain_seg_N: ", remain_seg_cap_N, " \n")
                    if "halfcycle" in comments: print("goto_seg_N: ", goto_seg_N, " \n")
                    if "halfcycle" in comments: print("remain_seg_E: ", remain_seg_cap_E, " \n")
                    if "halfcycle" in comments: print("goto_seg_E: ", goto_seg_E, " \n")
                    if "halfcycle" in comments: print("remain_seg_S: ", remain_seg_cap_S, " \n")
                    if "halfcycle" in comments: print("goto_seg_S: ", goto_seg_S, " \n")
                    if "halfcycle" in comments: print("remain_seg_W: ", remain_seg_cap_W, " \n")
                    if "halfcycle" in comments: print("goto_seg_W: ", goto_seg_W, " \n")
                    if "halfcycle" in comments: print("remian_cap_enough_seg: ", remian_cap_enough_seg, " \n")



                    newPhasesArray = []
                    # enough and not enough decide diff new_GL_dur
                    new_GL_dur = 0  # new GL dur for next green light session
                    #################################################################################
                    ########################################  when remaining capacity enough
                    if len(remian_cap_enough_seg) > 0:
                        if "halfcycle" in comments: print("\n ------------------------  Remaining capacity is enough ------------------------")
                        re_schedule_when_enough_counter_totally += 1
                        if "halfcycle" in comments: print("half cycle, mean speed: N: ",  traci.edge.getLastStepMeanSpeed(orderedIncomingSeg[0]) , " S: ", traci.edge.getLastStepMeanSpeed(orderedIncomingSeg[2]) , " E: ", traci.edge.getLastStepMeanSpeed(orderedIncomingSeg[1]) , " W: ", traci.edge.getLastStepMeanSpeed(orderedIncomingSeg[3]) )
                        if "halfcycle" in comments: print("half cycle, len(orderedIncomingSeg): ", len(orderedIncomingSeg) )
                        
                        if "halfcycle" in comments: print("getLastStepOccupancy 0 lane 0: ", traci.lane.getLastStepOccupancy(orderedIncomingSeg[0]+"_0"), )
                        if "halfcycle" in comments: print("getLastStepOccupancy 0 lane 1: ", traci.lane.getLastStepOccupancy(orderedIncomingSeg[0]+"_1"), )
                        if "halfcycle" in comments: print("getLastStepOccupancy 1 lane 0: ", traci.lane.getLastStepOccupancy(orderedIncomingSeg[1]+"_0"), )
                        if "halfcycle" in comments: print("getLastStepOccupancy 1 lane 1: ", traci.lane.getLastStepOccupancy(orderedIncomingSeg[1]+"_1"), )
                        if "halfcycle" in comments: print("getLastStepOccupancy 2 lane 0: ", traci.lane.getLastStepOccupancy(orderedIncomingSeg[2]+"_0"), )
                        if "halfcycle" in comments: print("getLastStepOccupancy 2 lane 1: ", traci.lane.getLastStepOccupancy(orderedIncomingSeg[2]+"_1"), )
                        if "halfcycle" in comments: print("getLastStepOccupancy 3 lane 0: ", traci.lane.getLastStepOccupancy(orderedIncomingSeg[3]+"_0"), )
                        if "halfcycle" in comments: print("getLastStepOccupancy 3 lane 1: ", traci.lane.getLastStepOccupancy(orderedIncomingSeg[3]+"_1"), " \n")
                        
                        LANE_MAX_SPEED = 13.89 # unit is meter/second
                        ADJUST_RATIO_PARAM = 0.7 # I found when 0.7 it is full
                        if halfCycle_isFisrtHalf:    
                            farthest_dist, nearest_dist = helper_getNearestFarthestVehToIntersectionOnEachLane(allTLid[i_TLids], orderedIncomingSeg[1]+"_0")
                            lane_occupancy_ratio = traci.lane.getLastStepOccupancy(orderedIncomingSeg[1]+"_0") / ADJUST_RATIO_PARAM
                            lane_occupancy_ratio = 0.9 if lane_occupancy_ratio > 0.9 else lane_occupancy_ratio # to avoid when lane_occupancy_ratio is 1 then "err: float division by zero"
                            need_time1 = farthest_dist / (LANE_MAX_SPEED *  (1-lane_occupancy_ratio))

                            if "halfcycle" in comments: print("farthest_dist: ", farthest_dist, " lane_occupancy_ratio: ", lane_occupancy_ratio) 
                    
                            farthest_dist, nearest_dist = helper_getNearestFarthestVehToIntersectionOnEachLane(allTLid[i_TLids], orderedIncomingSeg[1]+"_1")
                            lane_occupancy_ratio = traci.lane.getLastStepOccupancy(orderedIncomingSeg[1]+"_1") / ADJUST_RATIO_PARAM
                            lane_occupancy_ratio = 0.9 if lane_occupancy_ratio > 0.9 else lane_occupancy_ratio
                            need_time2 = farthest_dist / (LANE_MAX_SPEED *  (1-lane_occupancy_ratio))
                        
                            if "halfcycle" in comments: print("farthest_dist: ", farthest_dist, " lane_occupancy_ratio: ", lane_occupancy_ratio) 

                            farthest_dist, nearest_dist = helper_getNearestFarthestVehToIntersectionOnEachLane(allTLid[i_TLids], orderedIncomingSeg[3]+"_0")
                            lane_occupancy_ratio = traci.lane.getLastStepOccupancy(orderedIncomingSeg[3]+"_0") / ADJUST_RATIO_PARAM
                            lane_occupancy_ratio = 0.9 if lane_occupancy_ratio > 0.9 else lane_occupancy_ratio
                            need_time3 = farthest_dist / (LANE_MAX_SPEED *  (1-lane_occupancy_ratio))

                            if "halfcycle" in comments: print("farthest_dist: ", farthest_dist, " lane_occupancy_ratio: ", lane_occupancy_ratio) 
                            

                            farthest_dist, nearest_dist = helper_getNearestFarthestVehToIntersectionOnEachLane(allTLid[i_TLids], orderedIncomingSeg[3]+"_1")
                            lane_occupancy_ratio = traci.lane.getLastStepOccupancy(orderedIncomingSeg[3]+"_1") / ADJUST_RATIO_PARAM
                            lane_occupancy_ratio = 0.9 if lane_occupancy_ratio > 0.9 else lane_occupancy_ratio
                            need_time4 = farthest_dist / (LANE_MAX_SPEED *  (1-lane_occupancy_ratio))

                            if "halfcycle" in comments: print("farthest_dist: ", farthest_dist, " lane_occupancy_ratio: ", lane_occupancy_ratio) 


                            if "halfcycle" in comments: print("1 need_time1: ", need_time1)
                            if "halfcycle" in comments: print("need_time2: ", need_time2)
                            if "halfcycle" in comments: print("need_time3: ", need_time3)
                            if "halfcycle" in comments: print("need_time4: ", need_time4)

                            new_GL_dur = max(need_time1, need_time2, need_time3, need_time4)
                        else :                     
                            farthest_dist, nearest_dist = helper_getNearestFarthestVehToIntersectionOnEachLane(allTLid[i_TLids], orderedIncomingSeg[0]+"_0")
                            lane_occupancy_ratio = traci.lane.getLastStepOccupancy(orderedIncomingSeg[0]+"_0") / ADJUST_RATIO_PARAM
                            lane_occupancy_ratio = 0.9 if lane_occupancy_ratio > 0.9 else lane_occupancy_ratio
                            need_time1 = farthest_dist / (LANE_MAX_SPEED *  (1-lane_occupancy_ratio))

                            if "halfcycle" in comments: print("farthest_dist: ", farthest_dist, " lane_occupancy_ratio: ", lane_occupancy_ratio) 


                            farthest_dist, nearest_dist = helper_getNearestFarthestVehToIntersectionOnEachLane(allTLid[i_TLids], orderedIncomingSeg[0]+"_1")
                            lane_occupancy_ratio = traci.lane.getLastStepOccupancy(orderedIncomingSeg[0]+"_1") / ADJUST_RATIO_PARAM
                            lane_occupancy_ratio = 0.9 if lane_occupancy_ratio > 0.9 else lane_occupancy_ratio
                            need_time2 = farthest_dist / (LANE_MAX_SPEED *  (1-lane_occupancy_ratio))

                            if "halfcycle" in comments: print("farthest_dist: ", farthest_dist, " lane_occupancy_ratio: ", lane_occupancy_ratio) 


                            farthest_dist, nearest_dist = helper_getNearestFarthestVehToIntersectionOnEachLane(allTLid[i_TLids], orderedIncomingSeg[2]+"_0")
                            lane_occupancy_ratio = traci.lane.getLastStepOccupancy(orderedIncomingSeg[2]+"_0") / ADJUST_RATIO_PARAM
                            lane_occupancy_ratio = 0.9 if lane_occupancy_ratio > 0.9 else lane_occupancy_ratio
                            need_time3 = farthest_dist / (LANE_MAX_SPEED *  (1-lane_occupancy_ratio))

                            if "halfcycle" in comments: print("farthest_dist: ", farthest_dist, " lane_occupancy_ratio: ", lane_occupancy_ratio) 


                            farthest_dist, nearest_dist = helper_getNearestFarthestVehToIntersectionOnEachLane(allTLid[i_TLids], orderedIncomingSeg[2]+"_1")
                            lane_occupancy_ratio = traci.lane.getLastStepOccupancy(orderedIncomingSeg[2]+"_1") / ADJUST_RATIO_PARAM
                            lane_occupancy_ratio = 0.9 if lane_occupancy_ratio > 0.9 else lane_occupancy_ratio
                            need_time4 = farthest_dist / (LANE_MAX_SPEED *  (1-lane_occupancy_ratio))

                            if "halfcycle" in comments: print("farthest_dist: ", farthest_dist, " lane_occupancy_ratio: ", lane_occupancy_ratio) 


                            if "halfcycle" in comments: print("2 need_time1: ", need_time1)
                            if "halfcycle" in comments: print("need_time2: ", need_time2)
                            if "halfcycle" in comments: print("need_time3: ", need_time3)
                            if "halfcycle" in comments: print("need_time4: ", need_time4)

                            new_GL_dur = max(need_time1, need_time2, need_time3, need_time4)
                        # G at least 3 second in case it is always 0 when no v
                        new_GL_dur = 3 if new_GL_dur < 3 else new_GL_dur 
                        
                    #################################################################################
                    ########################################  when remaining capacity NOT enough
                    else:
                        if "newTL" in comments: print("\n ------------------------  Remaining capacity is NOT enough ------------------------")
                        re_schedule_when_NOT_enough_counter_totally += 1

                        # # Step 9.2: re-schedule for next cycle, get current TL schedule and parse
                        #  deleted: if  (cycleDivider[allTLid[i_TLids]] == True) & (initialOnlyOnce[allTLid[i_TLids]] >= 1):
                        if "newTL" in comments: print("\n\n\n ------------------------  BEGIN of Section to schedule the next Cycle Traffic Lights System ------------------------")
                        if "newTL" in comments: print("allPhasesOfThisProgramLogicInThisTL: ", allPhasesOfThisProgramLogicInThisTL)
                        if "newTL" in comments: print("phasesTotalAmount: ", phasesTotalAmount)
                        if "newTL" in comments: print("orderedIncomingSeg: ", orderedIncomingSeg)

                        max_npv_r, max_awt_r, max_ndv_r, max_nev_r =  1, 1, 1, 1
                        curr_ratio = 1
                        if halfCycle_isFisrtHalf:
                            max_npv_r, max_awt_r, max_ndv_r, max_nev_r = helper_getMaxFourRatios(orderedIncomingSeg[1], orderedIncomingSeg[3], i_TLids)
                            if "newTL" in comments: print("first half cycle, to schedule for 2nd half, max_npv_r ", max_npv_r, "max_awt_r ", max_awt_r, "max_ndv_r ", max_ndv_r)
                        else:
                            max_npv_r, max_awt_r, max_ndv_r, max_nev_r = helper_getMaxFourRatios(orderedIncomingSeg[0], orderedIncomingSeg[2], i_TLids)
                            if "newTL" in comments: print("second half cycle, to schedule for next 1st half, max_npv_r ", max_npv_r, "max_awt_r ", max_awt_r, "max_ndv_r ", max_ndv_r)

                        if max_npv_r > 1 and max_awt_r > 1 and max_ndv_r > 1:
                            curr_ratio= helper_my_sum(max_npv_r, max_awt_r, max_ndv_r) / 3
                            if "newTL" in comments: print("case 1\n")
                        elif max_npv_r > 1 and max_awt_r < 1 and max_ndv_r < 1:
                            curr_ratio= helper_my_sum(max_awt_r, max_ndv_r) / 2
                            if "newTL" in comments: print("case 2\n")
                        elif max_npv_r < 1 and max_awt_r > 1 and max_ndv_r > 1:
                            curr_ratio= max_npv_r
                            if "newTL" in comments: print("case 3\n")
                        elif max_npv_r < 1 and max_awt_r < 1 and max_ndv_r < 1 and max_nev_r < 1:
                            curr_ratio= helper_my_sum(max_npv_r, max_awt_r, max_ndv_r, max_nev_r) / 4
                            if "newTL" in comments: print("case 4\n")
                        curr_ratio = 1 if curr_ratio == 0 else curr_ratio
                        if "newTL" in comments: print("new curr_ratio ", curr_ratio)
                        if halfCycle_isFisrtHalf:
                            new_GL_dur = allPhasesOfThisProgramLogicInThisTL[2].duration * curr_ratio
                        else:
                            new_GL_dur = allPhasesOfThisProgramLogicInThisTL[0].duration * curr_ratio
                        

                    # set new TL for next green light session
                    if halfCycle_isFisrtHalf:
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[0])
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[1])
                        if "halfcycle" in comments: print("half cycle, old phase 1: ", allPhasesOfThisProgramLogicInThisTL[0])
                        if "halfcycle" in comments: print("half cycle, old phase 2: ", allPhasesOfThisProgramLogicInThisTL[1])
                        phase3 = allPhasesOfThisProgramLogicInThisTL[2]
                        if "halfcycle" in comments: print("half cycle, old phase 3: ", phase3)
                        new_minDur = new_GL_dur if (new_GL_dur < phase3.minDur) else phase3.minDur
                        new_maxDur = new_GL_dur if (new_GL_dur > phase3.maxDur) else phase3.maxDur
                        newPhasesArray.append( traci.trafficlight.Phase(new_GL_dur, phase3.state, new_minDur, new_maxDur, phase3.next, phase3.name) )  
                        if "halfcycle" in comments: print("half cycle, new phase 3: ", traci.trafficlight.Phase(new_GL_dur, phase3.state, new_minDur, new_maxDur, phase3.next, phase3.name) )   
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[3])
                        if "halfcycle" in comments: print("half cycle, old phase 4: ", allPhasesOfThisProgramLogicInThisTL[3])
                    else:
                        phase1 = allPhasesOfThisProgramLogicInThisTL[0]
                        if "halfcycle" in comments: print("half cycle, old phase 1: ", phase1)
                        new_minDur = new_GL_dur if (new_GL_dur < phase1.minDur) else phase1.minDur
                        new_maxDur = new_GL_dur if (new_GL_dur > phase1.maxDur) else phase1.maxDur
                        newPhasesArray.append( traci.trafficlight.Phase(new_GL_dur, phase1.state, new_minDur, new_maxDur, phase1.next, phase1.name) )   
                        if "halfcycle" in comments: print("half cycle, new phase 1: ", traci.trafficlight.Phase(new_GL_dur, phase1.state, new_minDur, new_maxDur, phase1.next, phase1.name) )                     
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[1])
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[2])
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[3])
                        if "halfcycle" in comments: print("half cycle, old phase 2: ", allPhasesOfThisProgramLogicInThisTL[1])
                        if "halfcycle" in comments: print("half cycle, old phase 3: ", allPhasesOfThisProgramLogicInThisTL[2])
                        if "halfcycle" in comments: print("half cycle, old phase 4: ", allPhasesOfThisProgramLogicInThisTL[3])
                    # set for next green light session
                    newLogic = traci.trafficlight.Logic(allProgramLogicInThisTL[0].programID, allProgramLogicInThisTL[0].type, allProgramLogicInThisTL[0].currentPhaseIndex, newPhasesArray, allProgramLogicInThisTL[0].subParameter)
                    if "halfcycle" in comments: print("half cycle, newLogic: ", newLogic)
                    # below two lines together set the new TL for next cycle
                    traci.trafficlight.setCompleteRedYellowGreenDefinition(allTLid[i_TLids], newLogic)
                    traci.trafficlight.setPhase(allTLid[i_TLids], 2 if halfCycle_isFisrtHalf else 0)
                    stepCounter_forGreenLight[allTLid[i_TLids]] = 0
                    if "halfcycle" in comments: print("\n ------------------------  END of Section to schedule the next Green Light Session Traffic Lights System ------------------------")
                 


                
                # Step 11.3.Temp check point 4 Green Light Extender
                if allTLid[i_TLids] not in {'A0', 'A1', 'A2', 'A3', 'A4', 'B0', 'B4', 'C0', 'C4', 'D0', 'D1', 'D2', 'D3', 'D4'}:
                    if greenLightEndsDivider[allTLid[i_TLids]] == True:
                        if "greenLightEndsDivider" in comments: print("\n\n\n ------------------------  BEGIN of Section to decide extend current green light or not ------------------------")
                        # find platoon
                        if phaseCurrentStep == 0: #at then end of 1st phase, green for N-S
                            # N-S
                            # only if when there are no vehicles within 3s to TL in orthogonal directions 
                            if not helper_hasVehiclesWithIn3sToTLOrNot(orderedIncomingSeg[1], orderedIncomingSeg[3], allTLid[i_TLids]): #input are orthogonal directions
                                noPlatoonFlag_N, platoonNeededTime_N_start, platoonNeededTime_N_end = helper_getPlatoonIntersectionLeaderEnderTimeOnThisEdge(orderedIncomingSeg[0], allTLid[i_TLids])
                                noPlatoonFlag_S, platoonNeededTime_S_start, platoonNeededTime_S_end = helper_getPlatoonIntersectionLeaderEnderTimeOnThisEdge(orderedIncomingSeg[2], allTLid[i_TLids])
                                if noPlatoonFlag_N == 1 and noPlatoonFlag_S == 1: # if no platoon                            
                                    if helper_hasVehiclesWithIn3sToTLOrNot(orderedIncomingSeg[0], orderedIncomingSeg[2], allTLid[i_TLids]): # but has unplatoon vehicles <= 3s                                    
                                        traci.trafficlight.setPhaseDuration(allTLid[i_TLids], 3) # add 3s more
                                else: # if has platoon <= 3s, extend the time this pltoon needs
                                    if platoonNeededTime_N_start <= 3 and platoonNeededTime_S_start > 3:
                                        traci.trafficlight.setPhaseDuration(allTLid[i_TLids], platoonNeededTime_N_end) # extend until platoonNeededTime_N_end
                                    elif platoonNeededTime_N_start > 3 and platoonNeededTime_S_start <= 3:
                                        traci.trafficlight.setPhaseDuration(allTLid[i_TLids], platoonNeededTime_S_end) # extend until platoonNeededTime_S_end
                                    elif platoonNeededTime_N_start <= 3 and platoonNeededTime_S_start <= 3:
                                        traci.trafficlight.setPhaseDuration(allTLid[i_TLids], max(platoonNeededTime_N_end, platoonNeededTime_S_end)) # extend until max of two
                        
                        elif phaseCurrentStep == 2: #at then end of 3rd phase, green for W-E
                            # W-E
                            # only if when there are no vehicles within 3s to TL in orthogonal directions 
                            if not helper_hasVehiclesWithIn3sToTLOrNot(orderedIncomingSeg[0], orderedIncomingSeg[2], allTLid[i_TLids]): #input are orthogonal directions
                                noPlatoonFlag_E, platoonNeededTime_E_start, platoonNeededTime_E_end = helper_getPlatoonIntersectionLeaderEnderTimeOnThisEdge(orderedIncomingSeg[1], allTLid[i_TLids])
                                noPlatoonFlag_W, platoonNeededTime_W_start, platoonNeededTime_W_end = helper_getPlatoonIntersectionLeaderEnderTimeOnThisEdge(orderedIncomingSeg[3], allTLid[i_TLids])
                                if noPlatoonFlag_E == 1 and noPlatoonFlag_W == 1: # if no platoon                            
                                    if helper_hasVehiclesWithIn3sToTLOrNot(orderedIncomingSeg[1], orderedIncomingSeg[3], allTLid[i_TLids]): # but has unplatoon vehicles <= 3s                                    
                                        traci.trafficlight.setPhaseDuration(allTLid[i_TLids], 3) # add 3s more
                                else: # if has platoon <= 3s, extend the time this pltoon needs
                                    if platoonNeededTime_E_start <= 3 and platoonNeededTime_W_start > 3:
                                        traci.trafficlight.setPhaseDuration(allTLid[i_TLids], platoonNeededTime_E_end) # extend until platoonNeededTime_E_end
                                    elif platoonNeededTime_E_start > 3 and platoonNeededTime_W_start <= 3:
                                        traci.trafficlight.setPhaseDuration(allTLid[i_TLids], platoonNeededTime_W_end) # extend until platoonNeededTime_W_end
                                    elif platoonNeededTime_E_start <= 3 and platoonNeededTime_W_start <= 3:
                                        traci.trafficlight.setPhaseDuration(allTLid[i_TLids], max(platoonNeededTime_E_end, platoonNeededTime_W_end)) # extend until max of two
                
                    

                """
                    # set new TL for next green light session
                    if halfCycle_isFisrtHalf:
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[0])
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[1])
                        if "halfcycle" in comments: print("half cycle, old phase 1: ", allPhasesOfThisProgramLogicInThisTL[0])
                        if "halfcycle" in comments: print("half cycle, old phase 2: ", allPhasesOfThisProgramLogicInThisTL[1])
                        phase3 = allPhasesOfThisProgramLogicInThisTL[2]
                        if "halfcycle" in comments: print("half cycle, old phase 3: ", phase3)
                        new_minDur = new_GL_dur if (new_GL_dur < phase3.minDur) else phase3.minDur
                        new_maxDur = new_GL_dur if (new_GL_dur > phase3.maxDur) else phase3.maxDur
                        newPhasesArray.append( traci.trafficlight.Phase(new_GL_dur, phase3.state, new_minDur, new_maxDur, phase3.next, phase3.name) )  
                        if "halfcycle" in comments: print("half cycle, new phase 3: ", traci.trafficlight.Phase(new_GL_dur, phase3.state, new_minDur, new_maxDur, phase3.next, phase3.name) )   
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[3])
                        if "halfcycle" in comments: print("half cycle, old phase 4: ", allPhasesOfThisProgramLogicInThisTL[3])
                    else:
                        phase1 = allPhasesOfThisProgramLogicInThisTL[0]
                        if "halfcycle" in comments: print("half cycle, old phase 1: ", phase1)
                        new_minDur = new_GL_dur if (new_GL_dur < phase1.minDur) else phase1.minDur
                        new_maxDur = new_GL_dur if (new_GL_dur > phase1.maxDur) else phase1.maxDur
                        newPhasesArray.append( traci.trafficlight.Phase(new_GL_dur, phase1.state, new_minDur, new_maxDur, phase1.next, phase1.name) )   
                        if "halfcycle" in comments: print("half cycle, new phase 1: ", traci.trafficlight.Phase(new_GL_dur, phase1.state, new_minDur, new_maxDur, phase1.next, phase1.name) )                     
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[1])
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[2])
                        newPhasesArray.append(allPhasesOfThisProgramLogicInThisTL[3])
                        if "halfcycle" in comments: print("half cycle, old phase 2: ", allPhasesOfThisProgramLogicInThisTL[1])
                        if "halfcycle" in comments: print("half cycle, old phase 3: ", allPhasesOfThisProgramLogicInThisTL[2])
                        if "halfcycle" in comments: print("half cycle, old phase 4: ", allPhasesOfThisProgramLogicInThisTL[3])
                    # set for next green light session
                    newLogic = traci.trafficlight.Logic(allProgramLogicInThisTL[0].programID, allProgramLogicInThisTL[0].type, allProgramLogicInThisTL[0].currentPhaseIndex, newPhasesArray, allProgramLogicInThisTL[0].subParameter)
                    if "halfcycle" in comments: print("half cycle, newLogic: ", newLogic)
                    # below two lines together set the new TL for next cycle
                    traci.trafficlight.setCompleteRedYellowGreenDefinition(allTLid[i_TLids], newLogic)
                    traci.trafficlight.setPhase(allTLid[i_TLids], 2 if halfCycle_isFisrtHalf else 0)
                """
                    # if "greenLightEndsDivider" in comments: print("\n ------------------------  END of Section to decide extend current green light or not ------------------------")
                 




                """reference:
                [getRedYellowGreenState]: GGGggrrrrrGGGggrrrrr
                [getAllProgramLogics]: [Logic(programID='0', type=0, currentPhaseIndex=0, phases=[Phase(duration=42.0, state='GGGggrrrrrGGGggrrrrr', minDur=42.0, maxDur=42.0, next=()), Phase(duration=3.0, state='yyyyyrrrrryyyyyrrrrr', minDur=3.0, maxDur=3.0, next=()), Phase(duration=42.0, state='rrrrrGGGggrrrrrGGGgg', minDur=42.0, maxDur=42.0, next=()), Phase(duration=3.0, state='rrrrryyyyyrrrrryyyyy', minDur=3.0, maxDur=3.0, next=())], subParameter={})]
                allPhasesOfThisProgramLogicInThisTL: [phases all]: [Phase(duration=42.0, state='GGGggrrrrrGGGggrrrrr', minDur=42.0, maxDur=42.0, next=()), Phase(duration=3.0, state='yyyyyrrrrryyyyyrrrrr', minDur=3.0, maxDur=3.0, next=()), Phase(duration=42.0, state='rrrrrGGGggrrrrrGGGgg', minDur=42.0, maxDur=42.0, next=()), Phase(duration=3.0, state='rrrrryyyyyrrrrryyyyy', minDur=3.0, maxDur=3.0, next=())]
                [phasesTotalAmount]: 4
                """

                # Next (new current) Cycle Traffic Lights System updated. 
                # Section of next Cycle update END.

                
                #############################################################
                #########   transfer variables for new next cycle   #########
                #############################################################
                # transfer for new next cycle, before xxx_eachTLeachFlow_currentCycle is wrote into new values. 
                # Do this at the befining or each cycle except program begins
                # Skip when program just begins (10086) bc at that time data structure is not initialized yet. 
                if  ((cycleDivider[allTLid[i_TLids]] == True) & (initialOnlyOnce[allTLid[i_TLids]] >= 1) ):
                    # Step 4.4: for next cycle
                    NPV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]]                
                    NPV_eachTLeachFlow_allCycles[allTLid[i_TLids]][ cycleNo[allTLid[i_TLids]] ] = NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]]
                    cycleNo[allTLid[i_TLids]] += 1
                    
                    # Step 5.4: for next cycle
                    NDV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] 
                    # Step 6.3: for next cycle
                    AWT_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]] 
                    # Step 7.7: for next cycle
                    NEV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = NEV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] 


               


                
                # Step 2: TL's connected edges
                outgoingEdges = outgoingEdgesOfEachTL[allTLid[i_TLids]]
                incomingEdges = incomingEdgesOfEachTL[allTLid[i_TLids]]
                if "2connectedEdges" in comments: print("\n TL", allTLid[i_TLids], "'s outgoingEdges:", outgoingEdges) # outgoingEdges: [<edge id="C2B2" from="C2" to="C2B2.580.00"/>, <edge id="C2C1" from="C2" to="C2C1.480.00"/>, <edge id="C2C3" from="C2" to="C2C3.480.00"/>, <edge id="C2D2" from="C2" to="C2D2.580.00"/>]            
                if "2connectedEdges" in comments: print("\n TL", allTLid[i_TLids], "'s incomingEdges:", incomingEdges) # incomingEdges: [<edge id="B2C2.580.00" from="B2C2.580.00" to="C2"/>, <edge id="C1C2.480.00" from="C1C2.480.00" to="C2"/>, <edge id="C3C2.480.00" from="C3C2.480.00" to="C2"/>, <edge id="D2C2.580.00" from="D2C2.580.00" to="C2"/>]
                

                # Step 4: record throughput of each TL each flow: NPV_t(F(sou,tgt))
                # Step 4.1: prepare data structure for NPV_t(F(sou,tgt)), do it only once when program starts 
                # and set it to 0 every time when cycles begin
                # prepare data structure to record NPV of each TL each flow
                # Added: prepare data structure for NDV # Step 5.1
                # Added: prepare data structure for AWT # Step 6.1
                # Added: prepare data structure for NEV # Step 7.1
                if ( initialOnlyOnce[allTLid[i_TLids]] == 0 ) | ( cycleDivider[allTLid[i_TLids]] == True  ):
                    if "4prepareFlowSouTgtDataStructure" in comments: print("\n -----\nPrepare Data Structure Section:\n")
                    flowSouTgt = {}
                    flowSouTgt_NDVspecial = {} # Step 5.1 
                    flowSouTgt_AWTspecial = {} # Step 6.1 
                    for inEdge in incomingEdges:
                        # Below 2 are old when has reduntant connecting turning area
                        # sourceEdge = helper_nearbyEdgesGetIDs(True, False, inEdge) # True for incoming edge
                        #sourceEdge = inEdge.getFromNode().getID() # incomingEdges: [<edge id="A1A0.480.00" from="A1A0.480.00" to="A0"/>, <edge id="B0A0.580.00" from="B0A0.580.00" to="A0"/>, <edge id="bottom0A0" from="bottom0" to="A0"/>, <edge id="left0A0" from="left0" to="A0"/>]
                        # Below 1 are NEW after fix the reduntant connecting turning area issue
                        sourceEdge = inEdge.getID() # TL C2 's incomingEdges: [<edge id="B2C2" from="B2" to="C2"/>, <edge id="C1C2" from="C1" to="C2"/>, <edge id="C3C2" from="C3" to="C2"/>, <edge id="D2C2" from="D2" to="C2"/>]                      
                        targetEdgeAll = {}
                        targetEdgeAll_NDVspecial = {} # Step 5.1 
                        targetEdgeAll_AWTspecial = {} # Step 6.1 
                        for outEdge in outgoingEdges:
                            # Below 2 are old when has reduntant connecting turning area
                            # targetEdge = helper_nearbyEdgesGetIDs(False, True, outEdge) # True for outgoing edge
                            #targetEdge = outEdge.getToNode().getID()
                            # Below 1 are NEW after fix the reduntant connecting turning area issue
                            targetEdge = outEdge.getID()
                            targetEdgeAll[targetEdge] = 0
                            targetEdgeAll_NDVspecial[targetEdge] = [] # Step 5.1, to maintain a list of delayed v.
                            targetEdgeAll_AWTspecial[targetEdge] = {} # Step 6.1, to maintain a dic of delayed v.
                        if "4prepareFlowSouTgtDataStructure" in comments: print("\n targetEdgeAll:", targetEdgeAll)
                        if "4prepareFlowSouTgtDataStructure" in comments: print("\n targetEdgeAll_NDVspecial:", targetEdgeAll_NDVspecial) # Step 5.1 
                        if "4prepareFlowSouTgtDataStructure" in comments: print("\n targetEdgeAll_AWTspecial:", targetEdgeAll_AWTspecial) # Step 6.1 
                        flowSouTgt[sourceEdge] = targetEdgeAll
                        flowSouTgt_NDVspecial[sourceEdge] = targetEdgeAll_NDVspecial # Step 5.1, to maintain a list of delayed v.
                        flowSouTgt_AWTspecial[sourceEdge] = targetEdgeAll_AWTspecial # Step 6.1, to maintain a dic of delayed v.
                        if "4prepareFlowSouTgtDataStructure" in comments: print("\n flowSouTgt:", flowSouTgt)
                        if "4prepareFlowSouTgtDataStructure" in comments: print("\n flowSouTgt_NDVspecial:", flowSouTgt_NDVspecial) # Step 5.1 
                        if "4prepareFlowSouTgtDataStructure" in comments: print("\n flowSouTgt_AWTspecial:", flowSouTgt_AWTspecial) # Step 6.1 
                    NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] = flowSouTgt
                    NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] = flowSouTgt_NDVspecial # Step 5.1: initial NDV data structure.
                    #AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]] = flowSouTgt_AWTspecial # Step 6.1: initial AWT data structure, one more level than NDV.
                    NEV_eachTLeachFlow_currentCycle[allTLid[i_TLids]] = flowSouTgt_ofAllTLs # Step 7.1: initial NEV data structure. It must use this as it needs all TLs, cannot flowSouTgt.                    
                    if ( initialOnlyOnce[allTLid[i_TLids]] == 0 ):  # do it only once when program starts, since it will be overrided in afterwards cycles 
                        AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]] = flowSouTgt_AWTspecial # Step 6.1: initial AWT data structure, one more level than NDV. Only once since we need to track delayed steps(seconds) accumulatively.
                        NPV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = flowSouTgt 
                        NDV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = flowSouTgt_NDVspecial # Step 5.1: initial NDV data structure.
                        AWT_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = flowSouTgt_AWTspecial # Step 6.1: initial AWT data structure, one more level than NDV.
                        NEV_eachTLeachFlow_previousCycle[allTLid[i_TLids]] = flowSouTgt_ofAllTLs # Step 7.1: initial NEV data structure.  It must use this as it needs all TLs, cannot flowSouTgt.                        
                    if "4prepareNxVDataStructure" in comments: print("\n NPV_eachTLeachFlow_currentCycle data structure preparation:", NPV_eachTLeachFlow_currentCycle)
                    if "4prepareNxVDataStructure" in comments: print("\n NPV_eachTLeachFlow_previousCycle data structure preparation:", NPV_eachTLeachFlow_previousCycle)
                    if "4prepareNxVDataStructure" in comments: print("\n NDV_eachTLeachFlow_currentCycle data structure preparation:", NDV_eachTLeachFlow_currentCycle) # Step 5.1 
                    if "4prepareNxVDataStructure" in comments: print("\n NDV_eachTLeachFlow_previousCycle data structure preparation:", NDV_eachTLeachFlow_previousCycle) # Step 5.1 
                    if "4prepareNxVDataStructure" in comments: print("\n AWT_eachTLeachFlow_currentCycle data structure preparation:", AWT_eachTLeachFlow_currentCycle) # Step 6.1 
                    if "4prepareNxVDataStructure" in comments: print("\n AWT_eachTLeachFlow_previousCycle data structure preparation:", AWT_eachTLeachFlow_previousCycle) # Step 6.1
                    if "4prepareNxVDataStructure" in comments: print("\n NEV_eachTLeachFlow_currentCycle data structure preparation:", NEV_eachTLeachFlow_currentCycle) # Step 7.1
                    if "4prepareNxVDataStructure" in comments: print("\n NEV_eachTLeachFlow_previousCycle data structure preparation:", NEV_eachTLeachFlow_previousCycle) # Step 7.1                     
                    initialOnlyOnce[allTLid[i_TLids]] += 1
                    if "4prepareFlowSouTgtDataStructure" in comments: print("\n Prepare Data Structure Section END.\n------\n")


                if ((cycleDivider[allTLid[i_TLids]] == True) & (initialOnlyOnce[allTLid[i_TLids]] >= 1) ):
                    cycleDivider[allTLid[i_TLids]] = False # it's true when first step of new cycle, and set it back to false at the end of this first step of new cycle
                    if "core" in comments: print("\n cycleDivider[", allTLid[i_TLids], "]", cycleDivider[allTLid[i_TLids]]  , ", has been changed back to False.")
                    cycle_ctr_totally += 1
                # Step 11.2.3
                if (halfCycleDivider[allTLid[i_TLids]] == True) :
                    halfCycleDivider[allTLid[i_TLids]] = False 
                    if "core" in comments: print("\n halfCycleDivider[", allTLid[i_TLids], "]", halfCycleDivider[allTLid[i_TLids]]  , ", has been changed back to False.")
                # Step 11.3.Temp check point 4
                if (greenLightEndsDivider[allTLid[i_TLids]] == True) :
                    greenLightEndsDivider[allTLid[i_TLids]] = False 
                    if "core" in comments: print("\n greenLightEndsDivider[", allTLid[i_TLids], "]", greenLightEndsDivider[allTLid[i_TLids]]  , ", has been changed back to False.")


                # Step 3: record throughput of each TL
                allVehiclesAtIncomingEdges = []
                allVehiclesAtOutgoingEdges = []
                countedVehicles = [] # to be removed after TP + 1.
                # Step 4.0: each vehilce's in and out (source and target) edges when pass each TL. 
                vehivleInOutEdges = {} # Step 4. Temporary for current TL current Step only.
                # Step 2 & 3: collect all vehicles
                for edges_in_i in range(len(incomingEdges)): # collect all vehicles in incoming edges
                    #get vehicle IDs
                    incomingEdgeID = incomingEdges[edges_in_i].getID()
                    v_IDs = traci.edge.getLastStepVehicleIDs(incomingEdgeID) # get vehilces in incoming edges
                    allVehiclesAtIncomingEdges += (v_IDs)
                    if "3throughput" in comments: print("\n allVehiclesAtIncomingEdges : ", allVehiclesAtIncomingEdges, " at edge (accumulative): ", incomingEdgeID)
                    # Step 4.2: get (vehicle ID: {source edge ID, target edge ID} )
                    for v_IDs_i in v_IDs:
                        #thisVehicleWholeRoute = trimUnnecessaryCharsOfRoutes(traci.vehicle.getRoute(v_IDs_i))
                        thisVehicleWholeRoute = traci.vehicle.getRoute(v_IDs_i)
                        if "4NPV_vehivleInOutEdges" in comments: print("\n The vehicle ", v_IDs_i, "'s whole route (all edges): ", thisVehicleWholeRoute)
                        outgoingEdgeID = 0
                        for edge_i in thisVehicleWholeRoute:
                            if edge_i == incomingEdgeID: # (Assuming v pass this TL only once)
                                index = thisVehicleWholeRoute.index(edge_i)
                                if len(thisVehicleWholeRoute) > index +1: # Now it is "+1" after change road net TL area. It was "+2" to avoid out of range bug
                                    outgoingEdgeID = thisVehicleWholeRoute[ index + 1 ] #Now it is "+1" after change road net TL area. Old: "+1 is the wrong because +1 is the TL, +2 is next outgoing edge."
                                else: 
                                    outgoingEdgeID = 'null' # In this case this v's routes finish before going outside the TL.
                        vehivleInOutEdges[v_IDs_i] = {'source':incomingEdgeID,'target':outgoingEdgeID}
                        if "4NPV_vehivleInOutEdges" in comments: print("\n vehivleInOutEdges: ", vehivleInOutEdges)
                for edges_out_i in range(len(outgoingEdges)): # collect all vehicles in outgoing edges
                    outgoingEdgeID = outgoingEdges[edges_out_i].getID()
                    v_IDs = traci.edge.getLastStepVehicleIDs(outgoingEdgeID) # get vehilces in outgoing edges
                    allVehiclesAtOutgoingEdges += (v_IDs)
                    if "3throughput" in comments: print("\n allVehiclesAtOutgoingEdges : ", allVehiclesAtOutgoingEdges, " at edge (accumulative): ", outgoingEdgeID)
                    # Step 4 refine by adding vehivleInOutEdges for Vs in outgoingEdges
                    for v_IDs_i in v_IDs:
                        thisVehicleWholeRoute = traci.vehicle.getRoute(v_IDs_i)
                        if "4NPV_vehivleInOutEdges" in comments: print("\n The vehicle ", v_IDs_i, "'s whole route (all edges): ", thisVehicleWholeRoute)
                        incomingEdgeID = 0
                        for edge_i in thisVehicleWholeRoute:
                            if edge_i == outgoingEdgeID: # (Assuming v pass this TL only once)
                                index = thisVehicleWholeRoute.index(edge_i)
                                if index -1 >= 0: # Now it is "+1" after change road net TL area. It was "+2" to avoid out of range bug
                                    incomingEdgeID = thisVehicleWholeRoute[ index - 1 ] #Now it is "+1" after change road net TL area. Old: "+1 is the wrong because +1 is the TL, +2 is next outgoing edge."
                                else: 
                                    incomingEdgeID = 'null' # In this case this v's routes finish before going outside the TL.
                        vehivleInOutEdges[v_IDs_i] = {'source':incomingEdgeID,'target':outgoingEdgeID}
                        if "4NPV_vehivleInOutEdges" in comments: print("\n vehivleInOutEdges: ", vehivleInOutEdges)
                # Step 5.2: Add all v in incoming edges into NDV 
                if len(allVehiclesAtIncomingEdges) > 0:
                    for vehicle_i in allVehiclesAtIncomingEdges:
                        if vehicle_i in vehivleInOutEdges: # if exists. Otherwise null index err. 
                            incomingEdgeID = vehivleInOutEdges[vehicle_i]["source"]
                            outgoingEdgeID = vehivleInOutEdges[vehicle_i]["target"]
                            if "5NDV" in comments: print("\n\n\nAdding into NDV: vehicle_i:",vehicle_i, "incomingEdgeID:",incomingEdgeID, "outgoingEdgeID:",outgoingEdgeID)
                            if outgoingEdgeID != "null":
                                if vehicle_i not in NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID][outgoingEdgeID]:
                                    NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID][outgoingEdgeID].append(vehicle_i)
                                    if "5NDV" in comments: print("Added into NDV: vehicle_i:",vehicle_i, "Done.")
                                else: 
                                    if "5NDV" in comments: print("Added into NDV: vehicle_i:",vehicle_i, "Not needed.")
                # Step 6.2: AWT has same vehicles as NDV; Copy NDV v into AWT while adding one more data structure level                
                if len(NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]]) > 0:
                    for incomingEdgeID_i in NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]]:
                        if incomingEdgeID_i in AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]]:
                            if len(NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_i]) > 0:
                                for outgoingEdgeID_i in NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_i]:
                                    if "6AWT" in comments: print("\nAWT:", allTLid[i_TLids], "Flow(",incomingEdgeID_i,",",outgoingEdgeID_i,"):")
                                    if "6AWT" in comments: print("        Vehicles in incoming edges of this flow:",NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_i][outgoingEdgeID_i])
                                    if outgoingEdgeID_i in AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_i]:
                                        if len(NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_i][outgoingEdgeID_i]) > 0:
                                            for vehicle_i in NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_i][outgoingEdgeID_i]:
                                                if vehicle_i in AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_i][outgoingEdgeID_i]:
                                                    AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_i][outgoingEdgeID_i][vehicle_i] += 1 # if exist then the step recorder add 1. 
                                                    if "6AWT" in comments: print("AWT: vehicle_i:",vehicle_i, "exists. Add AWT by 1.")
                                                else:    
                                                    AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_i][outgoingEdgeID_i][vehicle_i] = 0 # if not exist then add this v. 
                                                    if "6AWT" in comments: print("Added into AWT: vehicle_i:",vehicle_i, "Done.")
                                                if "6AWT" in comments: print("AWT_eachTLeachFlow_currentCycle[",allTLid[i_TLids],"][",incomingEdgeID_i,"][",outgoingEdgeID_i,"] :",AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID_i][outgoingEdgeID_i] ) 
                if "6AWT" in comments: print("\n\n\nALL AWT_eachTLeachFlow_currentCycle[",allTLid[i_TLids],"] :",AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]] ) 
                # Step 5.2: Remove all v in outgoing edges from NDV 
                if len(allVehiclesAtOutgoingEdges) > 0:
                    for vehicle_i in allVehiclesAtOutgoingEdges:
                        if vehicle_i in vehivleInOutEdges: # if exists. Otherwise null index err. 
                            incomingEdgeID = vehivleInOutEdges[vehicle_i]["source"]
                            outgoingEdgeID = vehivleInOutEdges[vehicle_i]["target"]
                            if "5NDV" in comments: print("\n\n\nRemoving from NDV: vehicle_i:",vehicle_i, "incomingEdgeID:",incomingEdgeID, "outgoingEdgeID:",outgoingEdgeID)
                            if outgoingEdgeID != "null":
                                try:
                                    if vehicle_i in NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID][outgoingEdgeID]:
                                        NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID][outgoingEdgeID].remove(vehicle_i)            
                                        if "5NDV" in comments: print("Removed from NDV: vehicle_i:",vehicle_i, "Done.")
                                        # Step 6.2: Remove all v in outgoing edges from AWT
                                        AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID][outgoingEdgeID].pop(vehicle_i) 
                                        if "6AWT" in comments: print("Removed from AWT: vehicle_i:",vehicle_i, "Done.")
                                        # Step 6.2.
                                    else:
                                        if "5NDV" in comments: print("Removed from NDV: vehicle_i:",vehicle_i, "Not needed.")
                                except:
                                    if "5NDV" in comments: print("Removed from NDV: vehicle_i:",vehicle_i, "Failed.")
                if "6AWT" in comments: print("\n\n\nALL (after removing passed V) AWT_eachTLeachFlow_currentCycle[",allTLid[i_TLids],"] :",AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]] ) 




                # Step 3: record throughput (for Step 3)
                if len(allVehiclesAtIncomingEdges_previousAllSteps[allTLid[i_TLids]]) > 0: # record throughput   
                    for vehicle_i in allVehiclesAtIncomingEdges_previousAllSteps[allTLid[i_TLids]]:
                        if "3throughput" in comments: print("\n vehicle_i who will be counted for TP:", vehicle_i)
                        # Step 3: Logic: if v was in all previous incoming edges and is in current outgoing edges then it means it just passed the intersection.
                        if (vehicle_i not in allVehiclesAtIncomingEdges) & (vehicle_i in  allVehiclesAtOutgoingEdges) & (vehicle_i not in allVehiclesAtOutgoingEdges_previous1Step[allTLid[i_TLids]]):
                            throughput[allTLid[i_TLids]] += 1 # Throughput of this TL +1
                            countedVehicles.append(vehicle_i)
                            # Step 4.3: record throughput of each TL each flow: NPV_t(F(sou,tgt))
                            incomingEdgeID = vehivleInOutEdges[vehicle_i]["source"]
                            outgoingEdgeID = vehivleInOutEdges[vehicle_i]["target"]
                            if "3throughput" in comments: print("\n incomingEdgeID:", incomingEdgeID, "outgoingEdgeID:", outgoingEdgeID)
                            if outgoingEdgeID != "null":
                                NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID][outgoingEdgeID] += 1
                                if "3throughput" in comments: print("\n NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID][outgoingEdgeID] ", NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID][outgoingEdgeID])
                # Step 3: remove it so when this vehilce pass this TL again it'll be counted.
                if len(countedVehicles) > 0:
                    for vehicle_i in countedVehicles:
                        allVehiclesAtIncomingEdges_previousAllSteps[allTLid[i_TLids]].remove(vehicle_i) 
                        # Step 5.3: Remove all v which has been counted (which means it passed) from NDV
                        if vehicle_i in vehivleInOutEdges: # if exists. Otherwise null index err.
                            incomingEdgeID = vehivleInOutEdges[vehicle_i]["source"]
                            outgoingEdgeID = vehivleInOutEdges[vehicle_i]["target"]
                            if outgoingEdgeID != "null":
                                if vehicle_i in NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID][outgoingEdgeID]:
                                    NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]][incomingEdgeID][outgoingEdgeID].remove(vehicle_i)
                # Step 3: record all vehicles who will go in TL to calculate throughput in next step # for next step
                if len(allVehiclesAtIncomingEdges) > 0: 
                    for vehicle_i in allVehiclesAtIncomingEdges:
                        if vehicle_i not in allVehiclesAtIncomingEdges_previousAllSteps[allTLid[i_TLids]]:
                            allVehiclesAtIncomingEdges_previousAllSteps[allTLid[i_TLids]].append(vehicle_i)
                # record for next step
                # Step 3: 
                allVehiclesAtOutgoingEdges_previous1Step[allTLid[i_TLids]] = allVehiclesAtOutgoingEdges
                # Step 4.4: phasePreviousStep[allTLid[i_TLids]] = phaseCurrentStep for next step # update every step
                phasePreviousStep[allTLid[i_TLids]] = phaseCurrentStep
                


                if "3throughput" in comments: print("\n --------------\nResult of this simulation step:" )
                if "3throughputAll" in comments: print("\n allVehiclesAtIncomingEdges:", allVehiclesAtIncomingEdges)
                if "3throughputAll" in comments: print("\n allVehiclesAtIncomingEdges_previousAllSteps:", allVehiclesAtIncomingEdges_previousAllSteps)
                if "3throughputAll" in comments: print("\n allVehiclesAtOutgoingEdges_previous1Step:", allVehiclesAtOutgoingEdges_previous1Step)
                if "3throughputC2" in comments: print("\n allVehiclesAtIncomingEdges_previousAllSteps C2:", allVehiclesAtIncomingEdges_previousAllSteps[allTLid[i_TLids]])
                if "3throughputC2" in comments: print("\n allVehiclesAtOutgoingEdges_previous1Step C2:", allVehiclesAtOutgoingEdges_previous1Step[allTLid[i_TLids]])
                if "3throughput" in comments: print("\n allVehiclesAtOutgoingEdges:", allVehiclesAtOutgoingEdges)
                if "core" in comments: print("\n throughput after record:", throughput)

                if "core" in comments: print("\n NPV_eachTLeachFlow_currentCycle after record:", NPV_eachTLeachFlow_currentCycle)
                if "4NPVresult" in comments: print("\n NPV_eachTLeachFlow_currentCycle after record C2:", NPV_eachTLeachFlow_currentCycle[allTLid[i_TLids]])
                if "4NPVresult" in comments: print("\n NPV_eachTLeachFlow_allCycles after record C2:", NPV_eachTLeachFlow_allCycles[allTLid[i_TLids]])

                if "core" in comments: print("\n NDV_eachTLeachFlow_currentCycle after record:", NDV_eachTLeachFlow_currentCycle)
                if "5NDV" in comments: print("\n NDV_eachTLeachFlow_currentCycle after record C2:", NDV_eachTLeachFlow_currentCycle[allTLid[i_TLids]])
                if "5NDV" in comments: print("\n NDV_eachTLeachFlow_previousCycle after record C2:", NDV_eachTLeachFlow_previousCycle[allTLid[i_TLids]])

                if "core" in comments: print("\n AWT_eachTLeachFlow_currentCycle after record:", AWT_eachTLeachFlow_currentCycle)
                if "6AWT" in comments: print("\n AWT_eachTLeachFlow_currentCycle after record C2:", AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]])
                if "6AWT" in comments: print("\n AWT_eachTLeachFlow_currentCycle after record C2:", AWT_eachTLeachFlow_currentCycle[allTLid[i_TLids]])

                if "core" in comments: print("\n NEV_eachTLeachFlow_currentCycle after record:", NEV_eachTLeachFlow_currentCycle)
                if "7getNEV" in comments: print("\n NEV_eachTLeachFlow_currentCycle after record C2:", NEV_eachTLeachFlow_currentCycle[allTLid[i_TLids]])
                if "7getNEV" in comments: print("\n NEV_eachTLeachFlow_currentCycle after record C2:", NEV_eachTLeachFlow_currentCycle[allTLid[i_TLids]])

                


        step += 1
    
    print("step: ", step)
    print("cycle_ctr_totally: ", cycle_ctr_totally) 
    print("re_schedule_when_enough_counter_totally: ",re_schedule_when_enough_counter_totally)  
    print("re_schedule_when_NOT_enough_counter_totally: ", re_schedule_when_NOT_enough_counter_totally) 
    traci.close()
    sys.stdout.flush()

def helper_getAllIntersectionsXY(net_xml_file):
    tree = ET.parse(net_xml_file) # get the file
    root = tree.getroot() # loc the root
    allIntersectionsXY = dict()
    for tripinfo in root.findall('junction'):
        id = tripinfo.get('id')
        x = tripinfo.get('x')
        y = tripinfo.get('y')
        allIntersectionsXY[id] = tuple((x,y))
    return allIntersectionsXY

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
    print("All Vehicles Waiting Time Total:", vWaitingTimeTotal)
    print("All Vehicles Amount:", vCount)
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

    allIntersectionsXY = helper_getAllIntersectionsXY("netfiles/dayuan.grid.1.net.xml")
    

    # datetime object containing current date and time
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")
    print("date and time =", dt_string)	

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    # Keep use the static TL as default TL logic then my alg adjust it
    tripinfo_output_filename = "output/tripinfo.grid.myTL.vTypeDist.simpla" +dt_string+".xml"
    emission_output_filename = "output/emission.myTL." +dt_string+".xml"
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
    
