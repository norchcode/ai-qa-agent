"""
Test script for the enhanced test case analyzer.
This script tests the functionality of the enhanced test case analyzer.
"""
import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import xml.etree.ElementTree as ET

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_case_analyzer_enhanced import (
    TestCaseMetrics,
    CodeCoverageAnalyzer,
    RiskAssessment,
    EnhancedTestCaseAnalyzer
)

class TestTestCaseMetrics(unittest.TestCase):
    """Test case for the TestCaseMetrics class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.metrics_calculator = TestCaseMetrics()
        
        # Sample parsed test case
        self.parsed_test_case = {
            "feature": "User Authentication",
            "scenarios": [
                {
                    "title": "Successful login",
                    "type": "normal",
                    "given": ["I am on the login page"],
                    "when": ["I enter valid credentials", "I click the login button"],
                    "then": ["I should be redirected to the dashboard", "I should see a welcome message"],
                    "and": [],
                    "but": [],
                    "examples": []
                },
                {
                    "title": "Failed login with invalid password",
                    "type": "normal",
                    "given": ["I am on the login page"],
                    "when": ["I enter an invalid password", "I click the login button"],
                    "then": ["I should see an error message"],
                    "and": [],
                    "but": [],
                    "examples": []
                },
                {
                    "title": "Login with different user roles",
                    "type": "outline",
                    "given": ["I am on the login page"],
                    "when": ["I login as a <role>"],
                    "then": ["I should see <dashboard_type> dashboard"],
                    "and": [],
                    "but": [],
                    "examples": [
                        "| role | dashboard_type |",
                        "| admin | admin |",
                        "| user | standard |",
                        "| guest | limited |"
                    ]
                }
            ]
        }
        
        # Sample rule-based analysis
        self.rule_based_analysis = {
            "issues": ["Scenario 'Test scenario' has no Then steps (no assertions)"],
            "warnings": [
                "Step 'I click on element with xpath=\"//button\"' contains hardcoded locators which may be fragile",
                "Then step 'I see the page loads' may not contain an assertion"
            ],
            "suggestions": ["Use page objects instead of hardcoded locators"]
        }
    
    def test_calculate_complexity(self):
        """Test calculating complexity metrics."""
        metrics = self.metrics_calculator.calculate_complexity(self.parsed_test_case)
        
        # Verify basic counts
        self.assertEqual(metrics['total_scenarios'], 3)
        self.assertEqual(metrics['scenario_outlines'], 1)
        self.assertEqual(metrics['regular_scenarios'], 2)
        
        # Verify step counts
        self.assertEqual(metrics['total_steps'], 9)
        self.assertEqual(metrics['given_steps'], 3)
        self.assertEqual(metrics['when_steps'], 3)
        self.assertEqual(metrics['then_steps'], 3)
        
        # Verify calculated metrics
        self.assertEqual(metrics['avg_steps_per_scenario'], 3.0)
        self.assertGreater(metrics['cyclomatic_complexity'], 1)
        self.assertGreater(metrics['cognitive_complexity'], 0)
        self.assertGreaterEqual(metrics['maintainability_index'], 0)
        self.assertLessEqual(metrics['maintainability_index'], 100)
    
    def test_calculate_quality_metrics(self):
        """Test calculating quality metrics."""
        metrics = self.metrics_calculator.calculate_quality_metrics(
            self.parsed_test_case, self.rule_based_analysis
        )
        
        # Verify issue counts
        self.assertEqual(metrics['total_issues'], 1)
        self.assertEqual(metrics['total_warnings'], 2)
        
        # Verify calculated metrics
        self.assertEqual(metrics['issue_density'], 1/3)
        self.assertEqual(metrics['warning_density'], 2/3)
        
        # Verify quality score
        self.assertGreaterEqual(metrics['quality_score'], 0)
        self.assertLessEqual(metrics['quality_score'], 100)
    
    def test_calculate_coverage_metrics_without_coverage_data(self):
        """Test calculating coverage metrics without coverage data."""
        metrics = self.metrics_calculator.calculate_coverage_metrics(self.parsed_test_case)
        
        # Verify coverage metrics
        self.assertIsNone(metrics['line_coverage'])
        self.assertIsNone(metrics['branch_coverage'])
        
        # Verify scenario type counts
        self.assertEqual(metrics['scenario_types']['happy_path'], 3)
        
        # Verify feature coverage
        self.assertGreaterEqual(metrics['feature_coverage'], 0)
        self.assertLessEqual(metrics['feature_coverage'], 100)
    
    def test_calculate_coverage_metrics_with_coverage_data(self):
        """Test calculating coverage metrics with coverage data."""
        coverage_data = {
            'line_coverage': 75.5,
            'branch_coverage': 68.2,
            'function_coverage': 80.0,
            'statement_coverage': 76.3
        }
        
        metrics = self.metrics_calculator.calculate_coverage_metrics(
            self.parsed_test_case, coverage_data
        )
        
        # Verify coverage metrics
        self.assertEqual(metrics['line_coverage'], 75.5)
        self.assertEqual(metrics['branch_coverage'], 68.2)
        self.assertEqual(metrics['function_coverage'], 80.0)
        self.assertEqual(metrics['statement_coverage'], 76.3)


class TestCodeCoverageAnalyzer(unittest.TestCase):
    """Test case for the CodeCoverageAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.coverage_analyzer = CodeCoverageAnalyzer()
        
        # Create a temporary XML file for testing
        self.xml_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xml')
        
        # Create a simple Cobertura XML structure
        root = ET.Element('coverage', {
            'line-rate': '0.8',
            'branch-rate': '0.7',
            'version': '1.0'
        })
        
        packages = ET.SubElement(root, 'packages')
        package = ET.SubElement(packages, 'package', {
            'name': 'com.example',
            'line-rate': '0.75',
            'branch-rate': '0.65'
        })
        
        classes = ET.SubElement(package, 'classes')
        class_elem = ET.SubElement(classes, 'class', {
            'name': 'ExampleClass',
            'filename': 'ExampleClass.java',
            'line-rate': '0.7',
            'branch-rate': '0.6'
        })
        
        methods = ET.SubElement(class_elem, 'methods')
        method = ET.SubElement(methods, 'method', {
            'name': 'exampleMethod',
            'signature': '()V',
            'line-rate': '0.65',
            'branch-rate': '0.55'
        })
        
        # Write the XML to the temporary file
        tree = ET.ElementTree(root)
        tree.write(self.xml_file.name)
        
        # Create a temporary JSON file for testing
        self.json_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        
        # Create a simple Istanbul/NYC JSON structure
        coverage_json = {
            'total': {
                'lines': {'total': 100, 'covered': 80, 'skipped': 0, 'pct': 80.0},
                'statements': {'total': 120, 'covered': 90, 'skipped': 0, 'pct': 75.0},
                'functions': {'total': 30, 'covered': 25, 'skipped': 0, 'pct': 83.3},
                'branches': {'total': 50, 'covered': 35, 'skipped': 0, 'pct': 70.0}
            },
            'src/example.js': {
                'lines': {'total': 50, 'covered': 40, 'skipped': 0, 'pct': 80.0},
                'statements': {'total': 60, 'covered': 45, 'skipped': 0, 'pct': 75.0},
                'functions': {'total': 15, 'covered': 12, 'skipped': 0, 'pct': 80.0},
                'branches': {'total': 25, 'covered': 15, 'skipped': 0, 'pct': 60.0}
            },
            'src/lowcoverage.js': {
                'lines': {'total': 50, 'covered': 20, 'skipped': 0, 'pct': 40.0},
                'statements': {'total': 60, 'covered': 25, 'skipped': 0, 'pct': 41.7},
                'functions': {'total': 15, 'covered': 8, 'skipped': 0, 'pct': 53.3},
                'branches': {'total': 25, 'covered': 10, 'skipped': 0, 'pct': 40.0}
            }
        }
        
        # Write the JSON to the temporary file
        with open(self.json_file.name, 'w') as f:
            json.dump(coverage_json, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        os.unlink(self.xml_file.name)
        os.unlink(self.json_file.name)
    
    def test_parse_coverage_xml(self):
        """Test parsing coverage data from XML."""
        coverage_data = self.coverage_analyzer.parse_coverage_xml(self.xml_file.name)
        
        # Verify overall coverage metrics
        self.assertEqual(coverage_data['line_coverage'], 80.0)
        self.assertEqual(coverage_data['branch_coverage'], 70.0)
        
        # Verify package data
        self.assertIn('packages', coverage_data)
        self.assertIn('com.example', coverage_data['packages'])
        
        # Verify class data
        package_data = coverage_data['packages']['com.example']
        self.assertIn('classes', package_data)
        self.assertIn('ExampleClass', package_data['classes'])
        
        # Verify method data
        class_data = package_data['classes']['ExampleClass']
        self.assertIn('methods', class_data)
        self.assertIn('exampleMethod', class_data['methods'])
    
    def test_parse_coverage_json(self):
        """Test parsing coverage data from JSON."""
        coverage_data = self.coverage_analyzer.parse_coverage_json(self.json_file.name)
        
        # Verify overall coverage metrics
        self.assertEqual(coverage_data['line_coverage'], 80.0)
        self.assertEqual(coverage_data['branch_coverage'], 70.0)
        self.assertEqual(coverage_data['function_coverage'], 83.3)
        self.assertEqual(coverage_data['statement_coverage'], 75.0)
        
        # Verify file data
        self.assertIn('files', coverage_data)
        self.assertIn('src/example.js', coverage_data['files'])
        self.assertIn('src/lowcoverage.js', coverage_data['files'])
        
        # Verify file-specific coverage
        file_data = coverage_data['files']['src/example.js']
        self.assertEqual(file_data['line_coverage'], 80.0)
        self.assertEqual(file_data['branch_coverage'], 60.0)
    
    def test_analyze_coverage(self):
        """Test analyzing coverage data."""
        coverage_data = self.coverage_analyzer.parse_coverage_json(self.json_file.name)
        analysis = self.coverage_analyzer.analyze_coverage(coverage_data)
        
        # Verify analysis structure
        self.assertIn('overall_assessment', analysis)
        self.assertIn('low_coverage_areas', analysis)
        self.assertIn('recommendations', analysis)
        
        # Verify low coverage areas are identified
        self.assertTrue(any('src/lowcoverage.js' in area for area in analysis['low_coverage_areas']))
        
        # Verify recommendations are provided
        self.assertTrue(len(analysis['recommendations']) > 0)
    
    def test_suggest_test_cases(self):
        """Test suggesting test cases to improve coverage."""
        coverage_data = self.coverage_analyzer.parse_coverage_json(self.json_file.name)
        suggestions = self.coverage_analyzer.suggest_test_cases(coverage_data)
        
        # Verify suggestions are provided
        self.assertTrue(len(suggestions) > 0)


class TestRiskAssessment(unittest.TestCase):
    """Test case for the RiskAssessment class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.risk_assessor = RiskAssessment()
        
        # Sample test case data
        self.test_case = {
            'complexity': {
                'cyclomatic_complexity': 8,
                'cognitive_complexity': 12
            },
            'quality': {
                'quality_score': 75,
                'total_issues': 1,
                'total_warnings': 2
            },
            'name': 'User Authentication Test',
            'is_critical': True,
            'is_customer_facing': True
        }
        
        # Sample execution history
        self.execution_history = [
            {'status': 'PASS', 'timestamp': 1000},
            {'status': 'PASS', 'timestamp': 2000},
            {'status': 'FAIL', 'timestamp': 3000},
            {'status': 'PASS', 'timestamp': 4000},
            {'status': 'PASS', 'timestamp': 5000}
        ]
        
        # Sample code changes
        self.code_changes = {
            'affects_test_case': True,
            'magnitude': 'medium',
            'files_changed': ['auth.js', 'login.js']
        }
    
    def test_assess_risk(self):
        """Test assessing risk level of a test case."""
        risk_assessment = self.risk_assessor.assess_risk(
            self.test_case, self.execution_history, self.code_changes
        )
        
        # Verify risk assessment structure
        self.assertIn('risk_factors', risk_assessment)
        self.assertIn('overall_risk', risk_assessment)
        self.assertIn('risk_score', risk_assessment)
        
        # Verify risk factors
        risk_factors = risk_assessment['risk_factors']
        self.assertIn('complexity', risk_factors)
        self.assertIn('quality', risk_factors)
        self.assertIn('failure_history', risk_factors)
        self.assertIn('code_changes', risk_factors)
        
        # Verify overall risk is one of the expected values
        self.assertIn(risk_assessment['overall_risk'], ['low', 'medium', 'high'])
    
    def test_prioritize_test_cases(self):
        """Test prioritizing test cases based on risk assessment."""
        # Create multiple test cases with different risk levels
        test_cases = [
            {
                'id': 'TC-001',
                'name': 'High Risk Test',
                'risk_assessment': {
                    'overall_risk': 'high',
                    'risk_factors': {
                        'code_changes': 'high',
                        'recent_failures': 'high'
                    }
                },
                'is_critical': True,
                'is_customer_facing': True
            },
            {
                'id': 'TC-002',
                'name': 'Medium Risk Test',
                'risk_assessment': {
                    'overall_risk': 'medium',
                    'risk_factors': {
                        'code_changes': 'medium',
                        'recent_failures': 'low'
                    }
                },
                'is_critical': False,
                'is_customer_facing': True
            },
            {
                'id': 'TC-003',
                'name': 'Low Risk Test',
                'risk_assessment': {
                    'overall_risk': 'low',
                    'risk_factors': {
                        'code_changes': 'low',
                        'recent_failures': 'low'
                    }
                },
                'is_critical': False,
                'is_customer_facing': False
            }
        ]
        
        prioritized_test_cases = self.risk_assessor.prioritize_test_cases(test_cases)
        
        # Verify test cases are prioritized
        self.assertEqual(len(prioritized_test_cases), 3)
        
        # Verify priority scores and levels are assigned
        for test_case in prioritized_test_cases:
            self.assertIn('priority_score', test_case)
            self.assertIn('priority', test_case)
            self.assertIn(test_case['priority'], ['critical', 'high', 'medium', 'low'])
        
        # Verify order of prioritization (highest priority first)
        self.assertEqual(prioritized_test_cases[0]['id'], 'TC-001')
        self.assertEqual(prioritized_test_cases[2]['id'], 'TC-003')
    
    def test_generate_test_plan(self):
        """Test generating a test execution plan."""
        # Create prioritized test cases
        prioritized_test_cases = [
            {
                'id': 'TC-001',
                'name': 'Critical Test',
                'priority': 'critical',
                'priority_score': 8,
                'estimated_execution_time': 10,
                'feature': 'Authentication',
                'component': 'Login'
            },
            {
                'id': 'TC-002',
                'name': 'High Priority Test',
                'priority': 'high',
                'priority_score': 6,
                'estimated_execution_time': 5,
                'feature': 'User Management',
                'component': 'User Profile'
            },
            {
                'id': 'TC-003',
                'name': 'Medium Priority Test',
                'priority': 'medium',
                'priority_score': 4,
                'estimated_execution_time': 8,
                'feature': 'Authentication',
                'component': 'Password Reset'
            }
        ]
        
        # Generate test plan with no time budget
        test_plan = self.risk_assessor.generate_test_plan(prioritized_test_cases)
        
        # Verify test plan structure
        self.assertIn('test_cases', test_plan)
        self.assertIn('total_estimated_time', test_plan)
        self.assertIn('coverage', test_plan)
        
        # Verify all test cases are included
        self.assertEqual(len(test_plan['test_cases']), 3)
        
        # Verify total estimated time
        self.assertEqual(test_plan['total_estimated_time'], 23)
        
        # Verify coverage information
        coverage = test_plan['coverage']
        self.assertEqual(coverage['feature_count'], 2)
        self.assertEqual(coverage['component_count'], 3)
        
        # Generate test plan with time budget
        test_plan_with_budget = self.risk_assessor.generate_test_plan(prioritized_test_cases, time_budget=15)
        
        # Verify only high priority test cases are included
        self.assertLess(len(test_plan_with_budget['test_cases']), 3)
        self.assertLessEqual(test_plan_with_budget['total_estimated_time'], 15)


class TestEnhancedTestCaseAnalyzer(unittest.TestCase):
    """Test case for the EnhancedTestCaseAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the LLM integration
        self.llm_patcher = patch('test_case_analyzer_enhanced.get_llm_integration')
        self.mock_llm = self.llm_patcher.start()
        
        # Configure the mock LLM
        self.mock_llm_instance = MagicMock()
        self.mock_llm_instance.analyze_test_case.return_value = {
            'quality_score': 85,
            'improvement_suggestions': ['Add more assertions', 'Use better locators'],
            'missing_validations': ['Validate error messages']
        }
        self.mock_llm_instance.generate_completion.return_value = """
        ```gherkin
        Feature: Optimized User Authentication
        
        Scenario: Successful login
          Given I am on the login page
          When I enter valid credentials
          And I click the login button
          Then I should be redirected to the dashboard
          And I should see a welcome message with my username
        ```
        """
        self.mock_llm_instance.analyze_error.return_value = {
            'root_cause': 'Element not found',
            'suggested_fixes': ['Update locator', 'Add wait']
        }
        
        self.mock_llm.return_value = self.mock_llm_instance
        
        # Create the analyzer
        self.analyzer = EnhancedTestCaseAnalyzer(llm_provider='mock_provider')
        
        # Sample test case in Gherkin format
        self.test_case = """
        Feature: User Authentication
        
        Scenario: Successful login
          Given I am on the login page
          When I enter valid credentials
          And I click the login button
          Then I should be redirected to the dashboard
          And I should see a welcome message
        
        Scenario: Failed login with invalid password
          Given I am on the login page
          When I enter an invalid password
          And I click the login button
          Then I should see an error message
        """
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.llm_patcher.stop()
    
    def test_parse_gherkin(self):
        """Test parsing Gherkin text."""
        parsed = self.analyzer.parse_gherkin(self.test_case)
        
        # Verify feature is parsed
        self.assertEqual(parsed['feature'], 'User Authentication')
        
        # Verify scenarios are parsed
        self.assertEqual(len(parsed['scenarios']), 2)
        self.assertEqual(parsed['scenarios'][0]['title'], 'Successful login')
        self.assertEqual(parsed['scenarios'][1]['title'], 'Failed login with invalid password')
        
        # Verify steps are parsed
        self.assertEqual(len(parsed['scenarios'][0]['given']), 1)
        self.assertEqual(len(parsed['scenarios'][0]['when']), 1)
        self.assertEqual(len(parsed['scenarios'][0]['then']), 2)
    
    def test_analyze_test_case(self):
        """Test analyzing a test case."""
        analysis = self.analyzer.analyze_test_case(self.test_case)
        
        # Verify analysis structure
        self.assertIn('parsed_structure', analysis)
        self.assertIn('rule_based_analysis', analysis)
        self.assertIn('complexity_metrics', analysis)
        self.assertIn('quality_metrics', analysis)
        self.assertIn('coverage_metrics', analysis)
        self.assertIn('llm_analysis', analysis)
        self.assertIn('risk_assessment', analysis)
        
        # Verify LLM was called
        self.mock_llm_instance.analyze_test_case.assert_called_once_with(self.test_case)
    
    def test_suggest_improvements(self):
        """Test suggesting improvements for a test case."""
        suggestions = self.analyzer.suggest_improvements(self.test_case)
        
        # Verify suggestions structure
        self.assertIn('rule_based', suggestions)
        self.assertIn('llm', suggestions)
        self.assertIn('complexity', suggestions)
        self.assertIn('quality', suggestions)
        self.assertIn('coverage', suggestions)
        
        # Verify LLM suggestions are included
        self.assertEqual(suggestions['llm'], ['Add more assertions', 'Use better locators'])
    
    def test_optimize_test_case(self):
        """Test optimizing a test case."""
        optimized = self.analyzer.optimize_test_case(self.test_case)
        
        # Verify optimized test case is returned
        self.assertIn('Feature: Optimized User Authentication', optimized)
        self.assertIn('Scenario: Successful login', optimized)
        
        # Verify LLM was called
        self.assertTrue(self.mock_llm_instance.generate_completion.called)
    
    def test_analyze_error(self):
        """Test analyzing an error."""
        error_message = "Element not found: //button[@id='login']"
        test_step = "When I click the login button"
        
        analysis = self.analyzer.analyze_error(error_message, test_step)
        
        # Verify analysis includes LLM results
        self.assertEqual(analysis['root_cause'], 'Element not found')
        self.assertEqual(analysis['suggested_fixes'], ['Update locator', 'Add wait'])
        
        # Verify LLM was called
        self.mock_llm_instance.analyze_error.assert_called_once()
    
    def test_suggest_alternative_steps(self):
        """Test suggesting alternative steps."""
        error_message = "Element not found: //button[@id='login']"
        failed_step = "When I click the login button"
        
        # Configure mock to return JSON
        self.mock_llm_instance.generate_completion.return_value = json.dumps([
            {
                "step": "When I click the login button using JavaScript",
                "explanation": "Using JavaScript to click can bypass visibility issues",
                "preconditions": "None"
            },
            {
                "step": "When I wait for the login button to be clickable and then click it",
                "explanation": "Adding an explicit wait can resolve timing issues",
                "preconditions": "None"
            }
        ])
        
        alternatives = self.analyzer.suggest_alternative_steps(failed_step, error_message)
        
        # Verify alternatives are returned
        self.assertEqual(len(alternatives), 2)
        self.assertEqual(alternatives[0]['step'], "When I click the login button using JavaScript")
        
        # Verify LLM was called
        self.assertTrue(self.mock_llm_instance.generate_completion.called)


if __name__ == '__main__':
    unittest.main()
