import asyncio
import websockets
import queue
import threading
import json 
import os 

class artemis_socket:
    
    # Heartbeat
    heartbeat = json.dumps(({ "type" : "heartbeat", "attribute" : "", "name" : "" }))

    # Connected status
    connected = False

    # Constructor
    def __init__(self, callbackMessageReceived, ip:str = '127.0.0.1', port:int = 5678):
        self.ip = ip
        self.port = port
        self.messages = queue.Queue(maxsize=0)
        self.callbackMessageReceived = callbackMessageReceived
        self.connected = False

    # Check if connected
    def isConnected(self):
        return self.connected

    # Enqueue message to send to server
    def send(self, message):
        self.messages.put(message)

    # Main server function
    async def server(self, ws:str, path:int):
        while True:

            # Wait for message
            try:
                message = await ws.recv()
            except websockets.exceptions.ConnectionClosed as e:
                print("[Artemis] Connection closed")
                os._exit(1)
                break

            # Set connected
            self.connected = True

            # Notify callbacks
            self.callbackMessageReceived(message)

            # Send messages in queue
            while not self.messages.empty():
                message = self.messages.get()
                await ws.send(message)

            # Send message
            await ws.send(self.heartbeat)
    
    # Set server event loop
    def launch_main_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        Server = websockets.serve(self.server, self.ip, self.port)
        asyncio.get_event_loop().run_until_complete(Server)
        asyncio.get_event_loop().run_forever()

    # Launch server
    def run(self):
        thread = threading.Thread(target=self.launch_main_loop, daemon=True)
        thread.start()