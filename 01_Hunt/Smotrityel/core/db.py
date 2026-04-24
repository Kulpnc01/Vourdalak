import sqlite3
import os
import json

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_schema()

    def _create_schema(self):
        cursor = self.conn.cursor()
        
        # 1. Behavioral Events (Temporal)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                timestamp REAL,
                platform TEXT,
                sender TEXT,
                content TEXT,
                type TEXT,
                psych_score REAL,
                category TEXT,
                lat REAL,
                lon REAL,
                spatial_delta REAL,
                heart_rate REAL,
                biometric_delta REAL,
                raw_json TEXT
            )
        ''')
        
        # Safe migration for existing DBs
        try:
            cursor.execute('ALTER TABLE events ADD COLUMN spatial_delta REAL')
        except sqlite3.OperationalError:
            pass # Column already exists
            
        try:
            cursor.execute('ALTER TABLE events ADD COLUMN biometric_delta REAL')
        except sqlite3.OperationalError:
            pass # Column already exists

        # 2. Spatial Records (Raw GPS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spatial (
                timestamp REAL,
                lat REAL,
                lon REAL,
                accuracy REAL
            )
        ''')

        # 3. Biometric Records (Physiology)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS biometric (
                timestamp REAL,
                metric TEXT,
                value REAL
            )
        ''')

        # 4. Media Records (Photos/Video)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media (
                id TEXT PRIMARY KEY,
                event_id TEXT,
                timestamp REAL,
                file_path TEXT,
                original_path TEXT,
                metadata TEXT
            )
        ''')
        
        self.conn.commit()

    def save_event(self, event_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO events 
            (id, timestamp, platform, sender, content, type, psych_score, category, lat, lon, spatial_delta, heart_rate, biometric_delta, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data.get('id'),
            event_data.get('timestamp'),
            event_data.get('platform'),
            event_data.get('sender'),
            event_data.get('content'),
            event_data.get('type'),
            event_data.get('psych_score'),
            event_data.get('category'),
            event_data.get('lat'),
            event_data.get('lon'),
            event_data.get('spatial_delta'),
            event_data.get('heart_rate'),
            event_data.get('biometric_delta'),
            json.dumps(event_data)
        ))
        self.conn.commit()

    def save_spatial(self, ts, lat, lon, acc):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO spatial (timestamp, lat, lon, accuracy) VALUES (?, ?, ?, ?)', (ts, lat, lon, acc))
        self.conn.commit()

    def save_biometric(self, ts, metric, val):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO biometric (timestamp, metric, value) VALUES (?, ?, ?)', (ts, metric, float(val)))
        except: pass
        self.conn.commit()

    def save_media(self, media_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO media (id, event_id, timestamp, file_path, original_path, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            media_data.get('id'),
            media_data.get('event_id'),
            media_data.get('timestamp'),
            media_data.get('file_path'),
            media_data.get('original_path'),
            json.dumps(media_data.get('metadata', {}))
        ))
        self.conn.commit()

    def close(self):
        self.conn.close()
