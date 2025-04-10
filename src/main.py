"""
Main entry point for the AI QA Agent.
"""
import os
import sys
import argparse
import logging
from dotenv import load_dotenv

from .core.agent import AIQAAgent
from .utils.logger import setup_logger
from .ui.webui_enhanced import start_webui

def main():
    """Main entry point for the AI QA Agent."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI QA Agent')
    parser.add_argument('--webui', action='store_true', help='Start the Web UI')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind the Web UI to')
    parser.add_argument('--port', type=int, default=7788, help='Port to bind the Web UI to')
    parser.add_argument('--test-file', type=str, help='Path to test file or directory to run')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze test cases, do not execute them')
    parser.add_argument('--report-format', type=str, choices=['pdf', 'html', 'json'], default='pdf', help='Report format')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Logging level')
    parser.add_argument('--log-file', type=str, default='./logs/ai_qa_agent.log', help='Log file path')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    args = parser.parse_args()
    
    # Set up logging
    setup_logger(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    logger.info("Starting AI QA Agent")
    
    # Load configuration
    config = {}
    if args.config:
        import json
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.error(f"Error loading configuration from {args.config}: {e}")
            sys.exit(1)
    
    # Update configuration with command line arguments
    config.update({
        'analyze_only': args.analyze_only,
        'report_format': args.report_format,
        'log_level': args.log_level,
        'log_file': args.log_file
    })
    
    # Initialize the AI QA Agent
    agent = AIQAAgent(config)
    
    # Run tests if a test file is provided
    if args.test_file:
        logger.info(f"Running tests from {args.test_file}")
        results = agent.run_tests(args.test_file)
        print(f"Test Results: {results}")
    
    # Start the Web UI if requested
    if args.webui:
        logger.info(f"Starting Web UI on {args.host}:{args.port}")
        start_webui(agent, args.host, args.port)
    
    # If no action is specified, start the Web UI by default
    if not args.test_file and not args.webui:
        logger.info(f"No action specified, starting Web UI on {args.host}:{args.port}")
        start_webui(agent, args.host, args.port)

if __name__ == '__main__':
    main()
