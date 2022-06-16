import paho.mqtt.client as mqtt
import json
import time


def publish_cam(client, message):
    client.publish("vanetza/in/cam", message)


def publish_denm(client, message):
    client.publish("vanetza/in/denm", message)


def message_cam(coordenates):
    message = {
        "accEngaged": True,
        "acceleration": 0,
        "altitude": 800001,
        "altitudeConf": 15,
        "brakePedal": True,
        "collisionWarning": True,
        "cruiseControl": True,
        "curvature": 1023,
        "driveDirection": "FORWARD",
        "emergencyBrake": True,
        "gasPedal": False,
        "heading": 3601,
        "headingConf": 127,
        "latitude": 40.0000000,
        "length": 10.0,
        "longitude": -8.0000000,
        "semiMajorConf": 4095,
        "semiMajorOrient": 3601,
        "semiMinorConf": 4095,
        "specialVehicle": {
            "publicTransportContainer": {
                "embarkationStatus": False
            }
        },
        "speed": 16383,
        "speedConf": 127,
        "speedLimiter": True,
        "stationID": 1,
        "stationType": 15,
        "width": 3.0,
        "yawRate": 0
    }

    message["latitude"] = coordenates["latitude"]
    message["longitude"] = coordenates["longitude"]

    return json.dumps(message)


def message_demn(causeCode, subCauseCode, detectionTime, eventPosition):
    message = {
        "management": {
            "actionID": {
                "originatingStationID": 1798587532,
                "sequenceNumber": 0
            },
            "detectionTime": 1626453837.658,
            "referenceTime": 1626453837.658,
            "eventPosition": {
                "latitude": 40.637799251415686,
                "longitude": -8.652353364491056,
                "positionConfidenceEllipse": {
                    "semiMajorConfidence": 0,
                    "semiMinorConfidence": 0,
                    "semiMajorOrientation": 0
                },
                "altitude": {
                    "altitudeValue": 0,
                    "altitudeConfidence": 1
                }
            },
            "validityDuration": 0,
            "stationType": 0
        },
        "situation": {
            "informationQuality": 7,
            "eventType": {
                "causeCode": 14,
                "subCauseCode": 14
            }
        }
    }

    message["situation"]["eventType"]["causeCode"] = causeCode
    message["situation"]["eventType"]["subCauseCode"] = subCauseCode
    message["management"]["detectionTime"] = detectionTime
    message["management"]["referenceTime"] = detectionTime
    message["management"]["eventPosition"]["latitude"] = eventPosition["latitude"]
    message["management"]["eventPosition"]["longitude"] = eventPosition["longitude"]

    return json.dumps(message)


def on_message(client, userdata, message):
    print("Received message '" + str(message.payload) + "' on topic '"
          + message.topic + "' with QoS " + str(message.qos))


def main():

    obu1 = mqtt.Client()
    obu2 = mqtt.Client()
    obu3 = mqtt.Client()

    obu1.connect("192.168.98.20")
    obu2.connect("192.168.98.30")
    obu3.connect("192.168.98.40")

    obu1.on_message = on_message
    obu2.on_message = on_message
    obu3.on_message = on_message

    obu1.subscribe("vanetza/out/denm")
    obu2.subscribe("vanetza/out/denm")
    obu3.subscribe("vanetza/out/denm")

    coordinates = [(40.675051, -8.573572), (40.675057, -8.573565), (40.675066, -8.573558),
                   (40.675073, -8.573550), (40.675082, -8.573542), (40.675093, -8.573534)]

    obu1.loop_start()
    obu2.loop_start()
    obu3.loop_start()

    while(True):

        obu1_coordenates = {}

        obu2_coordenates = {}

        obu3_coordenates = {}

        obu1_animal = {}

        for i in range(len(coordinates)-1):  # 0 a 4

            if i == 0:
                obu1_coordenates["latitude"] = coordinates[i][0]
                obu1_coordenates["longitude"] = coordinates[i][1]

                cam1 = message_cam(obu1_coordenates)
            elif i == 1:
                obu1_coordenates["latitude"] = coordinates[i][0]
                obu1_coordenates["longitude"] = coordinates[i][1]

                obu2_coordenates["latitude"] = coordinates[i-1][0]
                obu2_coordenates["longitude"] = coordinates[i-1][1]

                cam1 = message_cam(obu1_coordenates)
                cam2 = message_cam(obu2_coordenates)

            obu1_coordenates["latitude"] = coordinates[i][0]
            obu1_coordenates["longitude"] = coordinates[i][1]

            obu2_coordenates["latitude"] = coordinates[i-1][0]
            obu2_coordenates["longitude"] = coordinates[i-1][1]

            obu3_coordenates["latitude"] = coordinates[i-1][0]
            obu3_coordenates["longitude"] = coordinates[i-1][1]

            cam1 = message_cam(obu1_coordenates)
            cam2 = message_cam(obu2_coordenates)
            cam3 = message_cam(obu3_coordenates)

            publish_cam(obu1, cam1)
            publish_cam(obu2, cam2)
            publish_cam(obu3, cam3)
            time.sleep(2)

        obu1_animal["latitude"] = coordinates[5][0]
        obu1_animal["longitude"] = coordinates[5][1]
        denm = message_demn(11, 1, time.time(), obu1_animal)
        publish_denm(obu1, denm)

        time.sleep(5)

    obu1.loop_stop()
    obu2.loop_stop()
    obu3.loop_stop()


main()
