## <p align="center">A simple monitoring and notfier app</p>

### Implemetation

#### About the app

- User can simple post about a website and we will keep updating them about the status weather the side is up or not on discrod through webhook

##### Endpoints

- GET "/api/all/" to get all the registered website which getting monitored
- POST "api/add/" to add a new website
- GET "api/get/id/" to get info of particular registered website
- DELETE "api/delete/id" to delete the registered website and stop monitoring thread.
