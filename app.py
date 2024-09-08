from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_restful import Api
from api import user_api, ReportAPI, AnalyticsAPI
import requests
import sqlite3
import math

app = Flask(__name__)
app.secret_key = 'shazam'

api = Api(app)
api.add_resource(user_api, '/api/user')
api.add_resource(ReportAPI, '/api/report/<int:mine_id>')
api.add_resource(AnalyticsAPI, '/api/analytics/<int:mine_id>')

def get_db_connection():
    conn = sqlite3.connect('carbon')
    conn.row_factory = sqlite3.Row
    conn.create_function("FLOOR", 1, lambda x: math.floor(x) if x is not None else None)
    return conn

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login = {
            'username': request.form['username'],
            'password': request.form['password'],    
        }
        res = requests.get(request.url_root + 'api/user', json=login)
        if res.status_code == 200:
            session['username'] = login['username']
            return redirect(url_for('report'))
        else:
            return render_template('login.html', message="Wrong Username Or Password")
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        register = {
            'username': request.form['username'],
            'password': request.form['password'],
        }
        res = requests.post(request.url_root + 'api/user', json=register)
        if res.status_code == 200:
            return redirect(url_for('login'))
        else:
            return render_template('registration.html', message="Username already registered")
    return render_template('registration.html')

@app.route('/report', methods=['POST', 'GET'])
def report():
    if request.method == 'POST':
        try:
            data = {
        "quarter": request.form.get("quarter"),
        "year": request.form.get("year"),
        "excavation_emission": request.form.get("excavation_emission"),
        "transportation_emission": request.form.get("transportation_emission"),
        "equipment_emission": request.form.get("equipment_emission"),
        "renewable_energy_usage": request.form.get("renewable_energy_usage"),
        "afforestation_needed": request.form.get("afforestation_needed"),
        "carbon_credits_earned": request.form.get("carbon_credits_earned"),
        "electricity_consumption": request.form.get("electricity_consumption"),
        "energy_source_breakdown": request.form.get("energy_source_breakdown"),
        "renewable_energy_share": request.form.get("renewable_energy_share"),
        "diesel_consumption": request.form.get("diesel_consumption"),
        "gasoline_consumption": request.form.get("gasoline_consumption"),
        "natural_gas_consumption": request.form.get("natural_gas_consumption"),
        "other_fuels": request.form.get("other_fuels"),
        "generator_usage": request.form.get("generator_usage"),
        "equipment_list": request.form.get("equipment_list"),
        "equipment_fuel_consumption": request.form.get("equipment_fuel_consumption"),
        "equipment_operating_hours": request.form.get("equipment_operating_hours"),
        "equipment_power_rating": request.form.get("equipment_power_rating"),
        "fuel_type": request.form.get("fuel_type"),
        "maintenance_schedule": request.form.get("maintenance_schedule"),
        "volume_extracted": request.form.get("volume_extracted"),
        "blasting_details": request.form.get("blasting_details"),
        "processing_energy_consumption": request.form.get("processing_energy_consumption"),
        "waste_volume": request.form.get("waste_volume"),
        "water_consumption": request.form.get("water_consumption"),
        "water_source": request.form.get("water_source"),
        "water_treatment": request.form.get("water_treatment"),
        "other_resources": request.form.get("other_resources"),
        "methane_capture": request.form.get("methane_capture"),
        "methane_volume": request.form.get("methane_volume"),
        "methane_efficiency": request.form.get("methane_efficiency"),
        "dust_suppression": request.form.get("dust_suppression"),
        "air_quality_data": request.form.get("air_quality_data"),
        "ventilation_energy": request.form.get("ventilation_energy"),
        "airflow_rate": request.form.get("airflow_rate"),
        "waste_types": request.form.get("waste_types"),
        "waste_disposal_methods": request.form.get("waste_disposal_methods"),
        "emissions_from_waste": request.form.get("emissions_from_waste"),
        "carbon_sinks_area": request.form.get("carbon_sinks_area"),
        "vegetation_type": request.form.get("vegetation_type"),
        "carbon_sequestration_existing": request.form.get("carbon_sequestration_existing"),
        "afforestation_plans": request.form.get("afforestation_plans"),
        "carbon_sequestration_planned": request.form.get("carbon_sequestration_planned"),
        "qualifying_projects": request.form.get("qualifying_projects"),
        "current_carbon_credit_price": request.form.get("current_carbon_credit_price"),
        "renewable_energy_projects": request.form.get("renewable_energy_projects"),
        "energy_generated_renewables": request.form.get("energy_generated_renewables"),
        "energy_efficiency_measures": request.form.get("energy_efficiency_measures"),
        "recycling_programs": request.form.get("recycling_programs"),
        "recycled_material_amount": request.form.get("recycled_material_amount")
    }
            jsonify(data)
            response = requests.post(request.url_root + 'api/report/' + session['username'], json=data)
            if response.status_code == 201:
                return redirect(url_for('analysis'))
            else:
                # Render the template with a failure message if the response is not successful
                return render_template('index.html', message="Failed to submit report. Please try again.")
        except requests.RequestException as e:
            # Catch any errors during the API request and provide feedback
            return render_template('index.html', message=f"An error occurred: {e}")
    else:
        # Render the template for GET requests
        return render_template('index.html')
    
@app.route('/analysis', methods=['POST','GET'])
def analysis():
    mine_id = session.get('username')
    print(mine_id)
    response = requests.get(request.url_root + f'api/analytics/{mine_id}')
    if response.status_code == 200:
        return redirect(url_for('static', filename='content.pdf'))
    else:
        return "Analysis not available", 404

if __name__ == '__main__':
    app.run(debug=True)
