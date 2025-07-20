#!/usr/bin/env python3
"""
Trucking Fleet Optimization Audit System
A comprehensive tool for analyzing trucking fleet performance and identifying cost-saving opportunities.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

class TruckingOptimizationAuditor:
    def __init__(self):
        self.data = None
        self.analysis_results = {}
        self.opportunities = []
        self.charts = {}
        
    def create_sample_data(self, num_records=500):
        """Generate realistic sample trucking data"""
        print("📊 Creating sample trucking data...")
        
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
        print(f"✅ Sample data created: {filename}")
        
        return filename
    
    def load_data(self, csv_file):
        """Load trucking data from CSV file"""
        try:
            self.data = pd.read_csv(csv_file)
            self.data['Date'] = pd.to_datetime(self.data['Date'])
            print(f"✅ Successfully loaded {len(self.data)} records")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def analyze_fleet_performance(self):
        """Perform comprehensive fleet performance analysis"""
        print("🔍 Analyzing fleet performance...")
        
        if self.data is None:
            print("❌ No data loaded. Please load data first.")
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
        
        print("✅ Fleet performance analysis complete")
    
    def identify_optimization_opportunities(self):
        """Identify specific optimization opportunities and calculate potential savings"""
        print("💡 Identifying optimization opportunities...")
        
        opportunities = []
        
        # 1. Fuel Efficiency Improvement
        current_avg_mpg = self.analysis_results['avg_mpg']
        top_25_percentile_mpg = self.data['MPG'].quantile(0.75)
        
        if top_25_percentile_mpg > current_avg_mpg:
            mpg_improvement = top_25_percentile_mpg - current_avg_mpg
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
        if route_costs.max() - route_costs.min() > 0.1:  # Significant difference in route costs
            
            # Find most expensive routes
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
        
        print(f"✅ Identified {len(opportunities)} optimization opportunities")
        print(f"💰 Total potential annual savings: ${total_savings:,.2f}")
        
        return total_savings
    
    def create_visualizations(self):
        """Create visualizations for the audit report"""
        print("📊 Creating visualizations...")
        
        # Set up the plotting style
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
        
        # 1. MPG Distribution
        plt.figure(figsize=(10, 6))
        plt.hist(self.data['MPG'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(self.data['MPG'].mean(), color='red', linestyle='--', linewidth=2, label=f'Average: {self.data["MPG"].mean():.2f}')
        plt.xlabel('Miles Per Gallon (MPG)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Fuel Efficiency (MPG)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('mpg_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Cost Analysis by Truck Type
        plt.figure(figsize=(12, 6))
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
        plt.savefig('cost_by_truck_type.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Driver Performance Scatter Plot
        plt.figure(figsize=(10, 6))
        driver_stats = self.data.groupby('Driver_ID').agg({
            'MPG': 'mean',
            'Total_Operational_Cost': 'mean',
            'Miles_Driven': 'sum'
        })
        
        scatter = plt.scatter(driver_stats['MPG'], driver_stats['Total_Operational_Cost'], 
                            s=driver_stats['Miles_Driven']/20, alpha=0.6, c='coral')
        plt.xlabel('Average MPG')
        plt.ylabel('Average Operational Cost ($)')
        plt.title('Driver Performance: MPG vs Operational Cost\n(Bubble size = Total Miles Driven)')
        plt.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(driver_stats['MPG'], driver_stats['Total_Operational_Cost'], 1)
        p = np.poly1d(z)
        plt.plot(driver_stats['MPG'], p(driver_stats['MPG']), "r--", alpha=0.8)
        
        plt.tight_layout()
        plt.savefig('driver_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Monthly Trend Analysis
        plt.figure(figsize=(12, 6))
        monthly_data = self.data.groupby(self.data['Date'].dt.to_period('M')).agg({
            'MPG': 'mean',
            'Total_Operational_Cost': 'sum'
        })
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        color = 'tab:blue'
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Average MPG', color=color)
        line1 = ax1.plot(range(len(monthly_data)), monthly_data['MPG'], color=color, marker='o', linewidth=2)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, alpha=0.3)
        
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Total Operational Cost ($)', color=color)
        line2 = ax2.plot(range(len(monthly_data)), monthly_data['Total_Operational_Cost'], color=color, marker='s', linewidth=2)
        ax2.tick_params(axis='y', labelcolor=color)
        
        # Set x-axis labels
        ax1.set_xticks(range(len(monthly_data)))
        ax1.set_xticklabels([str(period) for period in monthly_data.index], rotation=45)
        
        plt.title('Monthly Performance Trends')
        plt.tight_layout()
        plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Visualizations created")
    
    def generate_text_report(self, company_name="Fleet Company", output_filename="fleet_audit_report.txt"):
        """Generate a comprehensive text report"""
        print("📄 Generating text report...")
        
        report_content = []
        report_content.append("="*60)
        report_content.append("TRUCKING FLEET OPTIMIZATION AUDIT REPORT")
        report_content.append("="*60)
        report_content.append(f"Company: {company_name}")
        report_content.append(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append(f"Analysis Period: {self.data['Date'].min().strftime('%Y-%m-%d')} to {self.data['Date'].max().strftime('%Y-%m-%d')}")
        report_content.append("")
        
        # Executive Summary
        report_content.append("EXECUTIVE SUMMARY")
        report_content.append("-" * 20)
        total_savings = sum(opp['potential_annual_savings'] for opp in self.opportunities)
        report_content.append(f"Total Records Analyzed: {self.analysis_results['total_trips']:,}")
        report_content.append(f"Total Miles Driven: {self.analysis_results['total_miles']:,.0f}")
        report_content.append(f"Total Fuel Costs: ${self.analysis_results['total_fuel_cost']:,.2f}")
        report_content.append(f"Average MPG: {self.analysis_results['avg_mpg']:.2f}")
        report_content.append(f"Average Cost per Mile: ${self.analysis_results['avg_cost_per_mile']:.2f}")
        report_content.append(f"POTENTIAL ANNUAL SAVINGS: ${total_savings:,.2f}")
        report_content.append("")
        
        # Fleet Performance Analysis
        report_content.append("FLEET PERFORMANCE ANALYSIS")
        report_content.append("-" * 30)
        report_content.append("\nPerformance by Truck Type:")
        for truck_type, metrics in self.analysis_results['truck_performance'].iterrows():
            report_content.append(f"  {truck_type}:")
            report_content.append(f"    - Average MPG: {metrics['MPG']:.2f}")
            report_content.append(f"    - Average Cost: ${metrics['Total_Operational_Cost']:.2f}")
            report_content.append(f"    - Total Miles: {metrics['Miles_Driven']:,.0f}")
        
        report_content.append("\nTop 5 Performing Drivers (by MPG):")
        for idx, (driver_id, metrics) in enumerate(self.analysis_results['top_drivers'].iterrows(), 1):
            report_content.append(f"  {idx}. {driver_id}: {metrics['MPG']:.2f} MPG")
        
        report_content.append("\nBottom 5 Performing Drivers (by MPG):")
        for idx, (driver_id, metrics) in enumerate(self.analysis_results['bottom_drivers'].iterrows(), 1):
            report_content.append(f"  {idx}. {driver_id}: {metrics['MPG']:.2f} MPG")
        
        # Optimization Opportunities
        report_content.append("\n\nOPTIMIZATION OPPORTUNITIES")
        report_content.append("-" * 35)
        for i, opp in enumerate(self.opportunities, 1):
            report_content.append(f"\n{i}. {opp['category']}")
            report_content.append(f"   Description: {opp['description']}")
            report_content.append(f"   Potential Annual Savings: ${opp['potential_annual_savings']:,.2f}")
            report_content.append(f"   Implementation: {opp['implementation']}")
        
        # Recommendations
        report_content.append("\n\nRECOMMENDATIONS")
        report_content.append("-" * 15)
        report_content.append("1. Implement comprehensive driver training program focusing on fuel-efficient driving")
        report_content.append("2. Install telematics systems for real-time monitoring of vehicle performance")
        report_content.append("3. Optimize route planning using advanced logistics software")
        report_content.append("4. Establish regular vehicle maintenance schedules")
        report_content.append("5. Consider fleet modernization for older, less efficient vehicles")
        report_content.append("6. Implement driver incentive programs based on fuel efficiency metrics")
        
        # Save report
        with open(output_filename, 'w') as f:
            f.write('\n'.join(report_content))
        
        print(f"✅ Text report generated: {output_filename}")
        return output_filename
    
    def run_complete_audit(self, csv_file_path=None, company_name="Fleet Company", output_filename="fleet_audit_report.txt"):
        """Run the complete audit process"""
        print("🚛 Starting Trucking Fleet Optimization Audit...")
        print("=" * 50)
        
        # Load or create data
        if csv_file_path is None:
            csv_file_path = self.create_sample_data()
        
        if not self.load_data(csv_file_path):
            return
        
        # Perform analysis
        self.analyze_fleet_performance()
        total_savings = self.identify_optimization_opportunities()
        self.create_visualizations()
        report_file = self.generate_text_report(company_name, output_filename)
        
        print("=" * 50)
        print("🎉 Audit complete! Check your files for detailed findings.")
        print(f"📊 Charts saved as PNG files")
        print(f"📄 Report saved as: {report_file}")
        print(f"💰 POTENTIAL ANNUAL SAVINGS: ${total_savings:,.2f}")
        
        return {
            'total_savings': total_savings,
            'report_file': report_file,
            'opportunities': len(self.opportunities)
        }

# Main execution
if __name__ == "__main__":
    # Create auditor instance
    auditor = TruckingOptimizationAuditor()
    
    # Run the complete audit
    results = auditor.run_complete_audit(
        csv_file_path=None,  # Will create sample data
        company_name="Demo Trucking Company",
        output_filename="demo_fleet_audit.txt"
    )
    
    print("\n📁 Generated Files:")
    print("- sample_trucking_data.csv (sample data)")
    print("- demo_fleet_audit.txt (detailed report)")
    print("- mpg_distribution.png (fuel efficiency chart)")
    print("- cost_by_truck_type.png (cost analysis chart)")
    print("- driver_performance.png (driver performance chart)")
    print("- monthly_trends.png (trend analysis chart)")