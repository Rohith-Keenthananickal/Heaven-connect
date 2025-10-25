"""
Template Management Script
Helper script to manage email templates
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.template_loader import template_loader


def list_templates():
    """List all available templates"""
    print("📧 Available Email Templates:")
    print("=" * 40)
    
    templates = template_loader.get_available_templates()
    
    if not templates:
        print("No templates found.")
        return
    
    for template in templates:
        print(f"✅ {template}")
        
        # Check if both HTML and text versions exist
        html_exists = template_loader.template_exists(template, "html")
        txt_exists = template_loader.template_exists(template, "txt")
        
        status = []
        if html_exists:
            status.append("HTML")
        if txt_exists:
            status.append("TXT")
        
        print(f"   📄 {', '.join(status)}")
        print()


def test_template(template_name: str):
    """Test a template with sample data"""
    print(f"🧪 Testing template: {template_name}")
    print("=" * 40)
    
    # Sample variables for testing
    sample_variables = {
        "user_name": "John Doe",
        "reset_link": "https://app.heavenconnect.com/reset?token=abc123",
        "otp_code": "123456",
        "expires_in_minutes": 10,
        "login_link_html": '<a href="https://app.heavenconnect.com/login">Login</a>',
        "login_link_text": "https://app.heavenconnect.com/login",
        "property_name": "Beautiful Villa",
        "check_in": "2024-01-15",
        "check_out": "2024-01-20",
        "guests": 4,
        "total_amount": 25000,
        "status_text": "approved",
        "message": "Your property has been approved!"
    }
    
    try:
        # Test HTML template
        if template_loader.template_exists(template_name, "html"):
            print("📄 HTML Template:")
            html_content = template_loader.render_template(template_name, sample_variables, "html")
            print(html_content[:200] + "..." if len(html_content) > 200 else html_content)
            print()
        
        # Test text template
        if template_loader.template_exists(template_name, "txt"):
            print("📄 Text Template:")
            txt_content = template_loader.render_template(template_name, sample_variables, "txt")
            print(txt_content)
            print()
            
    except Exception as e:
        print(f"❌ Error testing template: {str(e)}")


def create_template(template_name: str):
    """Create a new template with basic structure"""
    print(f"📝 Creating template: {template_name}")
    print("=" * 40)
    
    templates_dir = Path("app/templates/emails")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # HTML template
    html_file = templates_dir / f"{template_name}.html"
    if not html_file.exists():
        html_content = f"""<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
        <h2 style="color: #333; text-align: center;">{template_name.replace('_', ' ').title()}</h2>
        <p>Hello {{user_name}},</p>
        <p>Your email content here.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #666; font-size: 12px; text-align: center;">
            Best regards,<br>Heaven Connect Team
        </p>
    </div>
</body>
</html>"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Created: {html_file}")
    
    # Text template
    txt_file = templates_dir / f"{template_name}.txt"
    if not txt_file.exists():
        txt_content = f"""{template_name.replace('_', ' ').title()}

Hello {{user_name}},

Your email content here.

Best regards,
Heaven Connect Team"""
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        print(f"✅ Created: {txt_file}")
    
    print(f"🎉 Template '{template_name}' created successfully!")


def clear_cache():
    """Clear template cache"""
    print("🗑️ Clearing template cache...")
    template_loader.clear_cache()
    print("✅ Template cache cleared!")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("📧 Email Template Manager")
        print("=" * 30)
        print("Usage:")
        print("  python manage_templates.py list                    # List all templates")
        print("  python manage_templates.py test <template_name>    # Test a template")
        print("  python manage_templates.py create <template_name>  # Create a new template")
        print("  python manage_templates.py clear                    # Clear template cache")
        print()
        print("Examples:")
        print("  python manage_templates.py list")
        print("  python manage_templates.py test forgot_password")
        print("  python manage_templates.py create new_template")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_templates()
    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ Please provide template name")
            print("Usage: python manage_templates.py test <template_name>")
            return
        template_name = sys.argv[2]
        test_template(template_name)
    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ Please provide template name")
            print("Usage: python manage_templates.py create <template_name>")
            return
        template_name = sys.argv[2]
        create_template(template_name)
    elif command == "clear":
        clear_cache()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: list, test, create, clear")


if __name__ == "__main__":
    main()


