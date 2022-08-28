

<table border="1px">
<tr><td>
This phase's target: get 4 main parameters 

- 1. At the end of this cycle:

  - 1.1 For each TL:

    For each edges:

    **NPV**: 
    
    -   How many v pass the intersection during this Green Lights (=cycle) for each of three directions. There are only Green Lights can pass vehicles. 

    **NDV**: 
    -   Record all V at incoming edges, remove them when they appear at outgong edges.
    -   Those V at TL area don't count as delayed.

    **AWT**: 
    -   Record all delayed vehicled in incoming edges. 
    -   Add 1 untill they appear at outgong edges.
    -   Those V at TL area count as waiting time.
    -   Accumulatively works for those vehicles who cross multiple cycles. 
 
  
- 2. **NEV**: At this cycle ending moment (actually the begining moment of new cycle), each TL get neighboring TLs, then get their incoming edges, then get #v in those incoming edges and their dirctions.
  
- 3. For each v, record platoon or not, which platoon.
</td><tr>
</table>
