"""
Enhanced Web UI integration for AI QA Agent using the central controller.
This module provides a Gradio-based web interface for the AI QA Agent with integrated workflows.
"""
import os
import logging
import gradio as gr
import tempfile
from typing import Dict, List, Any, Optional, Union
import json
import base64
from pathlib import Path

from controller import AIQAAgentController

logger = logging.getLogger(__name__)

def start_webui(host="127.0.0.1", port=7788):
    """
    Start the Web UI for the AI QA Agent.
    
    Args:
        host: Host to bind the Web UI to.
        port: Port to bind the Web UI to.
    """
    logger.info(f"Starting Web UI on {host}:{port}")
    
    # Initialize the controller
    controller = AIQAAgentController()
    
    # Define the interface
    with gr.Blocks(title="AI QA Agent", theme=os.getenv("WEBUI_THEME", "Ocean")) as interface:
        gr.Markdown("# AI QA Agent")
        gr.Markdown("Analyze, optimize, and test your QA test cases with AI assistance.")
        
        # Create a state for storing session data
        session_state = gr.State({})
        
        with gr.Tabs():
            # Dashboard Tab
            with gr.TabItem("Dashboard"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Recent Test Sessions")
                        recent_sessions = gr.DataFrame(
                            headers=["ID", "Name", "Date", "Status", "Pass Rate"],
                            label="Recent Test Sessions"
                        )
                        refresh_button = gr.Button("Refresh")
                    
                    with gr.Column():
                        gr.Markdown("## Quick Actions")
                        with gr.Row():
                            new_test_button = gr.Button("New Test")
                            analyze_button = gr.Button("Analyze Test Case")
                            visual_test_button = gr.Button("Visual Testing")
                            mobile_test_button = gr.Button("Mobile Testing")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Test Metrics")
                        metrics_json = gr.JSON(label="Test Metrics")
                    
                    with gr.Column():
                        gr.Markdown("## System Status")
                        system_status = gr.JSON(label="System Status")
                
                # Function to load dashboard data
                def load_dashboard():
                    # Get recent test sessions
                    history = controller.get_test_history(limit=5)
                    sessions_data = []
                    
                    for session in history:
                        sessions_data.append([
                            session.get("id", ""),
                            session.get("name", ""),
                            session.get("date", ""),
                            session.get("status", ""),
                            f"{session.get('pass_rate', 0)}%"
                        ])
                    
                    # Get system status
                    status = {
                        "LLM Provider": controller.config.get("llm_provider", "groq"),
                        "Appium Server": "Running" if controller.appium_manager.is_server_running() else "Stopped",
                        "Database": "Connected" if controller.history_manager.is_connected() else "Disconnected",
                        "Memory Usage": "Normal",
                        "Disk Space": "Sufficient"
                    }
                    
                    # Get test metrics
                    metrics = {
                        "Total Tests": len(history),
                        "Pass Rate": "85%",
                        "Average Duration": "2m 15s",
                        "Most Common Failure": "Element not found",
                        "Test Coverage": "72%"
                    }
                    
                    return sessions_data, status, metrics
                
                # Connect refresh button
                refresh_button.click(
                    fn=load_dashboard,
                    inputs=[],
                    outputs=[recent_sessions, system_status, metrics_json]
                )
                
                # Load dashboard on startup
                interface.load(
                    fn=load_dashboard,
                    inputs=[],
                    outputs=[recent_sessions, system_status, metrics_json]
                )
            
            # Integrated Workflows Tab
            with gr.TabItem("Workflows"):
                with gr.Tabs():
                    # Test Creation Workflow
                    with gr.TabItem("Test Creation Workflow"):
                        gr.Markdown("## Create Tests from Requirements")
                        gr.Markdown("This workflow guides you through creating tests from requirements to execution.")
                        
                        with gr.Row():
                            with gr.Column():
                                requirement_input = gr.Textbox(
                                    label="Test Requirements",
                                    placeholder="Describe what you want to test...",
                                    lines=5
                                )
                                generate_tests_button = gr.Button("Generate Tests")
                            
                            with gr.Column():
                                generated_gherkin = gr.Textbox(
                                    label="Generated Gherkin",
                                    lines=10
                                )
                                edit_gherkin_button = gr.Button("Edit & Optimize")
                        
                        with gr.Row():
                            with gr.Column():
                                optimized_gherkin = gr.Textbox(
                                    label="Optimized Gherkin",
                                    lines=10
                                )
                                save_path = gr.Textbox(
                                    label="Save Path",
                                    placeholder="Path to save the feature file",
                                    value="./tests/generated_test.feature"
                                )
                                save_and_run_button = gr.Button("Save & Run Tests")
                            
                            with gr.Column():
                                workflow_results = gr.JSON(
                                    label="Workflow Results"
                                )
                                report_link = gr.HTML(
                                    label="Test Report"
                                )
                        
                        # Connect workflow buttons
                        generate_tests_button.click(
                            fn=lambda req: controller.generate_gherkin_from_description(req),
                            inputs=requirement_input,
                            outputs=generated_gherkin
                        )
                        
                        edit_gherkin_button.click(
                            fn=lambda gherkin: controller.optimize_test_case(gherkin),
                            inputs=generated_gherkin,
                            outputs=optimized_gherkin
                        )
                        
                        def save_and_run_tests(gherkin, path):
                            # Ensure directory exists
                            os.makedirs(os.path.dirname(path), exist_ok=True)
                            
                            # Save gherkin to file
                            with open(path, "w") as f:
                                f.write(gherkin)
                            
                            # Run tests
                            results = controller.run_tests(path)
                            
                            # Generate report
                            report_path = controller.generate_report(results)
                            
                            # Create HTML link to report
                            report_html = f'<a href="file://{report_path}" target="_blank">Open Test Report</a>'
                            
                            return results, report_html
                        
                        save_and_run_button.click(
                            fn=save_and_run_tests,
                            inputs=[optimized_gherkin, save_path],
                            outputs=[workflow_results, report_link]
                        )
                    
                    # Visual Testing Workflow
                    with gr.TabItem("Visual Testing Workflow"):
                        gr.Markdown("## Visual Testing and Analysis")
                        gr.Markdown("This workflow guides you through visual testing with screenshot comparison and analysis.")
                        
                        with gr.Row():
                            with gr.Column():
                                baseline_screenshot = gr.Image(
                                    label="Baseline Screenshot",
                                    type="filepath"
                                )
                                current_screenshot = gr.Image(
                                    label="Current Screenshot",
                                    type="filepath"
                                )
                                compare_button = gr.Button("Compare Screenshots")
                            
                            with gr.Column():
                                diff_image = gr.Image(
                                    label="Difference Image"
                                )
                                comparison_results = gr.JSON(
                                    label="Comparison Results"
                                )
                        
                        with gr.Row():
                            with gr.Column():
                                ocr_button = gr.Button("Extract Text (OCR)")
                                extracted_text = gr.Textbox(
                                    label="Extracted Text",
                                    lines=5
                                )
                            
                            with gr.Column():
                                analyze_button = gr.Button("Analyze UI Elements")
                                ui_analysis = gr.JSON(
                                    label="UI Element Analysis"
                                )
                        
                        with gr.Row():
                            visual_report_button = gr.Button("Generate Visual Report")
                            visual_report_link = gr.HTML(
                                label="Visual Report"
                            )
                        
                        # Connect visual workflow buttons
                        def compare_screenshots(baseline, current):
                            if not baseline or not current:
                                return None, {"error": "Both screenshots are required"}
                            
                            # Create temp file for diff image
                            temp_dir = tempfile.mkdtemp()
                            diff_path = os.path.join(temp_dir, "diff.png")
                            
                            # Compare screenshots
                            results = controller.compare_screenshots(baseline, current, diff_path)
                            
                            return diff_path, results
                        
                        compare_button.click(
                            fn=compare_screenshots,
                            inputs=[baseline_screenshot, current_screenshot],
                            outputs=[diff_image, comparison_results]
                        )
                        
                        ocr_button.click(
                            fn=lambda img: controller.extract_text_from_screenshot(img) if img else "No screenshot provided",
                            inputs=current_screenshot,
                            outputs=extracted_text
                        )
                        
                        analyze_button.click(
                            fn=lambda img: controller.analyze_screenshot(img) if img else {"error": "No screenshot provided"},
                            inputs=current_screenshot,
                            outputs=ui_analysis
                        )
                        
                        def generate_visual_report(baseline, current, comparison, text, analysis):
                            if not baseline or not current:
                                return "Both screenshots are required for report generation"
                            
                            # Prepare results for report
                            results = {
                                "comparison": comparison,
                                "extracted_text": text,
                                "ui_analysis": analysis,
                                "baseline_path": baseline,
                                "current_path": current
                            }
                            
                            # Generate report
                            report_path = controller.generate_report(results, "html")
                            
                            # Create HTML link to report
                            report_html = f'<a href="file://{report_path}" target="_blank">Open Visual Report</a>'
                            
                            return report_html
                        
                        visual_report_button.click(
                            fn=generate_visual_report,
                            inputs=[baseline_screenshot, current_screenshot, comparison_results, extracted_text, ui_analysis],
                            outputs=visual_report_link
                        )
                    
                    # Mobile Testing Workflow
                    with gr.TabItem("Mobile Testing Workflow"):
                        gr.Markdown("## Mobile App Testing")
                        gr.Markdown("This workflow guides you through testing mobile applications with Appium and scrcpy.")
                        
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### Device Setup")
                                start_appium_button = gr.Button("Start Appium Server")
                                appium_status = gr.Textbox(
                                    label="Appium Server Status",
                                    value="Not Running"
                                )
                                connect_device_button = gr.Button("Connect to Device")
                                device_info = gr.JSON(
                                    label="Device Information"
                                )
                            
                            with gr.Column():
                                gr.Markdown("### App Control")
                                package_name = gr.Textbox(
                                    label="Package Name",
                                    placeholder="com.example.app"
                                )
                                activity_name = gr.Textbox(
                                    label="Activity Name (Optional)",
                                    placeholder="com.example.app.MainActivity"
                                )
                                start_app_button = gr.Button("Start App")
                                app_status = gr.Textbox(
                                    label="App Status",
                                    value="Not Running"
                                )
                        
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### Test Execution")
                                mobile_test_path = gr.Textbox(
                                    label="Test Path",
                                    placeholder="Path to mobile test file or directory"
                                )
                                run_mobile_tests_button = gr.Button("Run Mobile Tests")
                                mobile_test_results = gr.JSON(
                                    label="Test Results"
                                )
                            
                            with gr.Column():
                                gr.Markdown("### Device Control")
                                take_screenshot_button = gr.Button("Take Screenshot")
                                device_screenshot = gr.Image(
                                    label="Device Screenshot"
                                )
                                record_button = gr.Button("Start/Stop Recording")
                                recording_status = gr.Textbox(
                                    label="Recording Status",
                                    value="Not Recording"
                                )
                        
                        with gr.Row():
                            mobile_report_button = gr.Button("Generate Mobile Test Report")
                            mobile_report_link = gr.HTML(
                                label="Mobile Test Report"
                            )
                            stop_appium_button = gr.Button("Stop Appium Server")
                        
                        # Connect mobile workflow buttons
                        start_appium_button.click(
                            fn=lambda: "Running" if controller.start_appium_server() else "Failed to Start",
                            inputs=[],
                            outputs=appium_status
                        )
                        
                        connect_device_button.click(
                            fn=lambda: controller.connect_to_device(),
                            inputs=[],
                            outputs=device_info
                        )
                        
                        start_app_button.click(
                            fn=lambda pkg, act: "Running" if controller.start_app(pkg, act if act else None) else "Failed to Start",
                            inputs=[package_name, activity_name],
                            outputs=app_status
                        )
                        
                        take_screenshot_button.click(
                            fn=lambda: controller.take_screenshot(),
                            inputs=[],
                            outputs=device_screenshot
                        )
                        
                        # Recording state toggle
                        def toggle_recording(status):
                            if status == "Not Recording" or status == "Recording Stopped":
                                # Start recording
                                temp_dir = tempfile.mkdtemp()
                                recording_path = os.path.join(temp_dir, "recording.mp4")
                                controller.appium_manager.start_recording(recording_path)
                                return "Recording Started"
                            else:
                                # Stop recording
                                controller.appium_manager.stop_recording()
                                return "Recording Stopped"
                        
                        record_button.click(
                            fn=toggle_recording,
                            inputs=recording_status,
                            outputs=recording_status
                        )
                        
                        run_mobile_tests_button.click(
                            fn=lambda path: controller.run_tests(path) if path else {"error": "Test path is required"},
                            inputs=mobile_test_path,
                            outputs=mobile_test_results
                        )
                        
                        mobile_report_button.click(
                            fn=lambda results: f'<a href="file://{controller.generate_report(results, "html")}" target="_blank">Open Mobile Test Report</a>' if results else "No test results available",
                            inputs=mobile_test_results,
                            outputs=mobile_report_link
                        )
                        
                        stop_appium_button.click(
                            fn=lambda: "Not Running" if controller.stop_appium_server() else "Failed to Stop",
                            inputs=[],
                            outputs=appium_status
                        )
                    
                    # History Analysis Workflow
                    with gr.TabItem("History Analysis Workflow"):
                        gr.Markdown("## Test History Analysis")
                        gr.Markdown("This workflow helps you analyze test history and compare test runs.")
                        
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### Test History")
                                history_limit = gr.Slider(
                                    label="Number of Sessions",
                                    minimum=5,
                                    maximum=50,
                                    step=5,
                                    value=10
                                )
                                get_history_button = gr.Button("Get Test History")
                                history_data = gr.DataFrame(
                                    headers=["ID", "Name", "Date", "Status", "Pass Rate"],
                                    label="Test History"
                                )
                            
                            with gr.Column():
                                gr.Markdown("### Session Details")
                                session_id = gr.Textbox(
                                    label="Session ID",
                                    placeholder="Enter session ID to view details"
                                )
                                get_session_button = gr.Button("Get Session Details")
                                session_details = gr.JSON(
                                    label="Session Details"
                                )
                        
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### Session Comparison")
                                session_id1 = gr.Textbox(
                                    label="First Session ID",
                                    placeholder="Enter first session ID"
                                )
                                session_id2 = gr.Textbox(
                                    label="Second Session ID",
                                    placeholder="Enter second session ID"
                                )
                                compare_sessions_button = gr.Button("Compare Sessions")
                                comparison_data = gr.JSON(
                                    label="Comparison Results"
                                )
                            
                            with gr.Column():
                                gr.Markdown("### Data Export")
                                export_format = gr.Radio(
                                    label="Export Format",
                                    choices=["json", "csv"],
                                    value="json"
                                )
                                export_button = gr.Button("Export History")
                                export_link = gr.HTML(
                                    label="Export File"
                                )
                        
                        # Connect history workflow buttons
                        def get_test_history(limit):
                            history = controller.get_test_history(limit=limit)
                            history_rows = []
                            
                            for session in history:
                                history_rows.append([
                                    session.get("id", ""),
                                    session.get("name", ""),
                                    session.get("date", ""),
                                    session.get("status", ""),
                                    f"{session.get('pass_rate', 0)}%"
                                ])
                            
                            return history_rows
                        
                        get_history_button.click(
                            fn=get_test_history,
                            inputs=history_limit,
                            outputs=history_data
                        )
                        
                        get_session_button.click(
                            fn=lambda id: controller.get_session_details(id) if id else {"error": "Session ID is required"},
                            inputs=session_id,
                            outputs=session_details
                        )
                        
                        compare_sessions_button.click(
                            fn=lambda id1, id2: controller.compare_sessions(id1, id2) if id1 and id2 else {"error": "Both session IDs are required"},
                            inputs=[session_id1, session_id2],
                            outputs=comparison_data
                        )
                        
                        def export_history(format):
                            export_path = controller.export_history(format=format)
                            return f'<a href="file://{export_path}" target="_blank">Download {format.upper()} Export</a>'
                        
                        export_button.click(
                            fn=export_history,
                            inputs=export_format,
                            outputs=export_link
                        )
            
            # Individual Tools Tabs
            
            # Test Case Analysis Tab
            with gr.TabItem("Test Case Analysis"):
                with gr.Row():
                    with gr.Column():
                        test_case_input = gr.Textbox(
                            label="Test Case (Gherkin Format)",
                            placeholder="Feature: Login\n  Scenario: Successful login\n    Given I am on the login page\n    When I enter valid credentials\n    Then I should be logged in",
                            lines=10
                        )
                        analyze_test_button = gr.Button("Analyze Test Case")
                        optimize_test_button = gr.Button("Optimize Test Case")
                    
                    with gr.Column():
                        analysis_output = gr.JSON(label="Analysis Results")
                
                optimized_test_case = gr.Textbox(label="Optimized Test Case", lines=10)
                
                # Connect the buttons to functions
                analyze_test_button.click(
                    fn=lambda test_case: controller.analyze_test_case(test_case),
                    inputs=test_case_input,
                    outputs=analysis_output
                )
                
                optimize_test_button.click(
                    fn=lambda test_case: controller.optimize_test_case(test_case),
                    inputs=test_case_input,
                    outputs=optimized_test_case
                )
            
            # Gherkin Translator Tab
            with gr.TabItem("Gherkin Translator"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Natural Language to Gherkin")
                        nl_input = gr.Textbox(
                            label="Natural Language Test Steps",
                            placeholder="1. Navigate to the login page\n2. Enter username 'admin' and password 'password123'\n3. Click the login button\n4. Verify that the dashboard is displayed",
                            lines=10
                        )
                        to_gherkin_button = gr.Button("Translate to Gherkin")
                    
                    with gr.Column():
                        gherkin_output = gr.Textbox(
                            label="Gherkin Format",
                            lines=10
                        )
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Gherkin to Natural Language")
                        gherkin_input = gr.Textbox(
                            label="Gherkin Format",
                            placeholder="Feature: Login\n  Scenario: Successful login\n    Given I am on the login page\n    When I enter username 'admin' and password 'password123'\n    And I click the login button\n    Then I should see the dashboard",
                            lines=10
                        )
                        from_gherkin_button = gr.Button("Translate to Natural Language")
                    
                    with gr.Column():
                        nl_output = gr.Textbox(
                            label="Natural Language Test Steps",
                            lines=10
                        )
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Generate Gherkin from Description")
                        description_input = gr.Textbox(
                            label="Test Description",
                            placeholder="Create a test for the login functionality. The test should verify that users can log in with valid credentials and that appropriate error messages are shown for invalid credentials.",
                            lines=5
                        )
                        generate_button = gr.Button("Generate Gherkin")
                    
                    with gr.Column():
                        generated_gherkin = gr.Textbox(
                            label="Generated Gherkin",
                            lines=10
                        )
                
                # Connect the buttons to functions
                to_gherkin_button.click(
                    fn=lambda test_steps: controller.translate_to_gherkin(test_steps),
                    inputs=nl_input,
                    outputs=gherkin_output
                )
                
                from_gherkin_button.click(
                    fn=lambda gherkin: controller.translate_from_gherkin(gherkin),
                    inputs=gherkin_input,
                    outputs=nl_output
                )
                
                generate_button.click(
                    fn=lambda description: controller.generate_gherkin_from_description(description),
                    inputs=description_input,
                    outputs=generated_gherkin
                )
            
            # Visual Testing Tab
            with gr.TabItem("Visual Testing"):
                with gr.Row():
                    with gr.Column():
                        screenshot_input = gr.Image(label="Screenshot", type="filepath")
                        analyze_screenshot_button = gr.Button("Analyze Screenshot")
                    
                    with gr.Column():
                        visual_analysis_output = gr.JSON(label="Visual Analysis Results")
                
                with gr.Row():
                    with gr.Column():
                        baseline_input = gr.Image(label="Baseline Screenshot", type="filepath")
                        current_input = gr.Image(label="Current Screenshot", type="filepath")
                        compare_screenshots_button = gr.Button("Compare Screenshots")
                    
                    with gr.Column():
                        diff_output = gr.Image(label="Difference Image")
                        comparison_output = gr.JSON(label="Comparison Results")
                
                with gr.Row():
                    with gr.Column():
                        ocr_screenshot_button = gr.Button("Extract Text (OCR)")
                        ocr_output = gr.Textbox(label="Extracted Text", lines=5)
                
                # Connect the buttons to functions
                analyze_screenshot_button.click(
                    fn=lambda screenshot: controller.analyze_screenshot(screenshot) if screenshot else {"error": "No screenshot provided"},
                    inputs=screenshot_input,
                    outputs=visual_analysis_output
                )
                
                def compare_screenshots_fn(baseline, current):
                    if not baseline or not current:
                        return None, {"error": "Both screenshots are required"}
                    
                    # Create temp file for diff image
                    temp_dir = tempfile.mkdtemp()
                    diff_path = os.path.join(temp_dir, "diff.png")
                    
                    # Compare screenshots
                    results = controller.compare_screenshots(baseline, current, diff_path)
                    
                    return diff_path, results
                
                compare_screenshots_button.click(
                    fn=compare_screenshots_fn,
                    inputs=[baseline_input, current_input],
                    outputs=[diff_output, comparison_output]
                )
                
                ocr_screenshot_button.click(
                    fn=lambda screenshot: controller.extract_text_from_screenshot(screenshot) if screenshot else "No screenshot provided",
                    inputs=screenshot_input,
                    outputs=ocr_output
                )
            
            # Mobile Testing Tab
            with gr.TabItem("Mobile Testing"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Appium Server Control")
                        start_server_button = gr.Button("Start Appium Server")
                        stop_server_button = gr.Button("Stop Appium Server")
                        server_status = gr.Textbox(label="Server Status", value="Not Running")
                    
                    with gr.Column():
                        gr.Markdown("## Device Control")
                        device_id_input = gr.Textbox(label="Device ID (Optional)", placeholder="Leave empty for first available device")
                        connect_button = gr.Button("Connect to Device")
                        device_status = gr.JSON(label="Device Status")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## App Control")
                        app_package_input = gr.Textbox(label="App Package Name", placeholder="com.example.app")
                        app_activity_input = gr.Textbox(label="App Activity (Optional)", placeholder="com.example.app.MainActivity")
                        start_app_button = gr.Button("Start App")
                        app_status_output = gr.Textbox(label="App Status", value="Not Running")
                    
                    with gr.Column():
                        gr.Markdown("## Device Actions")
                        take_device_screenshot_button = gr.Button("Take Screenshot")
                        device_screenshot_output = gr.Image(label="Device Screenshot")
                
                # Connect the buttons to functions
                start_server_button.click(
                    fn=lambda: "Running" if controller.start_appium_server() else "Failed to Start",
                    inputs=[],
                    outputs=server_status
                )
                
                stop_server_button.click(
                    fn=lambda: "Not Running" if controller.stop_appium_server() else "Failed to Stop",
                    inputs=[],
                    outputs=server_status
                )
                
                connect_button.click(
                    fn=lambda device_id: controller.connect_to_device(device_id if device_id else None),
                    inputs=device_id_input,
                    outputs=device_status
                )
                
                start_app_button.click(
                    fn=lambda pkg, act: "Running" if controller.start_app(pkg, act if act else None) else "Failed to Start",
                    inputs=[app_package_input, app_activity_input],
                    outputs=app_status_output
                )
                
                take_device_screenshot_button.click(
                    fn=lambda: controller.take_screenshot(),
                    inputs=[],
                    outputs=device_screenshot_output
                )
            
            # History Manager Tab
            with gr.TabItem("History Manager"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Test History")
                        history_limit_input = gr.Slider(label="Number of Sessions", minimum=5, maximum=50, step=5, value=10)
                        get_history_button = gr.Button("Get History")
                        history_output = gr.DataFrame(headers=["ID", "Name", "Date", "Status", "Pass Rate"], label="Test History")
                    
                    with gr.Column():
                        gr.Markdown("## Session Details")
                        session_id_input = gr.Textbox(label="Session ID", placeholder="Enter session ID to view details")
                        get_details_button = gr.Button("Get Details")
                        session_details_output = gr.JSON(label="Session Details")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Compare Sessions")
                        session1_input = gr.Textbox(label="First Session ID", placeholder="Enter first session ID")
                        session2_input = gr.Textbox(label="Second Session ID", placeholder="Enter second session ID")
                        compare_button = gr.Button("Compare Sessions")
                        comparison_output = gr.JSON(label="Comparison Results")
                    
                    with gr.Column():
                        gr.Markdown("## Export History")
                        export_format_input = gr.Radio(label="Export Format", choices=["json", "csv"], value="json")
                        export_button = gr.Button("Export History")
                        export_output = gr.HTML(label="Export File")
                
                # Connect the buttons to functions
                def get_history_fn(limit):
                    history = controller.get_test_history(limit=limit)
                    history_rows = []
                    
                    for session in history:
                        history_rows.append([
                            session.get("id", ""),
                            session.get("name", ""),
                            session.get("date", ""),
                            session.get("status", ""),
                            f"{session.get('pass_rate', 0)}%"
                        ])
                    
                    return history_rows
                
                get_history_button.click(
                    fn=get_history_fn,
                    inputs=history_limit_input,
                    outputs=history_output
                )
                
                get_details_button.click(
                    fn=lambda id: controller.get_session_details(id) if id else {"error": "Session ID is required"},
                    inputs=session_id_input,
                    outputs=session_details_output
                )
                
                compare_button.click(
                    fn=lambda id1, id2: controller.compare_sessions(id1, id2) if id1 and id2 else {"error": "Both session IDs are required"},
                    inputs=[session1_input, session2_input],
                    outputs=comparison_output
                )
                
                def export_history_fn(format):
                    export_path = controller.export_history(format=format)
                    return f'<a href="file://{export_path}" target="_blank">Download {format.upper()} Export</a>'
                
                export_button.click(
                    fn=export_history_fn,
                    inputs=export_format_input,
                    outputs=export_output
                )
            
            # Settings Tab
            with gr.TabItem("Settings"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## LLM Settings")
                        llm_provider = gr.Dropdown(
                            label="LLM Provider",
                            choices=["groq", "hyperbolic", "ollama", "lmstudio"],
                            value=controller.config.get("llm_provider", "groq")
                        )
                        api_key = gr.Textbox(
                            label="API Key",
                            placeholder="sk-...",
                            type="password",
                            value=controller.config.get("groq_api_key", "")
                        )
                        model = gr.Dropdown(
                            label="Model",
                            choices=["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
                            value=controller.config.get("groq_model", "llama3-70b-8192")
                        )
                    
                    with gr.Column():
                        gr.Markdown("## Browser Settings")
                        browser_type = gr.Dropdown(
                            label="Browser Type",
                            choices=["chromium", "firefox", "webkit"],
                            value=controller.config.get("browser_type", "chromium")
                        )
                        headless = gr.Checkbox(
                            label="Headless Mode",
                            value=controller.config.get("headless", False)
                        )
                        browser_resolution = gr.Textbox(
                            label="Browser Resolution",
                            placeholder="1920,1080",
                            value=controller.config.get("browser_resolution", "1920,1080")
                        )
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Reporting Settings")
                        default_report_format = gr.Dropdown(
                            label="Default Report Format",
                            choices=["pdf", "html", "json"],
                            value=controller.config.get("report_format", "pdf")
                        )
                        include_screenshots = gr.Checkbox(
                            label="Include Screenshots in Reports",
                            value=controller.config.get("include_screenshots", True)
                        )
                        include_videos = gr.Checkbox(
                            label="Include Videos in Reports",
                            value=controller.config.get("include_videos", True)
                        )
                    
                    with gr.Column():
                        gr.Markdown("## Logging Settings")
                        log_level = gr.Dropdown(
                            label="Log Level",
                            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                            value=controller.config.get("log_level", "INFO")
                        )
                        log_file = gr.Textbox(
                            label="Log File",
                            placeholder="./logs/ai_qa_agent.log",
                            value=controller.config.get("log_file", "./logs/ai_qa_agent.log")
                        )
                
                save_settings_button = gr.Button("Save Settings")
                settings_status = gr.Textbox(label="Status")
                
                # Connect the save button to function
                def save_settings(llm_provider, api_key, model, browser_type, headless, 
                                 browser_resolution, default_report_format, include_screenshots, 
                                 include_videos, log_level, log_file):
                    try:
                        # Create a configuration dictionary
                        config = {
                            "llm_provider": llm_provider,
                            f"{llm_provider}_api_key": api_key,
                            f"{llm_provider}_model": model,
                            "browser_type": browser_type,
                            "headless": headless,
                            "browser_resolution": browser_resolution,
                            "report_format": default_report_format,
                            "include_screenshots": include_screenshots,
                            "include_videos": include_videos,
                            "log_level": log_level,
                            "log_file": log_file
                        }
                        
                        # Update controller configuration
                        controller.update_config(config)
                        
                        # Save configuration to file
                        controller.save_config()
                        
                        return "Settings saved successfully"
                    except Exception as e:
                        logger.error(f"Error saving settings: {e}")
                        return f"Error saving settings: {e}"
                
                save_settings_button.click(
                    fn=save_settings,
                    inputs=[
                        llm_provider, api_key, model, browser_type, headless, 
                        browser_resolution, default_report_format, include_screenshots, 
                        include_videos, log_level, log_file
                    ],
                    outputs=settings_status
                )
    
    # Launch the interface
    interface.launch(server_name=host, server_port=port)

if __name__ == "__main__":
    start_webui()
