"""
Report Generator module for AI QA Agent.
This module provides functionality for generating various types of test reports.
"""
import os
import logging
import json
import datetime
from typing import Dict, List, Any, Optional, Union
import base64
from pathlib import Path
import re
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from io import BytesIO

# PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.units import inch

# HTML generation
import jinja2

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Class for generating various types of test reports."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the Report Generator.
        
        Args:
            templates_dir: Optional directory containing report templates.
        """
        self.templates_dir = templates_dir or os.path.join(os.path.dirname(__file__), 'report_templates')
        
        # Create templates directory if it doesn't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Initialize Jinja2 environment for HTML templates
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        logger.info(f"Initialized Report Generator with templates directory: {self.templates_dir}")
    
    def generate_pdf_report(self, data: Dict[str, Any], output_path: str, 
                           template: str = 'detailed') -> bool:
        """
        Generate a PDF report.
        
        Args:
            data: Dictionary containing report data.
            output_path: Path to save the PDF report.
            template: Template to use for the report ('detailed', 'summary', 'executive').
            
        Returns:
            True if the report was generated successfully, False otherwise.
        """
        logger.info(f"Generating PDF report using template '{template}' to {output_path}")
        
        try:
            # Create the PDF document
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Create custom styles
            styles.add(ParagraphStyle(
                name='Heading1',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=12
            ))
            styles.add(ParagraphStyle(
                name='Heading2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=8
            ))
            styles.add(ParagraphStyle(
                name='Heading3',
                parent=styles['Heading3'],
                fontSize=12,
                spaceAfter=6
            ))
            styles.add(ParagraphStyle(
                name='Normal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            ))
            
            # Create the content based on the template
            content = []
            
            if template == 'detailed':
                content = self._create_detailed_pdf_content(data, styles)
            elif template == 'summary':
                content = self._create_summary_pdf_content(data, styles)
            elif template == 'executive':
                content = self._create_executive_pdf_content(data, styles)
            else:
                logger.warning(f"Unknown template: {template}, using 'detailed' instead")
                content = self._create_detailed_pdf_content(data, styles)
            
            # Build the PDF
            doc.build(content)
            
            logger.info(f"PDF report generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return False
    
    def _create_detailed_pdf_content(self, data: Dict[str, Any], styles: Dict[str, Any]) -> List[Any]:
        """
        Create content for a detailed PDF report.
        
        Args:
            data: Dictionary containing report data.
            styles: Dictionary of paragraph styles.
            
        Returns:
            List of flowables for the PDF document.
        """
        content = []
        
        # Title
        title = data.get('title', 'Test Report')
        content.append(Paragraph(title, styles['Heading1']))
        content.append(Spacer(1, 0.25 * inch))
        
        # Report metadata
        report_date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        content.append(Paragraph(f"Report Date: {report_date}", styles['Normal']))
        
        if 'project' in data:
            content.append(Paragraph(f"Project: {data['project']}", styles['Normal']))
        
        if 'author' in data:
            content.append(Paragraph(f"Author: {data['author']}", styles['Normal']))
        
        content.append(Spacer(1, 0.25 * inch))
        content.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        content.append(Spacer(1, 0.25 * inch))
        
        # Executive Summary
        if 'summary' in data:
            content.append(Paragraph("Executive Summary", styles['Heading2']))
            content.append(Paragraph(data['summary'], styles['Normal']))
            content.append(Spacer(1, 0.25 * inch))
        
        # Test Environment
        if 'environment' in data:
            content.append(Paragraph("Test Environment", styles['Heading2']))
            for key, value in data['environment'].items():
                content.append(Paragraph(f"{key}: {value}", styles['Normal']))
            content.append(Spacer(1, 0.25 * inch))
        
        # Test Results Summary
        if 'results_summary' in data:
            content.append(Paragraph("Test Results Summary", styles['Heading2']))
            
            summary = data['results_summary']
            summary_data = [
                ["Metric", "Value"],
                ["Total Tests", summary.get('total_tests', 0)],
                ["Passed", summary.get('passed', 0)],
                ["Failed", summary.get('failed', 0)],
                ["Skipped", summary.get('skipped', 0)],
                ["Duration", summary.get('duration', '0s')]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(summary_table)
            content.append(Spacer(1, 0.25 * inch))
            
            # Add a chart if data is available
            if all(k in summary for k in ['passed', 'failed', 'skipped']):
                # Create a pie chart
                plt.figure(figsize=(6, 4))
                labels = ['Passed', 'Failed', 'Skipped']
                sizes = [summary.get('passed', 0), summary.get('failed', 0), summary.get('skipped', 0)]
                colors_pie = ['#4CAF50', '#F44336', '#FFC107']
                plt.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
                plt.title('Test Results')
                
                # Save the chart to a BytesIO object
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                
                # Add the chart to the PDF
                img = Image(buffer)
                img.drawHeight = 3 * inch
                img.drawWidth = 4 * inch
                content.append(img)
                
                plt.close()
            
            content.append(Spacer(1, 0.25 * inch))
        
        # Detailed Test Results
        if 'test_results' in data:
            content.append(Paragraph("Detailed Test Results", styles['Heading2']))
            
            for i, test in enumerate(data['test_results']):
                # Add a page break every 5 tests to avoid crowding
                if i > 0 and i % 5 == 0:
                    content.append(PageBreak())
                
                test_id = test.get('id', f"Test {i+1}")
                test_name = test.get('name', 'Unnamed Test')
                test_result = test.get('result', 'UNKNOWN')
                
                # Set color based on result
                result_color = colors.black
                if test_result == 'PASS':
                    result_color = colors.green
                elif test_result == 'FAIL':
                    result_color = colors.red
                elif test_result == 'SKIP':
                    result_color = colors.orange
                
                # Create a custom style for the test result
                result_style = ParagraphStyle(
                    name=f'Result{i}',
                    parent=styles['Normal'],
                    textColor=result_color,
                    fontName='Helvetica-Bold'
                )
                
                content.append(Paragraph(f"{test_id}: {test_name}", styles['Heading3']))
                content.append(Paragraph(f"Result: {test_result}", result_style))
                
                if 'duration' in test:
                    content.append(Paragraph(f"Duration: {test['duration']} seconds", styles['Normal']))
                
                if 'description' in test:
                    content.append(Paragraph(f"Description: {test['description']}", styles['Normal']))
                
                if 'steps' in test:
                    content.append(Paragraph("Steps:", styles['Normal']))
                    for j, step in enumerate(test['steps']):
                        content.append(Paragraph(f"{j+1}. {step}", styles['Normal']))
                
                if 'error' in test:
                    content.append(Paragraph("Error:", styles['Normal']))
                    content.append(Paragraph(test['error'], styles['Normal']))
                
                if 'screenshot' in test:
                    try:
                        img = Image(test['screenshot'])
                        img.drawHeight = 3 * inch
                        img.drawWidth = 4 * inch
                        content.append(img)
                    except Exception as e:
                        logger.error(f"Error adding screenshot to PDF: {e}")
                
                content.append(Spacer(1, 0.25 * inch))
        
        # Issues and Recommendations
        if 'issues' in data:
            content.append(Paragraph("Issues and Recommendations", styles['Heading2']))
            
            for i, issue in enumerate(data['issues']):
                issue_title = issue.get('title', f"Issue {i+1}")
                issue_severity = issue.get('severity', 'Unknown')
                issue_description = issue.get('description', '')
                issue_recommendation = issue.get('recommendation', '')
                
                # Set color based on severity
                severity_color = colors.black
                if issue_severity.lower() == 'high':
                    severity_color = colors.red
                elif issue_severity.lower() == 'medium':
                    severity_color = colors.orange
                elif issue_severity.lower() == 'low':
                    severity_color = colors.green
                
                # Create a custom style for the severity
                severity_style = ParagraphStyle(
                    name=f'Severity{i}',
                    parent=styles['Normal'],
                    textColor=severity_color,
                    fontName='Helvetica-Bold'
                )
                
                content.append(Paragraph(issue_title, styles['Heading3']))
                content.append(Paragraph(f"Severity: {issue_severity}", severity_style))
                content.append(Paragraph(f"Description: {issue_description}", styles['Normal']))
                content.append(Paragraph(f"Recommendation: {issue_recommendation}", styles['Normal']))
                content.append(Spacer(1, 0.25 * inch))
        
        # Conclusion
        if 'conclusion' in data:
            content.append(Paragraph("Conclusion", styles['Heading2']))
            content.append(Paragraph(data['conclusion'], styles['Normal']))
        
        return content
    
    def _create_summary_pdf_content(self, data: Dict[str, Any], styles: Dict[str, Any]) -> List[Any]:
        """
        Create content for a summary PDF report.
        
        Args:
            data: Dictionary containing report data.
            styles: Dictionary of paragraph styles.
            
        Returns:
            List of flowables for the PDF document.
        """
        content = []
        
        # Title
        title = data.get('title', 'Test Summary Report')
        content.append(Paragraph(title, styles['Heading1']))
        content.append(Spacer(1, 0.25 * inch))
        
        # Report metadata
        report_date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        content.append(Paragraph(f"Report Date: {report_date}", styles['Normal']))
        
        if 'project' in data:
            content.append(Paragraph(f"Project: {data['project']}", styles['Normal']))
        
        content.append(Spacer(1, 0.25 * inch))
        content.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        content.append(Spacer(1, 0.25 * inch))
        
        # Executive Summary
        if 'summary' in data:
            content.append(Paragraph("Executive Summary", styles['Heading2']))
            content.append(Paragraph(data['summary'], styles['Normal']))
            content.append(Spacer(1, 0.25 * inch))
        
        # Test Results Summary
        if 'results_summary' in data:
            content.append(Paragraph("Test Results Summary", styles['Heading2']))
            
            summary = data['results_summary']
            summary_data = [
                ["Metric", "Value"],
                ["Total Tests", summary.get('total_tests', 0)],
                ["Passed", summary.get('passed', 0)],
                ["Failed", summary.get('failed', 0)],
                ["Skipped", summary.get('skipped', 0)],
                ["Duration", summary.get('duration', '0s')]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(summary_table)
            content.append(Spacer(1, 0.25 * inch))
            
            # Add a chart if data is available
            if all(k in summary for k in ['passed', 'failed', 'skipped']):
                # Create a pie chart
                plt.figure(figsize=(6, 4))
                labels = ['Passed', 'Failed', 'Skipped']
                sizes = [summary.get('passed', 0), summary.get('failed', 0), summary.get('skipped', 0)]
                colors_pie = ['#4CAF50', '#F44336', '#FFC107']
                plt.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
                plt.title('Test Results')
                
                # Save the chart to a BytesIO object
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                
                # Add the chart to the PDF
                img = Image(buffer)
                img.drawHeight = 3 * inch
                img.drawWidth = 4 * inch
                content.append(img)
                
                plt.close()
            
            content.append(Spacer(1, 0.25 * inch))
        
        # Failed Tests Summary
        if 'test_results' in data:
            failed_tests = [test for test in data['test_results'] if test.get('result', '') == 'FAIL']
            
            if failed_tests:
                content.append(Paragraph("Failed Tests Summary", styles['Heading2']))
                
                for i, test in enumerate(failed_tests):
                    test_id = test.get('id', f"Test {i+1}")
                    test_name = test.get('name', 'Unnamed Test')
                    
                    content.append(Paragraph(f"{test_id}: {test_name}", styles['Heading3']))
                    
                    if 'error' in test:
                        content.append(Paragraph("Error:", styles['Normal']))
                        content.append(Paragraph(test['error'], styles['Normal']))
                    
                    content.append(Spacer(1, 0.25 * inch))
        
        # Key Issues
        if 'issues' in data:
            high_priority_issues = [issue for issue in data['issues'] 
                                   if issue.get('severity', '').lower() == 'high']
            
            if high_priority_issues:
                content.append(Paragraph("Key Issues", styles['Heading2']))
                
                for i, issue in enumerate(high_priority_issues):
                    issue_title = issue.get('title', f"Issue {i+1}")
                    issue_description = issue.get('description', '')
                    
                    content.append(Paragraph(issue_title, styles['Heading3']))
                    content.append(Paragraph(issue_description, styles['Normal']))
                    content.append(Spacer(1, 0.25 * inch))
        
        # Conclusion
        if 'conclusion' in data:
            content.append(Paragraph("Conclusion", styles['Heading2']))
            content.append(Paragraph(data['conclusion'], styles['Normal']))
        
        return content
    
    def _create_executive_pdf_content(self, data: Dict[str, Any], styles: Dict[str, Any]) -> List[Any]:
        """
        Create content for an executive PDF report.
        
        Args:
            data: Dictionary containing report data.
            styles: Dictionary of paragraph styles.
            
        Returns:
            List of flowables for the PDF document.
        """
        content = []
        
        # Title
        title = data.get('title', 'Executive Test Report')
        content.append(Paragraph(title, styles['Heading1']))
        content.append(Spacer(1, 0.25 * inch))
        
        # Report metadata
        report_date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        content.append(Paragraph(f"Report Date: {report_date}", styles['Normal']))
        
        if 'project' in data:
            content.append(Paragraph(f"Project: {data['project']}", styles['Normal']))
        
        content.append(Spacer(1, 0.25 * inch))
        content.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        content.append(Spacer(1, 0.25 * inch))
        
        # Executive Summary
        if 'summary' in data:
            content.append(Paragraph("Executive Summary", styles['Heading2']))
            content.append(Paragraph(data['summary'], styles['Normal']))
            content.append(Spacer(1, 0.25 * inch))
        
        # Test Results Summary
        if 'results_summary' in data:
            content.append(Paragraph("Test Results Overview", styles['Heading2']))
            
            summary = data['results_summary']
            
            # Add a chart if data is available
            if all(k in summary for k in ['passed', 'failed', 'skipped']):
                # Create a pie chart
                plt.figure(figsize=(6, 4))
                labels = ['Passed', 'Failed', 'Skipped']
                sizes = [summary.get('passed', 0), summary.get('failed', 0), summary.get('skipped', 0)]
                colors_pie = ['#4CAF50', '#F44336', '#FFC107']
                plt.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
                plt.title('Test Results')
                
                # Save the chart to a BytesIO object
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                
                # Add the chart to the PDF
                img = Image(buffer)
                img.drawHeight = 3 * inch
                img.drawWidth = 4 * inch
                content.append(img)
                
                plt.close()
            
            content.append(Spacer(1, 0.25 * inch))
            
            # Add a simple text summary
            total = summary.get('total_tests', 0)
            passed = summary.get('passed', 0)
            failed = summary.get('failed', 0)
            skipped = summary.get('skipped', 0)
            
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            content.append(Paragraph(f"Total Tests: {total}", styles['Normal']))
            content.append(Paragraph(f"Pass Rate: {pass_rate:.1f}%", styles['Normal']))
            content.append(Paragraph(f"Failed Tests: {failed}", styles['Normal']))
            
            content.append(Spacer(1, 0.25 * inch))
        
        # Key Issues
        if 'issues' in data:
            content.append(Paragraph("Key Issues and Risks", styles['Heading2']))
            
            # Group issues by severity
            high_issues = [issue for issue in data['issues'] 
                          if issue.get('severity', '').lower() == 'high']
            medium_issues = [issue for issue in data['issues'] 
                            if issue.get('severity', '').lower() == 'medium']
            
            if high_issues:
                content.append(Paragraph("High Priority Issues:", styles['Heading3']))
                for issue in high_issues:
                    content.append(Paragraph(f"• {issue.get('title', 'Unnamed Issue')}", styles['Normal']))
                content.append(Spacer(1, 0.15 * inch))
            
            if medium_issues:
                content.append(Paragraph("Medium Priority Issues:", styles['Heading3']))
                for issue in medium_issues:
                    content.append(Paragraph(f"• {issue.get('title', 'Unnamed Issue')}", styles['Normal']))
                content.append(Spacer(1, 0.15 * inch))
            
            if not high_issues and not medium_issues:
                content.append(Paragraph("No significant issues identified.", styles['Normal']))
            
            content.append(Spacer(1, 0.25 * inch))
        
        # Recommendations
        if 'recommendations' in data:
            content.append(Paragraph("Recommendations", styles['Heading2']))
            
            for i, recommendation in enumerate(data['recommendations']):
                content.append(Paragraph(f"{i+1}. {recommendation}", styles['Normal']))
            
            content.append(Spacer(1, 0.25 * inch))
        elif 'issues' in data:
            # Extract recommendations from issues if available
            recommendations = []
            for issue in data['issues']:
                if 'recommendation' in issue and issue['recommendation']:
                    recommendations.append(issue['recommendation'])
            
            if recommendations:
                content.append(Paragraph("Recommendations", styles['Heading2']))
                
                for i, recommendation in enumerate(recommendations):
                    content.append(Paragraph(f"{i+1}. {recommendation}", styles['Normal']))
                
                content.append(Spacer(1, 0.25 * inch))
        
        # Next Steps
        if 'next_steps' in data:
            content.append(Paragraph("Next Steps", styles['Heading2']))
            
            for i, step in enumerate(data['next_steps']):
                content.append(Paragraph(f"{i+1}. {step}", styles['Normal']))
            
            content.append(Spacer(1, 0.25 * inch))
        
        # Conclusion
        if 'conclusion' in data:
            content.append(Paragraph("Conclusion", styles['Heading2']))
            content.append(Paragraph(data['conclusion'], styles['Normal']))
        
        return content
    
    def generate_html_report(self, data: Dict[str, Any], output_path: str, 
                            template_name: str = 'detailed.html') -> bool:
        """
        Generate an HTML report.
        
        Args:
            data: Dictionary containing report data.
            output_path: Path to save the HTML report.
            template_name: Name of the HTML template to use.
            
        Returns:
            True if the report was generated successfully, False otherwise.
        """
        logger.info(f"Generating HTML report using template '{template_name}' to {output_path}")
        
        try:
            # Check if the template exists
            template_path = os.path.join(self.templates_dir, template_name)
            if not os.path.exists(template_path):
                # Create the template if it doesn't exist
                self._create_html_template(template_name)
            
            # Load the template
            template = self.jinja_env.get_template(template_name)
            
            # Add additional data for the template
            report_data = data.copy()
            report_data['generation_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Generate charts if needed
            if 'results_summary' in report_data:
                summary = report_data['results_summary']
                if all(k in summary for k in ['passed', 'failed', 'skipped']):
                    # Create a pie chart
                    plt.figure(figsize=(6, 4))
                    labels = ['Passed', 'Failed', 'Skipped']
                    sizes = [summary.get('passed', 0), summary.get('failed', 0), summary.get('skipped', 0)]
                    colors_pie = ['#4CAF50', '#F44336', '#FFC107']
                    plt.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
                    plt.axis('equal')
                    plt.title('Test Results')
                    
                    # Save the chart to a BytesIO object
                    buffer = BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    
                    # Convert to base64 for embedding in HTML
                    chart_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    report_data['results_chart'] = f"data:image/png;base64,{chart_base64}"
                    
                    plt.close()
            
            # Render the template
            html_content = template.render(**report_data)
            
            # Write the HTML file
            with open(output_path, 'w') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return False
    
    def _create_html_template(self, template_name: str) -> bool:
        """
        Create an HTML template if it doesn't exist.
        
        Args:
            template_name: Name of the HTML template to create.
            
        Returns:
            True if the template was created successfully, False otherwise.
        """
        logger.info(f"Creating HTML template: {template_name}")
        
        try:
            template_path = os.path.join(self.templates_dir, template_name)
            
            if template_name == 'detailed.html':
                template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2c3e50;
            margin-top: 30px;
        }
        h3 {
            color: #2c3e50;
        }
        .metadata {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .summary {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .results-summary {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .summary-table {
            width: 40%;
        }
        .chart {
            width: 55%;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .test-case {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 5px solid #3498db;
        }
        .test-case.pass {
            border-left-color: #2ecc71;
        }
        .test-case.fail {
            border-left-color: #e74c3c;
        }
        .test-case.skip {
            border-left-color: #f39c12;
        }
        .result {
            font-weight: bold;
        }
        .result.pass {
            color: #2ecc71;
        }
        .result.fail {
            color: #e74c3c;
        }
        .result.skip {
            color: #f39c12;
        }
        .steps {
            margin-left: 20px;
        }
        .error {
            background-color: #ffebee;
            padding: 10px;
            border-radius: 5px;
            color: #c62828;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .screenshot {
            max-width: 100%;
            height: auto;
            margin-top: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .issue {
            background-color: #fff8e1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 5px solid #f39c12;
        }
        .issue.high {
            border-left-color: #e74c3c;
        }
        .issue.medium {
            border-left-color: #f39c12;
        }
        .issue.low {
            border-left-color: #2ecc71;
        }
        .severity {
            font-weight: bold;
        }
        .severity.high {
            color: #e74c3c;
        }
        .severity.medium {
            color: #f39c12;
        }
        .severity.low {
            color: #2ecc71;
        }
        .conclusion {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin-top: 30px;
        }
        footer {
            margin-top: 50px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        /* Interactive elements */
        .collapsible {
            background-color: #f1f1f1;
            color: #444;
            cursor: pointer;
            padding: 18px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 15px;
            transition: 0.4s;
            border-radius: 5px;
            margin-bottom: 5px;
        }
        .active, .collapsible:hover {
            background-color: #ccc;
        }
        .content {
            padding: 0 18px;
            display: none;
            overflow: hidden;
            background-color: #f9f9f9;
            border-radius: 0 0 5px 5px;
        }
        
        /* Tabs */
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 5px 5px 0 0;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            font-size: 17px;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #3498db;
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 6px 12px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 5px 5px;
            animation: fadeEffect 1s;
        }
        @keyframes fadeEffect {
            from {opacity: 0;}
            to {opacity: 1;}
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    
    <div class="metadata">
        <p><strong>Report Date:</strong> {{ generation_date }}</p>
        {% if project %}<p><strong>Project:</strong> {{ project }}</p>{% endif %}
        {% if author %}<p><strong>Author:</strong> {{ author }}</p>{% endif %}
    </div>
    
    {% if summary %}
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>{{ summary }}</p>
    </div>
    {% endif %}
    
    {% if environment %}
    <h2>Test Environment</h2>
    <table>
        <tr>
            <th>Property</th>
            <th>Value</th>
        </tr>
        {% for key, value in environment.items() %}
        <tr>
            <td>{{ key }}</td>
            <td>{{ value }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
    
    {% if results_summary %}
    <h2>Test Results Summary</h2>
    <div class="results-summary">
        <div class="summary-table">
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Tests</td>
                    <td>{{ results_summary.total_tests }}</td>
                </tr>
                <tr>
                    <td>Passed</td>
                    <td>{{ results_summary.passed }}</td>
                </tr>
                <tr>
                    <td>Failed</td>
                    <td>{{ results_summary.failed }}</td>
                </tr>
                <tr>
                    <td>Skipped</td>
                    <td>{{ results_summary.skipped }}</td>
                </tr>
                <tr>
                    <td>Duration</td>
                    <td>{{ results_summary.duration }}</td>
                </tr>
            </table>
        </div>
        
        {% if results_chart %}
        <div class="chart">
            <img src="{{ results_chart }}" alt="Test Results Chart">
        </div>
        {% endif %}
    </div>
    {% endif %}
    
    {% if test_results %}
    <h2>Detailed Test Results</h2>
    
    <div class="tab">
        <button class="tablinks active" onclick="openTab(event, 'AllTests')">All Tests</button>
        <button class="tablinks" onclick="openTab(event, 'PassedTests')">Passed</button>
        <button class="tablinks" onclick="openTab(event, 'FailedTests')">Failed</button>
        <button class="tablinks" onclick="openTab(event, 'SkippedTests')">Skipped</button>
    </div>
    
    <div id="AllTests" class="tabcontent" style="display: block;">
        {% for test in test_results %}
        <button class="collapsible">{{ test.id }}: {{ test.name }} - <span class="result {{ test.result|lower }}">{{ test.result }}</span></button>
        <div class="content">
            <div class="test-case {{ test.result|lower }}">
                {% if test.duration %}<p><strong>Duration:</strong> {{ test.duration }} seconds</p>{% endif %}
                {% if test.description %}<p><strong>Description:</strong> {{ test.description }}</p>{% endif %}
                
                {% if test.steps %}
                <p><strong>Steps:</strong></p>
                <ol class="steps">
                    {% for step in test.steps %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ol>
                {% endif %}
                
                {% if test.error %}
                <p><strong>Error:</strong></p>
                <div class="error">{{ test.error }}</div>
                {% endif %}
                
                {% if test.screenshot %}
                <p><strong>Screenshot:</strong></p>
                <img class="screenshot" src="{{ test.screenshot }}" alt="Test Screenshot">
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div id="PassedTests" class="tabcontent">
        {% for test in test_results if test.result == 'PASS' %}
        <button class="collapsible">{{ test.id }}: {{ test.name }} - <span class="result pass">{{ test.result }}</span></button>
        <div class="content">
            <div class="test-case pass">
                {% if test.duration %}<p><strong>Duration:</strong> {{ test.duration }} seconds</p>{% endif %}
                {% if test.description %}<p><strong>Description:</strong> {{ test.description }}</p>{% endif %}
                
                {% if test.steps %}
                <p><strong>Steps:</strong></p>
                <ol class="steps">
                    {% for step in test.steps %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ol>
                {% endif %}
                
                {% if test.screenshot %}
                <p><strong>Screenshot:</strong></p>
                <img class="screenshot" src="{{ test.screenshot }}" alt="Test Screenshot">
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div id="FailedTests" class="tabcontent">
        {% for test in test_results if test.result == 'FAIL' %}
        <button class="collapsible">{{ test.id }}: {{ test.name }} - <span class="result fail">{{ test.result }}</span></button>
        <div class="content">
            <div class="test-case fail">
                {% if test.duration %}<p><strong>Duration:</strong> {{ test.duration }} seconds</p>{% endif %}
                {% if test.description %}<p><strong>Description:</strong> {{ test.description }}</p>{% endif %}
                
                {% if test.steps %}
                <p><strong>Steps:</strong></p>
                <ol class="steps">
                    {% for step in test.steps %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ol>
                {% endif %}
                
                {% if test.error %}
                <p><strong>Error:</strong></p>
                <div class="error">{{ test.error }}</div>
                {% endif %}
                
                {% if test.screenshot %}
                <p><strong>Screenshot:</strong></p>
                <img class="screenshot" src="{{ test.screenshot }}" alt="Test Screenshot">
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div id="SkippedTests" class="tabcontent">
        {% for test in test_results if test.result == 'SKIP' %}
        <button class="collapsible">{{ test.id }}: {{ test.name }} - <span class="result skip">{{ test.result }}</span></button>
        <div class="content">
            <div class="test-case skip">
                {% if test.duration %}<p><strong>Duration:</strong> {{ test.duration }} seconds</p>{% endif %}
                {% if test.description %}<p><strong>Description:</strong> {{ test.description }}</p>{% endif %}
                
                {% if test.steps %}
                <p><strong>Steps:</strong></p>
                <ol class="steps">
                    {% for step in test.steps %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ol>
                {% endif %}
                
                {% if test.screenshot %}
                <p><strong>Screenshot:</strong></p>
                <img class="screenshot" src="{{ test.screenshot }}" alt="Test Screenshot">
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if issues %}
    <h2>Issues and Recommendations</h2>
    {% for issue in issues %}
    <div class="issue {{ issue.severity|lower }}">
        <h3>{{ issue.title }}</h3>
        <p><strong>Severity:</strong> <span class="severity {{ issue.severity|lower }}">{{ issue.severity }}</span></p>
        <p><strong>Description:</strong> {{ issue.description }}</p>
        <p><strong>Recommendation:</strong> {{ issue.recommendation }}</p>
    </div>
    {% endfor %}
    {% endif %}
    
    {% if conclusion %}
    <div class="conclusion">
        <h2>Conclusion</h2>
        <p>{{ conclusion }}</p>
    </div>
    {% endif %}
    
    <footer>
        <p>Generated on {{ generation_date }} by AI QA Agent</p>
    </footer>
    
    <script>
        // Collapsible sections
        var coll = document.getElementsByClassName("collapsible");
        for (var i = 0; i < coll.length; i++) {
            coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.display === "block") {
                    content.style.display = "none";
                } else {
                    content.style.display = "block";
                }
            });
        }
        
        // Tabs
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
    </script>
</body>
</html>"""
            elif template_name == 'executive.html':
                template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2c3e50;
            margin-top: 30px;
        }
        h3 {
            color: #2c3e50;
        }
        .metadata {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .summary {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .chart-container {
            text-align: center;
            margin: 20px 0;
        }
        .chart {
            max-width: 100%;
            height: auto;
        }
        .metrics {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            text-align: center;
        }
        .metric {
            padding: 20px;
            border-radius: 5px;
            background-color: #f8f9fa;
            width: 30%;
        }
        .metric h3 {
            margin-top: 0;
        }
        .metric .value {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        .issues {
            margin: 20px 0;
        }
        .issue {
            background-color: #fff8e1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 5px solid #f39c12;
        }
        .issue.high {
            border-left-color: #e74c3c;
        }
        .issue.medium {
            border-left-color: #f39c12;
        }
        .issue.low {
            border-left-color: #2ecc71;
        }
        .recommendations {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .next-steps {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .conclusion {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin-top: 30px;
        }
        footer {
            margin-top: 50px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    
    <div class="metadata">
        <p><strong>Report Date:</strong> {{ generation_date }}</p>
        {% if project %}<p><strong>Project:</strong> {{ project }}</p>{% endif %}
    </div>
    
    {% if summary %}
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>{{ summary }}</p>
    </div>
    {% endif %}
    
    {% if results_summary %}
    <h2>Test Results Overview</h2>
    
    {% if results_chart %}
    <div class="chart-container">
        <img class="chart" src="{{ results_chart }}" alt="Test Results Chart">
    </div>
    {% endif %}
    
    <div class="metrics">
        <div class="metric">
            <h3>Total Tests</h3>
            <div class="value">{{ results_summary.total_tests }}</div>
        </div>
        
        <div class="metric">
            <h3>Pass Rate</h3>
            <div class="value">
                {% if results_summary.total_tests > 0 %}
                {{ (results_summary.passed / results_summary.total_tests * 100) | round(1) }}%
                {% else %}
                0%
                {% endif %}
            </div>
        </div>
        
        <div class="metric">
            <h3>Failed Tests</h3>
            <div class="value">{{ results_summary.failed }}</div>
        </div>
    </div>
    {% endif %}
    
    {% if issues %}
    <h2>Key Issues and Risks</h2>
    
    <div class="issues">
        <h3>High Priority Issues</h3>
        {% set high_issues = issues | selectattr('severity', 'equalto', 'High') | list %}
        {% if high_issues %}
            {% for issue in high_issues %}
            <div class="issue high">
                <h4>{{ issue.title }}</h4>
                <p>{{ issue.description }}</p>
            </div>
            {% endfor %}
        {% else %}
            <p>No high priority issues identified.</p>
        {% endif %}
        
        <h3>Medium Priority Issues</h3>
        {% set medium_issues = issues | selectattr('severity', 'equalto', 'Medium') | list %}
        {% if medium_issues %}
            {% for issue in medium_issues %}
            <div class="issue medium">
                <h4>{{ issue.title }}</h4>
                <p>{{ issue.description }}</p>
            </div>
            {% endfor %}
        {% else %}
            <p>No medium priority issues identified.</p>
        {% endif %}
    </div>
    {% endif %}
    
    {% if recommendations %}
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ol>
            {% for recommendation in recommendations %}
            <li>{{ recommendation }}</li>
            {% endfor %}
        </ol>
    </div>
    {% elif issues %}
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ol>
            {% for issue in issues %}
            {% if issue.recommendation %}
            <li>{{ issue.recommendation }}</li>
            {% endif %}
            {% endfor %}
        </ol>
    </div>
    {% endif %}
    
    {% if next_steps %}
    <div class="next-steps">
        <h2>Next Steps</h2>
        <ol>
            {% for step in next_steps %}
            <li>{{ step }}</li>
            {% endfor %}
        </ol>
    </div>
    {% endif %}
    
    {% if conclusion %}
    <div class="conclusion">
        <h2>Conclusion</h2>
        <p>{{ conclusion }}</p>
    </div>
    {% endif %}
    
    <footer>
        <p>Generated on {{ generation_date }} by AI QA Agent</p>
    </footer>
</body>
</html>"""
            else:
                # Default simple template
                template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2c3e50;
            margin-top: 30px;
        }
        footer {
            margin-top: 50px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    
    <p><strong>Report Date:</strong> {{ generation_date }}</p>
    
    {% if summary %}
    <h2>Summary</h2>
    <p>{{ summary }}</p>
    {% endif %}
    
    {% if results_summary %}
    <h2>Results</h2>
    <p>Total Tests: {{ results_summary.total_tests }}</p>
    <p>Passed: {{ results_summary.passed }}</p>
    <p>Failed: {{ results_summary.failed }}</p>
    <p>Skipped: {{ results_summary.skipped }}</p>
    {% endif %}
    
    {% if conclusion %}
    <h2>Conclusion</h2>
    <p>{{ conclusion }}</p>
    {% endif %}
    
    <footer>
        <p>Generated on {{ generation_date }} by AI QA Agent</p>
    </footer>
</body>
</html>"""
            
            # Create the template file
            with open(template_path, 'w') as f:
                f.write(template_content)
            
            logger.info(f"Created HTML template: {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating HTML template: {e}")
            return False
    
    def generate_executive_summary(self, data: Dict[str, Any], output_path: str) -> bool:
        """
        Generate an executive summary report.
        
        Args:
            data: Dictionary containing report data.
            output_path: Path to save the executive summary report.
            
        Returns:
            True if the report was generated successfully, False otherwise.
        """
        logger.info(f"Generating executive summary report to {output_path}")
        
        try:
            # Determine the file extension
            file_ext = os.path.splitext(output_path)[1].lower()
            
            if file_ext == '.pdf':
                return self.generate_pdf_report(data, output_path, template='executive')
            elif file_ext == '.html':
                return self.generate_html_report(data, output_path, template_name='executive.html')
            else:
                logger.warning(f"Unsupported file extension: {file_ext}, using PDF")
                return self.generate_pdf_report(data, output_path, template='executive')
                
        except Exception as e:
            logger.error(f"Error generating executive summary report: {e}")
            return False
