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
1. in tab survey, insert four rows as specified below
1. in tab survey, inspect fields of type **calculate**; if the calculation is oc4-specific, then delete the contents of the row
1. convert the xls into xml using **ODK XLSForm Offline v1.7.0**
1. upload the xml to http://oc.finddx.org:8081/odk_am001/

## rows to insert to make an oc-form an odk-form
|type|name|label|constraint|calculation|
|----|----|-----|----------|-----------|
|barcode|id_qr|Please scan the qr-code, or swipe this question if there's no qr-code available| | |
|text|id_manual|The Study Subject ID from the QR-code is ${id_qr}. If this is correct, swipe to the next question. If this is incorrect, please enter the correct Study Subject ID.|regex(.,'AM001((0[1-9])\|99)[0-9]{4}')| |
|calculate|study_subject_id|Study subject ID| |coalesce(${id_manual}, ${id_qr})|
|note|note_on_id|The data will be submitted to the server under the ID ${study_subject_id}| | |
