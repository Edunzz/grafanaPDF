import os
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def status():
    return jsonify({'status': 'ok'})

@app.route('/reporte/<uid>')
def reporte(uid):
    return(render_template("reporte_grafana.html",
                           report_name=data_grafana["meta"]["slug"],
                           from_date=dashboard_vars["from"],
                           to_date=dashboard_vars["to"],
                           data_render=data_render))

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=os.getenv('PORT'))
