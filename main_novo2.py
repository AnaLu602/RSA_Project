from queue import Queue
import threading
import os
import json
import paho.mqtt.client as mqtt
import time

queue = Queue()


def cam_keys():

    cam = json.load(open(f'messages/cam.json'))

    default_keys = cam.keys()

    return default_keys


def denm_keys():

    denm = json.load(open(f'messages/denm.json'))

    default_keys = denm.keys()

    return default_keys


def publish_cam(client, coordenates):

    cam = json.load(open(f'messages/cam.json'))

    cam["latitude"] = coordenates[0]
    cam["longitude"] = coordenates[1]

    client.publish("vanetza/in/cam", json.dumps(cam))


def publish_denm(client, causeCode, subCauseCode, detectionTime, eventPosition, validityDuration):

    denm = json.load(open(f'messages/denm.json'))

    # denm["situation"]["eventType"]["causeCode"] = causeCode
    # denm["situation"]["eventType"]["subCauseCode"] = subCauseCode
    # denm["management"]["detectionTime"] = detectionTime
    # denm["management"]["referenceTime"] = detectionTime
    # denm["management"]["eventPosition"]["latitude"] = eventPosition[0]
    # denm["management"]["eventPosition"]["longitude"] = eventPosition[1]

    client.publish("vanetza/in/denm", json.dumps(denm))
    print("message publishde")


def on_connect(client, userdata, flags, rc):

    client.subscribe("vanetza/out/cam")
    client.subscribe("vanetza/out/denm")


def on_message(client, userdata, msg):
    print(msg.topic)
    if msg.topic == "vanetza/out/denm":
        print("on message denm")
        queue.put(msg)


def launch_denm_producer(data):

    obu = mqtt.Client()
    obu.on_connect = on_connect
    obu.on_message = on_message

    obu.connect(data["ip"][0]["ipv4"])

    obu.loop_start()

    count = 0
    if data["ip"][0]["ipv4"] == "192.168.98.20":
        publish_denm(obu, 11, 1, time.time(), (40675093, -8573534), 10)

    while True:
        print("ola")
# for instant in data["coordinates"][0]:
#     # coordenates = (data["coordinates"][0][instant]["latitude"],
#     #                data["coordinates"][0][instant]["longitude"])
#     # print(coordenates)
#     # publish_cam(obu, coordenates)
#     # count += 1
#     # print("contagem"+str(count))
#     if count == 0:
#         print("count 0")
#         publish_denm(obu, 11, 1, time.time(), (40675093, -8573534), 10)
#         count = 0
#     time.sleep(1)

    obu.disconnect()
    obu.loop_stop()


def launch_denm_consumer(data):

    obu = mqtt.Client()
    obu.on_connect = on_connect
    obu.on_message = on_message

    obu.connect(data["ip"][0]["ipv4"])

    obu.loop_start()

    latest = 0  # falta inicializar

    while not queue.empty():
        print("queue empty")

    while True:
        print("ola")
    # for instant in data["coordinates"][0]:
    #     if not queue.empty():
    #         message = queue.get()
    #         coordenates = (data["coordinates"][0][latest]["latitude"],
    #                        data["coordinates"][0][latest]["longitude"])
    #         print(message["management"]["validityDuration"])
    #         for i in range(message["management"]["validityDuration"]):
    #             print("denm heard" + i)
    #             # print(coordenates)
    #             publish_cam(obu, coordenates)
    #             time.sleep(1)
    #     else:
    #         coordenates = (data["coordinates"][0][instant]["latitude"],
    #                        data["coordinates"][0][instant]["longitude"])
    #         print("denm not heard")
    #         # print(coordenates)
    #         publish_cam(obu, coordenates)
    #         latest = instant
    #         time.sleep(1)

    obu.loop_stop()
    obu.disconnect()


def main():

    path = "obus"

    dir = os.listdir(path)

    threads = [threading.Thread(target=launch_denm_producer, args=(
        json.load(open(f'obus/{file}')), )) for file in dir]

    # start each thread
    [t.start() for t in threads]

    # threads join
    [t.join() for t in threads]


if __name__ == "__main__":
    main()
