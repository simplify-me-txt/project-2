"""
Time Predictor Module
Predicts cooking time based on recipe analysis
"""
import re

class TimePredictor:
    # Time indicators in recipe steps
    TIME_PATTERNS = [
        r'(\d+)\s*hours?',
        r'(\d+)\s*minutes?',
        r'(\d+)\s*mins?',
        r'(\d+)\s*seconds?',
        r'(\d+)\s*secs?',
    ]
    
    # Cooking methods and their typical duration multipliers
    COOKING_METHOD_TIME = {
        'bake': 30, 'baking': 30,
        'roast': 45, 'roasting': 45,
        'braise': 120, 'braising': 120,
        'simmer': 30, 'simmering': 30,
        'boil': 15, 'boiling': 15,
        'fry': 10, 'frying': 10,
        'sauté': 10, 'sautéing': 10,
        'grill': 20, 'grilling': 20,
        'steam': 15, 'steaming': 15,
        'marinate overnight': 480,
        'marinate': 30,
        'chill': 60, 'refrigerate': 60,
        'freeze': 120,
        'rest': 10, 'proof': 60,
    }
    
    @staticmethod
    def extract_explicit_time(steps_text):
        """
        Extract explicitly mentioned cooking times from steps
        Returns: total minutes mentioned
        """
        if not steps_text:
            return 0
        
        total_minutes = 0
        steps_lower = steps_text.lower()
        
        # Look for hour patterns
        hour_matches = re.findall(r'(\d+)\s*hours?', steps_lower)
        for hours in hour_matches:
            total_minutes += int(hours) * 60
        
        # Look for minute patterns
        minute_matches = re.findall(r'(\d+)\s*(?:minutes?|mins?)', steps_lower)
        for minutes in minute_matches:
            total_minutes += int(minutes)
        
        # Look for second patterns (convert to minutes)
        second_matches = re.findall(r'(\d+)\s*(?:seconds?|secs?)', steps_lower)
        for seconds in second_matches:
            total_minutes += int(seconds) / 60
        
        return round(total_minutes)
    
    @staticmethod
    def estimate_from_methods(steps_text):
        """
        Estimate time based on cooking methods mentioned
        Returns: estimated minutes
        """
        if not steps_text:
            return 0, []
        
        steps_lower = steps_text.lower()
        estimated_minutes = 0
        methods_found = []
        
        for method, duration in TimePredictor.COOKING_METHOD_TIME.items():
            if method in steps_lower:
                estimated_minutes += duration
                methods_found.append(method)
        
        return estimated_minutes, methods_found
    
    @staticmethod
    def estimate_from_steps(step_count):
        """
        Estimate prep time based on number of steps
        Assumes ~5 minutes per step for prep
        """
        return step_count * 5
    
    @staticmethod
    def predict_time(steps_text, step_count):
        """
        Main method to predict total cooking time
        Returns: dictionary with time prediction and category
        """
        # Try to extract explicit time mentions
        explicit_time = TimePredictor.extract_explicit_time(steps_text)
        
        # Estimate from cooking methods
        method_time, methods = TimePredictor.estimate_from_methods(steps_text)
        
        # Estimate prep time from steps
        prep_time = TimePredictor.estimate_from_steps(step_count)
        
        # Calculate total time
        # Use explicit time if available, otherwise use estimates
        if explicit_time > 0:
            total_minutes = explicit_time
        else:
            total_minutes = prep_time + method_time
        
        # Ensure minimum time
        total_minutes = max(10, total_minutes)
        
        # Categorize time
        if total_minutes <= 30:
            category = "Quick"
            description = "Ready in 30 minutes or less"
        elif total_minutes <= 60:
            category = "Medium"
            description = "Takes about 30-60 minutes"
        else:
            category = "Long"
            description = f"Takes over an hour (about {total_minutes // 60}h {total_minutes % 60}m)"
        
        # Convert to hours and minutes for display
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            time_display = f"{hours}h {minutes}m"
        else:
            time_display = f"{minutes}m"
        
        return {
            'category': category,
            'total_minutes': total_minutes,
            'time_display': time_display,
            'description': description,
            'explicit_time_found': explicit_time > 0,
            'methods_detected': methods[:3]  # Top 3 methods
        }