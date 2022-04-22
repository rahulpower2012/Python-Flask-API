from flask import Flask, request, Response
from flask_restful import Resource, Api
import requests
import json
from xml.etree import ElementTree as et
from dotenv import load_dotenv
import os


load_dotenv()
A_KEY = os.getenv("A_KEY")

app = Flask(__name__)
api = Api(app)


class Location(Resource):
    def get(self):
        return Response(json.dumps(
                        {"error": "only post requests are allowed"}
                        ),
                        status=400,
                        mimetype='application/json'
                        )

    def post(self):
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            data = request.get_json()

            if("output_format" not in data.keys() or
                "address" not in data.keys()
               ):
                return Response(json.dumps(
                                    {
                                        "error": "missing parameters",
                                        "required":
                                        {
                                            "output_format": "<json>OR<xml>",
                                            "address": "<YOUR ADDRESS>"
                                        }
                                    }
                                ),
                                status=400,
                                mimetype='application/json'
                                )
            elif(data["output_format"].replace(" ", "") == "" or
                    data["address"].replace(" ", "") == ""
                 ):
                return Response(json.dumps(
                                    {
                                        "error": "missing parameter values",
                                        "required":
                                        {
                                            "output_format": "<json>OR<xml>",
                                            "address": "<YOUR ADDRESS>"
                                        }
                                    }
                                ),
                                status=400,
                                mimetype='application/json'
                                )

            baseUrl = 'https://maps.googleapis.com/maps/api/geocode/json'
            endpoint = f"{baseUrl}?address={data['address']}&key={A_KEY}"

            r = requests.get(endpoint)
            try:
                if data["output_format"] == "json":
                    resp = {"address": data["address"],
                            "coordinates": {
                                "lat": r.json()
                                ['results'][0]['geometry']['location']['lat'],
                                "lng": r.json()
                                ['results'][0]['geometry']['location']['lng']
                            }}
                    return Response(json.dumps(resp),
                                    status=200,
                                    mimetype='application/json'
                                    )

                elif data["output_format"] == "xml":
                    root = et.Element("root")
                    address = et.SubElement(root, "address")
                    address.text = data["address"]
                    coordinates = et.SubElement(root, 'coordinates')
                    lat = et.SubElement(coordinates, "lat")
                    lat.text = str(r.json()
                                   ['results'][0]
                                   ['geometry']['location']['lat']
                                   )
                    lng = et.SubElement(coordinates, "lng")
                    lng.text = str(r.json()
                                   ['results'][0]
                                   ['geometry']['location']['lng']
                                   )
                    resp = et.tostring(root)

                    return Response(resp,
                                    status=200,
                                    mimetype='application/xml'
                                    )
            except:
                return Response(json.dumps(
                                {"error": "could not find location"}),
                                status=400,
                                mimetype='application/json'
                                )

        else:
            return Response(json.dumps(
                            {"error": "Content type not supported"}),
                            status=400,
                            mimetype='application/json'
                            )


api.add_resource(Location, "/getAddressDetails")

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    print(type(os.environ.get('DEV')))
    DEV = True if os.environ.get('DEV', 'False') == 'True' else False
    app.run(debug=DEV, port=PORT)
