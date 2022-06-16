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
        "latitude": 400000000,
        "length": 100,
        "longitude": -80000000,
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
        "width": 30,
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

def main():

    obu1 = mqtt.Client()
    obu2 = mqtt.Client()
    obu3 = mqtt.Client()
    
    obu1.connect("192.168.98.20")
    obu2.connect("192.168.98.30")
    obu3.connect("192.168.98.40")

    obu1_coordenates = {
        "latitude": 400000000,
        "longitude": -80000000
    }

    obu2_coordenates = {
        "latitude": 400001000,
        "longitude": -80001000
    }

    obu3_coordenates = {
        "latitude": 400002000,
        "longitude": -80002000
    }

    obu1_animal = {
        "latitude": 40.807799251415686,
        "longitude": -8.102353364491056
    }

    obu1.loop_start()
    obu2.loop_start()
    obu3.loop_start()

    counter = 0

    while(True):
        obu1_coordenates["latitude"] += 10
        obu1_coordenates["longitude"] += 10

        obu2_coordenates["latitude"] += 10
        obu2_coordenates["longitude"] += 10

        obu3_coordenates["latitude"] += 10
        obu3_coordenates["longitude"] += 10
        
        cam1 = message_cam(obu1_coordenates)
        cam2 = message_cam(obu2_coordenates)
        cam3 = message_cam(obu3_coordenates)
        
        publish_cam(obu1, cam1)
        publish_cam(obu2, cam2)
        publish_cam(obu3, cam3)

        if (counter % 100 == 0):
            denm = message_demn(11, 1, time.time(), obu1_animal)
            publish_denm(obu1, denm)

        time.sleep(10)
        counter += 0

    obu1.loop_stop()
    obu2.loop_stop()
    obu3.loop_stop()



if __name__ == "__main__":
    main()