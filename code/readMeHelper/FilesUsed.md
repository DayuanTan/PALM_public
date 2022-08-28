

# <span id="table1">Table 1: Files used.</span>

<table  border=1>
  <tr>
    <th>Algs</th>
    <th>net files used</th> 
    <th>trip files used (temp, used to gen route files)</th>
    <th>route files used</th>
    <th>sumocfg</th>
    <th>simpla config</th>
    <th>python files</th>
  </tr>
  <tr>
    <td>Static TL</td>
    <td>netfiles/dayuan.grid.1.net.xml</td> 
    <td rowspan="6">dayuan.grid.me.add.HV.AH.vTypeDist.xml,
    dayuan.grid.2.vTypeDist.simpla.trips.xml
    </td>
    <td rowspan="6">ROUTE FILE: netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.rou.alt.xml,
    <s>TEMP: netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouter.vType.xml</s>,
    V_TYPE FILE: netfiles/route_with_platoon/dayuan.grid.4.simpla.duarouterModifiedByHand.vType.xml</td>
    <td>sumocfg/dayuan.grid.staticTL.vTypeDist.simpla.sumocfg</td>
    <td rowspan="6">simpla_configure/dayuan.platoon.cfg.xml,
    simpla_configure/dayuan.grid.PlatoonVTypes.map</td>
    <td>dayuan.grid.staticTL.vTypeDist.simpla.runMe.py</td>
  </tr>
  <tr>
    <td rowspan = "3">ATL</td>
    <td>temp: netfiles/ATL/plain_ATL.con.xml, plain_ATL.edg.xml, plain_ATL.nod.xml, plain_ATL.tll.xml</td>
    <td rowspan="3">sumocfg/dayuan.grid.ATL.vTypeDist.simpla.sumocfg</td>
    <td rowspan="3">dayuan.grid.ATL.vTypeDist.simpla.runMe.py</td>
  </tr>
  <tr>
    <td>temp 2: netfiles/ATL/dayuan.grid.3.updatedGenerated.ATL.net.xml</td>
  </tr>
  <tr>
    <td>final: netfiles/ATL/dayuan.grid.3.updatedByHand.ATL.net.xml</td>
  </tr>
  <tr>
    <td>MyTL</td>
    <td>netfiles/dayuan.grid.1.net.xml</td>
    <td>sumocfg/ayuan.grid.staticTL.vTypeDist.simpla.sumocfg</td>
    <td>dayuan.grid.myTL.vTypeDist.simpla.runMe.py</td>
  </tr>
</table>

<br>