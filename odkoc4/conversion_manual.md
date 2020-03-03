# manual for converting oc4-crf's into odk-forms for AM001
The purpose of this document is to describe all activities involved in converting oc4-crf's, used in **AM001 Dx Accelerator**, into odk-forms. 

## naming conventions
### oc4
In oc4 the name of a crf can be anything. It appears that in setting up the study (almost) all crf's for **day 0** start with **CRFXX:** where XX is a number.

### odk 
Spaces can't be used in the name of an odk-form, so delete these

## workflow
1. download the latest version of a crf from oc4 into folder AM001/CRFs/1_DownloadedFromOc4
1. unzip the xls into folder AM001/CRFs/2_EditedForOdk
1. remove any spaces from the name of the xls
1. in tab **settings** change form_title to match the oc4-form-name, for example *CRF02: Inclusion Exclusion Criteria*
1. set the form_id using the following pattern: 10000 + the number of the visitx100 + the number of the crf; for example **Day 0 - CRF02: Inclusion Exclusion Criteria** will have form_id 10102
1. set the version to **1** and increase this for newer versions
1. in tab survey, insert a row as the second one of type **text**, name **study_subject_id** and label **0: Study Subject ID**; add a regular expression
1. in tab survey, inspect fields of type **calculate**; if the calculation is oc4-specific, then delete the contents of the row
1. convert the xls into xml using **ODK XLSForm Offline v1.7.0**
1. upload the xml to http://oc.finddx.org:8081/odk_am001/