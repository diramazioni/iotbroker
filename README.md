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

- GET all the messages for a given device as json `${base}/api/messages/${device_type}`  i.e. `/api/messages/weatherstation_s` it optionally accept a start and end date i.e. `/api/messages/weatherstation_s?start=2023-10-30T13:55:30.000Z&end=2023-10-30T23:55:30.000Z`

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
Install *python* preferebly with pyenv. pyenv allows you to quickly install and use different versions of python via the command line.
for example: `curl https://pyenv.run | bash` and `pyenv install 3.11.4` 

Install *node* preferably with nvm. nvm allows you to quickly install and use different versions of node via the command line. for example:
`curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash`
and `nvm install v18.19.0`

Optionally, install *pnpm* `curl -fsSL https://get.pnpm.io/install.sh | sh -`

Install *postgres* `sudo apt install postgresql`
`sudo -u postgres psql template1` and set your db password
`ALTER USER postgres with encrypted password 'your_password';`

Run `pip install -r requirements.txt` for python 

then `cd ./svelte-dash` and `pnpm i `  for node packages

Be sure to have the right .env file with the credentials both in the root folder and in svelte-dash/

Recreate the `/www` static asset with the symbolic link/or directory pointing to your server static asset. 


### Generate Prisma client for python and Javascript. 


Configure the `DATABASE_URL` accordingly. 

For example if use SQLlite `DATABASE_URL="file:../../data/iot_dev.db?connection_limit=1"` If you don't use SQLlite you can skip the `?connection_limit=1` part but set the right db in `svelte-dash/prisma/schema.prisma`. 

For postgres `DATABASE_URL="postgresql://postgres:your_password@localhost:5432/iotgreenlab?schema=public"`

For the async *python* client uncomment the relevant section at the top of `/svelte-dash/prisma/schema.prisma` then generate it with `python3 -m prisma generate` in the active environment and within the `svelte-dash/` directory

For the async *javascript* client, uncomment the relevant section at the top of `/svelte-dash/prisma/schema.prisma` then generate it with  `npx run generate` within the `svelte-dash/` directory


Create the db with `npx prisma db push`

Seed the db (if not using the example's SQLlite dev db)

## Running

For the python server: within the active enviroment at the root of the cloned repo, run `python mqtt_logger.py` this will listen to the MQTT server, spawn a websocket server and parse the incomming data inserting them into the DB

For the web server: within the `svelte-dash/` directory run `npm run dev` for the development version. To build run `npx run build` and to preview the build `npx run preview`


#### For development of different db schema
To change the schema make the changes in `svelte-dash/prisma/schema.prisma`. 

migrate with: `npx prisma migrate dev --name  1_add_ws` where 1_add_ws is the name of the migration