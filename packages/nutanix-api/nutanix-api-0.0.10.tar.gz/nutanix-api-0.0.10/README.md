
# Nutanix API
* Work in progress

Easily interact with Nutanix API v3 


## Installation

```bash
pip install nutanix-api
```


##  Usage 

```python
from nutanix_api import NutanixApiClient, NutanixVM, NutanixCluster

client = NutanixApiClient("username", "password", 9440, "https://path/to/endpoint")

# Virtual Machine
vm = NutanixVM.get(client, "61b13e12-1494-11ed-861d-0242ac120002")
vm.turn_off()  # Turn VM off 
vm.turn_on()  # Turn VM on

# Cluster
cluster = NutanixCluster.get(client, "81b13e12-1494-11ed-861d-0242ac120003")
print(cluster.name)

```
