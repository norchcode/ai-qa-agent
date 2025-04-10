"""
Unit tests for the Tool Recommender module.
"""
import unittest
import os
import sys
import json
from unittest.mock import MagicMock, patch
import tempfile
import shutil

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_tools_db.tool_recommender import ToolRecommender
from qa_tools_db.qa_tools_database import QAToolsDatabase

class TestToolRecommender(unittest.TestCase):
    """Test cases for the ToolRecommender class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.test_data_dir = tempfile.mkdtemp()
        
        # Create a mock QA Tools Database
        self.mock_db = MagicMock(spec=QAToolsDatabase)
        
        # Set up sample tool data
        self.sample_tools = {
            'test_automation_frameworks': [
                {
                    'name': 'Selenium',
                    'category': 'test_automation_frameworks',
                    'description': 'Web automation framework',
                    'features': ['Cross-browser testing', 'Multiple language support'],
                    'pros': ['Widely used', 'Good community support'],
                    'cons': ['Slow execution', 'Flaky tests'],
                    'license_type': 'open_source',
                    'supported_languages': ['python', 'java', 'javascript'],
                    'supported_app_types': ['web'],
                    'learning_curve': 'medium',
                    'enterprise_ready': True
                },
                {
                    'name': 'Cypress',
                    'category': 'test_automation_frameworks',
                    'description': 'JavaScript testing framework',
                    'features': ['Fast execution', 'Real-time reloading'],
                    'pros': ['Developer friendly', 'Good debugging'],
                    'cons': ['JavaScript only', 'Limited browser support'],
                    'license_type': 'open_source',
                    'supported_languages': ['javascript'],
                    'supported_app_types': ['web'],
                    'learning_curve': 'low',
                    'enterprise_ready': False
                }
            ],
            'api_testing_tools': [
                {
                    'name': 'Postman',
                    'category': 'api_testing_tools',
                    'description': 'API testing platform',
                    'features': ['Request builder', 'Automated testing'],
                    'pros': ['User friendly', 'Good collaboration'],
                    'cons': ['Limited scripting', 'Performance issues with large collections'],
                    'license_type': 'commercial',
                    'supported_languages': ['javascript'],
                    'supported_app_types': ['api'],
                    'learning_curve': 'low',
                    'enterprise_ready': True
                }
            ]
        }
        
        # Configure the mock database
        self.mock_db.get_all_tools.return_value = self.sample_tools
        self.mock_db.get_tools_by_category.side_effect = lambda category: self.sample_tools.get(category, [])
        self.mock_db.get_tool_by_name.side_effect = lambda name: next(
            (tool for category in self.sample_tools.values() 
             for tool in category if tool['name'].lower() == name.lower()), None)
        
        # Create a patcher for the QAToolsDatabase constructor
        self.patcher = patch('qa_tools_db.tool_recommender.QAToolsDatabase')
        self.mock_db_class = self.patcher.start()
        self.mock_db_class.return_value = self.mock_db
        
        # Create an instance of ToolRecommender
        self.recommender = ToolRecommender()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
        shutil.rmtree(self.test_data_dir)
    
    def test_get_all_categories(self):
        """Test getting all tool categories."""
        categories = self.recommender.get_all_categories()
        self.assertEqual(set(categories), set(['test_automation_frameworks', 'api_testing_tools']))
    
    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        tools = self.recommender.get_tools_by_category('test_automation_frameworks')
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0]['name'], 'Selenium')
        self.assertEqual(tools[1]['name'], 'Cypress')
    
    def test_get_tool_details(self):
        """Test getting tool details by name."""
        tool = self.recommender.get_tool_details('Selenium')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'Selenium')
        self.assertEqual(tool['category'], 'test_automation_frameworks')
        
        # Test case-insensitive search
        tool = self.recommender.get_tool_details('selenium')
        self.assertIsNotNone(tool)
        self.assertEqual(tool['name'], 'Selenium')
        
        # Test non-existent tool
        tool = self.recommender.get_tool_details('NonExistentTool')
        self.assertIsNone(tool)
    
    def test_recommend_tools(self):
        """Test recommending tools based on requirements."""
        # Configure the mock database to use a custom recommend_tools implementation
        def mock_recommend_tools(requirements):
            recommended = {}
            
            # Extract requirements
            app_type = requirements.get('application_type', '').lower()
            programming_language = requirements.get('programming_language', '').lower()
            test_types = [t.lower() for t in requirements.get('test_types', [])]
            budget = requirements.get('budget', '').lower()
            
            # Recommend test automation frameworks
            if 'functional' in test_types or 'automation' in test_types:
                frameworks = self.sample_tools.get('test_automation_frameworks', [])
                recommended_frameworks = []
                
                for framework in frameworks:
                    score = 0
                    
                    # Match application type
                    if app_type and app_type in framework.get('supported_app_types', []):
                        score += 3
                    
                    # Match programming language
                    if programming_language and programming_language in framework.get('supported_languages', []):
                        score += 3
                    
                    # Match budget
                    if budget == 'open_source' and framework.get('license_type') == 'open_source':
                        score += 2
                    
                    if score > 0:
                        recommended_frameworks.append({
                            **framework,
                            'recommendation_score': score
                        })
                
                # Sort by recommendation score
                recommended_frameworks.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
                
                # Add to recommended tools
                if recommended_frameworks:
                    recommended['test_automation_frameworks'] = recommended_frameworks
            
            # Recommend API testing tools
            if 'api' in test_types:
                api_tools = self.sample_tools.get('api_testing_tools', [])
                recommended_api_tools = []
                
                for tool in api_tools:
                    score = 0
                    
                    # Match programming language
                    if programming_language and programming_language in tool.get('supported_languages', []):
                        score += 3
                    
                    # Match budget
                    if budget == 'open_source' and tool.get('license_type') == 'open_source':
                        score += 2
                    elif budget == 'commercial' and tool.get('license_type') == 'commercial':
                        score += 2
                    
                    if score > 0:
                        recommended_api_tools.append({
                            **tool,
                            'recommendation_score': score
                        })
                
                # Sort by recommendation score
                recommended_api_tools.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
                
                # Add to recommended tools
                if recommended_api_tools:
                    recommended['api_testing_tools'] = recommended_api_tools
            
            return recommended
        
        self.mock_db.recommend_tools.side_effect = mock_recommend_tools
        
        # Test recommending tools for web automation with Python
        requirements = {
            'application_type': 'web',
            'programming_language': 'python',
            'test_types': ['functional'],
            'budget': 'open_source'
        }
        
        recommendations = self.recommender.recommend_tools(requirements)
        
        # Verify recommendations
        self.assertIn('test_automation_frameworks', recommendations)
        self.assertGreaterEqual(len(recommendations['test_automation_frameworks']), 1)
        # Check if Selenium is in the recommendations (it should be the highest scored)
        selenium_found = False
        for tool in recommendations['test_automation_frameworks']:
            if tool['name'] == 'Selenium':
                selenium_found = True
                break
        self.assertTrue(selenium_found, "Selenium should be in the recommendations")
        
        # Test recommending tools for API testing with JavaScript
        requirements = {
            'application_type': 'api',
            'programming_language': 'javascript',
            'test_types': ['api'],
            'budget': 'commercial'
        }
        
        recommendations = self.recommender.recommend_tools(requirements)
        
        # Verify recommendations
        self.assertIn('api_testing_tools', recommendations)
        self.assertEqual(len(recommendations['api_testing_tools']), 1)
        self.assertEqual(recommendations['api_testing_tools'][0]['name'], 'Postman')
    
    def test_get_tool_comparison(self):
        """Test comparing multiple tools."""
        comparison = self.recommender.get_tool_comparison(['Selenium', 'Cypress'])
        
        # Verify comparison results
        self.assertIn('tools', comparison)
        self.assertEqual(set(comparison['tools']), set(['Selenium', 'Cypress']))
        
        # Verify features comparison
        self.assertIn('features', comparison)
        self.assertIn('license_type', comparison)
        self.assertIn('supported_languages', comparison)
        self.assertIn('learning_curve', comparison)
        
        # Verify specific tool properties
        self.assertEqual(comparison['license_type']['Selenium'], 'open_source')
        self.assertEqual(comparison['license_type']['Cypress'], 'open_source')
        self.assertEqual(comparison['learning_curve']['Selenium'], 'medium')
        self.assertEqual(comparison['learning_curve']['Cypress'], 'low')

if __name__ == '__main__':
    unittest.main()
