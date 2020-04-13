# Logs Store


### Installation

Clone the project:
```bash
git clone https://github.com/karshh/oh-backend.git logstore
cd logstore
```

Create a virtualenv and activate it. Then install the requirements
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Create a copy of the .env file using the example file provided.
```bash
cp .env.example .env
```
Modify the environment variables to add your mongodb connection. For example:
```bash
MONGO_URL='mongodb://localhost:27017/dev'
TEST_MONGO_URL='mongodb://localhost:27017/test'
```
You can also use mongomock for TEST_MONGO_URL although certain features implemented in the code arent available in the library.

To test, run:
```bash
pytest
```

to run the app, run:
```bash
python app.py
```


### API Doc

- #### `GET /logs/`

Gets an array of logs. Optional Query Parameters
- `userId`: Retrieves logs that match the userId value
- `from`: Retrieves logs with actions that have occured after (and including) this value. Format must be as `%Y-%m-%dT%H:%M:%S-06:00`, example: `2019-10-18T21:37:28-06:00`
- `to`: Retrieves logs with actions that have occured before (and including)  this value. Format must be as `%Y-%m-%dT%H:%M:%S-06:00`, example: `2019-10-18T21:37:28-06:00`
- `types`:  Retrieves logs with actions of the listed type. 

Example: 

`GET /logs/?userId=ASDF&types=CLICK,VIEW,NAVIGATE&from=2019-10-18T21:37:28-06:00&to=2019-11-18T21:37:28-06:00`

- #### `POST /logs/`
Validates and inserts logs into storage. Accepts JSON as format. Example of a body that is accepted:

<details>
<summary>Example</summary>
<br>

```json
[
    {
      "userId": "ABC123XYZ",
      "sessionId": "XYZ456ABC",
      "actions": [
        {
          "time": "2018-10-18T21:37:28-06:00",
          "type": "CLICK",
          "properties": {
            "locationX": 52,
            "locationY": 11
          }
        },
        {
          "time": "2018-10-18T21:37:30-06:00",
          "type": "VIEW",
          "properties": {
            "viewedId": "FDJKLHSLD"
          }
        },
        {
          "time": "2018-10-18T21:37:30-06:00",
          "type": "NAVIGATE",
          "properties": {
            "pageFrom": "communities",
            "pageTo": "inventory"
          }
        }
      ]
    },
    { 
    	"userId": "asd", 
    	"sessionId": "asdfg", 
    	"actions" : [
    		{
    			"time": "2018-10-18T21:37:28-06:00",
    			"type": "CLICK",
    			"properties": {
    				"locationX": 52,
    				"locationY": 22
    			}
    		},
    		{
    			"time": "2018-10-20T21:37:28-06:00",
    			"type": "NAVIGATE",
    			"properties": {
    				"pageFrom": "X",
    				"pageTo": "Y"
    			}
    		}
    	]
    }
]
```

</details>

Validations in this body:
- Body must have atleast 1 log.
- Each log must have a `sessionId` and `userId` value
- Each log must have atleast 1 `action`
- Each `action` must have a `time` of format `%Y-%m-%dT%H:%M:%S-06:00`
- Each `action` must have a `type` of value `NAVIGATE`, `VIEW` or `CLICK`
- For a `NAVIGATE` type, `properties` must have a `pageFrom` and `pageTo` value.
- For a `CLICK` type, `properties` must have a `locationX` and `locationY` value.
- For a `VIEW` type, `properties` must have a `viewedId` value.

Voilation of this validation results in a 400 status error with the appropriate error code sent in body.

### Deployment

This is my first time using heroku for deployment. As such, I did the following steps:

- Install Heroku CLI and log in using the command ```heroku login```
- Clone the project
    ```bash
    git clone https://github.com/karshh/oh-backend.git logstore
    cd logstore
    ```
- Run the following command to create a new heroku app: 
    ```
    heroku create app-name
    ```
- Add MONGO_URL to heroku config. (Replace string with your mongo cloud URL, this is just an example): 
    ```
    heroku config:set MONGO_URL='mongodb://<username>:<password>@hostname/prod?retryWrites=false'
    ```
- Push code to heroku
    ```
    git push heroku master
    ```

This step had bootstrapped the heroku app for me at ```https://app-name.herokuapp.com```

### Limitations:
- I couldn't within the assessment timeframe get timestamp checking to work within mongo. So for now I store and retrieve time as string with fromat `%Y-%m-%dT%H:%M:%S-06:00`, and validate this format on every query or insertion before checking
- I should be restricting `types` query parameter in `GET /logs/` to just CLICK, VIEW and NAVIGATE
- The validations of the body is done prior to inserting into the db, rather than a mongo-specific solution. The body doesn't get inserted if even one of the logs is invalid, and this validation check is done in code. 


### Answer to Follow-up question
I would do the following to make this application more cloud-scalable:
- Starting at the database level, R/W speeds must be as minimal as possible. My sandbox mlab cloud server would probably not be optimal for this, but purchasing a more premium services (or purchasing some beast servers and using them as storage) would be a good idea.
- Resource-allocation: Ensuring that the application has the appropriate resources it needs to handle traffic. A load balancing service, which may dynamically allocate virtual matches to scale would be a good example here.
- This application is written in Flask, and only serves 1 request at a time. (Although on researching gunicorn while deploying to heroku, I've read that it takes care of this issue), but a more asynchronous multithreaded solution/framework would probably help resolve more requests at a time.
- A cache in the implementation can help speed up recently frequent requests if there hasn't been any writes to the database that may have changed the cached value. A tradeoff would be how much resource it eats up.