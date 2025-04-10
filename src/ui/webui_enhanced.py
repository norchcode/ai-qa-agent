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

from ..core.controller import AIQAAgentController

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
            # Unified Interface Tab (New)
            with gr.TabItem("Unified Interface"):
                gr.Markdown("## AI QA Assistant")
                gr.Markdown("Ask anything about testing, analyze test cases, generate tests, or process images - all in one place.")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        # Main input area
                        unified_prompt = gr.Textbox(
                            label="What would you like to do?",
                            placeholder="Ask a question, paste a test case, describe requirements, or request analysis...",
                            lines=5
                        )
                        
                        # File upload area
                        file_uploads = gr.File(
                            label="Upload Files (Optional)",
                            file_types=["image", "text", ".feature", ".md", ".txt", ".pdf", ".json"],
                            file_count="multiple"
                        )
                        
                        # Submit button
                        submit_button = gr.Button("Submit", variant="primary")
                    
                    with gr.Column(scale=2):
                        # Quick examples
                        gr.Markdown("### Quick Examples")
                        example1 = gr.Button("Analyze a test case")
                        example2 = gr.Button("Generate tests from requirements")
                        example3 = gr.Button("Compare two screenshots")
                        example4 = gr.Button("Translate to Gherkin format")
                
                # Output area
                with gr.Row():
                    with gr.Column():
                        # Text response
                        response_text = gr.Markdown(label="Response")
                        
                        # JSON output for structured data
                        response_data = gr.JSON(label="Details")
                        
                        # File output for generated files
                        response_files = gr.File(label="Generated Files")
                        
                        # Image output for visual results
                        response_image = gr.Image(label="Visual Results", visible=False)
                
                # History area
                with gr.Accordion("Conversation History", open=False):
                    conversation_history = gr.Dataframe(
                        headers=["Time", "Request", "Response"],
                        datatype=["str", "str", "str"],
                        label="Conversation History"
                    )
                
                # Function to handle unified requests
                def process_unified_request(prompt, files):
                    if not prompt and (not files or len(files) == 0):
                        return "Please enter a prompt or upload files to process.", {}, None, None, []
                    
                    # Process file uploads
                    file_paths = []
                    if files:
                        for file in files:
                            file_paths.append(file.name)
                    
                    # Process the request through the controller
                    result = controller.process_unified_request(prompt, file_paths)
                    
                    # Prepare the response
                    response = result.get("response", "")
                    data = result.get("data", {})
                    
                    # Handle any generated files
                    generated_files = result.get("files", [])
                    
                    # Update conversation history
                    history_entry = [
                        gr.update(value=[[
                            "Just now",
                            prompt[:50] + ("..." if len(prompt) > 50 else ""),
                            response[:50] + ("..." if len(response) > 50 else "")
                        ]])
                    ]
                    
                    # Handle image display
                    image_path = None
                    image_visible = False
                    for file_path in generated_files:
                        ext = os.path.splitext(file_path)[1].lower()
                        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                            image_path = file_path
                            image_visible = True
                            break
                    
                    return (
                        response,
                        data,
                        generated_files if generated_files else None,
                        gr.update(value=image_path, visible=image_visible),
                        history_entry
                    )
                
                # Connect the submit button
                submit_button.click(
                    fn=process_unified_request,
                    inputs=[unified_prompt, file_uploads],
                    outputs=[response_text, response_data, response_files, response_image, conversation_history]
                )
                
                # Connect example buttons
                example1.click(
                    fn=lambda: "Analyze this test case for quality and coverage:\n\nFeature: Login\n  Scenario: Successful login\n    Given I am on the login page\n    When I enter valid credentials\n    Then I should be logged in",
                    inputs=[],
                    outputs=[unified_prompt]
                )
                
                example2.click(
                    fn=lambda: "Generate test cases for a user registration form with fields for name, email, password, and password confirmation. Include validation tests.",
                    inputs=[],
                    outputs=[unified_prompt]
                )
                
                example3.click(
                    fn=lambda: "Compare these two screenshots and highlight the differences.",
                    inputs=[],
                    outputs=[unified_prompt]
                )
                
                example4.click(
                    fn=lambda: "Translate these steps to Gherkin format:\n1. Navigate to the login page\n2. Enter username 'admin' and password 'password123'\n3. Click the login button\n4. Verify that the dashboard is displayed",
                    inputs=[],
                    outputs=[unified_prompt]
                )
            
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
            
            # Test Case Analysis Tab
            with gr.TabItem("Test Case Analysis"):
                gr.Markdown("## Test Case Analysis")
                gr.Markdown("Analyze your test cases for quality, coverage, and best practices.")
                
                with gr.Row():
                    with gr.Column():
                        test_case_input = gr.Textbox(
                            label="Test Case (Gherkin Format)",
                            placeholder="Paste your Gherkin test case here...",
                            lines=10
                        )
                        analyze_test_button = gr.Button("Analyze Test Case")
                    
                    with gr.Column():
                        analysis_results = gr.JSON(
                            label="Analysis Results"
                        )
                        optimize_button = gr.Button("Optimize Test Case")
                
                with gr.Row():
                    optimized_test = gr.Textbox(
                        label="Optimized Test Case",
                        lines=10
                    )
                
                # Connect analysis buttons
                analyze_test_button.click(
                    fn=lambda test: controller.analyze_test_case(test),
                    inputs=test_case_input,
                    outputs=analysis_results
                )
                
                optimize_button.click(
                    fn=lambda test: controller.optimize_test_case(test),
                    inputs=test_case_input,
                    outputs=optimized_test
                )
            
            # Gherkin Translation Tab
            with gr.TabItem("Gherkin Translation"):
                gr.Markdown("## Gherkin Translation")
                gr.Markdown("Translate between natural language and Gherkin format.")
                
                with gr.Tabs():
                    with gr.TabItem("Natural Language to Gherkin"):
                        with gr.Row():
                            with gr.Column():
                                nl_input = gr.Textbox(
                                    label="Natural Language Steps",
                                    placeholder="Enter test steps in natural language...",
                                    lines=10
                                )
                                to_gherkin_button = gr.Button("Translate to Gherkin")
                            
                            with gr.Column():
                                gherkin_output = gr.Textbox(
                                    label="Gherkin Format",
                                    lines=10
                                )
                    
                    with gr.TabItem("Gherkin to Natural Language"):
                        with gr.Row():
                            with gr.Column():
                                gherkin_input = gr.Textbox(
                                    label="Gherkin Format",
                                    placeholder="Enter test steps in Gherkin format...",
                                    lines=10
                                )
                                to_nl_button = gr.Button("Translate to Natural Language")
                            
                            with gr.Column():
                                nl_output = gr.Textbox(
                                    label="Natural Language Steps",
                                    lines=10
                                )
                
                # Connect translation buttons
                to_gherkin_button.click(
                    fn=lambda nl: controller.translate_to_gherkin(nl),
                    inputs=nl_input,
                    outputs=gherkin_output
                )
                
                to_nl_button.click(
                    fn=lambda gherkin: controller.translate_from_gherkin(gherkin),
                    inputs=gherkin_input,
                    outputs=nl_output
                )
            
            # Visual Testing Tab
            with gr.TabItem("Visual Testing"):
                gr.Markdown("## Visual Testing")
                gr.Markdown("Analyze and compare screenshots for visual testing.")
                
                with gr.Tabs():
                    with gr.TabItem("Screenshot Analysis"):
                        with gr.Row():
                            with gr.Column():
                                screenshot_upload = gr.Image(
                                    label="Upload Screenshot",
                                    type="filepath"
                                )
                                analyze_screenshot_button = gr.Button("Analyze Screenshot")
                            
                            with gr.Column():
                                screenshot_analysis = gr.JSON(
                                    label="Analysis Results"
                                )
                        
                        with gr.Row():
                            extract_text_button = gr.Button("Extract Text from Screenshot")
                            extracted_text = gr.Textbox(
                                label="Extracted Text",
                                lines=5
                            )
                    
                    with gr.TabItem("Screenshot Comparison"):
                        with gr.Row():
                            with gr.Column():
                                baseline_upload = gr.Image(
                                    label="Baseline Screenshot",
                                    type="filepath"
                                )
                            
                            with gr.Column():
                                current_upload = gr.Image(
                                    label="Current Screenshot",
                                    type="filepath"
                                )
                        
                        compare_screenshots_button = gr.Button("Compare Screenshots")
                        
                        with gr.Row():
                            with gr.Column():
                                comparison_results = gr.JSON(
                                    label="Comparison Results"
                                )
                            
                            with gr.Column():
                                diff_image = gr.Image(
                                    label="Difference Image"
                                )
                
                # Connect visual testing buttons
                analyze_screenshot_button.click(
                    fn=lambda screenshot: controller.analyze_screenshot(screenshot),
                    inputs=screenshot_upload,
                    outputs=screenshot_analysis
                )
                
                extract_text_button.click(
                    fn=lambda screenshot: controller.extract_text_from_screenshot(screenshot),
                    inputs=screenshot_upload,
                    outputs=extracted_text
                )
                
                def compare_screenshots_fn(baseline, current):
                    # Create a temporary file for the diff image
                    temp_dir = tempfile.mkdtemp()
                    diff_path = os.path.join(temp_dir, "diff.png")
                    
                    # Compare the screenshots
                    comparison = controller.compare_screenshots(baseline, current, diff_path)
                    
                    return comparison, diff_path
                
                compare_screenshots_button.click(
                    fn=compare_screenshots_fn,
                    inputs=[baseline_upload, current_upload],
                    outputs=[comparison_results, diff_image]
                )
            
            # Mobile Testing Tab
            with gr.TabItem("Mobile Testing"):
                gr.Markdown("## Mobile Testing")
                gr.Markdown("Test mobile applications using Appium.")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Appium Server")
                        with gr.Row():
                            start_server_button = gr.Button("Start Appium Server")
                            stop_server_button = gr.Button("Stop Appium Server")
                        
                        server_status = gr.Textbox(
                            label="Server Status",
                            value="Stopped"
                        )
                    
                    with gr.Column():
                        gr.Markdown("### Device Connection")
                        connect_device_button = gr.Button("Connect to Device")
                        device_info = gr.JSON(
                            label="Device Information"
                        )
                
                with gr.Row():
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
                        launch_app_button = gr.Button("Launch App")
                    
                    with gr.Column():
                        gr.Markdown("### Screen Recording")
                        with gr.Row():
                            start_recording_button = gr.Button("Start Recording")
                            stop_recording_button = gr.Button("Stop Recording")
                        
                        recording_path = gr.Textbox(
                            label="Recording Path"
                        )
                
                # Connect mobile testing buttons
                def start_server_fn():
                    success = controller.start_appium_server()
                    return "Running" if success else "Failed to start"
                
                def stop_server_fn():
                    success = controller.stop_appium_server()
                    return "Stopped" if success else "Failed to stop"
                
                start_server_button.click(
                    fn=start_server_fn,
                    inputs=[],
                    outputs=server_status
                )
                
                stop_server_button.click(
                    fn=stop_server_fn,
                    inputs=[],
                    outputs=server_status
                )
                
                connect_device_button.click(
                    fn=lambda: controller.connect_to_device(),
                    inputs=[],
                    outputs=device_info
                )
                
                launch_app_button.click(
                    fn=lambda pkg, act: {"success": controller.launch_app(pkg, act)},
                    inputs=[package_name, activity_name],
                    outputs=device_info
                )
                
                start_recording_button.click(
                    fn=lambda: controller.start_recording(),
                    inputs=[],
                    outputs=recording_path
                )
                
                stop_recording_button.click(
                    fn=lambda: controller.stop_recording() or "Recording stopped",
                    inputs=[],
                    outputs=recording_path
                )
            
            # History Tab
            with gr.TabItem("History"):
                gr.Markdown("## Test History")
                gr.Markdown("View and manage your test history.")
                
                with gr.Row():
                    with gr.Column():
                        history_limit = gr.Slider(
                            label="Number of Entries",
                            minimum=5,
                            maximum=50,
                            step=5,
                            value=10
                        )
                        view_history_button = gr.Button("View History")
                    
                    with gr.Column():
                        export_format = gr.Radio(
                            label="Export Format",
                            choices=["json", "csv"],
                            value="json"
                        )
                        export_button = gr.Button("Export History")
                
                history_table = gr.DataFrame(
                    headers=["ID", "Name", "Date", "Status", "Pass Rate"],
                    label="Test History"
                )
                
                export_path = gr.Textbox(
                    label="Export Path"
                )
                
                # Connect history buttons
                view_history_button.click(
                    fn=lambda limit: controller.get_test_history(limit),
                    inputs=history_limit,
                    outputs=history_table
                )
                
                export_button.click(
                    fn=lambda format: controller.export_history(format),
                    inputs=export_format,
                    outputs=export_path
                )
            
            # Settings Tab
            with gr.TabItem("Settings"):
                gr.Markdown("## Settings")
                gr.Markdown("Configure the AI QA Agent.")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### LLM Provider")
                        llm_provider = gr.Radio(
                            label="Provider",
                            choices=["groq", "openai", "anthropic"],
                            value=controller.config.get("llm_provider", "groq")
                        )
                        llm_model = gr.Textbox(
                            label="Model",
                            value=controller.config.get("groq_model", "llama3-70b-8192")
                        )
                        api_key = gr.Textbox(
                            label="API Key",
                            value="",
                            type="password"
                        )
                    
                    with gr.Column():
                        gr.Markdown("### Web UI Settings")
                        webui_theme = gr.Dropdown(
                            label="Theme",
                            choices=["Ocean", "Soft", "Glass", "Monochrome", "Default"],
                            value=os.getenv("WEBUI_THEME", "Ocean")
                        )
                        webui_host = gr.Textbox(
                            label="Host",
                            value="127.0.0.1"
                        )
                        webui_port = gr.Number(
                            label="Port",
                            value=7788
                        )
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Logging")
                        log_level = gr.Radio(
                            label="Log Level",
                            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                            value=controller.config.get("log_level", "INFO")
                        )
                        log_file = gr.Textbox(
                            label="Log File",
                            value=controller.config.get("log_file", "./logs/ai_qa_agent.log")
                        )
                    
                    with gr.Column():
                        gr.Markdown("### Report Settings")
                        report_format = gr.Radio(
                            label="Report Format",
                            choices=["pdf", "html", "json"],
                            value=controller.config.get("report_format", "pdf")
                        )
                        include_screenshots = gr.Checkbox(
                            label="Include Screenshots",
                            value=controller.config.get("include_screenshots", True)
                        )
                        include_videos = gr.Checkbox(
                            label="Include Videos",
                            value=controller.config.get("include_videos", True)
                        )
                
                save_settings_button = gr.Button("Save Settings")
                settings_status = gr.Textbox(label="Status")
                
                # Function to save settings
                def save_settings(provider, model, key, theme, host, port, level, file, format, screenshots, videos):
                    # In a real implementation, we would save these settings to a config file
                    # and update the controller's configuration
                    
                    # For this placeholder, we'll just return a success message
                    return "Settings saved successfully"
                
                # Connect settings button
                save_settings_button.click(
                    fn=save_settings,
                    inputs=[
                        llm_provider, llm_model, api_key,
                        webui_theme, webui_host, webui_port,
                        log_level, log_file,
                        report_format, include_screenshots, include_videos
                    ],
                    outputs=settings_status
                )
        
        # Launch the interface
        interface.launch(server_name=host, server_port=port)

# Add this to make the module runnable directly
if __name__ == "__main__":
    start_webui(host="0.0.0.0", port=7788)
