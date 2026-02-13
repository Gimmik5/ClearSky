"""
Data Manager Module
Manages analysis data storage, history, and statistics
"""

import os
import json
from datetime import datetime
from python_config import (
    SAVE_ANALYSIS_DATA, DATA_FILE, MAX_HISTORY_ENTRIES,
    MAX_HISTORY_SAVED, CLEAR_SKY_THRESHOLD
)


class DataManager:
    """Manages image and analysis data storage"""
    
    def __init__(self):
        self.latest_data = {
            "timestamp": None,
            "image_path": None,
            "analysis": {}
        }
        self.history = []
        
        # Load existing data
        self.load_data()
    
    def update_latest(self, timestamp, image_path, analysis_results):
        """
        Update latest data with new analysis
        
        Args:
            timestamp: Timestamp string
            image_path: Path to saved image
            analysis_results: Dict from analysis_core.analyze_image()
        """
        self.latest_data = {
            "timestamp": timestamp,
            "image_path": image_path,
            "analysis": analysis_results
        }
        
        # Add to history
        self.add_to_history(self.latest_data.copy())
    
    def add_to_history(self, entry):
        """
        Add entry to history and trim if needed
        
        Args:
            entry: Data entry dict
        """
        self.history.append(entry)
        
        # Trim history if needed
        if len(self.history) > MAX_HISTORY_ENTRIES:
            self.history = self.history[-MAX_HISTORY_ENTRIES:]
    
    def get_latest(self):
        """
        Get latest analysis data
        
        Returns:
            dict: Latest data entry
        """
        return self.latest_data
    
    def get_history(self, limit=None):
        """
        Get historical data
        
        Args:
            limit: Optional maximum number of entries to return
        
        Returns:
            list: Historical entries
        """
        if limit:
            return self.history[-limit:]
        return self.history
    
    def save_data(self):
        """Save data to JSON file"""
        if not SAVE_ANALYSIS_DATA:
            return
        
        try:
            data = {
                "latest": self.latest_data,
                "history": self.history[-MAX_HISTORY_SAVED:],
                "saved_at": datetime.now().isoformat()
            }
            
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load data from JSON file"""
        if not os.path.exists(DATA_FILE):
            return
        
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            
            self.latest_data = data.get("latest", self.latest_data)
            self.history = data.get("history", [])
            
            print(f"✓ Loaded {len(self.history)} historical entries from {DATA_FILE}")
        
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def get_statistics(self):
        """
        Calculate statistics from history
        
        Returns:
            dict: Statistical summary
        """
        if not self.history:
            return {}
        
        scores = extract_clear_sky_scores(self.history)
        
        if not scores:
            return {}
        
        return {
            "total_captures": len(self.history),
            "average_score": round(sum(scores) / len(scores), 1),
            "max_score": max(scores),
            "min_score": min(scores),
            "clear_days": sum(1 for s in scores if s >= CLEAR_SKY_THRESHOLD)
        }
    
    def export_csv(self, filename="export.csv"):
        """
        Export history to CSV file
        
        Args:
            filename: Output CSV filename
        """
        try:
            import csv
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                write_csv_header(writer)
                
                # Write data rows
                for entry in self.history:
                    write_csv_row(writer, entry)
            
            print(f"✓ Exported {len(self.history)} entries to {filename}")
        
        except Exception as e:
            print(f"Error exporting CSV: {e}")


# ===== HELPER FUNCTIONS =====

def extract_clear_sky_scores(history):
    """
    Extract clear sky scores from history
    
    Args:
        history: List of historical entries
    
    Returns:
        list: Clear sky scores
    """
    scores = []
    for h in history:
        score = h.get("analysis", {}).get("clear_sky_score")
        if score is not None:
            scores.append(score)
    return scores


def write_csv_header(writer):
    """Write CSV header row"""
    writer.writerow([
        "Timestamp",
        "Clear Sky Score",
        "Brightness",
        "Condition",
        "Blue Coverage",
        "Gray Coverage",
        "White Coverage"
    ])


def write_csv_row(writer, entry):
    """
    Write a single CSV data row
    
    Args:
        writer: CSV writer object
        entry: Data entry dict
    """
    analysis = entry.get("analysis", {})
    brightness = analysis.get("brightness", {})
    features = analysis.get("features", {})
    
    writer.writerow([
        entry.get("timestamp", ""),
        analysis.get("clear_sky_score", ""),
        brightness.get("average", ""),
        analysis.get("sky_condition", ""),
        features.get("blue_coverage", ""),
        features.get("gray_coverage", ""),
        features.get("white_coverage", "")
    ])


# Global instance
data_manager = DataManager()
