from queue import Queue
import threading
import os
import json
import paho.mqtt.client as mqtt
import time
import sqlite3

queue = Queue()

conn = sqlite3.connect("test.db")


def publish_cam(client, coordenates):

    cam = json.load(open(f'messages/cam.json'))

    cam["latitude"] = coordenates[0]
    cam["longitude"] = coordenates[1]

    client.publish("vanetza/in/cam", json.dumps(cam))


def publish_denm(client, causeCode, subCauseCode, detectionTime, eventPosition, validityDuration):

    denm = json.load(open(f'messages/denm.json'))

    denm["situation"]["eventType"]["causeCode"] = causeCode
    denm["situation"]["eventType"]["subCauseCode"] = subCauseCode
    denm["management"]["detectionTime"] = detectionTime
    denm["management"]["referenceTime"] = detectionTime
    denm["management"]["validityDuration"] = validityDuration
    denm["management"]["eventPosition"]["latitude"] = eventPosition[0]
    denm["management"]["eventPosition"]["longitude"] = eventPosition[1]

    client.publish("vanetza/in/denm", json.dumps(denm))
    print("message published")


def on_connect(client, userdata, flags, rc):

    # client.subscribe("vanetza/out/cam")
    client.subscribe("vanetza/out/denm")

    print("connected")


def on_message(client, userdata, msg):
    # print("Received message '" + str(msg.payload) + "' on topic '"
    #       + msg.topic + "' with QoS " + str(msg.qos))
    if msg.topic == "vanetza/out/denm":
        print("on message denm")
        queue.put(msg)


def launch_denm_producer(data):
    print("producer")

    obu = mqtt.Client()
    obu.on_connect = on_connect
    obu.on_message = on_message

    obu.connect(data["ip"][0]["ipv4"])

    count = 0

    obu.loop_start()

    for instant in data["coordinates"][0]:
        coordenates = (data["coordinates"][0][instant]["latitude"],
                       data["coordinates"][0][instant]["longitude"])
        publish_cam(obu, coordenates)
        count += 1

        if count == 10:
            publish_denm(obu, 11, 1, time.time(), (40.675093, -8.573534), 10)
            count = 0
        time.sleep(1)

    obu.loop_stop()


def launch_denm_consumer(data):

    obu = mqtt.Client()
    obu.on_connect = on_connect
    obu.on_message = on_message
    print(data["ip"][0]["ipv4"])
    obu.connect(data["ip"][0]["ipv4"])

    obu.loop_start()

    for instant in data["coordinates"][0]:
        if not queue.empty():
            message = queue.get()
            coordenates = (data["coordinates"][0][latest]["latitude"],
                           data["coordinates"][0][latest]["longitude"])
            denm = json.loads(message.payload)
            for i in range(denm["fields"]["denm"]["management"]["validityDuration"]):
                publish_cam(obu, coordenates)
                time.sleep(1)
        else:
            coordenates = (data["coordinates"][0][instant]["latitude"],
                           data["coordinates"][0][instant]["longitude"])
            publish_cam(obu, coordenates)
            latest = instant
            time.sleep(1)

    obu.loop_stop()


def main():

    path = "obus"

    dir = os.listdir(path)

    threads = [threading.Thread(target=launch_denm_producer, args=(
        json.load(open(f'obus/{file}')), )) if file == "obu1.json" else threading.Thread(target=launch_denm_consumer, args=(
            json.load(open(f'obus/{file}')), )) for file in dir]

    # start each thread
    [t.start() for t in threads]

    # threads join
    [t.join() for t in threads]


if __name__ == "__main__":
    main()
