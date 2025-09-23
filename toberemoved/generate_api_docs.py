#!/usr/bin/env python3
"""
API Documentation Generator for Rice Mill ERP
Generates comprehensive API documentation from route files
"""

import os
import re
import json
from datetime import datetime

class APIDocumentationGenerator:
    def __init__(self):
        self.routes_dir = "backend/routes"
        self.api_docs = {
            "info": {
                "title": "Rice Mill ERP API",
                "version": "1.0.0",
                "description": "Comprehensive API for Rice Mill Management System",
                "generated_at": datetime.now().isoformat()
            },
            "base_url": "http://localhost:5000",
            "authentication": {
                "type": "Bearer Token (JWT)",
                "header": "Authorization: Bearer <token>",
                "login_endpoint": "/api/auth/login"
            },
            "endpoints": {}
        }
    
    def extract_routes_from_file(self, file_path):
        """Extract route information from Python file"""
        routes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find route decorators and functions
            route_pattern = r"@\w+\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?\)"
            function_pattern = r"def\s+(\w+)\([^)]*\):"
            docstring_pattern = r'"""([^"]+)"""'
            
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                route_match = re.search(route_pattern, line)
                if route_match:
                    path = route_match.group(1)
                    methods = route_match.group(2)
                    
                    if methods:
                        methods = [m.strip().strip("'\"") for m in methods.split(',')]
                    else:
                        methods = ['GET']
                    
                    # Find function name
                    func_name = None
                    description = None
                    
                    for j in range(i+1, min(i+10, len(lines))):
                        func_match = re.search(function_pattern, lines[j])
                        if func_match:
                            func_name = func_match.group(1)
                            
                            # Look for docstring
                            for k in range(j+1, min(j+5, len(lines))):
                                if '"""' in lines[k]:
                                    doc_start = k
                                    doc_lines = []
                                    for l in range(doc_start, min(doc_start+10, len(lines))):
                                        doc_lines.append(lines[l])
                                        if lines[l].count('"""') >= 2 or (l > doc_start and '"""' in lines[l]):
                                            break
                                    
                                    description = ' '.join(doc_lines).replace('"""', '').strip()
                                    break
                            break
                    
                    routes.append({
                        'path': path,
                        'methods': methods,
                        'function': func_name,
                        'description': description or f"Endpoint for {func_name}"
                    })
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return routes
    
    def generate_documentation(self):
        """Generate complete API documentation"""
        
        print("📚 Generating API Documentation...")
        
        # Process all route files
        route_files = [
            ('auth.py', 'Authentication', '/api/auth'),
            ('dashboard.py', 'Dashboard', '/api/dashboard'),
            ('farmer.py', 'Farmer Management', '/api/farmer'),
            ('inventory.py', 'Inventory Management', '/api/inventory'),
            ('production.py', 'Production Management', '/api/production'),
            ('sales.py', 'Sales Management', '/api/sales'),
            ('finance.py', 'Finance Management', '/api/finance'),
            ('customers.py', 'Customer Management', '/api/customers'),
            ('quality.py', 'Quality Control', '/api/quality'),
            ('analytics.py', 'Analytics', '/api/analytics'),
            ('compliance.py', 'Compliance', '/api/compliance'),
            ('supply_chain.py', 'Supply Chain', '/api/supply-chain'),
            ('logistics.py', 'Logistics', '/api/logistics'),
            ('notifications.py', 'Notifications', '/api'),
            ('ai_services.py', 'AI Services', '/api/ai'),
            ('biometric.py', 'Biometric', '/api/biometric'),
            ('quality_vision.py', 'Quality Vision', '/api/quality-vision'),
            ('financial_intelligence.py', 'Financial Intelligence', '/api/financial-intelligence'),
            ('compliance_gst.py', 'GST Compliance', '/api/compliance'),
            ('analytics_reporting.py', 'Analytics Reporting', '/api/analytics'),
        ]
        
        for filename, category, prefix in route_files:
            file_path = os.path.join(self.routes_dir, filename)
            
            if os.path.exists(file_path):
                routes = self.extract_routes_from_file(file_path)
                
                if routes:
                    self.api_docs['endpoints'][category] = {
                        'prefix': prefix,
                        'routes': routes
                    }
                    print(f"✅ Processed {filename}: {len(routes)} endpoints")
            else:
                print(f"⚠️ File not found: {filename}")
        
        # Add sample requests and responses
        self.add_sample_data()
        
        # Generate different formats
        self.generate_json_docs()
        self.generate_markdown_docs()
        self.generate_html_docs()
        
        print("✅ API Documentation generated successfully!")
    
    def add_sample_data(self):
        """Add sample requests and responses"""
        
        samples = {
            'Authentication': {
                'login': {
                    'request': {
                        'username': 'admin',
                        'password': 'admin123'
                    },
                    'response': {
                        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'user': {
                            'id': 1,
                            'username': 'admin',
                            'role': 'admin'
                        }
                    }
                }
            },
            'Farmer Management': {
                'create_farmer': {
                    'request': {
                        'name': 'John Doe',
                        'phone': '9876543210',
                        'address': '123 Farm Road, Village',
                        'email': 'john@example.com'
                    },
                    'response': {
                        'id': 1,
                        'name': 'John Doe',
                        'phone': '9876543210',
                        'status': 'active'
                    }
                }
            }
        }
        
        # Add samples to endpoints
        for category, data in samples.items():
            if category in self.api_docs['endpoints']:
                self.api_docs['endpoints'][category]['samples'] = data
    
    def generate_json_docs(self):
        """Generate JSON documentation"""
        
        with open('docs/api_documentation.json', 'w') as f:
            json.dump(self.api_docs, f, indent=2)
        
        print("✅ Generated docs/api_documentation.json")
    
    def generate_markdown_docs(self):
        """Generate Markdown documentation"""
        
        md_content = f"""# Rice Mill ERP API Documentation

**Version:** {self.api_docs['info']['version']}  
**Generated:** {self.api_docs['info']['generated_at']}  
**Base URL:** {self.api_docs['base_url']}

## Authentication

This API uses JWT (JSON Web Token) authentication.

**Login Endpoint:** `POST /api/auth/login`

**Request:**
```json
{{
  "username": "your_username",
  "password": "your_password"
}}
```

**Response:**
```json
{{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {{
    "id": 1,
    "username": "admin",
    "role": "admin"
  }}
}}
```

**Using the Token:**
Include the token in the Authorization header:
```
Authorization: Bearer <your_token_here>
```

## API Endpoints

"""
        
        for category, data in self.api_docs['endpoints'].items():
            md_content += f"\n### {category}\n\n"
            md_content += f"**Base Path:** `{data['prefix']}`\n\n"
            
            for route in data['routes']:
                methods_str = ', '.join(route['methods'])
                md_content += f"#### `{methods_str}` {data['prefix']}{route['path']}\n\n"
                md_content += f"**Function:** `{route['function']}`\n\n"
                md_content += f"**Description:** {route['description']}\n\n"
                
                # Add sample if available
                if 'samples' in data:
                    for sample_name, sample_data in data['samples'].items():
                        if sample_name in route['function']:
                            md_content += "**Sample Request:**\n```json\n"
                            md_content += json.dumps(sample_data['request'], indent=2)
                            md_content += "\n```\n\n"
                            md_content += "**Sample Response:**\n```json\n"
                            md_content += json.dumps(sample_data['response'], indent=2)
                            md_content += "\n```\n\n"
                
                md_content += "---\n\n"
        
        # Add error codes section
        md_content += """
## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not Found |
| 422  | Validation Error |
| 500  | Internal Server Error |

## Rate Limiting

- **Default:** 1000 requests per hour
- **Login attempts:** 5 per minute
- **API calls:** 100 per minute

## Support

For API support, contact: admin@ricemill.com
"""
        
        os.makedirs('docs', exist_ok=True)
        with open('docs/API_DOCUMENTATION.md', 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print("✅ Generated docs/API_DOCUMENTATION.md")
    
    def generate_html_docs(self):
        """Generate HTML documentation"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rice Mill ERP API Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .header {{ background: linear-gradient(135deg, #4caf50, #45a049); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .endpoint {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #4caf50; border-radius: 4px; }}
        .method {{ background: #007bff; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
        .path {{ font-family: monospace; background: #e9ecef; padding: 4px 8px; border-radius: 4px; }}
        pre {{ background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 4px; overflow-x: auto; }}
        .category {{ margin: 20px 0; }}
        .toc {{ background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 Rice Mill ERP API Documentation</h1>
            <p>Version: {self.api_docs['info']['version']} | Generated: {self.api_docs['info']['generated_at']}</p>
        </div>
        
        <div class="toc">
            <h3>📋 Table of Contents</h3>
            <ul>
"""
        
        # Add table of contents
        for category in self.api_docs['endpoints'].keys():
            html_content += f'                <li><a href="#{category.lower().replace(" ", "-")}">{category}</a></li>\n'
        
        html_content += """            </ul>
        </div>
        
        <div class="category">
            <h2>🔐 Authentication</h2>
            <p>This API uses JWT (JSON Web Token) authentication.</p>
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/auth/login</span>
                <pre>{
  "username": "your_username",
  "password": "your_password"
}</pre>
            </div>
        </div>
"""
        
        # Add endpoints
        for category, data in self.api_docs['endpoints'].items():
            category_id = category.lower().replace(' ', '-')
            html_content += f"""
        <div class="category" id="{category_id}">
            <h2>📊 {category}</h2>
            <p><strong>Base Path:</strong> <code>{data['prefix']}</code></p>
"""
            
            for route in data['routes']:
                methods_html = ' '.join([f'<span class="method">{method}</span>' for method in route['methods']])
                html_content += f"""
            <div class="endpoint">
                {methods_html} <span class="path">{data['prefix']}{route['path']}</span>
                <p><strong>Function:</strong> {route['function']}</p>
                <p>{route['description']}</p>
            </div>
"""
        
        html_content += """
        </div>
        
        <div class="category">
            <h2>📞 Support</h2>
            <p>For API support and questions:</p>
            <ul>
                <li>Email: admin@ricemill.com</li>
                <li>Documentation: <a href="API_DOCUMENTATION.md">Markdown Version</a></li>
                <li>JSON Schema: <a href="api_documentation.json">JSON Version</a></li>
            </ul>
        </div>
    </div>
</body>
</html>"""
        
        with open('docs/api_documentation.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Generated docs/api_documentation.html")

def main():
    """Main documentation generation function"""
    
    print("📚 Rice Mill ERP - API Documentation Generator")
    print("=" * 60)
    
    generator = APIDocumentationGenerator()
    generator.generate_documentation()
    
    print("\n🎉 Documentation Generation Complete!")
    print("📄 Files generated:")
    print("  - docs/api_documentation.json")
    print("  - docs/API_DOCUMENTATION.md")
    print("  - docs/api_documentation.html")

if __name__ == "__main__":
    main()