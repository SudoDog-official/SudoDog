from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless handler for telemetry events
    """
    
    def do_POST(self):
        """Handle POST requests from SudoDog clients"""
        
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
            
            # Store event in database
            success = self._store_event(event)
            
            if not success:
                self.send_error(500, "Failed to store event")
                return
            
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
            import traceback
            traceback.print_exc()
            self.send_error(500, "Internal Server Error")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _ensure_table_exists(self, cursor):
        """Create table if it doesn't exist"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_events (
                id SERIAL PRIMARY KEY,
                anonymous_id VARCHAR(50) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                version VARCHAR(20),
                properties JSONB,
                user_agent VARCHAR(500),
                ip_address INET,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_anonymous_id ON telemetry_events(anonymous_id);
            CREATE INDEX IF NOT EXISTS idx_event_type ON telemetry_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_timestamp ON telemetry_events(timestamp);
        """)
    
    def _store_event(self, event: dict) -> bool:
        """
        Store telemetry event in Postgres database
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import psycopg2
            from psycopg2.extras import Json
            
            # Get database URL from environment (automatically set by Vercel)
            database_url = os.environ.get('POSTGRES_URL')
            
            if not database_url:
                print("Warning: POSTGRES_URL not set, logging to console only")
                print(f"[TELEMETRY] {event['event_type']} from {event['anonymous_id'][:12]}... at {event['timestamp']}")
                return True
            
            # Connect to database
            conn = psycopg2.connect(database_url, sslmode='require')
            cursor = conn.cursor()
            
            # Ensure table exists (creates on first run)
            self._ensure_table_exists(cursor)
            conn.commit()
            
            # Insert event
            cursor.execute("""
                INSERT INTO telemetry_events 
                (anonymous_id, event_type, timestamp, version, properties, user_agent, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                event['anonymous_id'],
                event['event_type'],
                event['timestamp'],
                event['version'],
                Json(event.get('properties', {})),
                self.headers.get('User-Agent'),
                self.client_address[0] if self.client_address else None
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Log to console for visibility
            print(f"[TELEMETRY] ✓ Stored to DB: {event['event_type']} from {event['anonymous_id'][:12]}... at {event['timestamp']}")
            
            return True
            
        except Exception as e:
            print(f"Database error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to console logging
            print(f"[TELEMETRY] (fallback) {event['event_type']} from {event['anonymous_id'][:12]}... at {event['timestamp']}")
            return True  # Still return True so client doesn't error
