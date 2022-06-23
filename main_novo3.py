from queue import Queue
import threading
import os
import json
import paho.mqtt.client as mqtt
import time
import sqlite3

queue = Queue()


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
    if msg.topic == "vanetza/out/denm":
        print("on message denm")
        queue.put(msg)


def identificate_denm(object):

    print("Object: {}".format(object[0][0]))
    if object[0][0] == "Cão" or object[0][0] == "Vaca" or object[0][0] == "Gato" or object[0][0] == "Cavalo":
        return (9, 11)
    elif object == "Ciclista":
        return (10, 12)

    return "not defined"


def launch_denm_producer(data):

    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()

    cursor.execute('''DELETE from MESSAGES ''')
    conn.commit()

    obu = mqtt.Client()
    obu.on_connect = on_connect
    obu.on_message = on_message

    obu.connect(data["ip"][0]["ipv4"])

    lastInstant = 0

    msg = None

    obu.loop_start()

    for instant in data["coordinates"][0]:
        coordenates = (data["coordinates"][0][instant]["latitude"],
                       data["coordinates"][0][instant]["longitude"])

        publish_cam(obu, coordenates)
        print("{} sent CAM and is passing at ({},{})." .format(
            data["obu"][0]["name"], coordenates[0], coordenates[1]))

        cursor.execute('''SELECT COUNT(*) from MESSAGES ''')
        result = cursor.fetchall()
        if result[0][0] != 0:
            cursor.execute('''SELECT * from MESSAGES LIMIT 1''')
            msg = cursor.fetchall()
            lastInstant = instant
            print("DENM Message identificated on ({},{})".format(
                data["coordinates"][0][instant]["latitude"], data["coordinates"][0][instant]["longitude"]))
            break
        time.sleep(2)

    if msg != None:
        cause = identificate_denm(msg)
        print("Cause: {}".format(cause))

        if cause != "not defined":
            publish_denm(obu, cause[0], cause[1], time.time(), (data["coordinates"][0][lastInstant]
                                                                ["latitude"] + 0.000020, data["coordinates"][0][lastInstant]["longitude"]), 10)

            count = 0

            while count != 10:
                coordenates = (data["coordinates"][0][lastInstant]["latitude"] + 0.000010,
                               data["coordinates"][0][lastInstant]["longitude"])
                publish_cam(obu, coordenates)
                print("{} sent CAM and is stoping at ({},{})." .format(
                    data["obu"][0]["name"], coordenates[0], coordenates[1]))
                count += 1
                time.sleep(2)

    obu.disconnect()
    obu.loop_stop()


def launch_denm_consumer(data):

    obu = mqtt.Client()
    obu.on_connect = on_connect
    obu.on_message = on_message
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
                print("DENM received")
                print("{} sent CAM and is stoping at ({},{})." .format(
                    data["obu"][0]["name"], coordenates[0], coordenates[1]))
                time.sleep(2)
            break
        else:
            coordenates = (data["coordinates"][0][instant]["latitude"],
                           data["coordinates"][0][instant]["longitude"])
            publish_cam(obu, coordenates)
            print("{} sent CAM and is passing at ({},{})." .format(
                data["obu"][0]["name"], coordenates[0], coordenates[1]))
            latest = instant
            time.sleep(2)

    obu.disconnect()

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
