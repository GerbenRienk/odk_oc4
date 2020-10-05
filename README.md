# odk_oc4
a python script to go through data collected in odk and prepare them to be imported oc4

## configuration  
This script uses two configuration-files:  

- odkoc4.config, which holds information about accounts, servers, etc.
- data_definition.json, which holds information about which postgresql table should be read and to which event, form, item-group and item the values should be mapped; this files has two variant, data_definition_test.json and data_definition_prod.json, so that one odk-aggregate server can be used in two different environments.

## workflow
The script runs continuously, that is to say: it is scheduled to loop through a series of commands, until the total looping time has reached a certain value. This value is set in odkoc4.config by parameter loop_this_long. In the AM001 project this is set to 2 hours, because the AWS server on which it runs automatically cancels scripts that run longer than that. Because we want the odk-data to be imported during the day, crontab-jobs are scheduled to start script.
Because the script starts multiple times a day and because per start the script loops multiple times, when a line is written to the report/log, first a check is made that this line is not already present.

In one cycle the script executes the following actions: 
- it reads the configuration file 
- it makes connections to the odk-database and the util-database for the administration
- it makes a call to the oc4-webservice to retrieve a list of all subjects of our study known in oc4
- it updates the information about the study subjects in table study_subjec_oc, regarding the id and oid
- it then loops through all odk-tables and lists doubles in the report, based on the study_subject_id
- it then loops again through all odk-tables and verifies if the study subject can be correctly assigned to a site, as specified in the data-definition
- if the site is valid, a subject will be created in oc4, if it isn't already present; if the creation results in an error, this is written in the log
- now the script checks if this particular record in the odk-table is already marked as complete and if not, it schedules the event, associated with the odk-table in the data_definition
- if the record in the odk-table isn't marked as complete, the script then composes the odm-file with all data combined and submits this file to the oc4-api; in return the oc4-api sends the job-id of this request to import data
- when all odk-tables have been processed the script takes the job-id's of all the import-jobs and requests the job-log; if an error was found in the log, this is copied to the script-log; if it doesn't find any error messages it will mark the odk-table-records as complete
- at the end of the script the enrolment-check is done, taking the most recent clinical-data of  


## oc4 api / webservices
swagger info can be found at:
https://your_org.openclinica.io/OpenClinica/pages/swagger-ui.html
