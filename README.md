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


