"""
Difficulty Analyzer Module
Determines recipe difficulty based on multiple factors
"""

class DifficultyAnalyzer:
    # Keywords that indicate complexity
    COMPLEX_TECHNIQUES = [
        'fold', 'temper', 'caramelize', 'julienne', 'deglaze', 'braise',
        'sous vide', 'emulsify', 'flambe', 'reduce', 'blanch', 'poach',
        'sear', 'sauté', 'roast', 'braise', 'confit', 'marinate overnight',
        'knead', 'proof', 'ferment', 'clarify', 'strain', 'rest dough'
    ]
    
    MODERATE_TECHNIQUES = [
        'simmer', 'whisk', 'brown', 'season', 'coat', 'toss',
        'marinate', 'chill', 'grill', 'bake', 'steam', 'drain'
    ]
    
    @staticmethod
    def count_steps(steps_text):
        """Count number of steps in the recipe"""
        if not steps_text:
            return 0
        
        # Split by common delimiters
        lines = [line.strip() for line in steps_text.split('\n') if line.strip()]
        
        # Also check for numbered steps
        import re
        numbered_steps = re.findall(r'\d+[\.\)]\s+', steps_text)
        
        return max(len(lines), len(numbered_steps))
    
    @staticmethod
    def analyze_complexity(steps_text):
        """
        Analyze the complexity of cooking techniques used
        Returns: (complexity_score, techniques_found)
        """
        if not steps_text:
            return 0, []
        
        steps_lower = steps_text.lower()
        complexity_score = 0
        techniques_found = []
        
        # Check for complex techniques
        for technique in DifficultyAnalyzer.COMPLEX_TECHNIQUES:
            if technique in steps_lower:
                complexity_score += 3
                techniques_found.append(technique)
        
        # Check for moderate techniques
        for technique in DifficultyAnalyzer.MODERATE_TECHNIQUES:
            if technique in steps_lower:
                complexity_score += 1
                techniques_found.append(technique)
        
        return complexity_score, list(set(techniques_found))
    
    @staticmethod
    def analyze_difficulty(ingredients_list, steps_text):
        """
        Main method to determine recipe difficulty
        Returns: dictionary with difficulty level and reasoning
        """
        # Factor 1: Number of ingredients
        ingredient_count = len([i for i in ingredients_list if i.strip()])
        ingredient_score = 0
        
        if ingredient_count <= 5:
            ingredient_score = 1
        elif ingredient_count <= 10:
            ingredient_score = 2
        else:
            ingredient_score = 3
        
        # Factor 2: Number of steps
        step_count = DifficultyAnalyzer.count_steps(steps_text)
        step_score = 0
        
        if step_count <= 3:
            step_score = 1
        elif step_count <= 6:
            step_score = 2
        else:
            step_score = 3
        
        # Factor 3: Complexity of techniques
        complexity_score, techniques = DifficultyAnalyzer.analyze_complexity(steps_text)
        technique_score = min(3, complexity_score // 2)  # Normalize to 1-3
        
        # Calculate total score
        total_score = ingredient_score + step_score + technique_score
        
        # Determine difficulty level
        if total_score <= 4:
            difficulty = "Beginner"
            description = "Simple recipe perfect for cooking beginners"
        elif total_score <= 7:
            difficulty = "Intermediate"
            description = "Moderate difficulty, some cooking experience helpful"
        else:
            difficulty = "Advanced"
            description = "Complex recipe requiring culinary skills and patience"
        
        # Build reasoning
        factors = []
        factors.append(f"{ingredient_count} ingredients")
        factors.append(f"{step_count} steps")
        if techniques:
            factors.append(f"requires {len(techniques)} cooking technique(s)")
        
        return {
            'difficulty': difficulty,
            'score': total_score,
            'description': description,
            'factors': factors,
            'techniques_found': techniques[:5],  # Top 5 techniques
            'ingredient_count': ingredient_count,
            'step_count': step_count
        }