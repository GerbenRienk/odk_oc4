First of all we have to have for development a copy of the database with odk-data
we transfer it from the server to D:\OC\FindDX\PNG_HS_RDT\DatabaseDumps
and then more or less do the following:
cd C:\Program Files\PostgreSQL\9.4\bin 
psql -U postgres
drop database odk_prod;
create database odk_prod with encoding='UTF-8' owner=odk_user;
\q
psql -U postgres odk_prod < D:\OC\FindDX\PNG_HS_RDT\DatabaseDumps\pgd_odk_prod_20180818

now we modify the odkoc.config file to match the credentials for the database access
and add another set of parameters for the housekeeping database: odk_prod_util

in odk_prod_util we want to have a table for each odk_table that holds the _uri, the study subject id and a flag for successful import 

psql script for the util-db:
CREATE DATABASE odk_am001_util
  WITH OWNER = odk_admin
       ENCODING = 'UTF8';
       
in this database run the scripts to create two tables:
CREATE TABLE study_subject_oc
(
  study_subject_id character varying(32) NOT NULL,
  study_subject_oid character varying(32) NOT NULL,
  CONSTRAINT pk_study_subject_oc PRIMARY KEY (study_subject_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE study_subject_oc
  OWNER TO odk_admin;

CREATE TABLE uri_status
(
  uri character varying(80) NOT NULL,
  last_update_status timestamp without time zone NOT NULL,
  is_complete boolean,
  table_name character varying(50),
  odm_file_name character varying(100),
  odm_content character varying,
  import_job_uuid character varying(50),
  job_uuid_content character varying,
  CONSTRAINT uri_status_pkey PRIMARY KEY (uri)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE uri_status
  OWNER TO odk_admin;
