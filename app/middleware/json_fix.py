import json
import re
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp


class JSONFixMiddleware(BaseHTTPMiddleware):
    """Middleware to fix common JSON syntax errors"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Only process JSON requests
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type.lower():
            try:
                # Read the request body
                body = await request.body()
                if body:
                    # Try to parse JSON
                    try:
                        json.loads(body)
                        # JSON is valid, continue
                        return await call_next(request)
                    except json.JSONDecodeError as e:
                        # JSON is invalid, try to fix common issues
                        try:
                            body_str = body.decode('utf-8')
                            
                            # Fix trailing commas
                            body_str = re.sub(r',(\s*[}\]])', r'\1', body_str)
                            
                            # Fix missing quotes around property names
                            body_str = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', body_str)
                            
                            # Try to parse the fixed JSON
                            fixed_json = json.loads(body_str)
                            
                            # Create a new request with fixed body
                            new_body = body_str.encode('utf-8')
                            
                            # Create a new request object with the fixed body
                            # This is a bit hacky but should work for most cases
                            request._body = new_body
                            
                            print(f"DEBUG: Fixed malformed JSON automatically")
                            print(f"DEBUG: Original: {body[:100]}")
                            print(f"DEBUG: Fixed: {new_body[:100]}")
                            
                            return await call_next(request)
                            
                        except Exception as fix_error:
                            print(f"DEBUG: Could not fix JSON automatically: {fix_error}")
                            # Return a helpful error message
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "error": "Invalid JSON format",
                                    "message": "The request contains malformed JSON. Please check for trailing commas, missing quotes, or other syntax errors.",
                                    "details": str(e),
                                    "position": e.pos
                                }
                            )
            
            except Exception as e:
                print(f"DEBUG: Error in JSON fix middleware: {e}")
        
        # Continue with the request
        return await call_next(request)
