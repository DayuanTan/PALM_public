This file explains how to generate all needed files before running.

[Table 1: Files used.](FilesUsed.md)

---
---
---

# Below is:
# total_time=3600, ALT_max_gap=5, p=0.5 4x5=20Tls 200x150m No --grid.attach-length


# **Step 1: Net file**

## **1.1 For staticTL and myTL**: 

### **Instruction**:


``` netfiles$ netgenerate --grid --grid.x-number=4 --grid.y-number=5 --grid.x-length=200 --grid.y-length=150 --output-file=dayuan.grid.1.net.xml -L 2 --tls.guess true```
```Success.```


***Output***:
It generated file ***"dyt_grid/netfiles/dayuan.grid.1.net.xml"***


## **1.2 For ATL**: 


### **1.2.1 Instruction**:
```dyt_grid/netfiles/ATL$ netconvert -s ../dayuan.grid.1.net.xml --plain-output-prefix plain_ATL```

```Success.```

***Input***: ***"dyt_grid/netfiles/dayuan.grid.1.net.xml".***

***Output***: 
It generated 4 output files: 
- dyt_grid/netfiles/ATL/ 
  - "plain_ATL.con.xml", 
  - "plain_ATL.edg.xml", 
  - "plain_ATL.nod.xml", 
  - "plain_ATL.tll.xml".


 ## 1.2.2 Then **Instruction**:

```dyt_grid/netfiles/ATL$ netconvert -e plain_ATL.edg.xml -n plain_ATL.nod.xml -x plain_ATL.con.xml -o dayuan.grid.3.updatedGenerated.ATL.net.xml --ignore-errors.edge-type --tls.default-type actuated```

```Success.```

***Input***: ***"dyt_grid/netfiles/ATL/ 3 plain_ATL.XXX.xml".***

***Output***: 
It generated 1 file ***dyt_grid/netfiles/ATL/"dayuan.grid.3.updatedGenerated.ATL.net.xml"***. 


### **1.2.3 Set show-detectors true in net file tlLogic section**.

Copy file *"dayuan.grid.3.**updatedGenerated**.ATL.net.xml"* and change it then save as *"dayuan.grid.3.**updatedByHand**.ATL.net.xml"*. Go to \<tlLogic> section. It looks like this:
```
    <tlLogic id="A0" type="actuated" programID="0" offset="0">
        <phase duration="42" state="GGGggrrrrrGGGggrrrrr" minDur="5" maxDur="50"/>
        <phase duration="3"  state="yyyyyrrrrryyyyyrrrrr"/>
        <phase duration="42" state="rrrrrGGGggrrrrrGGGgg" minDur="5" maxDur="50"/>
        <phase duration="3"  state="rrrrryyyyyrrrrryyyyy"/>
    </tlLogic>
    <tlLogic id="A1" type="actuated" programID="0" offset="0">
        <phase duration="42" state="GGGggrrrrrGGGggrrrrr" minDur="5" maxDur="50"/>
        <phase duration="3"  state="yyyyyrrrrryyyyyrrrrr"/>
        <phase duration="42" state="rrrrrGGGggrrrrrGGGgg" minDur="5" maxDur="50"/>
        <phase duration="3"  state="rrrrryyyyyrrrrryyyyy"/>
    </tlLogic>
```

Then add following parameters to \<tlLogic> section and change it as follows: 
```
    <tlLogic id="A0" type="actuated" programID="0" offset="0">
        <param key="show-detectors" value="true"/>
        <param key="file" value="../../output/dayuan.grid.ATL.detectorA0.log.xml"/>
        <param key="freq" value="300"/>
        <param key="max-gap" value="5.0"/>
        <phase duration="42" state="GGGggrrrrrGGGggrrrrr" minDur="5" maxDur="50"/>
        <phase duration="3"  state="yyyyyrrrrryyyyyrrrrr"/>
        <phase duration="42" state="rrrrrGGGggrrrrrGGGgg" minDur="5" maxDur="50"/>
        <phase duration="3"  state="rrrrryyyyyrrrrryyyyy"/>
    </tlLogic>
    <tlLogic id="A1" type="actuated" programID="0" offset="0">
        <param key="show-detectors" value="true"/>
        <param key="file" value="../../output/dayuan.grid.ATL.detectorA1.log.xml"/>
        <param key="freq" value="300"/>
        <param key="max-gap" value="5.0"/>
        <phase duration="42" state="GGGggrrrrrGGGggrrrrr" minDur="5" maxDur="50"/>
        <phase duration="3"  state="yyyyyrrrrryyyyyrrrrr"/>
        <phase duration="42" state="rrrrrGGGggrrrrrGGGgg" minDur="5" maxDur="50"/>
        <phase duration="3"  state="rrrrryyyyyrrrrryyyyy"/>
    </tlLogic>
```

```Remember to edit the log file name for each TL.```

And repeat for all TL intersections.

I checked the "dayuan.grid.3.updatedByHand.ATL.net.xml" and "dayuan.grid.1.net.xml", they only have \<tlLogic> section diff. 


# **Step 2 Trip file**


    Notes: 

    **Traffic Demand** is the word we use to descripte how many vehicles we will have, types of vehicles, the route of each vehicles.

    A **trip** is a vehicle movement from one place to another defined by the starting edge (street), the destination edge, and the departure time.

    A **route** is an expanded trip, that means, that a route definition contains not only the first and the last edge, but all edges the vehicle will pass.


Write ***vTypes file*** by hand. ***dyt_grid/netfiles/"dayuan.grid.me.add.HV.AH.vTypeDist.xml".*** 

To add more vTypes. Now have 7 vTypes:
- myvTypeCar_platoon, 
- myvTypeBus_platoon, 
- myvTypeTaxi_platoon, 
- myvTypeCar_human_nojoinP, 
- myvTypeBus_human_nojoinP, 
- myvTypeTaxi_human_nojoinP, 
- myvTypeEmergency_human_nojoinP.  

## **For staticTL, ATL and myTL**: 

```dyt_grid/netfiles$ python3 ../../../tools/randomTrips.py -n dayuan.grid.1.net.xml -o dayuan.grid.2.vTypeDist.simpla.trips.xml --period 0.5 --additional-file dayuan.grid.me.add.HV.AV.vTypeDist.xml --fringe-factor 1000000000 --trip-attributes="type=\"typedist1\""```

||
|-|
|Add 'python3' before it to avoid 'code for hash sha512 was not found' 'ValueError: unsupported hash type sha512' error.|
||

***Input***:
It has 2 inputs:
***"dyt_grid/netfiles/dayuan.grid.1.net.xml"***
***"dyt_grid/netfiles/dayuan.grid.me.add.HV.AV.vTypeDist.xmll"***.

***Output***:
It has only one output:
***"dyt_grid/netfiles/dayuan.grid.2.vTypeDist.simpla.trips.xml"***. Which is the trip file used by all 3 algorithms.


# **Step 3 Route file**

## **3. 1 For staticTL, ATL and myTL**: 

We will run DUAROUTER by hand to generate the new route file.

The old one is called by randomTrips.py auto (**old record, not use here**:):
```python
dyt_grid/netfiles$ ../../../tools/randomTrips.py -n dayuan.grid.1.net.xml -o dayuan.grid.2.vTypeDist.trips.xml -r dayuan.grid.2.vTypeDist.rou.xml --period 0.2 --additional-file dayuan.grid.me.add.vTypeDist.xml --fringe-factor 100 --trip-attributes="type=\"typedist1\""

calling /usr/local/opt/sumo/share/sumo/bin/duarouter -n dayuan.grid.1.net.xml -r dayuan.grid.2.vTypeDist.trips.xml -o dayuan.grid.2.vTypeDist.rou.xml --ignore-errors --begin 0 --end 3600 --no-step-log --no-warnings --additional-files dayuan.grid.me.add.vTypeDist.xml

Success.
```


BUT here we call it **by hand**:

```netfiles$ duarouter -n dayuan.grid.1.net.xml -r dayuan.grid.2.vTypeDist.simpla.trips.xml -o "route_with_platoon/dayuan.grid.4.simpla.duarouter.rou.xml" --ignore-errors --begin 0 --end 3600 --no-step-log --no-warnings --additional-files dayuan.grid.me.add.HV.AH.vTypeDist.xml --vtype-output="route_with_platoon/dayuan.grid.4.simpla.duarouter.vType.xml"```

```Success.```

 

***Input***:

***"dyt_grid/netfiles/dayuan.grid.1.net.xml"***
***"dyt_grid/netfiles/dayuan.grid.me.add.HV.AV.vTypeDist.xmll"***.
***"dyt_grid/netfiles/dayuan.grid.2.vTypeDist.simpla.trips.xml"***

***Output***:

It generated 3 files:

***"dyt_grid/netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.rou.xml"*** (used by all algorithms),

***"dyt_grid/netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.rou.alt.xml"*** (no used),

***"dyt_grid/netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.vType.xml"*** (temp used).

<br>


## **3.2 Then modify platoon vType file by hand:**


Copy ***"dyt_grid/netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.vType.xml"*** and save as ***"dyt_grid/netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouterModifiedByHand.vType.xml"***. 

Add below 3*4 vType for platoon: (Don't need to worry about vType distribution which has been guaranteed in trip files.)
```

<!--add following vType for simpla. minGap default it 2.5m.-->
    <vType id="myvTypeCar_platoon_leader" length="4.50" maxSpeed="35.00"  vClass="passenger" guiShape="passenger" color="0,128,0"/><!--green-->
    <vType id="myvTypeTaxi_platoon_leader" length="4.50" maxSpeed="35.00"  vClass="taxi" guiShape="passenger" color="0,191,255"/>
    <vType id="myvTypeBus_platoon_leader" length="14.63" maxSpeed="30.00"  vClass="bus" guiShape="bus" color="0,128,0"/>

    <vType id="myvTypeCar_platoon_follower" length="4.50" maxSpeed="40.00"  vClass="passenger" guiShape="passenger" color="0,128,0" minGap="1.0"/>
    <vType id="myvTypeTaxi_platoon_follower" length="4.50" maxSpeed="40.00"  vClass="taxi" guiShape="passenger" color="0,191,255" minGap="1.0"/>
    <vType id="myvTypeBus_platoon_follower" length="14.63" maxSpeed="35.00"  vClass="bus" guiShape="bus" color="0,128,0" minGap="1.0"/>
   
    <vType id="myvTypeCar_platoon_catchup" length="4.50" maxSpeed="45.00"  vClass="passenger" guiShape="passenger" color="0,128,0" minGap="1.0"/>
    <vType id="myvTypeTaxi_platoon_catchup" length="4.50" maxSpeed="45.00"  vClass="taxi" guiShape="passenger" color="0,191,255" minGap="1.0"/>
    <vType id="myvTypeBus_platoon_catchup" length="14.63" maxSpeed="40.00"  vClass="bus" guiShape="bus" color="0,128,0" minGap="1.0"/>
   
    <vType id="myvTypeCar_platoon_catchupFollower" length="4.50" maxSpeed="45.00"  vClass="passenger" guiShape="passenger" color="0,128,0" minGap="1.0"/>
    <vType id="myvTypeTaxi_platoon_catchupFollower" length="4.50" maxSpeed="45.00"  vClass="taxi" guiShape="passenger" color="0,191,255" minGap="1.0"/>
    <vType id="myvTypeBus_platoon_catchupFollower" length="14.63" maxSpeed="40.00"  vClass="bus" guiShape="bus" color="0,128,0" minGap="1.0"/>
   

```

Change \<route file> and \<addition file> (used for all 3 algorithms) in sumocfg:
```
<input>

<route-files value="netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.rou.alt.xml"/>

<additional-files value="netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouterModifiedByHand.vType.xml"/>

</input>
```
All 3 algorithms use 2 sumocfg files, which have only \<net-file ...> are diff. 


There are two more files are only needed for myTL algorithm (They are called in myTL runMe python file.): 
- ***dyt_grid/simpla_configure/ "dayuan.grid.PlatoonVTypes.map"***, 
- ***dyt_grid/simpla_configure/ "dayuan.platoon.cfg.xml".*** 


# Above is:
# total_time=3600, ALT_max_gap=5, p=0.5 4x5=20Tls 200x150m No --grid.attach-length
## If want to change the parameter, need to re-do from Step 2. (Below are not fully steps to generate all files. Just change where we need to change.)
---
---
---


# Below is:
# total_time=3600, ALT_max_gap=5, p=0.4 4x5=20Tls 200x150m No --grid.attach-length


# re-run: 
||
|-|
Copy everything in the base directory *```dyt_grid/netfiles_v3_balabala/netfiles_p0.5_no--grid.attach-length_calledNewRoadNetV2```* to ```"dyt_grid/netfiles"``` and do following inside the directory. Then copy everything in *```"dyt_grid/netfiles"```* back to ```dyt_grid/netfiles_v3_balabala/netfiles_p0.4```. 
||



# **Step 2 Trip file after vTypes** 

## **For staticTL, ATL and myTL**: 


||
|-|
**```Only change``` comparing with the basic version is the ```--period 0.5``` to ```0.4```.**
||


```dyt_grid/netfiles$ python3 ../../../tools/randomTrips.py -n dayuan.grid.1.net.xml -o dayuan.grid.2.vTypeDist.simpla.trips.xml --period 0.4 --additional-file dayuan.grid.me.add.HV.AV.vTypeDist.xml --fringe-factor 1000000000 --trip-attributes="type=\"typedist1\""```

||
|-|
|Add 'python3' before it to avoid 'code for hash sha512 was not found' 'ValueError: unsupported hash type sha512' error.|
||

***Input***:
It has 2 inputs:
***"dyt_grid/netfiles/dayuan.grid.1.net.xml"***
***"dyt_grid/netfiles/dayuan.grid.me.add.HV.AV.vTypeDist.xmll"***.

***Output***:
It has only one output:
***"dyt_grid/netfiles/dayuan.grid.2.vTypeDist.simpla.trips.xml"***. Which is the trip file used by all 3 algorithms.


# **Step 3 Route file**

## **3. 1 For staticTL, ATL and myTL**: 

||
|-|
**```Only change``` comparing with the basic version is the ```directory```.**
||

We will run DUAROUTER by hand to generate the new route file.
 
we call it **by hand**:

```dyt_grid/netfiles$ duarouter -n dayuan.grid.1.net.xml -r dayuan.grid.2.vTypeDist.simpla.trips.xml -o "route_with_platoon/dayuan.grid.4.simpla.duarouter.rou.xml" --ignore-errors --begin 0 --end 3600 --no-step-log --no-warnings --additional-files dayuan.grid.me.add.HV.AH.vTypeDist.xml --vtype-output="route_with_platoon/dayuan.grid.4.simpla.duarouter.vType.xml"```

```Success.```

 

***Input***:

***"dyt_grid/netfiles/dayuan.grid.1.net.xml"***
***"dyt_grid/netfiles/dayuan.grid.me.add.HV.AV.vTypeDist.xmll"***.
***"dyt_grid/netfiles/dayuan.grid.2.vTypeDist.simpla.trips.xml"***

***Output***:

It generated 3 files:

***"dyt_grid/netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.rou.xml"*** (used by all algorithms),

***"dyt_grid/netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.rou.alt.xml"*** (no used),

***"dyt_grid/netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.vType.xml"*** (temp used).

<br>


## **3.2 Then modify platoon vType file by hand:**


||
|-|
**```Only change``` comparing with the basic version is the ```directory```.**
||


Copy ***"dyt_grid/netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.vType.xml"*** and save as ***"dyt_grid/netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouterModifiedByHand.vType.xml"***. 

Add below 3*4 vType for platoon: (Don't need to worry about vType distribution which has been guaranteed in trip files.)
```

<!--add following vType for simpla. minGap default it 2.5m.-->
    <vType id="myvTypeCar_platoon_leader" length="4.50" maxSpeed="35.00"  vClass="passenger" guiShape="passenger" color="0,128,0"/><!--green-->
    <vType id="myvTypeTaxi_platoon_leader" length="4.50" maxSpeed="35.00"  vClass="taxi" guiShape="passenger" color="0,191,255"/>
    <vType id="myvTypeBus_platoon_leader" length="14.63" maxSpeed="30.00"  vClass="bus" guiShape="bus" color="0,128,0"/>

    <vType id="myvTypeCar_platoon_follower" length="4.50" maxSpeed="40.00"  vClass="passenger" guiShape="passenger" color="0,128,0" minGap="1.0"/>
    <vType id="myvTypeTaxi_platoon_follower" length="4.50" maxSpeed="40.00"  vClass="taxi" guiShape="passenger" color="0,191,255" minGap="1.0"/>
    <vType id="myvTypeBus_platoon_follower" length="14.63" maxSpeed="35.00"  vClass="bus" guiShape="bus" color="0,128,0" minGap="1.0"/>
   
    <vType id="myvTypeCar_platoon_catchup" length="4.50" maxSpeed="45.00"  vClass="passenger" guiShape="passenger" color="0,128,0" minGap="1.0"/>
    <vType id="myvTypeTaxi_platoon_catchup" length="4.50" maxSpeed="45.00"  vClass="taxi" guiShape="passenger" color="0,191,255" minGap="1.0"/>
    <vType id="myvTypeBus_platoon_catchup" length="14.63" maxSpeed="40.00"  vClass="bus" guiShape="bus" color="0,128,0" minGap="1.0"/>
   
    <vType id="myvTypeCar_platoon_catchupFollower" length="4.50" maxSpeed="45.00"  vClass="passenger" guiShape="passenger" color="0,128,0" minGap="1.0"/>
    <vType id="myvTypeTaxi_platoon_catchupFollower" length="4.50" maxSpeed="45.00"  vClass="taxi" guiShape="passenger" color="0,191,255" minGap="1.0"/>
    <vType id="myvTypeBus_platoon_catchupFollower" length="14.63" maxSpeed="40.00"  vClass="bus" guiShape="bus" color="0,128,0" minGap="1.0"/>
   

```

||
|-|
Copy everything in *```"dyt_grid/netfiles"```* back to ```dyt_grid/netfiles_v3_balabala/netfiles_p0.4```. 
||


||
|-|
**When run this parameters set, copy the whole ```dyt_grid/netfiles_v3_balabala/netfiles_p0.4``` to replace the ```dyt_grid/nefiles``` directory to run the ```balabala.runMe.py```.**
||



# Above is:
# total_time=3600, ALT_max_gap=5, p=0.4 4x5=20Tls 200x150m No --grid.attach-length
