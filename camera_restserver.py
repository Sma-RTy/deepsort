from flask import Flask
from flask import Response
from flask import request
from waitress import serve
from sensecam_control import onvif_control
import json

class CameraControl:

    def __init__(self, position_file, ip, login, password):
        self.app = Flask(__name__)
        self.app.add_url_rule('/set_position', 'set_position', self.SetPosition, methods=['POST'])
        self.app.add_url_rule('/go_home', 'go_home', self.GoHome, methods=['POST'])
        self.camcontrol = onvif_control.CameraControl(ip, login, password)
        self.camcontrol.camera_start()
        self.camcontrol.go_home_position()
        self.camera_positions = json.load(open(position_file))
      
    def SetPosition(self):
      data = json.loads(request.data)
      
      if data['position'] in self.camera_positions:
        print ("Set position to %s (%s, %s, %s)" % (data['position'], self.camera_positions[ data['position']]['pan'], self.camera_positions[ data['position']]['tilt'], self.camera_positions[ data['position']]['zoom']))
        resp = Response("Set Camera to position %s\n" % data['position'])
        resp.status = 200
        self.camcontrol.absolute_move(self.camera_positions[ data['position']]['pan'], self.camera_positions[ data['position']]['tilt'], self.camera_positions[ data['position']]['zoom'])
      else:
        resp = Response("Position not allowed\n")
        resp.status = 500
      return resp

    def GoHome(self):
        print ("Set position to Home")
        resp = Response("Set Camera to Home position\n")
        resp.status = 200
        self.camcontrol.go_home_position()
        return resp
    
    def Run(self):
        print("Starting Camera Server App")
        serve(self.app, host="0.0.0.0", port=5200)
        return