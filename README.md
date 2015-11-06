testing specs for recipes

name:string
summary:text
description:text

- name must be present
- name must be 5 - 100 characters
- summary must be present
- summary must be 10-150 characters
- description must be present
- description must be 20-500 chracters
- chef_id must be present
- 

testing specs for chefs
chefname: string
email: string

- chef name must be present
- chef name must be 3-40 characters
- email must be present
- email must be unique (since we will use this for logins later)
- mail must be valid


Chefs:

What we have already:
-Chef model and validations
-chefs table with columns and email

What we need to:
-Add password to the chefs table so chefs can be authenticated
-Use email as log in credentials
-Ability to register new chefs
-to displau chegf profile
-to list chefs 
-for chefs to log in an dlog out
-restrict actions like create recipe edit etc for chefs only
-Restrict edit of recipes who created the recipe

