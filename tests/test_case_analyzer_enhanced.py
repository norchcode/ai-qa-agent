"""
Enhanced Test Case Analyzer module for AI QA Agent.
This module provides advanced functionality for analyzing and improving test cases.
"""
import os
import logging
import json
import re
import math
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import xml.etree.ElementTree as ET
import numpy as np
from collections import defaultdict

from llm_integration import get_llm_integration

logger = logging.getLogger(__name__)

class TestCaseMetrics:
    """Class for calculating detailed test case metrics."""
    
    def __init__(self):
        """Initialize the TestCaseMetrics class."""
        pass
    
    def calculate_complexity(self, parsed_test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate complexity metrics for a test case.
        
        Args:
            parsed_test_case: The parsed test case structure.
            
        Returns:
            Dictionary containing complexity metrics.
        """
        metrics = {}
        
        # Count total scenarios
        scenarios = parsed_test_case.get('scenarios', [])
        metrics['total_scenarios'] = len(scenarios)
        
        # Count scenario outlines separately
        metrics['scenario_outlines'] = sum(1 for s in scenarios if s.get('type') == 'outline')
        metrics['regular_scenarios'] = metrics['total_scenarios'] - metrics['scenario_outlines']
        
        # Count steps by type
        total_steps = 0
        given_steps = 0
        when_steps = 0
        then_steps = 0
        and_but_steps = 0
        
        for scenario in scenarios:
            given_steps += len(scenario.get('given', []))
            when_steps += len(scenario.get('when', []))
            then_steps += len(scenario.get('then', []))
            and_but_steps += len(scenario.get('and', [])) + len(scenario.get('but', []))
        
        total_steps = given_steps + when_steps + then_steps + and_but_steps
        
        metrics['total_steps'] = total_steps
        metrics['given_steps'] = given_steps
        metrics['when_steps'] = when_steps
        metrics['then_steps'] = then_steps
        metrics['and_but_steps'] = and_but_steps
        
        # Calculate average steps per scenario
        metrics['avg_steps_per_scenario'] = total_steps / max(1, metrics['total_scenarios'])
        
        # Calculate step distribution
        if total_steps > 0:
            metrics['given_steps_percentage'] = (given_steps / total_steps) * 100
            metrics['when_steps_percentage'] = (when_steps / total_steps) * 100
            metrics['then_steps_percentage'] = (then_steps / total_steps) * 100
            metrics['and_but_steps_percentage'] = (and_but_steps / total_steps) * 100
        else:
            metrics['given_steps_percentage'] = 0
            metrics['when_steps_percentage'] = 0
            metrics['then_steps_percentage'] = 0
            metrics['and_but_steps_percentage'] = 0
        
        # Calculate cyclomatic complexity (based on decision points)
        cyclomatic_complexity = 1  # Base complexity
        
        # Add complexity for scenario outlines (each example row adds a path)
        for scenario in scenarios:
            if scenario.get('type') == 'outline':
                example_rows = [row for row in scenario.get('examples', []) if '|' in row]
                # First row is usually header, so subtract 1 if there are multiple rows
                if len(example_rows) > 1:
                    cyclomatic_complexity += len(example_rows) - 1
        
        # Add complexity for conditional steps (containing "if" or "depending on")
        for scenario in scenarios:
            for step_type in ['given', 'when', 'then', 'and', 'but']:
                for step in scenario.get(step_type, []):
                    if re.search(r'\b(if|depending on|based on|when)\b', step, re.IGNORECASE):
                        cyclomatic_complexity += 1
        
        metrics['cyclomatic_complexity'] = cyclomatic_complexity
        
        # Calculate cognitive complexity (based on nesting and logical operations)
        cognitive_complexity = 0
        
        # Add complexity for nested steps and logical operations
        for scenario in scenarios:
            # Add base complexity for each scenario
            cognitive_complexity += 1
            
            # Check for nested conditions in steps
            for step_type in ['given', 'when', 'then', 'and', 'but']:
                for step in scenario.get(step_type, []):
                    # Add complexity for logical operations
                    cognitive_complexity += step.lower().count(' and ') + step.lower().count(' or ')
                    
                    # Add complexity for nested conditions
                    if re.search(r'\b(if|depending on|based on|when)\b', step, re.IGNORECASE):
                        cognitive_complexity += 2
        
        metrics['cognitive_complexity'] = cognitive_complexity
        
        # Calculate maintainability index
        # Simplified version of the maintainability index formula
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(L)
        # where V is Halstead Volume, G is cyclomatic complexity, and L is lines of code
        # We'll use a simplified version based on our available metrics
        
        # Use total steps as a proxy for lines of code
        lines_of_code = total_steps
        
        # Use cyclomatic complexity as is
        cyclo = cyclomatic_complexity
        
        # Calculate a simplified maintainability index
        if lines_of_code > 0:
            maintainability_index = 171 - 0.23 * cyclo - 16.2 * math.log(lines_of_code)
            # Normalize to 0-100 scale
            maintainability_index = max(0, min(100, maintainability_index))
        else:
            maintainability_index = 100
        
        metrics['maintainability_index'] = maintainability_index
        
        return metrics
    
    def calculate_quality_metrics(self, parsed_test_case: Dict[str, Any], rule_based_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate quality metrics for a test case.
        
        Args:
            parsed_test_case: The parsed test case structure.
            rule_based_analysis: The rule-based analysis results.
            
        Returns:
            Dictionary containing quality metrics.
        """
        metrics = {}
        
        # Count issues and warnings
        metrics['total_issues'] = len(rule_based_analysis.get('issues', []))
        metrics['total_warnings'] = len(rule_based_analysis.get('warnings', []))
        
        # Calculate issue density (issues per scenario)
        scenarios = parsed_test_case.get('scenarios', [])
        if scenarios:
            metrics['issue_density'] = metrics['total_issues'] / len(scenarios)
            metrics['warning_density'] = metrics['total_warnings'] / len(scenarios)
        else:
            metrics['issue_density'] = 0
            metrics['warning_density'] = 0
        
        # Check for assertion coverage
        total_then_steps = 0
        then_steps_with_assertions = 0
        
        for scenario in scenarios:
            then_steps = scenario.get('then', [])
            total_then_steps += len(then_steps)
            
            for step in then_steps:
                if any(word in step.lower() for word in ['should', 'expect', 'verify', 'check', 'assert', 'validate', 'confirm']):
                    then_steps_with_assertions += 1
        
        if total_then_steps > 0:
            metrics['assertion_coverage'] = (then_steps_with_assertions / total_then_steps) * 100
        else:
            metrics['assertion_coverage'] = 0
        
        # Check for locator usage
        total_steps = 0
        steps_with_locators = 0
        
        for scenario in scenarios:
            for step_type in ['given', 'when', 'then', 'and', 'but']:
                steps = scenario.get(step_type, [])
                total_steps += len(steps)
                
                for step in steps:
                    if re.search(r'(id|class|xpath|css|selector)=[\'"]', step, re.IGNORECASE):
                        steps_with_locators += 1
        
        if total_steps > 0:
            metrics['locator_usage'] = (steps_with_locators / total_steps) * 100
        else:
            metrics['locator_usage'] = 0
        
        # Calculate overall quality score (0-100)
        # This is a weighted score based on various factors
        
        # Start with a perfect score and subtract for issues
        quality_score = 100
        
        # Subtract for issues and warnings
        quality_score -= metrics['total_issues'] * 5  # Each issue reduces score by 5 points
        quality_score -= metrics['total_warnings'] * 2  # Each warning reduces score by 2 points
        
        # Adjust for assertion coverage
        if metrics['assertion_coverage'] < 100:
            quality_score -= (100 - metrics['assertion_coverage']) * 0.2
        
        # Adjust for locator usage (high locator usage is bad for maintainability)
        if metrics['locator_usage'] > 0:
            quality_score -= metrics['locator_usage'] * 0.1
        
        # Ensure score is between 0 and 100
        quality_score = max(0, min(100, quality_score))
        
        metrics['quality_score'] = quality_score
        
        return metrics
    
    def calculate_coverage_metrics(self, parsed_test_case: Dict[str, Any], coverage_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate coverage metrics for a test case.
        
        Args:
            parsed_test_case: The parsed test case structure.
            coverage_data: Optional code coverage data.
            
        Returns:
            Dictionary containing coverage metrics.
        """
        metrics = {}
        
        if coverage_data:
            # Use provided coverage data
            metrics['line_coverage'] = coverage_data.get('line_coverage', 0)
            metrics['branch_coverage'] = coverage_data.get('branch_coverage', 0)
            metrics['function_coverage'] = coverage_data.get('function_coverage', 0)
            metrics['statement_coverage'] = coverage_data.get('statement_coverage', 0)
        else:
            # No coverage data available
            metrics['line_coverage'] = None
            metrics['branch_coverage'] = None
            metrics['function_coverage'] = None
            metrics['statement_coverage'] = None
        
        # Calculate feature coverage based on the test case itself
        # This is an estimate of how well the test case covers the feature it's testing
        
        # Check if the test case has a good structure
        has_feature_description = bool(parsed_test_case.get('feature', ''))
        
        scenarios = parsed_test_case.get('scenarios', [])
        has_multiple_scenarios = len(scenarios) > 1
        
        # Check for different types of scenarios (happy path, edge cases, error cases)
        scenario_types = {
            'happy_path': 0,
            'edge_case': 0,
            'error_case': 0
        }
        
        for scenario in scenarios:
            title = scenario.get('title', '').lower()
            
            # Classify scenario types based on keywords in title
            if any(word in title for word in ['invalid', 'error', 'fail', 'negative', 'exception']):
                scenario_types['error_case'] += 1
            elif any(word in title for word in ['edge', 'boundary', 'limit', 'max', 'min', 'empty', 'null']):
                scenario_types['edge_case'] += 1
            else:
                scenario_types['happy_path'] += 1
        
        metrics['scenario_types'] = scenario_types
        
        # Calculate feature coverage score
        feature_coverage = 0
        
        # Start with base points
        if has_feature_description:
            feature_coverage += 10
        
        if has_multiple_scenarios:
            feature_coverage += 10
        
        # Add points for different scenario types
        if scenario_types['happy_path'] > 0:
            feature_coverage += 30  # Happy path is essential
        
        if scenario_types['edge_case'] > 0:
            feature_coverage += 25  # Edge cases are important
        
        if scenario_types['error_case'] > 0:
            feature_coverage += 25  # Error cases are important
        
        # Normalize to 0-100
        feature_coverage = min(100, feature_coverage)
        
        metrics['feature_coverage'] = feature_coverage
        
        return metrics


class CodeCoverageAnalyzer:
    """Class for analyzing code coverage data."""
    
    def __init__(self):
        """Initialize the CodeCoverageAnalyzer class."""
        pass
    
    def parse_coverage_xml(self, xml_path: str) -> Dict[str, Any]:
        """
        Parse code coverage data from a Cobertura XML file.
        
        Args:
            xml_path: Path to the Cobertura XML file.
            
        Returns:
            Dictionary containing parsed coverage data.
        """
        if not os.path.exists(xml_path):
            logger.warning(f"Coverage XML file not found: {xml_path}")
            return {}
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            coverage_data = {}
            
            # Get overall coverage metrics
            if 'line-rate' in root.attrib:
                coverage_data['line_coverage'] = float(root.attrib['line-rate']) * 100
            
            if 'branch-rate' in root.attrib:
                coverage_data['branch_coverage'] = float(root.attrib['branch-rate']) * 100
            
            # Parse package data
            packages = {}
            for package in root.findall('.//package'):
                package_name = package.attrib.get('name', '')
                
                package_data = {
                    'line_coverage': float(package.attrib.get('line-rate', 0)) * 100,
                    'branch_coverage': float(package.attrib.get('branch-rate', 0)) * 100,
                    'classes': {}
                }
                
                # Parse class data
                for class_elem in package.findall('.//class'):
                    class_name = class_elem.attrib.get('name', '')
                    
                    class_data = {
                        'line_coverage': float(class_elem.attrib.get('line-rate', 0)) * 100,
                        'branch_coverage': float(class_elem.attrib.get('branch-rate', 0)) * 100,
                        'methods': {}
                    }
                    
                    # Parse method data
                    for method in class_elem.findall('.//method'):
                        method_name = method.attrib.get('name', '')
                        
                        method_data = {
                            'line_coverage': float(method.attrib.get('line-rate', 0)) * 100,
                            'branch_coverage': float(method.attrib.get('branch-rate', 0)) * 100
                        }
                        
                        class_data['methods'][method_name] = method_data
                    
                    package_data['classes'][class_name] = class_data
                
                packages[package_name] = package_data
            
            coverage_data['packages'] = packages
            
            return coverage_data
        
        except Exception as e:
            logger.error(f"Error parsing coverage XML: {e}")
            return {}
    
    def parse_coverage_json(self, json_path: str) -> Dict[str, Any]:
        """
        Parse code coverage data from a JSON file (e.g., Istanbul/NYC format).
        
        Args:
            json_path: Path to the JSON coverage file.
            
        Returns:
            Dictionary containing parsed coverage data.
        """
        if not os.path.exists(json_path):
            logger.warning(f"Coverage JSON file not found: {json_path}")
            return {}
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            coverage_data = {}
            
            # Extract overall metrics if available
            if 'total' in data:
                total = data['total']
                
                if 'lines' in total:
                    coverage_data['line_coverage'] = total['lines']['pct']
                
                if 'branches' in total:
                    coverage_data['branch_coverage'] = total['branches']['pct']
                
                if 'functions' in total:
                    coverage_data['function_coverage'] = total['functions']['pct']
                
                if 'statements' in total:
                    coverage_data['statement_coverage'] = total['statements']['pct']
            
            # Parse file-specific data
            files = {}
            for file_path, file_data in data.items():
                if file_path == 'total':
                    continue
                
                file_coverage = {}
                
                if 'lines' in file_data:
                    file_coverage['line_coverage'] = file_data['lines']['pct']
                
                if 'branches' in file_data:
                    file_coverage['branch_coverage'] = file_data['branches']['pct']
                
                if 'functions' in file_data:
                    file_coverage['function_coverage'] = file_data['functions']['pct']
                
                if 'statements' in file_data:
                    file_coverage['statement_coverage'] = file_data['statements']['pct']
                
                files[file_path] = file_coverage
            
            coverage_data['files'] = files
            
            return coverage_data
        
        except Exception as e:
            logger.error(f"Error parsing coverage JSON: {e}")
            return {}
    
    def analyze_coverage(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code coverage data to identify areas for improvement.
        
        Args:
            coverage_data: Parsed coverage data.
            
        Returns:
            Dictionary containing analysis results.
        """
        analysis = {
            'overall_assessment': '',
            'low_coverage_areas': [],
            'uncovered_areas': [],
            'recommendations': []
        }
        
        # Assess overall coverage
        line_coverage = coverage_data.get('line_coverage')
        branch_coverage = coverage_data.get('branch_coverage')
        function_coverage = coverage_data.get('function_coverage')
        statement_coverage = coverage_data.get('statement_coverage')
        
        if line_coverage is not None:
            if line_coverage >= 80:
                analysis['overall_assessment'] = 'Good overall line coverage (≥80%)'
            elif line_coverage >= 60:
                analysis['overall_assessment'] = 'Moderate overall line coverage (60-80%)'
            else:
                analysis['overall_assessment'] = 'Poor overall line coverage (<60%)'
        
        # Identify low coverage areas
        if 'packages' in coverage_data:
            for package_name, package_data in coverage_data['packages'].items():
                package_line_coverage = package_data.get('line_coverage', 0)
                
                if package_line_coverage < 60:
                    analysis['low_coverage_areas'].append(f"Package '{package_name}' has low line coverage: {package_line_coverage:.1f}%")
                
                for class_name, class_data in package_data.get('classes', {}).items():
                    class_line_coverage = class_data.get('line_coverage', 0)
                    
                    if class_line_coverage < 60:
                        analysis['low_coverage_areas'].append(f"Class '{class_name}' has low line coverage: {class_line_coverage:.1f}%")
                    
                    for method_name, method_data in class_data.get('methods', {}).items():
                        method_line_coverage = method_data.get('line_coverage', 0)
                        
                        if method_line_coverage == 0:
                            analysis['uncovered_areas'].append(f"Method '{method_name}' in class '{class_name}' is not covered")
                        elif method_line_coverage < 50:
                            analysis['low_coverage_areas'].append(f"Method '{method_name}' in class '{class_name}' has low line coverage: {method_line_coverage:.1f}%")
        
        elif 'files' in coverage_data:
            for file_path, file_data in coverage_data.get('files', {}).items():
                file_line_coverage = file_data.get('line_coverage', 0)
                
                if file_line_coverage == 0:
                    analysis['uncovered_areas'].append(f"File '{file_path}' is not covered")
                elif file_line_coverage < 60:
                    analysis['low_coverage_areas'].append(f"File '{file_path}' has low line coverage: {file_line_coverage:.1f}%")
        
        # Generate recommendations
        if line_coverage is not None and line_coverage < 80:
            analysis['recommendations'].append("Increase overall line coverage to at least 80%")
        
        if branch_coverage is not None and branch_coverage < 70:
            analysis['recommendations'].append("Improve branch coverage to ensure all code paths are tested")
        
        if function_coverage is not None and function_coverage < 90:
            analysis['recommendations'].append("Ensure all functions have at least one test")
        
        if analysis['uncovered_areas']:
            analysis['recommendations'].append("Add tests for completely uncovered areas")
        
        if analysis['low_coverage_areas']:
            analysis['recommendations'].append("Focus on improving coverage in areas with low coverage")
        
        return analysis
    
    def suggest_test_cases(self, coverage_data: Dict[str, Any], source_code: Optional[str] = None) -> List[str]:
        """
        Suggest test cases to improve code coverage.
        
        Args:
            coverage_data: Parsed coverage data.
            source_code: Optional source code to analyze.
            
        Returns:
            List of suggested test cases.
        """
        suggestions = []
        
        # Identify uncovered areas
        uncovered_areas = []
        
        if 'packages' in coverage_data:
            for package_name, package_data in coverage_data['packages'].items():
                for class_name, class_data in package_data.get('classes', {}).items():
                    for method_name, method_data in class_data.get('methods', {}).items():
                        method_line_coverage = method_data.get('line_coverage', 0)
                        
                        if method_line_coverage == 0:
                            uncovered_areas.append({
                                'type': 'method',
                                'name': method_name,
                                'class': class_name,
                                'package': package_name
                            })
        
        elif 'files' in coverage_data:
            for file_path, file_data in coverage_data.get('files', {}).items():
                file_line_coverage = file_data.get('line_coverage', 0)
                
                if file_line_coverage == 0:
                    uncovered_areas.append({
                        'type': 'file',
                        'name': file_path
                    })
        
        # Generate suggestions for uncovered areas
        for area in uncovered_areas:
            if area['type'] == 'method':
                suggestions.append(f"Create a test for method '{area['name']}' in class '{area['class']}'")
            elif area['type'] == 'file':
                suggestions.append(f"Create tests for file '{area['name']}'")
        
        # If source code is provided, analyze it for additional suggestions
        if source_code and not suggestions:
            # This would involve more complex analysis of the source code
            # For now, we'll just provide a generic suggestion
            suggestions.append("Analyze the source code to identify edge cases and error conditions that need testing")
        
        return suggestions


class RiskAssessment:
    """Class for assessing risk and prioritizing test cases."""
    
    def __init__(self):
        """Initialize the RiskAssessment class."""
        pass
    
    def assess_risk(self, test_case: Dict[str, Any], execution_history: Optional[List[Dict[str, Any]]] = None, 
                   code_changes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assess the risk level of a test case.
        
        Args:
            test_case: The test case data.
            execution_history: Optional list of previous execution results.
            code_changes: Optional information about recent code changes.
            
        Returns:
            Dictionary containing risk assessment results.
        """
        risk_factors = {}
        
        # Assess risk based on test case complexity
        complexity = test_case.get('complexity', {})
        cyclomatic_complexity = complexity.get('cyclomatic_complexity', 0)
        cognitive_complexity = complexity.get('cognitive_complexity', 0)
        
        if cyclomatic_complexity > 10 or cognitive_complexity > 15:
            risk_factors['complexity'] = 'high'
        elif cyclomatic_complexity > 5 or cognitive_complexity > 10:
            risk_factors['complexity'] = 'medium'
        else:
            risk_factors['complexity'] = 'low'
        
        # Assess risk based on test case quality
        quality = test_case.get('quality', {})
        quality_score = quality.get('quality_score', 0)
        
        if quality_score < 60:
            risk_factors['quality'] = 'high'
        elif quality_score < 80:
            risk_factors['quality'] = 'medium'
        else:
            risk_factors['quality'] = 'low'
        
        # Assess risk based on execution history
        if execution_history:
            # Calculate failure rate
            total_executions = len(execution_history)
            failed_executions = sum(1 for result in execution_history if result.get('status') == 'FAIL')
            
            if total_executions > 0:
                failure_rate = (failed_executions / total_executions) * 100
                
                if failure_rate > 20:
                    risk_factors['failure_history'] = 'high'
                elif failure_rate > 5:
                    risk_factors['failure_history'] = 'medium'
                else:
                    risk_factors['failure_history'] = 'low'
                
                # Check for recent failures
                recent_executions = execution_history[-3:]  # Last 3 executions
                recent_failures = sum(1 for result in recent_executions if result.get('status') == 'FAIL')
                
                if recent_failures > 0:
                    risk_factors['recent_failures'] = 'high'
                else:
                    risk_factors['recent_failures'] = 'low'
            else:
                risk_factors['failure_history'] = 'unknown'
                risk_factors['recent_failures'] = 'unknown'
        else:
            risk_factors['failure_history'] = 'unknown'
            risk_factors['recent_failures'] = 'unknown'
        
        # Assess risk based on code changes
        if code_changes:
            # Check if the test case is affected by recent changes
            affected_by_changes = code_changes.get('affects_test_case', False)
            change_magnitude = code_changes.get('magnitude', 'small')
            
            if affected_by_changes:
                if change_magnitude == 'large':
                    risk_factors['code_changes'] = 'high'
                elif change_magnitude == 'medium':
                    risk_factors['code_changes'] = 'medium'
                else:
                    risk_factors['code_changes'] = 'low'
            else:
                risk_factors['code_changes'] = 'low'
        else:
            risk_factors['code_changes'] = 'unknown'
        
        # Calculate overall risk level
        risk_levels = {
            'high': 3,
            'medium': 2,
            'low': 1,
            'unknown': 1.5  # Assign a middle value to unknown factors
        }
        
        risk_scores = [risk_levels[level] for level in risk_factors.values()]
        avg_risk_score = sum(risk_scores) / len(risk_scores)
        
        if avg_risk_score > 2.5:
            overall_risk = 'high'
        elif avg_risk_score > 1.5:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        return {
            'risk_factors': risk_factors,
            'overall_risk': overall_risk,
            'risk_score': avg_risk_score
        }
    
    def prioritize_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize test cases based on risk assessment.
        
        Args:
            test_cases: List of test cases with risk assessments.
            
        Returns:
            Prioritized list of test cases.
        """
        # Define priority scores for risk levels
        risk_priority = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        # Calculate priority score for each test case
        for test_case in test_cases:
            risk_assessment = test_case.get('risk_assessment', {})
            overall_risk = risk_assessment.get('overall_risk', 'low')
            
            # Base priority on overall risk
            priority_score = risk_priority.get(overall_risk, 1)
            
            # Adjust priority based on additional factors
            
            # Increase priority for critical functionality
            if test_case.get('is_critical', False):
                priority_score += 2
            
            # Increase priority for customer-facing functionality
            if test_case.get('is_customer_facing', False):
                priority_score += 1
            
            # Increase priority for recently changed code
            risk_factors = risk_assessment.get('risk_factors', {})
            if risk_factors.get('code_changes') == 'high':
                priority_score += 2
            elif risk_factors.get('code_changes') == 'medium':
                priority_score += 1
            
            # Increase priority for tests with recent failures
            if risk_factors.get('recent_failures') == 'high':
                priority_score += 2
            
            # Store the priority score
            test_case['priority_score'] = priority_score
            
            # Assign priority level based on score
            if priority_score >= 6:
                test_case['priority'] = 'critical'
            elif priority_score >= 4:
                test_case['priority'] = 'high'
            elif priority_score >= 2:
                test_case['priority'] = 'medium'
            else:
                test_case['priority'] = 'low'
        
        # Sort test cases by priority score (descending)
        prioritized_test_cases = sorted(test_cases, key=lambda x: x.get('priority_score', 0), reverse=True)
        
        return prioritized_test_cases
    
    def generate_test_plan(self, prioritized_test_cases: List[Dict[str, Any]], time_budget: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate a test execution plan based on prioritized test cases.
        
        Args:
            prioritized_test_cases: Prioritized list of test cases.
            time_budget: Optional time budget in minutes.
            
        Returns:
            Dictionary containing the test execution plan.
        """
        test_plan = {
            'test_cases': [],
            'total_estimated_time': 0,
            'coverage': {}
        }
        
        # Track coverage of features/components
        covered_features = set()
        covered_components = set()
        
        # Track estimated execution time
        total_time = 0
        
        # Add test cases to the plan based on priority
        for test_case in prioritized_test_cases:
            # Check if we've exceeded the time budget
            if time_budget and total_time >= time_budget:
                break
            
            # Get estimated execution time
            estimated_time = test_case.get('estimated_execution_time', 5)  # Default to 5 minutes
            
            # Add test case to the plan
            test_plan['test_cases'].append({
                'id': test_case.get('id'),
                'name': test_case.get('name'),
                'priority': test_case.get('priority'),
                'estimated_time': estimated_time
            })
            
            # Update total time
            total_time += estimated_time
            
            # Update coverage
            if 'feature' in test_case:
                covered_features.add(test_case['feature'])
            
            if 'component' in test_case:
                covered_components.add(test_case['component'])
        
        # Update plan metadata
        test_plan['total_estimated_time'] = total_time
        test_plan['coverage'] = {
            'features': list(covered_features),
            'components': list(covered_components),
            'feature_count': len(covered_features),
            'component_count': len(covered_components)
        }
        
        return test_plan


class EnhancedTestCaseAnalyzer:
    """Enhanced analyzer for test cases with advanced metrics and risk assessment."""
    
    def __init__(self, llm_provider: str = "groq"):
        """
        Initialize the Enhanced Test Case Analyzer.
        
        Args:
            llm_provider: The LLM provider to use for analysis.
        """
        self.llm = get_llm_integration(llm_provider)
        self.metrics_calculator = TestCaseMetrics()
        self.coverage_analyzer = CodeCoverageAnalyzer()
        self.risk_assessor = RiskAssessment()
        
        logger.info(f"Initialized Enhanced Test Case Analyzer with LLM provider: {llm_provider}")
    
    def parse_gherkin(self, gherkin_text: str) -> Dict[str, Any]:
        """
        Parse Gherkin text into a structured format.
        
        Args:
            gherkin_text: The Gherkin text to parse.
            
        Returns:
            Dictionary containing the parsed Gherkin structure.
        """
        result = {
            "feature": "",
            "scenarios": []
        }
        
        current_scenario = None
        current_step_type = None
        
        for line in gherkin_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Feature
            if line.startswith('Feature:'):
                result['feature'] = line[8:].strip()
            
            # Scenario or Scenario Outline
            elif line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                if current_scenario:
                    result['scenarios'].append(current_scenario)
                
                scenario_type = 'outline' if line.startswith('Scenario Outline:') else 'normal'
                title = line[line.index(':') + 1:].strip()
                
                current_scenario = {
                    'title': title,
                    'type': scenario_type,
                    'given': [],
                    'when': [],
                    'then': [],
                    'and': [],
                    'but': [],
                    'examples': []
                }
            
            # Steps
            elif line.startswith('Given '):
                current_step_type = 'given'
                current_scenario[current_step_type].append(line[6:].strip())
            elif line.startswith('When '):
                current_step_type = 'when'
                current_scenario[current_step_type].append(line[5:].strip())
            elif line.startswith('Then '):
                current_step_type = 'then'
                current_scenario[current_step_type].append(line[5:].strip())
            elif line.startswith('And ') and current_step_type:
                current_scenario[current_step_type].append(line[4:].strip())
            elif line.startswith('But ') and current_step_type:
                current_scenario[current_step_type].append(line[4:].strip())
            
            # Examples
            elif line.startswith('Examples:'):
                current_step_type = 'examples'
            elif current_step_type == 'examples' and '|' in line:
                current_scenario['examples'].append(line.strip())
        
        # Add the last scenario
        if current_scenario:
            result['scenarios'].append(current_scenario)
            
        return result
    
    def _rule_based_analysis(self, parsed_test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform rule-based analysis on a parsed test case.
        
        Args:
            parsed_test_case: The parsed test case structure.
            
        Returns:
            Dictionary containing rule-based analysis results.
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check for empty sections
        for scenario in parsed_test_case.get('scenarios', []):
            if not scenario.get('given', []):
                warnings.append(f"Scenario '{scenario['title']}' has no Given steps")
            if not scenario.get('when', []):
                warnings.append(f"Scenario '{scenario['title']}' has no When steps")
            if not scenario.get('then', []):
                issues.append(f"Scenario '{scenario['title']}' has no Then steps (no assertions)")
            
            # Check for scenario outline without examples
            if scenario['type'] == 'outline' and not scenario.get('examples', []):
                issues.append(f"Scenario Outline '{scenario['title']}' has no Examples")
            
            # Check for assertions in Then steps
            for then_step in scenario.get('then', []):
                if not any(word in then_step.lower() for word in ['should', 'expect', 'verify', 'check', 'assert', 'validate', 'confirm']):
                    warnings.append(f"Then step '{then_step}' may not contain an assertion")
            
            # Check for UI locators in steps
            for step_type in ['given', 'when', 'then']:
                for step in scenario.get(step_type, []):
                    if re.search(r'(id|class|xpath|css|selector)=[\'"]', step, re.IGNORECASE):
                        warnings.append(f"Step '{step}' contains hardcoded locators which may be fragile")
            
            # Check for long steps
            for step_type in ['given', 'when', 'then']:
                for step in scenario.get(step_type, []):
                    if len(step) > 100:
                        warnings.append(f"Step '{step[:50]}...' is too long and may be hard to maintain")
            
            # Check for complex conditionals in steps
            for step_type in ['given', 'when', 'then']:
                for step in scenario.get(step_type, []):
                    if step.lower().count(' and ') > 1 or step.lower().count(' or ') > 0:
                        warnings.append(f"Step '{step}' contains complex conditionals and should be simplified")
        
        # Check for feature description
        if not parsed_test_case.get('feature', ''):
            warnings.append("Test case has no Feature description")
        
        # Generate suggestions based on issues and warnings
        if issues or warnings:
            suggestions.append("Consider refactoring the test case to address the identified issues and warnings")
        
        if any("locator" in warning for warning in warnings):
            suggestions.append("Use page objects or centralized locator definitions instead of hardcoded locators")
        
        if any("assertion" in warning for warning in warnings):
            suggestions.append("Ensure all Then steps contain explicit assertions")
        
        if any("long" in warning for warning in warnings):
            suggestions.append("Break down long steps into smaller, more focused steps")
        
        if any("complex conditionals" in warning for warning in warnings):
            suggestions.append("Split steps with multiple conditions into separate steps")
        
        return {
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def analyze_test_case(self, test_case: str, coverage_data: Optional[Dict[str, Any]] = None, 
                         execution_history: Optional[List[Dict[str, Any]]] = None,
                         code_changes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a test case with enhanced metrics and risk assessment.
        
        Args:
            test_case: The test case to analyze, in Gherkin format.
            coverage_data: Optional code coverage data.
            execution_history: Optional list of previous execution results.
            code_changes: Optional information about recent code changes.
            
        Returns:
            Dictionary containing comprehensive analysis results.
        """
        logger.info("Analyzing test case with enhanced metrics")
        
        # Parse the Gherkin structure
        parsed_test_case = self.parse_gherkin(test_case)
        
        # Perform rule-based analysis
        rule_based_analysis = self._rule_based_analysis(parsed_test_case)
        
        # Calculate complexity metrics
        complexity_metrics = self.metrics_calculator.calculate_complexity(parsed_test_case)
        
        # Calculate quality metrics
        quality_metrics = self.metrics_calculator.calculate_quality_metrics(parsed_test_case, rule_based_analysis)
        
        # Calculate coverage metrics
        coverage_metrics = self.metrics_calculator.calculate_coverage_metrics(parsed_test_case, coverage_data)
        
        # Use LLM to analyze the test case
        llm_analysis = self.llm.analyze_test_case(test_case)
        
        # Prepare test case data for risk assessment
        test_case_data = {
            'complexity': complexity_metrics,
            'quality': quality_metrics,
            'coverage': coverage_metrics,
            'name': parsed_test_case.get('feature', 'Unknown Test Case'),
            'is_critical': 'critical' in parsed_test_case.get('feature', '').lower(),
            'is_customer_facing': 'user' in parsed_test_case.get('feature', '').lower() or 'customer' in parsed_test_case.get('feature', '').lower()
        }
        
        # Perform risk assessment
        risk_assessment = self.risk_assessor.assess_risk(test_case_data, execution_history, code_changes)
        
        # Combine all analyses
        combined_analysis = {
            "parsed_structure": parsed_test_case,
            "rule_based_analysis": rule_based_analysis,
            "complexity_metrics": complexity_metrics,
            "quality_metrics": quality_metrics,
            "coverage_metrics": coverage_metrics,
            "llm_analysis": llm_analysis,
            "risk_assessment": risk_assessment
        }
        
        return combined_analysis
    
    def analyze_test_suite(self, test_cases: List[str], coverage_data: Optional[Dict[str, Any]] = None,
                          execution_history: Optional[Dict[str, List[Dict[str, Any]]]] = None,
                          code_changes: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Analyze a suite of test cases and prioritize them.
        
        Args:
            test_cases: List of test cases in Gherkin format.
            coverage_data: Optional code coverage data.
            execution_history: Optional dictionary mapping test case IDs to execution history.
            code_changes: Optional dictionary mapping test case IDs to code change information.
            
        Returns:
            Dictionary containing suite analysis and prioritized test cases.
        """
        logger.info(f"Analyzing test suite with {len(test_cases)} test cases")
        
        # Analyze each test case
        analyzed_test_cases = []
        
        for i, test_case in enumerate(test_cases):
            test_case_id = f"TC-{i+1}"
            
            # Get execution history for this test case if available
            test_execution_history = None
            if execution_history and test_case_id in execution_history:
                test_execution_history = execution_history[test_case_id]
            
            # Get code change information for this test case if available
            test_code_changes = None
            if code_changes and test_case_id in code_changes:
                test_code_changes = code_changes[test_case_id]
            
            # Analyze the test case
            analysis = self.analyze_test_case(test_case, coverage_data, test_execution_history, test_code_changes)
            
            # Extract key information for prioritization
            test_case_data = {
                'id': test_case_id,
                'name': analysis['parsed_structure'].get('feature', f'Test Case {i+1}'),
                'complexity': analysis['complexity_metrics'],
                'quality': analysis['quality_metrics'],
                'coverage': analysis['coverage_metrics'],
                'risk_assessment': analysis['risk_assessment'],
                'is_critical': 'critical' in analysis['parsed_structure'].get('feature', '').lower(),
                'is_customer_facing': 'user' in analysis['parsed_structure'].get('feature', '').lower() or 'customer' in analysis['parsed_structure'].get('feature', '').lower(),
                'estimated_execution_time': 5  # Default to 5 minutes
            }
            
            analyzed_test_cases.append(test_case_data)
        
        # Prioritize test cases
        prioritized_test_cases = self.risk_assessor.prioritize_test_cases(analyzed_test_cases)
        
        # Generate test execution plan
        test_plan = self.risk_assessor.generate_test_plan(prioritized_test_cases)
        
        # Calculate suite-level metrics
        suite_metrics = self._calculate_suite_metrics(analyzed_test_cases)
        
        return {
            'test_cases': prioritized_test_cases,
            'test_plan': test_plan,
            'suite_metrics': suite_metrics
        }
    
    def _calculate_suite_metrics(self, analyzed_test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate metrics for the entire test suite.
        
        Args:
            analyzed_test_cases: List of analyzed test cases.
            
        Returns:
            Dictionary containing suite-level metrics.
        """
        metrics = {}
        
        # Count test cases by priority
        priority_counts = defaultdict(int)
        for test_case in analyzed_test_cases:
            priority = test_case.get('priority', 'low')
            priority_counts[priority] += 1
        
        metrics['priority_distribution'] = dict(priority_counts)
        
        # Calculate average complexity
        if analyzed_test_cases:
            avg_cyclomatic_complexity = np.mean([
                test_case.get('complexity', {}).get('cyclomatic_complexity', 0)
                for test_case in analyzed_test_cases
            ])
            
            avg_cognitive_complexity = np.mean([
                test_case.get('complexity', {}).get('cognitive_complexity', 0)
                for test_case in analyzed_test_cases
            ])
            
            metrics['average_cyclomatic_complexity'] = avg_cyclomatic_complexity
            metrics['average_cognitive_complexity'] = avg_cognitive_complexity
        
        # Calculate average quality score
        if analyzed_test_cases:
            avg_quality_score = np.mean([
                test_case.get('quality', {}).get('quality_score', 0)
                for test_case in analyzed_test_cases
            ])
            
            metrics['average_quality_score'] = avg_quality_score
        
        # Calculate risk distribution
        risk_counts = defaultdict(int)
        for test_case in analyzed_test_cases:
            risk = test_case.get('risk_assessment', {}).get('overall_risk', 'low')
            risk_counts[risk] += 1
        
        metrics['risk_distribution'] = dict(risk_counts)
        
        # Calculate estimated total execution time
        total_execution_time = sum(
            test_case.get('estimated_execution_time', 5)
            for test_case in analyzed_test_cases
        )
        
        metrics['total_estimated_execution_time'] = total_execution_time
        
        return metrics
    
    def suggest_improvements(self, test_case: str, execution_results: Optional[Dict[str, Any]] = None,
                            coverage_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Suggest comprehensive improvements for a test case.
        
        Args:
            test_case: The test case in Gherkin format.
            execution_results: Optional dictionary containing test execution results.
            coverage_data: Optional code coverage data.
            
        Returns:
            Dictionary containing suggested improvements.
        """
        logger.info("Suggesting comprehensive improvements for test case")
        
        # Analyze the test case
        analysis = self.analyze_test_case(test_case, coverage_data)
        
        # Get suggestions from rule-based analysis
        rule_based_suggestions = analysis['rule_based_analysis']['suggestions']
        
        # Get suggestions from LLM analysis
        llm_suggestions = []
        if 'improvement_suggestions' in analysis['llm_analysis']:
            if isinstance(analysis['llm_analysis']['improvement_suggestions'], list):
                llm_suggestions.extend(analysis['llm_analysis']['improvement_suggestions'])
            else:
                llm_suggestions.append(str(analysis['llm_analysis']['improvement_suggestions']))
        
        # Generate suggestions based on complexity metrics
        complexity_suggestions = []
        complexity_metrics = analysis['complexity_metrics']
        
        if complexity_metrics.get('cyclomatic_complexity', 0) > 10:
            complexity_suggestions.append("Reduce test complexity by breaking down into smaller, focused scenarios")
        
        if complexity_metrics.get('avg_steps_per_scenario', 0) > 10:
            complexity_suggestions.append("Reduce the number of steps per scenario for better maintainability")
        
        # Generate suggestions based on quality metrics
        quality_suggestions = []
        quality_metrics = analysis['quality_metrics']
        
        if quality_metrics.get('assertion_coverage', 0) < 100:
            quality_suggestions.append("Ensure all Then steps contain explicit assertions")
        
        if quality_metrics.get('locator_usage', 0) > 0:
            quality_suggestions.append("Replace hardcoded locators with page objects or centralized locator definitions")
        
        # Generate suggestions based on coverage metrics
        coverage_suggestions = []
        coverage_metrics = analysis['coverage_metrics']
        
        if coverage_metrics.get('feature_coverage', 0) < 80:
            coverage_suggestions.append("Improve feature coverage by adding scenarios for edge cases and error conditions")
        
        scenario_types = coverage_metrics.get('scenario_types', {})
        if scenario_types.get('edge_case', 0) == 0:
            coverage_suggestions.append("Add scenarios for edge cases (e.g., boundary values, empty inputs)")
        
        if scenario_types.get('error_case', 0) == 0:
            coverage_suggestions.append("Add scenarios for error conditions and exception handling")
        
        # If execution results are provided, use them for more targeted suggestions
        execution_suggestions = []
        if execution_results:
            # Use LLM to generate suggestions based on execution results
            execution_suggestions = self.llm.suggest_test_improvements(test_case, execution_results)
            
            # Add suggestions based on failure patterns
            if execution_results.get('status') == 'FAIL':
                failed_steps = [
                    step for step in execution_results.get('steps', [])
                    if step.get('status') == 'FAIL'
                ]
                
                if failed_steps:
                    for step in failed_steps:
                        error_message = step.get('error', '')
                        if 'timeout' in error_message.lower():
                            execution_suggestions.append(f"Add explicit waits before step '{step.get('step', '')}'")
                        elif 'element not found' in error_message.lower():
                            execution_suggestions.append(f"Update locator for step '{step.get('step', '')}'")
        
        # If coverage data is provided, suggest improvements based on coverage analysis
        coverage_analysis_suggestions = []
        if coverage_data:
            coverage_analysis = self.coverage_analyzer.analyze_coverage(coverage_data)
            coverage_analysis_suggestions = coverage_analysis.get('recommendations', [])
        
        # Combine all suggestions
        all_suggestions = {
            'rule_based': rule_based_suggestions,
            'llm': llm_suggestions,
            'complexity': complexity_suggestions,
            'quality': quality_suggestions,
            'coverage': coverage_suggestions,
            'execution': execution_suggestions,
            'coverage_analysis': coverage_analysis_suggestions
        }
        
        return all_suggestions
    
    def optimize_test_case(self, test_case: str, improvement_suggestions: Optional[Dict[str, List[str]]] = None) -> str:
        """
        Optimize a test case based on analysis and suggestions.
        
        Args:
            test_case: The test case in Gherkin format.
            improvement_suggestions: Optional dictionary of improvement suggestions.
            
        Returns:
            Optimized test case in Gherkin format.
        """
        logger.info("Optimizing test case")
        
        # If suggestions are not provided, generate them
        if not improvement_suggestions:
            # Analyze the test case
            analysis = self.analyze_test_case(test_case)
            
            # Generate suggestions
            improvement_suggestions = self.suggest_improvements(test_case)
        
        # Flatten suggestions into a single list
        flattened_suggestions = []
        for category, suggestions in improvement_suggestions.items():
            flattened_suggestions.extend(suggestions)
        
        # Use LLM to optimize the test case based on suggestions
        system_prompt = """
        You are a QA expert specialized in optimizing test cases. Your goal is to improve test cases
        based on analysis and suggestions. Focus on making the test case more reliable, efficient, and effective.
        Always return the complete optimized test case in Gherkin format.
        """
        
        prompt = f"""
        Here is a test case:
        
        ```gherkin
        {test_case}
        ```
        
        Here are suggestions for improvement:
        
        {json.dumps(flattened_suggestions, indent=2)}
        
        Please optimize this test case based on the suggestions.
        Focus on:
        1. Fixing identified issues
        2. Addressing warnings
        3. Implementing suggested improvements
        4. Making the test case more reliable and maintainable
        
        Return the complete optimized test case in Gherkin format.
        """
        
        optimized_test_case = self.llm.generate_completion(prompt, system_prompt)
        
        # Extract the Gherkin content from the response
        gherkin_pattern = r'```gherkin\s*(.*?)\s*```'
        match = re.search(gherkin_pattern, optimized_test_case, re.DOTALL)
        if match:
            optimized_test_case = match.group(1).strip()
        
        return optimized_test_case
    
    def analyze_error(self, error_message: str, test_step: str, screenshot_path: Optional[str] = None,
                     execution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze an error that occurred during test execution with enhanced context.
        
        Args:
            error_message: The error message from the test execution.
            test_step: The test step that failed.
            screenshot_path: Optional path to a screenshot taken at the time of the error.
            execution_context: Optional additional context about the execution environment.
            
        Returns:
            Dictionary containing error analysis and suggested fixes.
        """
        logger.info(f"Analyzing error for test step: {test_step}")
        
        # Get basic error analysis from LLM
        basic_analysis = self.llm.analyze_error(error_message, test_step, screenshot_path)
        
        # Enhance analysis with pattern matching
        enhanced_analysis = self._enhance_error_analysis(basic_analysis, error_message, test_step, execution_context)
        
        return enhanced_analysis
    
    def _enhance_error_analysis(self, basic_analysis: Dict[str, Any], error_message: str, test_step: str,
                              execution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhance error analysis with pattern matching and contextual information.
        
        Args:
            basic_analysis: Basic error analysis from LLM.
            error_message: The error message from the test execution.
            test_step: The test step that failed.
            execution_context: Optional additional context about the execution environment.
            
        Returns:
            Enhanced error analysis.
        """
        enhanced_analysis = basic_analysis.copy()
        
        # Add pattern-based analysis
        patterns = {
            'timeout': (
                r'timeout|wait|exceeded|timed out',
                "Synchronization issue - element not available in time",
                ["Increase timeout value", "Add explicit wait", "Use better synchronization strategy"]
            ),
            'element_not_found': (
                r'no such element|element not found|cannot find|not visible|not present',
                "Element locator issue - element not found or not visible",
                ["Update element locator", "Check if element is in viewport", "Verify element is not hidden"]
            ),
            'stale_element': (
                r'stale element|reference.*element.*stale',
                "Stale element reference - element was detached from DOM",
                ["Re-locate element before interaction", "Use more robust waiting strategy", "Avoid storing element references"]
            ),
            'assertion_error': (
                r'assert|expected|but got|should|to be',
                "Assertion failure - expected value not found",
                ["Update assertion to match actual behavior", "Verify test data", "Check if application behavior changed"]
            ),
            'permission_error': (
                r'permission|denied|unauthorized|access',
                "Permission issue - insufficient privileges",
                ["Verify test user permissions", "Update authentication method", "Check security settings"]
            )
        }
        
        for pattern_name, (pattern, diagnosis, solutions) in patterns.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                if 'pattern_analysis' not in enhanced_analysis:
                    enhanced_analysis['pattern_analysis'] = {}
                
                enhanced_analysis['pattern_analysis'][pattern_name] = {
                    'diagnosis': diagnosis,
                    'solutions': solutions
                }
        
        # Add contextual analysis if context is provided
        if execution_context:
            enhanced_analysis['contextual_analysis'] = {}
            
            # Check for browser/device specific issues
            if 'browser' in execution_context:
                browser = execution_context['browser']
                enhanced_analysis['contextual_analysis']['browser'] = {
                    'name': browser,
                    'known_issues': self._get_browser_specific_issues(browser, error_message)
                }
            
            # Check for environment specific issues
            if 'environment' in execution_context:
                environment = execution_context['environment']
                enhanced_analysis['contextual_analysis']['environment'] = {
                    'name': environment,
                    'known_issues': self._get_environment_specific_issues(environment, error_message)
                }
            
            # Check for timing/performance issues
            if 'execution_time' in execution_context:
                execution_time = execution_context['execution_time']
                if execution_time > 5000:  # More than 5 seconds
                    enhanced_analysis['contextual_analysis']['performance'] = {
                        'issue': "Slow execution time may indicate performance issues",
                        'recommendation': "Investigate performance bottlenecks"
                    }
        
        # Add historical analysis if this error has occurred before
        if 'error_history' in execution_context:
            error_history = execution_context['error_history']
            if error_history:
                enhanced_analysis['historical_analysis'] = {
                    'frequency': len(error_history),
                    'pattern': self._analyze_error_history_pattern(error_history)
                }
        
        return enhanced_analysis
    
    def _get_browser_specific_issues(self, browser: str, error_message: str) -> List[str]:
        """
        Get browser-specific issues based on the error message.
        
        Args:
            browser: The browser name.
            error_message: The error message.
            
        Returns:
            List of browser-specific issues.
        """
        issues = []
        
        browser = browser.lower()
        
        if browser == 'chrome':
            if 'shadow-root' in error_message.lower():
                issues.append("Chrome handles shadow DOM differently - use specific shadow DOM selectors")
            if 'webdriver' in error_message.lower():
                issues.append("Chrome WebDriver may need updating to match browser version")
        
        elif browser == 'firefox':
            if 'xpath' in error_message.lower():
                issues.append("Firefox XPath implementation may differ - try CSS selectors instead")
            if 'modal' in error_message.lower():
                issues.append("Firefox handles modal dialogs differently - use specific Firefox workarounds")
        
        elif browser == 'safari':
            if 'click' in error_message.lower():
                issues.append("Safari may have issues with certain click events - try JavaScript click")
            if 'iframe' in error_message.lower():
                issues.append("Safari has stricter iframe security - check frame switching approach")
        
        elif browser == 'edge':
            if 'element not interactable' in error_message.lower():
                issues.append("Edge may report elements as not interactable - ensure element is fully visible")
        
        return issues
    
    def _get_environment_specific_issues(self, environment: str, error_message: str) -> List[str]:
        """
        Get environment-specific issues based on the error message.
        
        Args:
            environment: The environment name.
            error_message: The error message.
            
        Returns:
            List of environment-specific issues.
        """
        issues = []
        
        environment = environment.lower()
        
        if environment == 'ci':
            if 'timeout' in error_message.lower():
                issues.append("CI environments often have slower performance - increase timeouts")
            if 'display' in error_message.lower():
                issues.append("CI may run headless - ensure tests are compatible with headless mode")
        
        elif environment == 'docker':
            if 'connection' in error_message.lower():
                issues.append("Docker networking may cause connection issues - check container networking")
            if 'permission' in error_message.lower():
                issues.append("Docker containers may have permission restrictions - check container permissions")
        
        elif environment == 'remote':
            if 'timeout' in error_message.lower():
                issues.append("Remote execution may have network latency - increase timeouts")
            if 'screenshot' in error_message.lower():
                issues.append("Remote screenshot capture may fail - check remote WebDriver configuration")
        
        return issues
    
    def _analyze_error_history_pattern(self, error_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in error history.
        
        Args:
            error_history: List of historical error occurrences.
            
        Returns:
            Dictionary containing error pattern analysis.
        """
        pattern_analysis = {}
        
        # Check if error is intermittent
        if len(error_history) > 3:
            success_between_failures = False
            for i in range(1, len(error_history)):
                if error_history[i]['timestamp'] - error_history[i-1]['timestamp'] > 3600:  # More than 1 hour between failures
                    success_between_failures = True
                    break
            
            if success_between_failures:
                pattern_analysis['type'] = 'intermittent'
                pattern_analysis['recommendation'] = "Investigate race conditions or timing issues"
            else:
                pattern_analysis['type'] = 'consistent'
                pattern_analysis['recommendation'] = "This appears to be a consistent issue that needs fixing"
        
        # Check if error frequency is increasing
        if len(error_history) >= 3:
            timestamps = [entry['timestamp'] for entry in error_history]
            intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
            
            if all(intervals[i] < intervals[i-1] for i in range(1, len(intervals))):
                pattern_analysis['frequency_trend'] = 'increasing'
                pattern_analysis['urgency'] = 'high'
            elif all(intervals[i] > intervals[i-1] for i in range(1, len(intervals))):
                pattern_analysis['frequency_trend'] = 'decreasing'
                pattern_analysis['urgency'] = 'medium'
            else:
                pattern_analysis['frequency_trend'] = 'variable'
                pattern_analysis['urgency'] = 'medium'
        
        return pattern_analysis
    
    def suggest_alternative_steps(self, failed_step: str, error_message: str, 
                                execution_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Suggest alternative steps when a test step fails with enhanced context.
        
        Args:
            failed_step: The test step that failed.
            error_message: The error message from the test execution.
            execution_context: Optional additional context about the execution environment.
            
        Returns:
            List of alternative steps with explanations.
        """
        logger.info(f"Suggesting alternative steps for failed step: {failed_step}")
        
        # Analyze the error
        error_analysis = self.analyze_error(error_message, failed_step, execution_context=execution_context)
        
        # Use LLM to generate alternative steps
        system_prompt = """
        You are a QA expert specialized in fixing failing test steps. Your goal is to suggest
        alternative steps that might work when a test step fails. Focus on practical, actionable
        alternatives that address the underlying issues.
        """
        
        prompt = f"""
        A test step failed during execution:
        
        Failed Step: {failed_step}
        
        Error Message: {error_message}
        
        Error Analysis: {json.dumps(error_analysis, indent=2)}
        
        Please suggest 3-5 alternative steps that might work instead of the failing step.
        For each alternative, provide:
        1. The alternative step in Gherkin format
        2. An explanation of why this alternative might work
        3. Any preconditions or setup needed for this alternative
        
        Return your suggestions as a JSON array of objects with fields: "step", "explanation", and "preconditions".
        """
        
        result = self.llm.generate_completion(prompt, system_prompt)
        
        # Try to parse the result as JSON
        try:
            alternatives = json.loads(result)
            if isinstance(alternatives, list):
                return alternatives
        except json.JSONDecodeError:
            pass
        
        # If JSON parsing fails, extract alternatives manually
        alternatives = []
        current_alternative = {}
        
        for line in result.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Alternative') or line.startswith('Option') or line.startswith('-'):
                if current_alternative and 'step' in current_alternative:
                    alternatives.append(current_alternative)
                current_alternative = {}
            
            elif line.startswith('Step:') or any(line.startswith(prefix) for prefix in ['Given ', 'When ', 'Then ', 'And ', 'But ']):
                if 'step' not in current_alternative:
                    current_alternative['step'] = line
            
            elif line.startswith('Explanation:') or line.startswith('Why:'):
                if 'explanation' not in current_alternative:
                    current_alternative['explanation'] = line.split(':', 1)[1].strip()
            
            elif line.startswith('Precondition') or line.startswith('Setup:'):
                if 'preconditions' not in current_alternative:
                    current_alternative['preconditions'] = line.split(':', 1)[1].strip()
        
        # Add the last alternative
        if current_alternative and 'step' in current_alternative:
            alternatives.append(current_alternative)
        
        # If still no alternatives, create a generic one
        if not alternatives:
            alternatives = [{
                'step': f"Then I wait and retry '{failed_step}'",
                'explanation': "Adding a wait before retrying may help with timing issues",
                'preconditions': "None"
            }]
        
        return alternatives
