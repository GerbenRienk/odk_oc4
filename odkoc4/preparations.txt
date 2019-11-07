first of all we have to have for development a copy of the databse with odk-data
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