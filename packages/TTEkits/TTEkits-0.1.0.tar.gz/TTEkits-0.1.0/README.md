# Background
Twenty-first century urban planner have identified the understanding of 
Complex city traffic pattern as a major priority, leading to a sharp increase
in the amount and the diversity of traffic data being collected. For instance,
taxi companies in an increasing number of major cities have started recording
metadata for every individual car ride, such as its origin, destination, and
travel time. In this paper, we show that we can leverage network optimization
insights to extract accurate travel time estimations from such origin-destination
data, using information from a large number of taxi trips to reconstruct the 
traffic patterns in an entire city.

This Python Library TTEkits used the algorithm proposed by Dimitris Bertsimas 
et al. in the paper published in Operation Research for travel time estimation.


## Install  
```pip install TTEkits```  
Before you can install TTEkits, you'll need to install some dependency libraries.  

## Usage  
>+ step 1: import library  

```
from TTEkits import model
```  

>+ step 2: instantiation

```
graph_model = model.World(type=1,num=1000,sigma=0.1,reg=1000,time_limit=0.6)
```  

>+ step 3: model train  
```
graph_model.train()
```  

>+ step 4: model test  

```
graph_model.test()
```  

>+ step 5: visualization  

```
G = ox.graph_from_place('Manhattan, New York City, New York, USA', network_type='drive')  
picture = Visualization(G,type=2,manual=True)
picture.plot_real_path(-73.98215485,40.76793671,-73.96463013,40.76560211)
```  

## License

@Elon Lau

This reposity is licensed under the MIT license.
See LICENSE for details.

