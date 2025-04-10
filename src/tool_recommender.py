"""
Tool Recommendation module for AI QA Agent.
This module provides recommendations for QA tools based on test requirements.
"""
import os
import logging
from typing import Dict, List, Any, Optional

from qa_tools_db import QAToolsDatabase

logger = logging.getLogger(__name__)

class ToolRecommender:
    """Tool recommendation functionality for suggesting appropriate QA tools."""
    
    def __init__(self):
        """Initialize the Tool Recommender."""
        self.qa_tools_db = QAToolsDatabase()
        logger.info("Initialized Tool Recommender")
    
    def recommend_tools(self, requirements: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recommend tools based on test requirements.
        
        Args:
            requirements: Dictionary containing requirements for tool recommendation.
                Example: {
                    'application_type': 'web',
                    'programming_language': 'python',
                    'test_types': ['functional', 'api', 'performance'],
                    'budget': 'open_source',
                    'team_size': 'small'
                }
            
        Returns:
            Dictionary containing recommended tools organized by category.
        """
        logger.info(f"Recommending tools based on requirements: {requirements}")
        return self.qa_tools_db.recommend_tools(requirements)
    
    def get_tool_details(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific tool.
        
        Args:
            tool_name: Name of the tool to get details for.
            
        Returns:
            Dictionary containing tool details if found, None otherwise.
        """
        logger.info(f"Getting details for tool: {tool_name}")
        return self.qa_tools_db.get_tool_by_name(tool_name)
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all tools in a specific category.
        
        Args:
            category: Category to get tools for.
            
        Returns:
            List of tools in the specified category.
        """
        logger.info(f"Getting tools for category: {category}")
        return self.qa_tools_db.get_tools_by_category(category)
    
    def get_all_categories(self) -> List[str]:
        """
        Get all available tool categories.
        
        Returns:
            List of available tool categories.
        """
        return list(self.qa_tools_db.get_all_tools().keys())
    
    def get_tool_comparison(self, tool_names: List[str]) -> Dict[str, Any]:
        """
        Compare multiple tools based on their features and capabilities.
        
        Args:
            tool_names: List of tool names to compare.
            
        Returns:
            Dictionary containing comparison results.
        """
        logger.info(f"Comparing tools: {tool_names}")
        
        comparison = {
            'tools': [],
            'features': {},
            'pros_cons': {},
            'license_type': {},
            'supported_languages': {},
            'learning_curve': {}
        }
        
        for tool_name in tool_names:
            tool = self.qa_tools_db.get_tool_by_name(tool_name)
            if tool:
                comparison['tools'].append(tool_name)
                
                # Compare features
                for feature in tool.get('features', []):
                    if feature not in comparison['features']:
                        comparison['features'][feature] = []
                    comparison['features'][feature].append(tool_name)
                
                # Compare pros and cons
                comparison['pros_cons'][tool_name] = {
                    'pros': tool.get('pros', []),
                    'cons': tool.get('cons', [])
                }
                
                # Compare license type
                comparison['license_type'][tool_name] = tool.get('license_type', 'unknown')
                
                # Compare supported languages
                comparison['supported_languages'][tool_name] = tool.get('supported_languages', [])
                
                # Compare learning curve
                comparison['learning_curve'][tool_name] = tool.get('learning_curve', 'medium')
        
        return comparison
