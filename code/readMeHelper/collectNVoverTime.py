import csv
import xml.etree.ElementTree as ET
import collections

def collectNumberOfVehiclesOverTime(input_file, output_file, output_file_accu):
    tree = ET.parse(input_file) # get the file
    root = tree.getroot() # loc the root

    NVoverT = dict()
    FinishedNVoverT = dict()
    AccuFinishedV = dict()

    for tripinfo in root.findall('tripinfo'):
        vDepartTime = tripinfo.get('depart')
        vArrivalTime = tripinfo.get('arrival')
        vDepartTime = int(float(vDepartTime))
        vArrivalTime = int(float(vArrivalTime))
        for time in range(vDepartTime, vArrivalTime + 1):
            if time in NVoverT.keys():
                NVoverT[time] += 1
            else:
                NVoverT[time] = 1 
        if vDepartTime in FinishedNVoverT.keys():
            FinishedNVoverT[vDepartTime] += 1
        else:
            FinishedNVoverT[vDepartTime] = 1
    
    NVoverT = collections.OrderedDict(sorted(NVoverT.items()))
    FinishedNVoverT = collections.OrderedDict(sorted(FinishedNVoverT.items()))

    total_finished_v_accu = 0
    for key, value in FinishedNVoverT.items():
        total_finished_v_accu += value
        AccuFinishedV[key] = total_finished_v_accu 


    with open(output_file, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Time', 'Number of alive vehicles at this time'])
        for key, value in NVoverT.items():
            csv_writer.writerow([key, value])

    with open(output_file_accu, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Time', 'Accu Number of Finished vehicles at this time'])
        for key, value in AccuFinishedV.items():
            csv_writer.writerow([key, value])
            

input_file = 'output/tripinfo.grid.myTL.vTypeDist.simpla.xml'
output_file = 'output/NumberOfVehiclesOverTime_myTL.csv'
output_file_accu = 'output/NumberOfVehiclesOverTime_myTL_accu.csv'
collectNumberOfVehiclesOverTime(input_file, output_file, output_file_accu)

input_file = 'output/tripinfo.grid.staticTL.vTypeDist.simpla.xml'
output_file = 'output/NumberOfVehiclesOverTime_static.csv'
output_file_accu = 'output/NumberOfVehiclesOverTime_static_accu.csv'
collectNumberOfVehiclesOverTime(input_file, output_file, output_file_accu)

input_file = 'output/tripinfo.grid.ATL.vTypeDist.simpla.xml'
output_file = 'output/NumberOfVehiclesOverTime_ATL.csv'
output_file_accu = 'output/NumberOfVehiclesOverTime_ATL_accu.csv'
collectNumberOfVehiclesOverTime(input_file, output_file, output_file_accu)