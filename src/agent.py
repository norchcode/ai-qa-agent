"""
Core Agent module for AI QA Agent.
This module integrates all components of the AI QA agent.
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import tempfile
import datetime

from llm_integration import get_llm_integration
from test_analyzer import TestCaseAnalyzer, GherkinTranslator
from visual_testing import VisualTesting
from utils.logger import setup_logger

logger = logging.getLogger(__name__)

class AIQAAgent:
    """Main AI QA Agent that integrates all components."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI QA Agent.
        
        Args:
            config: Optional configuration dictionary. If not provided, will use environment variables.
        """
        self.config = config or {}
        
        # Set up logging
        log_level = self.config.get('log_level', os.getenv('LOG_LEVEL', 'INFO'))
        log_file = self.config.get('log_file', os.getenv('LOG_FILE', './logs/ai_qa_agent.log'))
        setup_logger(log_level, log_file)
        
        # Initialize LLM provider
        llm_provider = self.config.get('llm_provider', os.getenv('LLM_PROVIDER', 'groq'))
        logger.info(f"Initializing AI QA Agent with LLM provider: {llm_provider}")
        
        # Initialize components
        self.llm = get_llm_integration(llm_provider)
        self.test_analyzer = TestCaseAnalyzer(llm_provider)
        self.visual_testing = VisualTesting(llm_provider)
        self.gherkin_translator = GherkinTranslator(llm_provider)
        
        # Initialize test results storage
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'visual_bugs': [],
            'ui_ux_issues': [],
            'root_cause_analysis': {},
            'screenshots': []
        }
        
        logger.info("AI QA Agent initialized successfully")
    
    def run_tests(self, test_file_path: str) -> Dict[str, Any]:
        """
        Run tests from a test file.
        
        Args:
            test_file_path: Path to the test file or directory.
            
        Returns:
            Dictionary containing test results.
        """
        logger.info(f"Running tests from: {test_file_path}")
        
        # Reset test results
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'visual_bugs': [],
            'ui_ux_issues': [],
            'root_cause_analysis': {},
            'screenshots': []
        }
        
        # Check if the file exists
        if not os.path.exists(test_file_path):
            logger.error(f"Test file not found: {test_file_path}")
            return {"error": f"Test file not found: {test_file_path}"}
        
        # Determine if it's a file or directory
        if os.path.isdir(test_file_path):
            return self._run_tests_from_directory(test_file_path)
        else:
            return self._run_test_file(test_file_path)
    
    def _run_tests_from_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Run tests from all files in a directory.
        
        Args:
            directory_path: Path to the directory containing test files.
            
        Returns:
            Dictionary containing test results.
        """
        logger.info(f"Running tests from directory: {directory_path}")
        
        # Find all test files in the directory
        test_files = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.feature'):
                    test_files.append(os.path.join(root, file))
        
        if not test_files:
            logger.warning(f"No test files found in directory: {directory_path}")
            return {"error": f"No test files found in directory: {directory_path}"}
        
        # Run each test file
        for test_file in test_files:
            self._run_test_file(test_file)
        
        # Generate a report
        report_path = self._generate_report()
        
        return {
            **self.test_results,
            'report_path': report_path
        }
    
    def _run_test_file(self, file_path: str) -> Dict[str, Any]:
        """
        Run tests from a single test file.
        
        Args:
            file_path: Path to the test file.
            
        Returns:
            Dictionary containing test results.
        """
        logger.info(f"Running test file: {file_path}")
        
        try:
            # Read the test file
            with open(file_path, 'r') as f:
                test_content = f.read()
            
            # Analyze the test case
            analysis = self.test_analyzer.analyze_test_case(test_content)
            
            # Determine if we should run the test or just analyze it
            if self.config.get('analyze_only', False):
                logger.info(f"Analysis only mode, not executing test: {file_path}")
                self.test_results['total_tests'] += 1
                
                # Add analysis to results
                if 'test_analysis' not in self.test_results:
                    self.test_results['test_analysis'] = {}
                self.test_results['test_analysis'][file_path] = analysis
                
                return {
                    'file_path': file_path,
                    'analysis': analysis,
                    'status': 'analyzed'
                }
            
            # Execute the test using TestZeus Hercules
            execution_results = self._execute_test_with_hercules(file_path)
            
            # Update test results
            self.test_results['total_tests'] += 1
            if execution_results.get('status') == 'passed':
                self.test_results['passed_tests'] += 1
            else:
                self.test_results['failed_tests'] += 1
            
            # Analyze screenshots for visual bugs
            screenshots = execution_results.get('screenshots', [])
            for screenshot in screenshots:
                self.test_results['screenshots'].append(screenshot)
                
                # Analyze the screenshot for visual bugs
                visual_analysis = self.visual_testing.analyze_screenshot(screenshot)
                if 'visual_bugs' in visual_analysis:
                    self.test_results['visual_bugs'].extend(visual_analysis['visual_bugs'])
                
                # Analyze UI/UX issues
                ui_ux_analysis = self.visual_testing.analyze_ui_ux_issues(
                    screenshot, execution_results.get('steps', [])
                )
                if 'ui_ux_issues' in ui_ux_analysis:
                    self.test_results['ui_ux_issues'].extend(ui_ux_analysis['ui_ux_issues'])
            
            # If the test failed, analyze the error
            if execution_results.get('status') == 'failed':
                error_message = execution_results.get('error_message', '')
                failed_step = execution_results.get('failed_step', '')
                screenshot = execution_results.get('error_screenshot', '')
                
                # Analyze the error
                error_analysis = self.test_analyzer.analyze_error(error_message, failed_step, screenshot)
                
                # Find root cause
                root_cause = self.visual_testing.find_root_cause(
                    f"Test failed at step: {failed_step}", screenshot, error_message
                )
                
                # Suggest alternative steps
                alternative_steps = self.test_analyzer.suggest_alternative_steps(failed_step, error_message)
                
                # Add to results
                if 'error_analysis' not in self.test_results:
                    self.test_results['error_analysis'] = {}
                self.test_results['error_analysis'][file_path] = error_analysis
                
                if 'root_cause_analysis' not in self.test_results:
                    self.test_results['root_cause_analysis'] = {}
                self.test_results['root_cause_analysis'][file_path] = root_cause
                
                if 'alternative_steps' not in self.test_results:
                    self.test_results['alternative_steps'] = {}
                self.test_results['alternative_steps'][file_path] = alternative_steps
            
            # Suggest improvements for the test case
            improvements = self.test_analyzer.suggest_improvements(test_content, execution_results)
            
            if 'improvements' not in self.test_results:
                self.test_results['improvements'] = {}
            self.test_results['improvements'][file_path] = improvements
            
            return {
                'file_path': file_path,
                'execution_results': execution_results,
                'analysis': analysis,
                'improvements': improvements,
                'status': execution_results.get('status', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error running test file {file_path}: {e}", exc_info=True)
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            
            return {
                'file_path': file_path,
                'error': str(e),
                'status': 'error'
            }
    
    def _execute_test_with_hercules(self, file_path: str) -> Dict[str, Any]:
        """
        Execute a test file using TestZeus Hercules.
        
        Args:
            file_path: Path to the test file.
            
        Returns:
            Dictionary containing execution results.
        """
        logger.info(f"Executing test with Hercules: {file_path}")
        
        try:
            # In a real implementation, we would use the testzeus-hercules package to execute the test
            # For now, we'll use a placeholder implementation that simulates test execution
            
            # Create output directory
            output_dir = self.config.get('output_dir', os.getenv('HERCULES_OUTPUT_PATH', './test_results'))
            os.makedirs(output_dir, exist_ok=True)
            
            # Create a temporary directory for screenshots
            screenshots_dir = os.path.join(output_dir, 'screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Simulate test execution
            # In a real implementation, this would call the testzeus-hercules API
            
            # For demonstration purposes, we'll simulate a successful test execution
            # In a real implementation, this would be the actual test result
            
            # Read the test file to extract steps
            with open(file_path, 'r') as f:
                test_content = f.read()
            
            # Parse the test content to extract steps
            steps = []
            for line in test_content.split('\n'):
                line = line.strip()
                if line.startswith('Given ') or line.startswith('When ') or line.startswith('Then ') or \
                   line.startswith('And ') or line.startswith('But '):
                    steps.append(line)
            
            # Simulate screenshots
            screenshots = []
            for i in range(min(3, len(steps))):
                # In a real implementation, these would be actual screenshots
                screenshot_path = os.path.join(screenshots_dir, f"step_{i+1}.png")
                
                # Create an empty file as a placeholder
                with open(screenshot_path, 'w') as f:
                    f.write(f"Placeholder for screenshot of step: {steps[i]}")
                
                screenshots.append(screenshot_path)
            
            # Simulate test result
            # In a real implementation, this would be determined by the actual test execution
            status = 'passed'  # or 'failed'
            
            # If we want to simulate a failure for testing
            if self.config.get('simulate_failure', False):
                status = 'failed'
                error_message = "Element not found: button[text='Submit']"
                failed_step = steps[-1] if steps else "Unknown step"
                error_screenshot = screenshots[-1] if screenshots else None
            else:
                error_message = None
                failed_step = None
                error_screenshot = None
            
            return {
                'status': status,
                'steps': steps,
                'screenshots': screenshots,
                'error_message': error_message,
                'failed_step': failed_step,
                'error_screenshot': error_screenshot
            }
            
        except Exception as e:
            logger.error(f"Error executing test with Hercules: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def analyze_test_case(self, test_case: str) -> Dict[str, Any]:
        """
        Analyze a test case without executing it.
        
        Args:
            test_case: The test case to analyze, in Gherkin format.
            
        Returns:
            Dictionary containing analysis results.
        """
        logger.info("Analyzing test case")
        
        return self.test_analyzer.analyze_test_case(test_case)
    
    def optimize_test_case(self, test_case: str) -> str:
        """
        Optimize a test case based on analysis.
        
        Args:
            test_case: The test case to optimize, in Gherkin format.
            
        Returns:
            Optimized test case in Gherkin format.
        """
        logger.info("Optimizing test case")
        
        return self.test_analyzer.optimize_test_case(test_case)
    
    def analyze_screenshot(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Analyze a screenshot for visual bugs.
        
        Args:
            screenshot_path: Path to the screenshot image.
            
        Returns:
            Dictionary containing analysis results.
        """
        logger.info(f"Analyzing screenshot: {screenshot_path}")
        
        return self.visual_testing.analyze_screenshot(screenshot_path)
    
    def find_root_cause(self, bug_description: str, screenshot_path: Optional[str] = None,
                       error_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Find the root cause of a bug and suggest fixes.
        
        Args:
            bug_description: Description of the bug.
            screenshot_path: Optional path to a screenshot showing the bug.
            error_message: Optional error message associated with the bug.
            
        Returns:
            Dictionary containing root cause analysis and fix suggestions.
        """
        logger.info(f"Finding root cause for bug: {bug_description}")
        
        return self.visual_testing.find_root_cause(bug_description, screenshot_path, error_message)
    
    def translate_to_gherkin(self, test_steps: str) -> str:
        """
        Translate natural language test steps into Gherkin format.
        
        Args:
            test_steps: Natural language test steps, one per line.
            
        Returns:
            Test steps in Gherkin format.
        """
        logger.info("Translating test steps to Gherkin format")
        
        return self.gherkin_translator.translate_to_gherkin(test_steps)
    
    def translate_from_gherkin(self, gherkin_text: str) -> str:
        """
        Translate Gherkin format into natural language test steps.
        
        Args:
            gherkin_text: Test steps in Gherkin f
(Content truncated due to size limit. Use line ranges to read in chunks)