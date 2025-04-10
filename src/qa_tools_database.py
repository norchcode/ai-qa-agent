"""
QA Tools Database module for AI QA Agent.
This module provides a comprehensive database of QA tools and frameworks with recommendation capabilities.
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class QAToolsDatabase:
    """Database of QA tools and frameworks with recommendation capabilities."""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the QA Tools Database.
        
        Args:
            data_path: Optional path to the data directory. If not provided, will use default.
        """
        self.data_path = data_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'qa_tools_db', 'data')
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize the tools database
        self.tools_db = {
            'test_automation_frameworks': [],
            'test_management_tools': [],
            'performance_testing_tools': [],
            'api_testing_tools': [],
            'mobile_testing_tools': [],
            'security_testing_tools': [],
            'cicd_tools': [],
            'cross_browser_testing_tools': [],
            'code_quality_tools': [],
            'visual_testing_tools': []
        }
        
        # Load the tools database
        self._load_database()
        
        logger.info(f"Initialized QA Tools Database with {sum(len(tools) for tools in self.tools_db.values())} tools")
    
    def _load_database(self):
        """Load the tools database from JSON files."""
        for category in self.tools_db.keys():
            file_path = os.path.join(self.data_path, f"{category}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        self.tools_db[category] = json.load(f)
                    logger.info(f"Loaded {len(self.tools_db[category])} tools for category: {category}")
                except Exception as e:
                    logger.error(f"Error loading tools database for category {category}: {e}")
    
    def save_database(self):
        """Save the tools database to JSON files."""
        for category, tools in self.tools_db.items():
            file_path = os.path.join(self.data_path, f"{category}.json")
            try:
                with open(file_path, 'w') as f:
                    json.dump(tools, f, indent=2)
                logger.info(f"Saved {len(tools)} tools for category: {category}")
            except Exception as e:
                logger.error(f"Error saving tools database for category {category}: {e}")
    
    def get_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all tools in the database.
        
        Returns:
            Dictionary containing all tools organized by category.
        """
        return self.tools_db
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get tools by category.
        
        Args:
            category: The category to get tools for.
            
        Returns:
            List of tools in the specified category.
        """
        return self.tools_db.get(category, [])
    
    def get_tool_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a tool by name.
        
        Args:
            name: The name of the tool to get.
            
        Returns:
            Tool information if found, None otherwise.
        """
        name_lower = name.lower()
        for category, tools in self.tools_db.items():
            for tool in tools:
                if tool.get('name', '').lower() == name_lower:
                    return tool
        return None
    
    def add_tool(self, category: str, tool_info: Dict[str, Any]) -> bool:
        """
        Add a tool to the database.
        
        Args:
            category: The category to add the tool to.
            tool_info: Information about the tool.
            
        Returns:
            True if the tool was added successfully, False otherwise.
        """
        if category not in self.tools_db:
            logger.error(f"Invalid category: {category}")
            return False
        
        # Check if the tool already exists
        name = tool_info.get('name')
        if not name:
            logger.error("Tool must have a name")
            return False
        
        existing_tool = self.get_tool_by_name(name)
        if existing_tool:
            logger.warning(f"Tool {name} already exists in the database")
            return False
        
        # Add the tool
        self.tools_db[category].append(tool_info)
        logger.info(f"Added tool {name} to category {category}")
        
        # Save the database
        self.save_database()
        
        return True
    
    def update_tool(self, name: str, updated_info: Dict[str, Any]) -> bool:
        """
        Update a tool in the database.
        
        Args:
            name: The name of the tool to update.
            updated_info: Updated information about the tool.
            
        Returns:
            True if the tool was updated successfully, False otherwise.
        """
        name_lower = name.lower()
        for category, tools in self.tools_db.items():
            for i, tool in enumerate(tools):
                if tool.get('name', '').lower() == name_lower:
                    # Update the tool
                    self.tools_db[category][i].update(updated_info)
                    logger.info(f"Updated tool {name}")
                    
                    # Save the database
                    self.save_database()
                    
                    return True
        
        logger.warning(f"Tool {name} not found in the database")
        return False
    
    def delete_tool(self, name: str) -> bool:
        """
        Delete a tool from the database.
        
        Args:
            name: The name of the tool to delete.
            
        Returns:
            True if the tool was deleted successfully, False otherwise.
        """
        name_lower = name.lower()
        for category, tools in self.tools_db.items():
            for i, tool in enumerate(tools):
                if tool.get('name', '').lower() == name_lower:
                    # Delete the tool
                    del self.tools_db[category][i]
                    logger.info(f"Deleted tool {name} from category {category}")
                    
                    # Save the database
                    self.save_database()
                    
                    return True
        
        logger.warning(f"Tool {name} not found in the database")
        return False
    
    def recommend_tools(self, requirements: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recommend tools based on requirements.
        
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
        recommended_tools = {}
        
        # Extract requirements
        app_type = requirements.get('application_type', '').lower()
        programming_language = requirements.get('programming_language', '').lower()
        test_types = [t.lower() for t in requirements.get('test_types', [])]
        budget = requirements.get('budget', '').lower()
        team_size = requirements.get('team_size', '').lower()
        
        # Recommend test automation frameworks
        if 'functional' in test_types or 'automation' in test_types:
            frameworks = self.get_tools_by_category('test_automation_frameworks')
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
                elif budget == 'commercial' and framework.get('license_type') == 'commercial':
                    score += 2
                
                # Match team size
                if team_size == 'small' and framework.get('learning_curve', '') == 'low':
                    score += 1
                elif team_size == 'large' and framework.get('enterprise_ready', False):
                    score += 1
                
                if score > 0:
                    recommended_frameworks.append({
                        **framework,
                        'recommendation_score': score
                    })
            
            # Sort by recommendation score
            recommended_frameworks.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
            
            # Add to recommended tools
            if recommended_frameworks:
                recommended_tools['test_automation_frameworks'] = recommended_frameworks
        
        # Recommend API testing tools
        if 'api' in test_types:
            api_tools = self.get_tools_by_category('api_testing_tools')
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
                recommended_tools['api_testing_tools'] = recommended_api_tools
        
        # Recommend performance testing tools
        if 'performance' in test_types:
            perf_tools = self.get_tools_by_category('performance_testing_tools')
            recommended_perf_tools = []
            
            for tool in perf_tools:
                score = 0
                
                # Match programming language
                if programming_language and programming_language in tool.get('supported_languages', []):
                    score += 2
                
                # Match budget
                if budget == 'open_source' and tool.get('license_type') == 'open_source':
                    score += 2
                elif budget == 'commercial' and tool.get('license_type') == 'commercial':
                    score += 2
                
                # Match team size
                if team_size == 'small' and tool.get('learning_curve', '') == 'low':
                    score += 1
                elif team_size == 'large' and tool.get('enterprise_ready', False):
                    score += 1
                
                if score > 0:
                    recommended_perf_tools.append({
                        **tool,
                        'recommendation_score': score
                    })
            
            # Sort by recommendation score
            recommended_perf_tools.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
            
            # Add to recommended tools
            if recommended_perf_tools:
                recommended_tools['performance_testing_tools'] = recommended_perf_tools
        
        # Add recommendations for other categories based on test types
        
        return recommended_tools
    
    def import_from_markdown(self, markdown_file: str, category: str) -> bool:
        """
        Import tools from a markdown file.
        
        Args:
            markdown_file: Path to the markdown file.
            category: The category to import tools to.
            
        Returns:
            True if tools were imported successfully, False otherwise.
        """
        if category not in self.tools_db:
            logger.error(f"Invalid category: {category}")
            return False
        
        try:
            with open(markdown_file, 'r') as f:
                content = f.read()
            
            # Parse the markdown content to extract tools
            tools = self._parse_markdown_tools(content, category)
            
            if not tools:
                logger.warning(f"No tools found in markdown file: {markdown_file}")
                return False
            
            # Add the tools to the database
            self.tools_db[category] = tools
            logger.info(f"Imported {len(tools)} tools for category {category} from {markdown_file}")
            
            # Save the database
            self.save_database()
            
            return True
            
        except Exception as e:
            logger.error(f"Error importing tools from markdown file {markdown_file}: {e}")
            return False
    
    def _parse_markdown_tools(self, content: str, category: str) -> List[Dict[str, Any]]:
        """
        Parse markdown content to extract tools.
        
        Args:
            content: Markdown content.
            category: The category of tools.
            
        Returns:
            List of tools extracted from the markdown content.
        """
        tools = []
        
        # Split the content by headers
        lines = content.split('\n')
        
        current_tool = None
        current_section = None
        
        for line in lines:
            # Check for tool headers (numbered items)
            if line.strip().startswith('###') and '**' in line:
                # Save the previous tool if it exists
                if current_tool:
                    tools.append(current_tool)
                
                # Extract the tool name
                tool_name = line.strip().replace('###', '').strip()
                tool_name = tool_name.replace('**', '').strip()
                
                # Create a new tool
                current_tool = {
                    'name': tool_name,
                    'category': category,
                    'description': '',
                    'features': [],
                    'pros': [],
                    'cons': [],
                    'license_type': 'unknown',
                    'supported_languages': [],
                    'supported_app_types': [],
                    'learning_curve': 'medium',
                    'enterprise_ready': False
                }
                
                current_section = 'description'
                
            # Check for section headers
            elif line.strip().startswith('**') and line.strip().endswith('**'):
                section_name = line.strip().replace('**', '').lower()
          
(Content truncated due to size limit. Use line ranges to read in chunks)