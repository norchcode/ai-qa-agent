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
    
    def __init__(self, config: Union[Dict[str, Any], str, None] = None):
        """
        Initialize the Report Generator.
        
        Args:
            config: Configuration dictionary or path to templates directory.
                   If a dictionary, it should contain a 'templates_dir' key.
                   If a string, it is treated as the templates directory path.
                   If None, a default path is used.
        """
        # Handle different types of config parameter
        if isinstance(config, dict):
            self.config = config
            templates_dir = config.get('templates_dir')
        elif isinstance(config, str):
            self.config = {'templates_dir': config}
            templates_dir = config
        else:
            self.config = {}
            templates_dir = None
            
        # Set templates directory
        self.templates_dir = templates_dir or os.path.join(os.path.dirname(__file__), 'report_templates')
        
        # Create templates directory if it doesn't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Initialize Jinja2 environment for HTML templates
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        logger.info(f"Initialized Report Generator with templates directory: {self.templates_dir}")
    
    def generate(self, results: Dict[str, Any], format: str = "pdf") -> str:
        """
        Generate a report from test results.
        
        Args:
            results: Test results dictionary.
            format: Report format (pdf, html, json).
            
        Returns:
            Path to the generated report.
        """
        logger.info(f"Generating {format} report")
        
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Generate report based on format
        if format.lower() == "pdf":
            report_path = os.path.join(reports_dir, f"report_{timestamp}.pdf")
            self.generate_pdf_report(results, report_path)
        elif format.lower() == "html":
            report_path = os.path.join(reports_dir, f"report_{timestamp}.html")
            self.generate_html_report(results, report_path)
        elif format.lower() == "json":
            report_path = os.path.join(reports_dir, f"report_{timestamp}.json")
            with open(report_path, "w") as f:
                json.dump(results, f, indent=2)
        else:
            logger.error(f"Unsupported report format: {format}")
            return ""
        
        logger.info(f"Report generated: {report_path}")
        return report_path
    
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
    
    def generate_html_report(self, data: Dict[str, Any], output_path: str,
                            template: str = 'detailed') -> bool:
        """
        Generate an HTML report.
        
        Args:
            data: Dictionary containing report data.
            output_path: Path to save the HTML report.
            template: Template to use for the report ('detailed', 'summary', 'executive').
            
        Returns:
            True if the report was generated successfully, False otherwise.
        """
        logger.info(f"Generating HTML report using template '{template}' to {output_path}")
        
        try:
            # Create a default template if it doesn't exist
            template_file = f"{template}.html"
            template_path = os.path.join(self.templates_dir, template_file)
            
            if not os.path.exists(template_path):
                self._create_default_html_template(template_path, template)
            
            # Render the template
            template = self.jinja_env.get_template(template_file)
            html = template.render(data=data)
            
            # Write the HTML to the output file
            with open(output_path, 'w') as f:
                f.write(html)
            
            logger.info(f"HTML report generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return False
    
    def _create_default_html_template(self, template_path: str, template_type: str) -> None:
        """
        Create a default HTML template if it doesn't exist.
        
        Args:
            template_path: Path to save the template.
            template_type: Type of template ('detailed', 'summary', 'executive').
        """
        logger.info(f"Creating default HTML template: {template_path}")
        
        # Create a basic HTML template
        html = """<!DOCTYPE html>
<html>
<head>
    <title>{{ data.title|default('Test Report') }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }
        h2 {
            color: #444;
            margin-top: 20px;
        }
        h3 {
            color: #555;
        }
        .metadata {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .summary {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .summary-box {
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            width: 30%;
            text-align: center;
        }
        .pass {
            color: green;
            font-weight: bold;
        }
        .fail {
            color: red;
            font-weight: bold;
        }
        .skip {
            color: orange;
            font-weight: bold;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .test-details {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
        }
        .error {
            background-color: #ffebee;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        .steps {
            margin-left: 20px;
        }
    </style>
</head>
<body>
    <h1>{{ data.title|default('Test Report') }}</h1>
    
    <div class="metadata">
        <p><strong>Report Date:</strong> {{ data.date|default(now) }}</p>
        {% if data.project %}
        <p><strong>Project:</strong> {{ data.project }}</p>
        {% endif %}
        {% if data.author %}
        <p><strong>Author:</strong> {{ data.author }}</p>
        {% endif %}
    </div>
    
    {% if data.summary %}
    <h2>Executive Summary</h2>
    <p>{{ data.summary }}</p>
    {% endif %}
    
    {% if data.environment %}
    <h2>Test Environment</h2>
    <table>
        <tr>
            <th>Property</th>
            <th>Value</th>
        </tr>
        {% for key, value in data.environment.items() %}
        <tr>
            <td>{{ key }}</td>
            <td>{{ value }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
    
    {% if data.results_summary %}
    <h2>Test Results Summary</h2>
    <div class="summary">
        <div class="summary-box">
            <h3>Total Tests</h3>
            <p>{{ data.results_summary.total_tests|default(0) }}</p>
        </div>
        <div class="summary-box">
            <h3>Passed</h3>
            <p class="pass">{{ data.results_summary.passed|default(0) }}</p>
        </div>
        <div class="summary-box">
            <h3>Failed</h3>
            <p class="fail">{{ data.results_summary.failed|default(0) }}</p>
        </div>
    </div>
    {% endif %}
    
    {% if data.test_results %}
    <h2>Detailed Test Results</h2>
    {% for test in data.test_results %}
    <div class="test-details">
        <h3>{{ test.id|default('Test ' ~ loop.index) }}: {{ test.name|default('Unnamed Test') }}</h3>
        
        {% if test.result == 'PASS' %}
        <p><strong>Result:</strong> <span class="pass">{{ test.result }}</span></p>
        {% elif test.result == 'FAIL' %}
        <p><strong>Result:</strong> <span class="fail">{{ test.result }}</span></p>
        {% elif test.result == 'SKIP' %}
        <p><strong>Result:</strong> <span class="skip">{{ test.result }}</span></p>
        {% else %}
        <p><strong>Result:</strong> {{ test.result|default('UNKNOWN') }}</p>
        {% endif %}
        
        {% if test.duration %}
        <p><strong>Duration:</strong> {{ test.duration }} seconds</p>
        {% endif %}
        
        {% if test.description %}
        <p><strong>Description:</strong> {{ test.description }}</p>
        {% endif %}
        
        {% if test.steps %}
        <p><strong>Steps:</strong></p>
        <ol class="steps">
            {% for step in test.steps %}
            <li>{{ step }}</li>
            {% endfor %}
        </ol>
        {% endif %}
        
        {% if test.error %}
        <div class="error">
            <p><strong>Error:</strong></p>
            <pre>{{ test.error }}</pre>
        </div>
        {% endif %}
        
        {% if test.screenshot %}
        <p><strong>Screenshot:</strong></p>
        <img src="{{ test.screenshot }}" alt="Test Screenshot" style="max-width: 100%;">
        {% endif %}
    </div>
    {% endfor %}
    {% endif %}
    
    {% if data.issues %}
    <h2>Issues and Recommendations</h2>
    {% for issue in data.issues %}
    <div class="test-details">
        <h3>{{ issue.title|default('Issue ' ~ loop.index) }}</h3>
        
        {% if issue.severity == 'high' %}
        <p><strong>Severity:</strong> <span class="fail">{{ issue.severity }}</span></p>
        {% elif issue.severity == 'medium' %}
        <p><strong>Severity:</strong> <span class="skip">{{ issue.severity }}</span></p>
        {% elif issue.severity == 'low' %}
        <p><strong>Severity:</strong> <span class="pass">{{ issue.severity }}</span></p>
        {% else %}
        <p><strong>Severity:</strong> {{ issue.severity|default('Unknown') }}</p>
        {% endif %}
        
        {% if issue.description %}
        <p><strong>Description:</strong> {{ issue.description }}</p>
        {% endif %}
        
        {% if issue.recommendation %}
        <p><strong>Recommendation:</strong> {{ issue.recommendation }}</p>
        {% endif %}
    </div>
    {% endfor %}
    {% endif %}
    
    {% if data.conclusion %}
    <h2>Conclusion</h2>
    <p>{{ data.conclusion }}</p>
    {% endif %}
    
    <footer>
        <p>Generated on {{ data.date|default(now) }}</p>
    </footer>
</body>
</html>
"""
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        # Write the template to the file
        with open(template_path, 'w') as f:
            f.write(html)
        
        logger.info(f"Created default HTML template: {template_path}")
    
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
        # Implementation similar to _create_detailed_pdf_content but with less detail
        content = []
        
        # Title
        title = data.get('title', 'Test Summary Report')
        content.append(Paragraph(title, styles['Heading1']))
        content.append(Spacer(1, 0.25 * inch))
        
        # Basic metadata and summary
        report_date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        content.append(Paragraph(f"Report Date: {report_date}", styles['Normal']))
        content.append(Spacer(1, 0.25 * inch))
        
        if 'summary' in data:
            content.append(Paragraph("Executive Summary", styles['Heading2']))
            content.append(Paragraph(data['summary'], styles['Normal']))
            content.append(Spacer(1, 0.25 * inch))
        
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
        # Implementation similar to _create_summary_pdf_content but with executive focus
        content = []
        
        # Title
        title = data.get('title', 'Executive Test Report')
        content.append(Paragraph(title, styles['Heading1']))
        content.append(Spacer(1, 0.25 * inch))
        
        # Basic metadata and summary
        report_date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        content.append(Paragraph(f"Report Date: {report_date}", styles['Normal']))
        content.append(Spacer(1, 0.25 * inch))
        
        if 'summary' in data:
            content.append(Paragraph("Executive Summary", styles['Heading2']))
            content.append(Paragraph(data['summary'], styles['Normal']))
            content.append(Spacer(1, 0.25 * inch))
        
        return content
