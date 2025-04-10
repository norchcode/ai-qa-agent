"""
Report generator module for AI QA Agent.
This module provides functionality for generating test reports.
"""
import os
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates test reports for the AI QA Agent.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the report generator.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config or {}
        self.include_screenshots = self.config.get("include_screenshots", True)
        self.include_videos = self.config.get("include_videos", True)
        logger.info("Report generator initialized")
    
    def generate(self, test_results: Dict[str, Any], format: str = "html") -> str:
        """
        Generate a report from test results.
        
        Args:
            test_results: Test results.
            format: Report format (pdf, html, json).
            
        Returns:
            Path to the generated report.
        """
        logger.info(f"Generating {format} report")
        
        # Create a temporary directory for the report
        report_dir = tempfile.mkdtemp()
        
        # Generate the report based on the format
        if format.lower() == "pdf":
            return self._generate_pdf_report(test_results, report_dir)
        elif format.lower() == "html":
            return self._generate_html_report(test_results, report_dir)
        elif format.lower() == "json":
            return self._generate_json_report(test_results, report_dir)
        else:
            logger.warning(f"Unsupported report format: {format}, defaulting to HTML")
            return self._generate_html_report(test_results, report_dir)
    
    def _generate_pdf_report(self, test_results: Dict[str, Any], report_dir: str) -> str:
        """
        Generate a PDF report.
        
        Args:
            test_results: Test results.
            report_dir: Directory to save the report.
            
        Returns:
            Path to the generated report.
        """
        # First generate an HTML report
        html_path = self._generate_html_report(test_results, report_dir)
        
        # Convert HTML to PDF
        pdf_path = os.path.join(report_dir, "report.pdf")
        
        try:
            # Check if weasyprint is available
            import weasyprint
            weasyprint.HTML(html_path).write_pdf(pdf_path)
            logger.info(f"Generated PDF report at {pdf_path}")
            return pdf_path
        except ImportError:
            # If weasyprint is not available, try using a subprocess
            try:
                import subprocess
                subprocess.run(["wkhtmltopdf", html_path, pdf_path], check=True)
                logger.info(f"Generated PDF report at {pdf_path}")
                return pdf_path
            except:
                logger.error("Failed to generate PDF report, returning HTML report instead")
                return html_path
    
    def _generate_html_report(self, test_results: Dict[str, Any], report_dir: str) -> str:
        """
        Generate an HTML report.
        
        Args:
            test_results: Test results.
            report_dir: Directory to save the report.
            
        Returns:
            Path to the generated report.
        """
        html_path = os.path.join(report_dir, "report.html")
        
        # Generate a simple HTML report
        with open(html_path, 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Report</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        color: #333;
                    }
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                    }
                    h1 {
                        color: #2c3e50;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                    }
                    .summary {
                        background-color: #f8f9fa;
                        padding: 15px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }
                    .step {
                        margin-bottom: 15px;
                        padding: 10px;
                        border-radius: 5px;
                    }
                    .step.passed {
                        background-color: #d4edda;
                        border-left: 5px solid #28a745;
                    }
                    .step.warning {
                        background-color: #fff3cd;
                        border-left: 5px solid #ffc107;
                    }
                    .step.failed {
                        background-color: #f8d7da;
                        border-left: 5px solid #dc3545;
                    }
                    .screenshot {
                        max-width: 100%;
                        height: auto;
                        margin-top: 10px;
                        border: 1px solid #ddd;
                    }
                    .details {
                        margin-top: 5px;
                        font-size: 0.9em;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Test Report</h1>
                    <div class="summary">
                        <h2>Summary</h2>
                        <p><strong>Status:</strong> """ + test_results.get("status", "Unknown") + """</p>
                        <p><strong>Timestamp:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
                    </div>
            """)
            
            # Add steps
            if "steps" in test_results:
                f.write("<h2>Steps</h2>")
                for i, step in enumerate(test_results["steps"]):
                    status = step.get("status", "unknown")
                    f.write(f"""
                    <div class="step {status}">
                        <h3>Step {i+1}: {step.get('step', 'Unknown')}</h3>
                        <p>{step.get('command', '')}</p>
                        <div class="details">{step.get('details', '')}</div>
                    """)
                    
                    # Add screenshot if available and enabled
                    if self.include_screenshots and "screenshots" in test_results and i < len(test_results["screenshots"]):
                        screenshot_path = test_results["screenshots"][i]
                        if os.path.exists(screenshot_path):
                            # Copy the screenshot to the report directory
                            import shutil
                            screenshot_name = f"step_{i+1}_screenshot.png"
                            screenshot_copy_path = os.path.join(report_dir, screenshot_name)
                            shutil.copy(screenshot_path, screenshot_copy_path)
                            
                            f.write(f"""
                            <img class="screenshot" src="{screenshot_name}" alt="Step {i+1} Screenshot">
                            """)
                    
                    f.write("</div>")
            
            # Close the HTML
            f.write("""
                </div>
            </body>
            </html>
            """)
        
        logger.info(f"Generated HTML report at {html_path}")
        return html_path
    
    def _generate_json_report(self, test_results: Dict[str, Any], report_dir: str) -> str:
        """
        Generate a JSON report.
        
        Args:
            test_results: Test results.
            report_dir: Directory to save the report.
            
        Returns:
            Path to the generated report.
        """
        json_path = os.path.join(report_dir, "report.json")
        
        # Add timestamp to the results
        report_data = {
            **test_results,
            "generated_at": datetime.now().isoformat()
        }
        
        # Write the JSON report
        with open(json_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Generated JSON report at {json_path}")
        return json_path
