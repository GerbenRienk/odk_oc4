# some things that are not yet clear
- it looks like some questions depend on the site, see column relevant ${site_id}
- odk-5 demographics and then especially date of birth

- will we talk about participant or about subjects?
- can we do some stress testing with 20k subjects?
- shall we make odk_admin data-entry for just the first site? it now has the role of data-entry-person for the study as a whole
- discuss naming conventions
- backup of odk and odk_util on aws


# first we should
- write a workflow about what to do in case of crf-changes
- make a list of tables
- don't import an empty string, for example PAGE_WELCOME_DEM_GRP_DEM_GRP1_OCCUP_SPE

# to make things nicer we could
- at the end of the daily cycle create a summary of what didn't go right
- write a script that goes through the data-definition and checks for double item-names and 
- use in the oc4api a parameter for response json or not, so we're more flexible
- keep track of who is known in the util database and also which events have been scheduled, so we don't repeat unnecessary actions
- check if event has already been scheduled before trying to do that
- do something with status 400 for scheduling event
- write functions for retrieving the event-info per participant, using rest/clinicaldata/json/view/
- setup jk_mount properly for tomcat8
- better feedback when using the util-db for inserts etc.
- we now import all subjects, also the ones that will not be entered off-line
- think of scenario where subjects in oc4 are deleted
- rewrite pg_api so that we can refer to classes without knowing the actual names of the classes
- rewrite _ODMParser to get all parameters in one json thing

# done that 
- upload CRF11 to odk aggregate
- study event repeat key for unscheduled and protocol deviations
- complete list will follow for site mapping 
- store the odm-xml in the util-db
- write the job-uid to postgres when submitting an import, so we can later retrieve the results
- make a script to dump the database on aws and retrieve it and restore it locally
- hard-code in the config file which odk-table corresponds with which oc4-event
- qr-code for ssid: see also https://opendatakit.org/2017/06/configure-collect-on-many-devices-with-qr-codes/
- what will the pattern of the study-subject-id be? will there be a connection between site and id? if not, we must build something between the reading of odk and adding the participants in oc4
- check for enrol=1 for odk-data
- how to deal with subjects already in oc4
- should we set the status of the crf to started or to complete?
