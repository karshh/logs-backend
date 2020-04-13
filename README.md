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

##### `GET /logs/`

Gets an array of logs. Optional Query Parameters
- `userId`: Retrieves logs that match the userId value
- `from`: Retrieves logs with actions that have occured after (and including) this value. Format must be as `%Y-%m-%dT%H:%M:%S-06:00`, example: `2019-10-18T21:37:28-06:00`
- `to`: Retrieves logs with actions that have occured before (and including)  this value. Format must be as `%Y-%m-%dT%H:%M:%S-06:00`, example: `2019-10-18T21:37:28-06:00`
- `types`:  Retrieves logs with actions of the listed type. 

Example: 

`GET /logs/?userId=ASDF&types=CLICK,VIEW,NAVIGATE&from=2019-10-18T21:37:28-06:00&to=2019-11-18T21:37:28-06:00`

##### `POST /logs/`
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
- Each `action` must have a type `NAVIGATE`, `VALID` or `CLICK`
- For a `NAVIGATE` type, `properties` must have a `pageFrom` and `pageTo` value.
- For a `CLICK` type, `properties` must have a `locationX` and `locationY` value.
- For a `VIEW` type, `properties` must have a `viewedId` value.

Voilation of this validation results in a 400 status error with the appropriate error code sent in body.

### Limitations:
- I couldn't within the assessment timeframe get timestamp checking to work within mongo. So for now I store and retrieve time as string with fromat `%Y-%m-%dT%H:%M:%S-06:00`, and validate this format on every query or insertion before checking
- I should be restricting `types` query parameter in `GET /logs/` to just CLICK, VIEW and NAVIGATE
- I wasn't able to have some transactional way of inserting logs into the DB. For now, this application does not guarantee that if any log has an error, that there will be a rollback. I implemented and commented out a test case for it. Also added in comments in code regarding this.

