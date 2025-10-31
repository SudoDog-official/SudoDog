from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless handler for telemetry events
    """
    
    def do_POST(self):
        """Handle POST requests from SudoDog clients"""
    
        # Accept any POST path (Vercel routes to this function)
        # No path checking needed            return
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse JSON
            try:
                event = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return
            
            # Validate event structure
            required_fields = ['anonymous_id', 'event_type', 'timestamp', 'version']
            if not all(field in event for field in required_fields):
                self.send_error(400, "Missing required fields")
                return
            
            # Validate anonymous_id format (should start with "anon-")
            if not event['anonymous_id'].startswith('anon-'):
                self.send_error(400, "Invalid anonymous_id format")
                return
            
            # Store event (for now, just log it)
            # TODO: Add database storage (e.g., Vercel Postgres, MongoDB, etc.)
            self._store_event(event)
            
            # Return success
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'success',
                'message': 'Event received'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            # Log error but don't expose details to client
            print(f"Error processing telemetry: {e}")
            self.send_error(500, "Internal Server Error")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _store_event(self, event: dict):
        """
        Store telemetry event
        
        For now, this just prints to logs.
        In production, you would:
        1. Store in a database (Vercel Postgres, MongoDB, etc.)
        2. Send to analytics platform (PostHog, Mixpanel, etc.)
        3. Aggregate stats for dashboard
        
        Example with Vercel Postgres:
        
        import psycopg2
        conn = psycopg2.connect(os.environ['POSTGRES_URL'])
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO telemetry_events (anonymous_id, event_type, timestamp, version, properties) VALUES (%s, %s, %s, %s, %s)",
            (event['anonymous_id'], event['event_type'], event['timestamp'], event['version'], json.dumps(event.get('properties', {})))
        )
        conn.commit()
