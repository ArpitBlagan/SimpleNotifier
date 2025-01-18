## <p align="center">A simple monitoring and notfier app using discord webhooks</p>

### Implemetation

- For this we simply create an django app where user can register a website which he want to get monitored as user hit the post route we store the info and simple start a thread which will pool the website's url on every particular interval of time and if the status doesn't match with previous one we send discord notification to the user using webhook.
- we use async/await , asyncio rate limitation, added a docker file etc.

#### About the app

- User can simple post about a website and we will keep updating them about the status weather the side is up or not on discrod through webhook.

##### Endpoints

- GET "/api/all/" to get all the registered website which getting monitored.
- POST "api/add/" to add a new website.
- GET "api/get/id/" to get info of particular registered website.
- DELETE "api/delete/id" to delete the registered website and stop monitoring thread.
