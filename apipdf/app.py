import os
from flask import Flask, jsonify, render_template
import requests
import urllib3

grafana_services="localhost:3000"
grafana_services_public=os.getenv('grafana_domain')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
headers = {'Content-Type': 'application/json',
           "Authorization": "Bearer eyJrIjoiRUNxWE8zeDhkNDhYNnRWdWNnSms4ZTFGYXZwcG9mU2oiLCJuIjoicmVwb3J0ZXIiLCJpZCI6MX0="
           }

app = Flask(__name__)

@app.route('/')
def status():
    return jsonify({'status': 'ok'})

@app.route('/reporte/<uid>')
def reporte(uid):
    url_dashboard="http://"+grafana_services+"/api/dashboards/uid/"+uid
    data_grafana = requests.get(url_dashboard, headers=headers, verify=False).json()
    dashboard_data = data_grafana["dashboard"]

    dashboard_vars={}
    for var in dashboard_data["templating"]["list"]:
      dashboard_vars["var-"+var["name"]]=var["current"]["text"]

    dashboard_vars["from"]=dashboard_data["time"]["from"]
    dashboard_vars["to"]=dashboard_data["time"]["to"]

    vars_url=""
    for glb_var in dashboard_vars:
      if glb_var != "var-host":
        vars_url+="&"+str(glb_var)+"="+dashboard_vars[glb_var].replace(" ","+")

    if type(dashboard_vars["var-host"]) == type(""):
      dashboard_vars["var-host"]=[dashboard_vars["var-host"]]

    dashboard_rows=[{
        "row-name":"System report : "+vars_item,
        "panels":[{
            "var-host":vars_item,
            "title":panel["title"],
            "type":panel["type"],
            "id":panel["id"],
            "h":panel["gridPos"]["h"],
            "w":panel["gridPos"]["w"],
            "x":panel["gridPos"]["x"],
            "y":panel["gridPos"]["y"]
            }
        for panel in dashboard_data["panels"]
        ]
    }
    for vars_item in dashboard_vars["var-host"]
    ]

    data_render = [{
        "row-name" : row["row-name"],
        "img_panels" : [{
            "title" : panel["title"],
            "url" : "http://"+grafana_services_public+"/render/d-solo/"+uid+"/_?"+"height="+str(round(panel["h"]*(1000/24)))+"&width="+str(round(panel["w"]*(1280/24)))+"&panelId="+str(panel["id"])+"&theme=light"+"&var-host="+panel["var-host"]+vars_url,
            "w" : str(panel["w"]*100/24)
        }
        for panel in row["panels"]
        ]
    }
    for row in dashboard_rows
    ]
    return(render_template("reporte_grafana.html",
                           report_name=data_grafana["meta"]["slug"].capitalize(),
                           from_date=dashboard_vars["from"],
                           to_date=dashboard_vars["to"],
                           hosts=dashboard_vars["var-host"],
                           data_render=data_render))

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=os.getenv('PORT'))
