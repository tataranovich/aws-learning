# AWS API Gateway

1. Create API using API gateway AWS service with resources, sub resources and path variables.
For ex. let’s imagine you need to create API for social network:
~~~
api/v1/users
api/v1/users/{id}
api/v1/users/{id}/friends (each user may have list of friends which are users too)
api/v1/groups
api/v1/groups/{id}
api/v1/groups/{id}/users
~~~
use different methods for get/update/delete user’s data: GET, POST, DELETE.

2. Map each method with lambda function, which will hit RDS (use postgres DB from previous tasks) for get, update, delete data. Use Python + boto for connect to DB

3. Optional (if you will have a time): create custom authorizer and attach to API gateway methods