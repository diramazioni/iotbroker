import asyncio
import websockets

async def send_image(file_path, server_uri):
    async with websockets.connect(server_uri) as websocket:
        # Read the image file as binary data
        with open(file_path, "rb") as f:
            image_data = f.read()
        await websocket.send(image_data)

        print(f"Image '{file_path}' sent successfully.")

image_file_path = "/home/es/Immagini/husky.jpg"
websocket_server_uri = "wss://greenlab.unibo.it:443/ws"

asyncio.get_event_loop().run_until_complete(send_image(image_file_path, websocket_server_uri))
