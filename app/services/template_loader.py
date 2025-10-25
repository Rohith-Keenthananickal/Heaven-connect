"""
Template Loader Service
Loads email templates from files and handles variable substitution
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TemplateLoader:
    """Service for loading and processing email templates"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "emails"
        self._template_cache = {}
    
    def load_template(self, template_name: str, template_type: str = "html") -> str:
        """
        Load email template from file
        
        Args:
            template_name: Name of the template (e.g., 'forgot_password')
            template_type: Type of template ('html' or 'txt')
            
        Returns:
            Template content as string
        """
        try:
            # Check cache first
            cache_key = f"{template_name}_{template_type}"
            if cache_key in self._template_cache:
                return self._template_cache[cache_key]
            
            # Load from file
            template_file = self.templates_dir / f"{template_name}.{template_type}"
            
            if not template_file.exists():
                logger.error(f"Template file not found: {template_file}")
                return self._get_fallback_template(template_name, template_type)
            
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cache the template
            self._template_cache[cache_key] = content
            return content
            
        except Exception as e:
            logger.error(f"Error loading template {template_name}.{template_type}: {str(e)}")
            return self._get_fallback_template(template_name, template_type)
    
    def render_template(self, template_name: str, variables: Dict[str, Any], template_type: str = "html") -> str:
        """
        Load template and substitute variables
        
        Args:
            template_name: Name of the template
            variables: Dictionary of variables to substitute
            template_type: Type of template ('html' or 'txt')
            
        Returns:
            Rendered template with variables substituted
        """
        try:
            template_content = self.load_template(template_name, template_type)
            return template_content.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return template_content
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            return template_content
    
    def _get_fallback_template(self, template_name: str, template_type: str) -> str:
        """Get fallback template when file is not found"""
        if template_type == "html":
            return f"""
            <html>
            <body>
                <h2>{template_name.replace('_', ' ').title()}</h2>
                <p>Template not found. Please contact support.</p>
            </body>
            </html>
            """
        else:
            return f"""
            {template_name.replace('_', ' ').title()}
            
            Template not found. Please contact support.
            """
    
    def clear_cache(self):
        """Clear template cache"""
        self._template_cache.clear()
        logger.info("Template cache cleared")
    
    def get_available_templates(self) -> list:
        """Get list of available templates"""
        try:
            templates = []
            for file_path in self.templates_dir.glob("*.html"):
                template_name = file_path.stem
                templates.append(template_name)
            return sorted(templates)
        except Exception as e:
            logger.error(f"Error getting available templates: {str(e)}")
            return []
    
    def template_exists(self, template_name: str, template_type: str = "html") -> bool:
        """Check if template file exists"""
        template_file = self.templates_dir / f"{template_name}.{template_type}"
        return template_file.exists()


# Create global instance
template_loader = TemplateLoader()


