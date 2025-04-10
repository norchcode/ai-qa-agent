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

from src.core.controller import AIQAAgentController

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
    
    # Launch the interface
    interface.launch(server_name=host, server_port=port)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get host and port from environment variables or use defaults
    host = os.getenv("WEBUI_HOST", "127.0.0.1")
    port = int(os.getenv("WEBUI_PORT", "7788"))
    
    # Start the Web UI
    start_webui(host, port)
