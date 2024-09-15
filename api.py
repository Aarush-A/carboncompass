from flask import request, jsonify
from flask_restful import Resource
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import os
from fpdf import FPDF
import pandas as pd
import seaborn as sns
def connect():
    conn = sqlite3.connect('carbon')
    return conn

static_folder = 'static'

class user_api(Resource):
    def get(self):
        data = request.json
        user = data.get('username')
        passw = data.get('password')
        
        conn = connect()
        cursor = conn.cursor()
        
        fetch = cursor.execute('SELECT * FROM users WHERE mine_id=? AND password=?', (user, passw)).fetchone()
        conn.close()
        
        if fetch:
            return {'message': 'Login Successful'}, 200
        else:
            return {'message': 'Invalid Credentials'}, 401

    def post(self):
        data = request.json
        user = data.get('username')
        passw = data.get('password')
        conn = connect()
        cursor = conn.cursor()
        fetch = cursor.execute('SELECT * FROM users WHERE mine_id=?', (user,)).fetchall()
        if fetch:
            conn.close()
            return {'message': 'Username already registered'}, 400
        else:
            cursor.execute('INSERT INTO users (mine_id, password) VALUES (?, ?)', (user, passw))
            conn.commit()
            conn.close()
            return {'message': 'Registration successful'}, 200

class ReportAPI(Resource):
    def post(self, mine_id):
        try:
            data = request.json
            conn = sqlite3.connect('carbon')  # Adjust to your database connection
            cursor = conn.cursor()
            x=mine_id
            print(x)
            cursor.execute('''INSERT INTO quarterly_reports (
                mine_id, quarter, "year", excavation_emission, transportation_emission, equipment_emission, 
                renewable_energy_usage, afforestation_needed, carbon_credits_earned, electricity_consumption, 
                energy_source_breakdown, renewable_energy_share, diesel_consumption, gasoline_consumption, 
                natural_gas_consumption, other_fuels, generator_usage, equipment_list, equipment_fuel_consumption, 
                equipment_operating_hours, equipment_power_rating, fuel_type, maintenance_schedule, volume_extracted, 
                blasting_details, processing_energy_consumption, waste_volume, water_consumption, water_source, 
                water_treatment, other_resources, methane_capture, methane_volume, methane_efficiency, dust_suppression, 
                air_quality_data, ventilation_energy, airflow_rate, waste_types, waste_disposal_methods, emissions_from_waste, 
                carbon_sinks_area, vegetation_type, carbon_sequestration_existing, afforestation_plans, carbon_sequestration_planned, 
                qualifying_projects, current_carbon_credit_price, renewable_energy_projects, energy_generated_renewables, 
                energy_efficiency_measures, recycling_programs, recycled_material_amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (int(x), 
             data.get('quarter'), 
             data.get('year'), 
             data.get('excavation_emission'), 
             data.get('transportation_emission'), 
             data.get('equipment_emission'), 
             data.get('renewable_energy_usage'), 
             data.get('afforestation_needed'), 
             data.get('carbon_credits_earned'), 
             data.get('electricity_consumption'), 
             data.get('energy_source_breakdown'), 
             data.get('renewable_energy_share'), 
             data.get('diesel_consumption'), 
             data.get('gasoline_consumption'), 
             data.get('natural_gas_consumption'), 
             data.get('other_fuels'), 
             data.get('generator_usage'), 
             data.get('equipment_list'), 
             data.get('equipment_fuel_consumption'), 
             data.get('equipment_operating_hours'), 
             data.get('equipment_power_rating'), 
             data.get('fuel_type'), 
             data.get('maintenance_schedule'), 
             data.get('volume_extracted'), 
             data.get('blasting_details'), 
             data.get('processing_energy_consumption'), 
             data.get('waste_volume'), 
             data.get('water_consumption'), 
             data.get('water_source'), 
             data.get('water_treatment'), 
             data.get('other_resources'), 
             data.get('methane_capture'), 
             data.get('methane_volume'), 
             data.get('methane_efficiency'), 
             data.get('dust_suppression'), 
             data.get('air_quality_data'), 
             data.get('ventilation_energy'), 
             data.get('airflow_rate'), 
             data.get('waste_types'), 
             data.get('waste_disposal_methods'), 
             data.get('emissions_from_waste'), 
             data.get('carbon_sinks_area'), 
             data.get('vegetation_type'), 
             data.get('carbon_sequestration_existing'), 
             data.get('afforestation_plans'), 
             data.get('carbon_sequestration_planned'), 
             data.get('qualifying_projects'), 
             data.get('current_carbon_credit_price'), 
             data.get('renewable_energy_projects'), 
             data.get('energy_generated_renewables'), 
             data.get('energy_efficiency_measures'), 
             data.get('recycling_programs'), 
             data.get('recycled_material_amount')))
             
            conn.commit()
            conn.close()
            return 201
        except Exception as e:
            print(f"Error occurred: {e}")
            return 400

class AnalyticsAPI(Resource):
    def post(self, mine_id):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute('''SELECT mine_id, quarter, "year", excavation_emission, transportation_emission, equipment_emission, 
                        renewable_energy_usage, carbon_credits_earned, electricity_consumption, energy_source_breakdown, 
                        volume_extracted
                        FROM quarterly_reports 
                        WHERE mine_id = ?''', (mine_id,))
        data = cursor.fetchall()
        conn.close()

        columns = ['mine_id', 'quarter', 'year', 'excavation_emission', 'transportation_emission', 
                   'equipment_emission', 'renewable_energy_usage', 'carbon_credits_earned', 
                   'electricity_consumption', 'energy_source_breakdown', 'volume_extracted']
        df = pd.DataFrame(data, columns=columns)

        if df.empty:
            return jsonify({'message': 'No data found for this mine ID'}), 404
        
        df['quarter_year'] = df['quarter'].astype(str) + '-' + df['year'].astype(str)

        plt.figure(figsize=(10, 6))
        plt.plot(df['quarter_year'], df['excavation_emission'], label='Excavation Emission')
        plt.plot(df['quarter_year'], df['transportation_emission'], label='Transportation Emission')
        plt.xlabel('Quarter-Year')
        plt.ylabel('Emissions')
        plt.title('Emissions Over Time')
        plt.legend()
        emissions_graph_path = os.path.join(static_folder, 'emissions_graph.png')
        plt.savefig(emissions_graph_path)
        plt.close()

        energy_sources = df['energy_source_breakdown'].str.split(',', expand=True).stack().value_counts()
        plt.figure(figsize=(7, 7))
        plt.pie(energy_sources, labels=energy_sources.index, autopct='%1.1f%%', startangle=140)
        plt.title('Energy Source Breakdown')
        pie_chart_path = os.path.join(static_folder, 'energy_source_pie_chart.png')
        plt.savefig(pie_chart_path)
        plt.close()

        plt.figure(figsize=(10, 6))
        plt.bar(df['quarter_year'], df['renewable_energy_usage'], color='green')
        plt.xlabel('Quarter-Year')
        plt.ylabel('Renewable Energy Usage (kWh)')
        plt.title('Renewable Energy Usage Over Time')
        renewable_energy_path = os.path.join(static_folder, 'renewable_energy_bar_chart.png')
        plt.savefig(renewable_energy_path)
        plt.close()

        emission_types = ['excavation_emission', 'transportation_emission', 'equipment_emission']
        df['total_emissions'] = df[emission_types].sum(axis=1)
        df.set_index('quarter_year')[emission_types].plot(kind='bar', stacked=True)
        plt.xlabel('Quarter-Year')
        plt.ylabel('Emissions')
        plt.title('Total Emissions by Category Over Time')
        plt.tight_layout()
        emissions_breakdown_path = os.path.join(static_folder, 'emissions_breakdown_stacked_bar.png')
        plt.savefig(emissions_breakdown_path)
        plt.close()

        plt.figure(figsize=(10, 8))
        corr_matrix = df[['excavation_emission', 'transportation_emission', 'equipment_emission', 
                          'carbon_credits_earned', 'electricity_consumption', 'renewable_energy_usage']].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
        plt.title('Correlation Between Key Metrics')
        heatmap_path = os.path.join(static_folder, 'correlation_heatmap.png')
        plt.savefig(heatmap_path)
        plt.close()

        total_extraction = df['volume_extracted'].sum()
        average_emission = df[['excavation_emission', 'transportation_emission']].mean().mean()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Data Analysis Report", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Total Volume Extracted: {total_extraction}", ln=True)
        pdf.cell(200, 10, txt=f"Average Emission: {average_emission:.2f}", ln=True)

        # Add graphs to the PDF
        pdf.image(emissions_graph_path, x=10, y=40, w=180)
        pdf.add_page()  # New page for each graph
        pdf.image(pie_chart_path, x=10, y=10, w=180)
        pdf.add_page()
        pdf.image(renewable_energy_path, x=10, y=10, w=180)
        pdf.add_page()
        pdf.image(emissions_breakdown_path, x=10, y=10, w=180)
        pdf.add_page()
        pdf.image(heatmap_path, x=10, y=10, w=180)

        pdf_output_path = os.path.join(static_folder, "data_analysis_report.pdf")
        pdf.output(pdf_output_path)

        return jsonify({'message': 'Analysis complete, report generated.', 'report_url': f'/{static_folder}/data_analysis_report.pdf'}), 200
