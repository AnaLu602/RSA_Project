# Importing the relevant libraries
from email import message
import websockets
import asyncio
import sqlite3

# Server data
PORT = 7890
print("Server listening on Port " + str(PORT))


# A set of connected ws clients
connected = set()

dbConnection = sqlite3.connect("test.db")
cursor = dbConnection.cursor()


# The main behavior function for this server
async def echo(websocket, path):

    print("A client just connected")
    # Store a copy of the connected client
    connected.add(websocket)
    # Handle incoming messages
    try:
        async for message in websocket:
            print("Received message from client: " + message)
            cursor.execute('''INSERT INTO MESSAGES VALUES (?)''', [message])
            dbConnection.commit()
            # Send a response to all connected clients except sender
            for conn in connected:
                if conn != websocket:
                    await conn.send("Someone said: " + message)
    # Handle disconnecting clients
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
    finally:
        connected.remove(websocket)


def main():
    # Start the server
    start_server = websockets.serve(echo, "192.168.1.110", PORT)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
