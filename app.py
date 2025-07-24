#!/usr/bin/env python3
"""
Web Interface for Trucking Fleet Optimization Audit System
"""

from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, render_template_string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import random
import warnings
import io
import base64
import os
import threading
import time
import zipfile
from werkzeug.utils import secure_filename
warnings.filterwarnings('ignore')

# Set matplotlib to use non-interactive backend
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'zip'}

# Global variable to store audit results
audit_results = {}
audit_status = {"running": False, "complete": False, "progress": 0}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_zip_file(zip_path, extract_to):
    """Extract zip file and return list of extracted files"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            return zip_ref.namelist()
    except zipfile.BadZipFile:
        return None

class TruckingOptimizationAuditor:
    def __init__(self):
        self.data = None
        self.analysis_results = {}
        self.opportunities = []
        self.charts = {}
        
    def create_sample_data(self, num_records=500):
        """Generate realistic sample trucking data"""
        global audit_status
        audit_status["progress"] = 10
        
        # Set random seed for reproducible results
        np.random.seed(42)
        random.seed(42)
        
        # Define truck types and their characteristics
        truck_types = {
            'Heavy Duty': {'mpg_range': (6, 8), 'capacity': 80000, 'maintenance_mult': 1.2},
            'Medium Duty': {'mpg_range': (8, 12), 'capacity': 26000, 'maintenance_mult': 1.0},
            'Light Duty': {'mpg_range': (12, 18), 'capacity': 10000, 'maintenance_mult': 0.8}
        }
        
        routes = [
            'Route A (Local)', 'Route B (Regional)', 'Route C (Long Haul)',
            'Route D (Express)', 'Route E (Freight)'
        ]
        
        drivers = [f"Driver_{i:03d}" for i in range(1, 101)]
        
        data = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(num_records):
            truck_type = random.choice(list(truck_types.keys()))
            truck_specs = truck_types[truck_type]
            
            # Generate realistic data with some correlation
            base_mpg = random.uniform(*truck_specs['mpg_range'])
            
            # Add seasonal and operational variations
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 365)
            mpg = base_mpg * seasonal_factor * random.uniform(0.85, 1.15)
            
            miles_driven = random.randint(200, 800)
            fuel_cost_per_gallon = random.uniform(3.20, 4.50)
            
            # Calculate fuel consumption and costs
            fuel_consumed = miles_driven / mpg
            fuel_cost = fuel_consumed * fuel_cost_per_gallon
            
            # Maintenance costs (correlated with miles and truck type)
            base_maintenance = miles_driven * 0.15 * truck_specs['maintenance_mult']
            maintenance_cost = base_maintenance * random.uniform(0.7, 1.5)
            
            # Driver performance factors
            driver_efficiency = random.uniform(0.8, 1.2)
            
            # Route difficulty
            route = random.choice(routes)
            route_difficulty = {
                'Route A (Local)': 0.9,
                'Route B (Regional)': 1.0,
                'Route C (Long Haul)': 1.1,
                'Route D (Express)': 1.2,
                'Route E (Freight)': 1.05
            }[route]
            
            # Calculate total operational cost
            total_cost = fuel_cost + maintenance_cost
            
            # Generate date
            trip_date = start_date + timedelta(days=random.randint(0, 365))
            
            data.append({
                'Date': trip_date,
                'Truck_ID': f"TRK_{i%50:03d}",
                'Truck_Type': truck_type,
                'Driver_ID': random.choice(drivers),
                'Route': route,
                'Miles_Driven': round(miles_driven, 1),
                'Fuel_Consumed_Gallons': round(fuel_consumed, 2),
                'Fuel_Cost_Per_Gallon': round(fuel_cost_per_gallon, 2),
                'Total_Fuel_Cost': round(fuel_cost, 2),
                'Maintenance_Cost': round(maintenance_cost, 2),
                'Total_Operational_Cost': round(total_cost, 2),
                'MPG': round(mpg, 2),
                'Driver_Efficiency_Score': round(driver_efficiency, 2),
                'Route_Difficulty': route_difficulty,
                'Load_Weight_lbs': random.randint(5000, truck_specs['capacity']),
                'Weather_Condition': random.choice(['Clear', 'Rain', 'Snow', 'Fog', 'Wind']),
                'Speed_Avg_MPH': random.randint(45, 75)
            })
        
        self.data = pd.DataFrame(data)
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        
        # Save to CSV
        filename = 'sample_trucking_data.csv'
        self.data.to_csv(filename, index=False)
        
        audit_status["progress"] = 20
        return filename
    
    def analyze_fleet_performance(self):
        """Perform comprehensive fleet performance analysis"""
        global audit_status
        audit_status["progress"] = 40
        
        if self.data is None:
            return
        
        # Basic statistics
        self.analysis_results['total_trips'] = len(self.data)
        self.analysis_results['total_miles'] = self.data['Miles_Driven'].sum()
        self.analysis_results['total_fuel_cost'] = self.data['Total_Fuel_Cost'].sum()
        self.analysis_results['total_maintenance_cost'] = self.data['Maintenance_Cost'].sum()
        self.analysis_results['avg_mpg'] = self.data['MPG'].mean()
        
        # Performance by truck type
        truck_performance = self.data.groupby('Truck_Type').agg({
            'MPG': 'mean',
            'Total_Operational_Cost': 'mean',
            'Miles_Driven': 'sum',
            'Driver_Efficiency_Score': 'mean'
        }).round(2)
        
        self.analysis_results['truck_performance'] = truck_performance
        
        # Driver performance analysis
        driver_performance = self.data.groupby('Driver_ID').agg({
            'MPG': 'mean',
            'Total_Operational_Cost': 'mean',
            'Driver_Efficiency_Score': 'mean',
            'Miles_Driven': 'sum'
        }).round(2)
        
        # Identify top and bottom performers
        self.analysis_results['top_drivers'] = driver_performance.nlargest(5, 'MPG')
        self.analysis_results['bottom_drivers'] = driver_performance.nsmallest(5, 'MPG')
        
        # Route efficiency analysis
        route_analysis = self.data.groupby('Route').agg({
            'MPG': 'mean',
            'Total_Operational_Cost': 'mean',
            'Miles_Driven': 'sum'
        }).round(2)
        
        self.analysis_results['route_performance'] = route_analysis
        
        # Cost per mile analysis
        self.data['Cost_Per_Mile'] = self.data['Total_Operational_Cost'] / self.data['Miles_Driven']
        self.analysis_results['avg_cost_per_mile'] = self.data['Cost_Per_Mile'].mean()
        
        audit_status["progress"] = 60
    
    def identify_optimization_opportunities(self):
        """Identify specific optimization opportunities and calculate potential savings"""
        global audit_status
        audit_status["progress"] = 70
        
        opportunities = []
        
        # 1. Fuel Efficiency Improvement
        current_avg_mpg = self.analysis_results['avg_mpg']
        top_25_percentile_mpg = self.data['MPG'].quantile(0.75)
        
        if top_25_percentile_mpg > current_avg_mpg:
            total_miles = self.analysis_results['total_miles']
            avg_fuel_price = self.data['Fuel_Cost_Per_Gallon'].mean()
            
            # Calculate potential savings from improved fuel efficiency
            current_fuel_gallons = total_miles / current_avg_mpg
            improved_fuel_gallons = total_miles / top_25_percentile_mpg
            fuel_savings_gallons = current_fuel_gallons - improved_fuel_gallons
            annual_fuel_savings = fuel_savings_gallons * avg_fuel_price
            
            opportunities.append({
                'category': 'Fuel Efficiency',
                'description': f'Improve average MPG from {current_avg_mpg:.2f} to {top_25_percentile_mpg:.2f}',
                'potential_annual_savings': annual_fuel_savings,
                'implementation': 'Driver training, vehicle maintenance, route optimization'
            })
        
        # 2. Driver Performance Optimization
        driver_perf = self.data.groupby('Driver_ID')['MPG'].mean()
        low_performers = driver_perf[driver_perf < driver_perf.quantile(0.25)]
        
        if len(low_performers) > 0:
            # Calculate potential savings from improving bottom 25% drivers
            bottom_25_avg = low_performers.mean()
            median_mpg = driver_perf.median()
            
            low_performer_data = self.data[self.data['Driver_ID'].isin(low_performers.index)]
            total_miles_low_perf = low_performer_data['Miles_Driven'].sum()
            avg_fuel_price = self.data['Fuel_Cost_Per_Gallon'].mean()
            
            current_gallons = total_miles_low_perf / bottom_25_avg
            improved_gallons = total_miles_low_perf / median_mpg
            driver_savings = (current_gallons - improved_gallons) * avg_fuel_price
            
            opportunities.append({
                'category': 'Driver Training',
                'description': f'Improve bottom 25% drivers ({len(low_performers)} drivers) to median performance',
                'potential_annual_savings': driver_savings,
                'implementation': 'Eco-driving training, performance monitoring, incentive programs'
            })
        
        # 3. Route Optimization
        route_costs = self.data.groupby('Route')['Cost_Per_Mile'].mean()
        if route_costs.max() - route_costs.min() > 0.1:
            expensive_routes = route_costs[route_costs > route_costs.quantile(0.75)]
            avg_cost_per_mile = route_costs.mean()
            
            expensive_route_data = self.data[self.data['Route'].isin(expensive_routes.index)]
            total_miles_expensive = expensive_route_data['Miles_Driven'].sum()
            
            current_route_cost = expensive_route_data['Total_Operational_Cost'].sum()
            optimized_cost = total_miles_expensive * avg_cost_per_mile
            route_savings = current_route_cost - optimized_cost
            
            opportunities.append({
                'category': 'Route Optimization',
                'description': f'Optimize {len(expensive_routes)} high-cost routes',
                'potential_annual_savings': route_savings,
                'implementation': 'Route planning software, traffic analysis, load consolidation'
            })
        
        self.opportunities = opportunities
        total_savings = sum(opp['potential_annual_savings'] for opp in opportunities)
        
        audit_status["progress"] = 80
        return total_savings
    
    def create_chart_mpg_distribution(self):
        """Create MPG distribution chart"""
        plt.figure(figsize=(10, 6))
        plt.hist(self.data['MPG'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(self.data['MPG'].mean(), color='red', linestyle='--', linewidth=2, 
                   label=f'Average: {self.data["MPG"].mean():.2f}')
        plt.xlabel('Miles Per Gallon (MPG)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Fuel Efficiency (MPG)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return img_str
    
    def create_chart_cost_by_truck_type(self):
        """Create cost by truck type chart"""
        plt.figure(figsize=(10, 6))
        truck_costs = self.data.groupby('Truck_Type')['Total_Operational_Cost'].mean()
        bars = plt.bar(truck_costs.index, truck_costs.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        plt.xlabel('Truck Type')
        plt.ylabel('Average Operational Cost ($)')
        plt.title('Average Operational Cost by Truck Type')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'${height:.0f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Convert to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return img_str

def run_audit_background():
    """Run the audit in background"""
    global audit_results, audit_status
    
    audit_status = {"running": True, "complete": False, "progress": 0}
    
    try:
        auditor = TruckingOptimizationAuditor()
        
        # Create sample data
        csv_file = auditor.create_sample_data()
        
        # Analyze performance
        auditor.analyze_fleet_performance()
        
        # Identify opportunities
        total_savings = auditor.identify_optimization_opportunities()
        
        # Create charts
        audit_status["progress"] = 90
        mpg_chart = auditor.create_chart_mpg_distribution()
        cost_chart = auditor.create_chart_cost_by_truck_type()
        
        # Store results
        audit_results = {
            'total_savings': total_savings,
            'analysis_results': auditor.analysis_results,
            'opportunities': auditor.opportunities,
            'charts': {
                'mpg_distribution': mpg_chart,
                'cost_by_truck_type': cost_chart
            }
        }
        
        audit_status = {"running": False, "complete": True, "progress": 100}
        
    except Exception as e:
        audit_status = {"running": False, "complete": False, "progress": 0, "error": str(e)}

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/run_audit', methods=['POST'])
def run_audit():
    """Start the audit process"""
    global audit_status
    
    if not audit_status["running"]:
        # Start audit in background thread
        thread = threading.Thread(target=run_audit_background)
        thread.daemon = True
        thread.start()
        
    return redirect(url_for('progress'))

@app.route('/progress')
def progress():
    """Show audit progress"""
    return render_template('progress.html')

@app.route('/api/progress')
def api_progress():
    """API endpoint for progress updates"""
    return jsonify(audit_status)

@app.route('/results')
def results():
    """Show audit results"""
    if audit_status["complete"] and audit_results:
        return render_template('results.html', results=audit_results)
    else:
        return redirect(url_for('index'))

@app.route('/download_csv')
def download_csv():
    """Download the sample CSV data"""
    if os.path.exists('sample_trucking_data.csv'):
        return send_file('sample_trucking_data.csv', as_attachment=True)
    else:
        return "File not found", 404

# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Create base template
base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Trucking Fleet Optimization Audit{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 80px 0;
        }
        .card {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: none;
        }
        .savings-highlight {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-truck"></i> Fleet Optimizer
            </a>
        </div>
    </nav>

    {% block content %}{% endblock %}

    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container text-center">
            <p>&copy; 2024 Trucking Fleet Optimization Audit Tool</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>"""

with open('templates/base.html', 'w') as f:
    f.write(base_template)

# Create index template
index_template = """{% extends "base.html" %}

{% block content %}
<div class="hero-section">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto text-center">
                <h1 class="display-4 mb-4">
                    <i class="fas fa-truck"></i> Trucking Fleet Optimization Audit
                </h1>
                <p class="lead mb-4">
                    Discover hidden cost savings in your trucking fleet with our comprehensive AI-powered analysis.
                    Identify optimization opportunities worth thousands of dollars annually.
                </p>
                <form method="POST" action="{{ url_for('run_audit') }}">
                    <button type="submit" class="btn btn-success btn-lg">
                        <i class="fas fa-play"></i> Start Free Demo Audit
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

<div class="container py-5">
    <div class="row">
        <div class="col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <i class="fas fa-chart-line fa-3x text-primary mb-3"></i>
                    <h4>Performance Analysis</h4>
                    <p>Comprehensive analysis of fuel efficiency, costs, and driver performance across your entire fleet.</p>
                </div>
            </div>
        </div>
        <div class="col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <i class="fas fa-dollar-sign fa-3x text-success mb-3"></i>
                    <h4>Cost Savings</h4>
                    <p>Identify specific opportunities for cost reduction with detailed calculations of potential annual savings.</p>
                </div>
            </div>
        </div>
        <div class="col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <i class="fas fa-route fa-3x text-info mb-3"></i>
                    <h4>Route Optimization</h4>
                    <p>Analyze route efficiency and identify opportunities for fuel savings through optimized routing.</p>
                </div>
            </div>
        </div>
    </div>

    <div class="row mt-5">
        <div class="col-lg-12">
            <h2 class="text-center mb-4">What You'll Get</h2>
            <div class="row">
                <div class="col-md-6">
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item"><i class="fas fa-check text-success"></i> Detailed performance analysis</li>
                        <li class="list-group-item"><i class="fas fa-check text-success"></i> Cost optimization opportunities</li>
                        <li class="list-group-item"><i class="fas fa-check text-success"></i> Driver performance rankings</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item"><i class="fas fa-check text-success"></i> Interactive charts and graphs</li>
                        <li class="list-group-item"><i class="fas fa-check text-success"></i> Implementation recommendations</li>
                        <li class="list-group-item"><i class="fas fa-check text-success"></i> Downloadable data and reports</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""

with open('templates/index.html', 'w') as f:
    f.write(index_template)

# Create progress template
progress_template = """{% extends "base.html" %}

{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-lg-8 mx-auto">
            <div class="card">
                <div class="card-body text-center">
                    <h2 class="mb-4">
                        <i class="fas fa-cogs"></i> Running Fleet Optimization Audit
                    </h2>
                    
                    <div class="progress mb-4" style="height: 30px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" id="progressBar" style="width: 0%">
                            <span id="progressText">0%</span>
                        </div>
                    </div>
                    
                    <p class="lead" id="statusText">Initializing audit...</p>
                    
                    <div id="completedSection" style="display: none;">
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle"></i> Audit completed successfully!
                        </div>
                        <a href="{{ url_for('results') }}" class="btn btn-primary btn-lg">
                            <i class="fas fa-chart-bar"></i> View Results
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function updateProgress() {
    fetch('/api/progress')
        .then(response => response.json())
        .then(data => {
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            const statusText = document.getElementById('statusText');
            const completedSection = document.getElementById('completedSection');
            
            progressBar.style.width = data.progress + '%';
            progressText.textContent = data.progress + '%';
            
            if (data.running) {
                if (data.progress < 20) {
                    statusText.textContent = 'Generating sample data...';
                } else if (data.progress < 40) {
                    statusText.textContent = 'Loading and validating data...';
                } else if (data.progress < 60) {
                    statusText.textContent = 'Analyzing fleet performance...';
                } else if (data.progress < 80) {
                    statusText.textContent = 'Identifying optimization opportunities...';
                } else {
                    statusText.textContent = 'Creating visualizations...';
                }
            } else if (data.complete) {
                statusText.textContent = 'Analysis complete!';
                completedSection.style.display = 'block';
                clearInterval(progressInterval);
            } else if (data.error) {
                statusText.textContent = 'Error: ' + data.error;
                progressBar.classList.add('bg-danger');
                clearInterval(progressInterval);
            }
        });
}

// Update progress every second
const progressInterval = setInterval(updateProgress, 1000);
updateProgress(); // Initial call
</script>
{% endblock %}"""

with open('templates/progress.html', 'w') as f:
    f.write(progress_template)

# Create results template
results_template = """{% extends "base.html" %}

{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="text-center mb-4">
                <i class="fas fa-chart-bar"></i> Fleet Optimization Audit Results
            </h1>
            
            <div class="savings-highlight">
                <h2><i class="fas fa-dollar-sign"></i> Potential Annual Savings</h2>
                <h1 class="display-3">${{ "{:,.2f}".format(results.total_savings) }}</h1>
                <p>Identified {{ results.opportunities|length }} optimization opportunities</p>
            </div>
        </div>
    </div>

    <div class="row mb-4">
        <div class="col-lg-6 mb-4">
            <div class="card">
                <div class="card-header">
                    <h4><i class="fas fa-tachometer-alt"></i> Fleet Performance Summary</h4>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-6">
                            <strong>Total Trips:</strong><br>
                            <span class="text-primary fs-4">{{ "{:,}".format(results.analysis_results.total_trips) }}</span>
                        </div>
                        <div class="col-6">
                            <strong>Total Miles:</strong><br>
                            <span class="text-primary fs-4">{{ "{:,.0f}".format(results.analysis_results.total_miles) }}</span>
                        </div>
                    </div>
                    <hr>
                    <div class="row">
                        <div class="col-6">
                            <strong>Average MPG:</strong><br>
                            <span class="text-success fs-4">{{ "{:.2f}".format(results.analysis_results.avg_mpg) }}</span>
                        </div>
                        <div class="col-6">
                            <strong>Cost per Mile:</strong><br>
                            <span class="text-warning fs-4">${{ "{:.2f}".format(results.analysis_results.avg_cost_per_mile) }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-lg-6 mb-4">
            <div class="card">
                <div class="card-header">
                    <h4><i class="fas fa-download"></i> Download Reports</h4>
                </div>
                <div class="card-body">
                    <p>Download your fleet data and analysis results:</p>
                    <a href="{{ url_for('download_csv') }}" class="btn btn-outline-primary btn-block mb-2">
                        <i class="fas fa-file-csv"></i> Download Sample Data (CSV)
                    </a>
                    <button class="btn btn-outline-secondary btn-block" onclick="window.print()">
                        <i class="fas fa-print"></i> Print This Report
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="row mb-4">
        <div class="col-lg-12">
            <div class="card">
                <div class="card-header">
                    <h4><i class="fas fa-lightbulb"></i> Optimization Opportunities</h4>
                </div>
                <div class="card-body">
                    {% for opp in results.opportunities %}
                    <div class="alert alert-info">
                        <h5><i class="fas fa-arrow-up"></i> {{ opp.category }}</h5>
                        <p><strong>Description:</strong> {{ opp.description }}</p>
                        <p><strong>Potential Annual Savings:</strong> <span class="text-success">${{ "{:,.2f}".format(opp.potential_annual_savings) }}</span></p>
                        <p><strong>Implementation:</strong> {{ opp.implementation }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <div class="row mb-4">
        <div class="col-lg-6 mb-4">
            <div class="card">
                <div class="card-header">
                    <h4><i class="fas fa-chart-histogram"></i> Fuel Efficiency Distribution</h4>
                </div>
                <div class="card-body text-center">
                    <img src="data:image/png;base64,{{ results.charts.mpg_distribution }}" 
                         class="img-fluid" alt="MPG Distribution Chart">
                </div>
            </div>
        </div>
        
        <div class="col-lg-6 mb-4">
            <div class="card">
                <div class="card-header">
                    <h4><i class="fas fa-chart-bar"></i> Cost by Truck Type</h4>
                </div>
                <div class="card-body text-center">
                    <img src="data:image/png;base64,{{ results.charts.cost_by_truck_type }}" 
                         class="img-fluid" alt="Cost by Truck Type Chart">
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-lg-12">
            <div class="card">
                <div class="card-header">
                    <h4><i class="fas fa-trophy"></i> Driver Performance</h4>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h5 class="text-success">Top Performing Drivers</h5>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Driver</th>
                                            <th>Avg MPG</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for driver_id, metrics in results.analysis_results.top_drivers.iterrows() %}
                                        <tr>
                                            <td>{{ driver_id }}</td>
                                            <td>{{ "{:.2f}".format(metrics.MPG) }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h5 class="text-warning">Improvement Opportunities</h5>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Driver</th>
                                            <th>Avg MPG</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for driver_id, metrics in results.analysis_results.bottom_drivers.iterrows() %}
                                        <tr>
                                            <td>{{ driver_id }}</td>
                                            <td>{{ "{:.2f}".format(metrics.MPG) }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row mt-4">
        <div class="col-lg-12 text-center">
            <a href="{{ url_for('index') }}" class="btn btn-primary btn-lg">
                <i class="fas fa-redo"></i> Run Another Audit
            </a>
        </div>
    </div>
</div>
{% endblock %}"""

with open('templates/results.html', 'w') as f:
    f.write(results_template)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle zip file uploads"""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(file_path)
                
                # Extract the zip file
                extract_path = os.path.join(app.config['UPLOAD_FOLDER'], f"extracted_{timestamp}")
                extracted_files = extract_zip_file(file_path, extract_path)
                
                if extracted_files:
                    flash(f'File successfully uploaded and extracted! Found {len(extracted_files)} files.')
                    return jsonify({
                        'success': True,
                        'message': f'Zip file uploaded and extracted successfully',
                        'filename': filename,
                        'extracted_files': extracted_files,
                        'extract_path': extract_path
                    })
                else:
                    flash('Error: Invalid zip file')
                    return jsonify({'success': False, 'error': 'Invalid zip file'})
                    
            except Exception as e:
                flash(f'Error uploading file: {str(e)}')
                return jsonify({'success': False, 'error': str(e)})
        else:
            flash('Error: Only .zip files are allowed')
            return jsonify({'success': False, 'error': 'Only .zip files are allowed'})
    
    # GET request - show upload form
    upload_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload Zip File</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .upload-container { max-width: 500px; margin: 0 auto; }
            .upload-area { 
                border: 2px dashed #ccc; 
                border-radius: 10px; 
                padding: 40px; 
                text-align: center; 
                background-color: #f9f9f9;
            }
            .upload-area:hover { border-color: #007bff; }
            .btn { 
                background-color: #007bff; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
            }
            .btn:hover { background-color: #0056b3; }
            .alert { padding: 15px; margin-bottom: 20px; border-radius: 4px; }
            .alert-success { background-color: #d4edda; color: #155724; }
            .alert-error { background-color: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="upload-container">
            <h1>Upload Zip File</h1>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-success">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="post" enctype="multipart/form-data">
                <div class="upload-area">
                    <p>Choose a zip file to upload</p>
                    <input type="file" name="file" accept=".zip" required>
                    <br><br>
                    <button type="submit" class="btn">Upload Zip File</button>
                </div>
            </form>
            
            <br>
            <a href="/">← Back to Main Page</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(upload_template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)