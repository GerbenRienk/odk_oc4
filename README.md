# odk_oc4
a python script to go through data collected in odk and prepare them to be imported oc4

## configuration  
This script uses two configuration-files:  

- odkoc4.config, which holds information about accounts, servers, etc.
- data_definition.json, which holds information about which postgresql table should be read and to which event, form, item-group and item the values should be mapped

An important limitation to the script is that we can only import items that belong to the same item-group. Therefore if an odk-table holds items from more than one item-group, it should have more than one entry in data_definition.json

---
swagger info can be found at:
https://yourorg.openclinica.io/OpenClinica/pages/swagger-ui.html
