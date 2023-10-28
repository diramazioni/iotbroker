# Documentation for WeLaser's iotbroker 

Iotbroker is part of the server infrastructure for the WeLaser project,

The data acquisition and brokering is made out of several python programs present in the project's root

The data visualization/web is made in Svelte/Sveltekit and is in `svelte-dash/`


## Data acquisition and brokering
```mermaid

graph TD

a{{field & robot images}} --- A

A[robot_img.py] -- Ardesia --> B((FTP))

A -- Ardesia --> C((MQTT))

B --> D[image_logger.py]

C --> D

D -- Cesena --> E((FTPS))

D -- Cesena --> F((MQTTS))

G[weather_logger.py] --> F

g{{sensors}} --- F

F --> H[mqtt_logger.py]

H --> I[websocket_async.py]

I --> L((WEB))

H --> M[message_parser.py]

M --> N[(DB)]

```

As shown in the image, the cameras in the fields and in the robots sends images to Ardesia FTP and MQTT server. 

`image_logger.py` is responsible to log the MQTT messages and resend the images/messages to Cesena FTP's and MQTTS's server. 

Also other devices, like the weather stations, send messages to Cesena MQTTS's server. 

Listening to all the messages is `mqtt_logger.py`that sends websocket event to the web interface (via `websocket_async.py`) and updates the db with `message_parser.py` that is also used to seed the db by the json in `data/`

`message_parser.py` reads json MQTT messages and translate it to a `Prisma` db query. 

`image_logger.py, mqtt_logger.py` and `weather_logger.py` inherits from the base class `AsyncMqttClient` from `mqtt_async.py`that use a custom `async_paho_mqtt_client`

`test_welaser.py` is interactive and used to test the different functionalities


## Data visualization/web 

`image_logger.py` creates `www/images.json` to help Svelte show the new camera images without having to rebuild the website.

`Prisma` javascript client is used for all the web realated queries.

`@carbon/charts` is used for 2D charts and `threlte` for 3D charts

### Public facing API
Public facing API are available from the `/api` routes, easing the integration of other web app:

- GET all the messages for a given device as json `${base}/api/messages/${device_type}`  i.e. `/api/messages/weatherstation_s`

- To GET the CSV for the selected device `${base}/api/csv/${device_type}/${device_selected}` i.e. `/api/csv/weatherstation_v/WeatherStation_v0` 

- By using POST to get the CSV it's possible to select also the categories and start/end date
```javascript
    category_on = ["temperature", "wind"]
    const start = new Date();
    start.setDate(start.getDate() - 5); // 5 days before now
    const range = [start, new Date()]
    csv_p = await post_CSV(range, device_type, device_selected, category_on )

async function post_CSV(range, device_type, device_selected, category_on ) {
    const url = `/iot/api/csv/${device_selected}`
    const response = await fetch(url, {
    method: 'POST',
    body: JSON.stringify({ 
        'device_type': device_type, 
        'category_on': category_on, 
        'range':range,
    }),
    headers: {
    'Content-Type': 'application/json; charset=UTF-8'
    }
    });
    const text = await response.text()
    if (response.ok) {
        return text
    } else {
        throw new Error(text)
    }
}
```

- carbon chart's data are with GET request `${base}/api/${device_type}/${device_selected}${params}` where params are the start and end date i.e. `/api/weatherstation_n/WeatherStation_n1?start=2023-09-16T13:12:43.108Z&end=2023-09-25T07:00:00.000Z`

- Likewise for carbon chart's options i.e. `/api/options/weatherstation_n/WeatherStation_n1?start=2023-09-16T13:12:43.108Z&end=2023-09-25T07:00:00.000Z shared.ts:34:9`

- To GET the list of the devices for a certain device_type `${base}/api/devices/${device_type}` like `/api/devices/weatherstation_v`

- To GET the timestamp ranges for a certain device `${base}/api/range/${device_selected}`  like `/api/range/WeatherStation_n1` this will return an array with `[firstDate, viewDate, lastDate]` with the firstDate being the first available record, viewDate being the selected start date, and  lastDate the selected end date, defaults to last records.






![carbon_charts](doc/2D_carbon_charts.png)
![Three.js/Threlte](doc/3D_1.png)
![Three.js/Threlte](doc/3D_2.png)
![Three.js/Threlte](doc/3D_3.png)

## Installing
Run `pip install -r requirements.txt` for python and `pnpm i ` in the `svelte-dash/` directory

Be sure to have the right .env file with the credentials both in the root folder and in svelte-dash/

Recreate the `/www` static asset with the symbolic link/or directory pointing to your server static asset. 


### Generate Prisma client for python and Javascript. 

Configure the `DATABASE_URL` accordingly. 

For example if use SQLlite `DATABASE_URL="file:../../data/iot_dev.db?connection_limit=1"` If you don't use SQLlite you can skip the `?connection_limit=1` part but set the right db in `svelte-dash/prisma/schema.prisma`. 

Create the db with `npx prisma db push`

Seed the db (if not using the example's SQLlite dev db)

The async python client is generated by `python3 -m prisma generate` in the active environment. 

The async javascript client can be generated commenting out the right client in the schema present in `prisma/`and running  `npx run generate`from the `svelte-dash/` directory

To change the schema make the migration with: `npx prisma migrate dev --name  1_add_ws` where 1_add_ws is the name of the migration