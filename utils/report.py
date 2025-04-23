import os
import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import tempfile

class ReportGenerator:
    def __init__(self, analytics_manager):
        self.analytics_manager = analytics_manager
        self.report_dir = 'data/reports'
        os.makedirs(self.report_dir, exist_ok=True)
    
    def _generate_charts(self, data, days):
        """Generate charts for the report"""
        daily_data = data['daily']
        
        if not daily_data:
            # Create empty charts if no data
            dates = [datetime.datetime.now().strftime('%Y-%m-%d')]
            screen_times = [0]
            blink_counts = [0]
            distances = [0]
            postures = [0]
        else:
            dates = [day['date'] for day in daily_data]
            screen_times = [day['screen_time_minutes'] / 60 for day in daily_data]  # Convert to hours
            blink_counts = [day['blink_count'] for day in daily_data]
            distances = [day['avg_distance'] for day in daily_data]
            postures = [day['good_posture_percentage'] for day in daily_data]
        
        charts = {}
        
        try:
            # Create screen time chart
            plt.figure(figsize=(10, 6))
            plt.bar(dates, screen_times, color='#4CAF50')
            plt.xlabel('Date')
            plt.ylabel('Screen Time (hours)')
            plt.title('Daily Screen Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            screen_time_chart = f"{self.report_dir}/screen_time_chart.png"
            plt.savefig(screen_time_chart)
            plt.close()
            charts['screen_time'] = screen_time_chart
            
            # Create blink count chart
            plt.figure(figsize=(10, 6))
            plt.bar(dates, blink_counts, color='#2196F3')
            plt.xlabel('Date')
            plt.ylabel('Blink Count')
            plt.title('Daily Blink Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            blink_count_chart = f"{self.report_dir}/blink_count_chart.png"
            plt.savefig(blink_count_chart)
            plt.close()
            charts['blink_count'] = blink_count_chart
            
            # Create distance chart
            plt.figure(figsize=(10, 6))
            plt.bar(dates, distances, color='#FFC107')
            plt.xlabel('Date')
            plt.ylabel('Average Distance (cm)')
            plt.title('Daily Average Distance from Screen')
            plt.xticks(rotation=45)
            plt.axhline(y=45, color='r', linestyle='-', label='Recommended Minimum (45cm)')
            plt.legend()
            plt.tight_layout()
            distance_chart = f"{self.report_dir}/distance_chart.png"
            plt.savefig(distance_chart)
            plt.close()
            charts['distance'] = distance_chart
            
            # Create posture chart
            plt.figure(figsize=(10, 6))
            plt.bar(dates, postures, color='#9C27B0')
            plt.xlabel('Date')
            plt.ylabel('Good Posture (%)')
            plt.title('Daily Good Posture Percentage')
            plt.xticks(rotation=45)
            plt.ylim(0, 100)
            plt.tight_layout()
            posture_chart = f"{self.report_dir}/posture_chart.png"
            plt.savefig(posture_chart)
            plt.close()
            charts['posture'] = posture_chart
        except Exception as e:
            print(f"Error generating charts: {e}")
            # Create placeholder images
            for chart_type in ['screen_time', 'blink_count', 'distance', 'posture']:
                if chart_type not in charts:
                    # Create a simple placeholder image
                    plt.figure(figsize=(10, 6))
                    plt.text(0.5, 0.5, f"No data available for {chart_type.replace('_', ' ')}",
                             horizontalalignment='center', verticalalignment='center', fontsize=14)
                    plt.axis('off')
                    chart_path = f"{self.report_dir}/{chart_type}_chart.png"
                    plt.savefig(chart_path)
                    plt.close()
                    charts[chart_type] = chart_path
        
        return charts
    
    def generate_report(self, days=7):
        """Generate a PDF report with analytics data"""
        data = self.analytics_manager.get_analytics_data(days)
        charts = self._generate_charts(data, days)
        
        try:
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Set up PDF
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Eye Care Assistant - Usage Report', 0, 1, 'C')
            pdf.set_font('Arial', '', 12)
            
            # Add date range
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days)
            pdf.cell(0, 10, f"Report Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", 0, 1)
            
            # Add summary
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Summary', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            totals = data['totals']
            pdf.cell(0, 8, f"Total Screen Time: {totals['total_screen_time']/60:.2f} hours", 0, 1)
            pdf.cell(0, 8, f"Total Blinks: {totals['total_blinks']}", 0, 1)
            pdf.cell(0, 8, f"Average Distance from Screen: {totals['avg_distance']:.2f} cm", 0, 1)
            pdf.cell(0, 8, f"Average Good Posture: {totals['avg_posture']:.2f}%", 0, 1)
            pdf.cell(0, 8, f"Total Eye Exercises Completed: {totals['total_exercises']}", 0, 1)
            
            # Add charts
            for chart_title, chart_path in [
                ('Screen Time Analysis', charts['screen_time']),
                ('Blink Analysis', charts['blink_count']),
                ('Distance Analysis', charts['distance']),
                ('Posture Analysis', charts['posture'])
            ]:
                pdf.add_page()
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, chart_title, 0, 1)
                
                try:
                    pdf.image(chart_path, x=10, y=30, w=190)
                except Exception as e:
                    print(f"Error adding image to PDF: {e}")
                    pdf.set_font('Arial', '', 12)
                    pdf.cell(0, 40, 'Chart image could not be loaded', 0, 1, 'C')
            
            # Add recommendations
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Recommendations', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            recommendations = [
                "Follow the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for 20 seconds.",
                "Maintain at least 45-50 cm distance from your screen.",
                "Aim for a blink rate of at least 15 blinks per minute during screen use.",
                "Maintain good posture with your back straight and screen at eye level.",
                "Use artificial tears if you experience dry eyes.",
                "Consider using blue light filtering glasses or screen filters.",
                "Take regular breaks from screen time.",
                "Ensure proper lighting in your workspace to reduce eye strain.",
                "Adjust your screen brightness to match your surroundings.",
                "Get regular eye check-ups, especially if you spend long hours in front of screens."
            ]
            
            for rec in recommendations:
                pdf.multi_cell(0, 8, f"• {rec}")
            
            # Save the report
            report_path = f"{self.report_dir}/eye_care_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(report_path)
            
            return report_path
        
        except Exception as e:
            print(f"Error generating report: {e}")
            # Create a simple error report
            error_pdf = FPDF()
            error_pdf.add_page()
            error_pdf.set_font('Arial', 'B', 16)
            error_pdf.cell(0, 10, 'Eye Care Assistant - Report Error', 0, 1, 'C')
            error_pdf.set_font('Arial', '', 12)
            error_pdf.cell(0, 10, 'There was an error generating your report.', 0, 1)
            error_pdf.cell(0, 10, 'Please try again later.', 0, 1)
            
            error_path = f"{self.report_dir}/eye_care_error_report.pdf"
            error_pdf.output(error_path)
            
            return error_path
