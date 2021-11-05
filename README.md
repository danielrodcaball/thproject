## Deploying

Run:

    docker-compose up --build -d

The project will be deployed at `http://127.0.0.1:8000/`.

You can manage the db from `http://127.0.0.1:8000/admin`, but first you have to create an admin user with the following 
command:

    docker-compose exec web python manage.py createsuperuser

If you want to populate the db with test data run:

    docker-compose exec web python manage.py populatedb
    
## Endpoints

### Find restaurants

Get all restaurants:

    GET http://127.0.0.1:8000/api/v1/restaurants/

Get all restaurants that match all dietary restrictions of diners sorted by total distance from diners to restaurants 
in ascending order:

    GET http://127.0.0.1:8000/api/v1/restaurants/?diners=<id>&diners=<id>...
    
Get all restaurants that match all dietary restrictions of diners and have an available table for the selected datetime,
sorted by total distance from diners to restaurants in ascending order:

    GET http://127.0.0.1:8000/api/v1/restaurants/?diners=<id>&diners=<id>...&target_datetime=<datetime>
    
The datetime format should be `%Y-%m-%d %H:%M:%S` , example: `2021-11-20 21:00:00`
    
### Create a reservation

    POST http://127.0.0.1:8000/api/v1/reservations/
    Content-Type: application/json
    
    {
      "diners": [1,2],
      "target_datetime": "2023-11-04 22:00:00",
      "table": 10
    }

    ###
    
### Delete a reservation

    DELETE http://127.0.0.1:8000/api/v1/reservations/<id>
    
## Running tests:
    
    docker-compose exec web python -Wa manage.py test