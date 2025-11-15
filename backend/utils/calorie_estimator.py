"""
Calorie Estimator Module
Estimates total calories based on ingredients using a comprehensive database
"""

class CalorieEstimator:
    # Comprehensive ingredient calorie database (per 100g or standard serving)
    CALORIE_DATABASE = {
        # Proteins
        'chicken': 165, 'chicken breast': 165, 'chicken thigh': 209,
        'beef': 250, 'ground beef': 250, 'steak': 271,
        'pork': 242, 'bacon': 541, 'ham': 145,
        'fish': 206, 'salmon': 208, 'tuna': 132, 'shrimp': 99,
        'egg': 155, 'eggs': 155, 'tofu': 76,
        
        # Dairy
        'milk': 42, 'cream': 340, 'heavy cream': 340, 'cheese': 402,
        'cheddar': 403, 'mozzarella': 280, 'parmesan': 431,
        'butter': 717, 'yogurt': 59, 'greek yogurt': 59,
        
        # Grains & Carbs
        'rice': 130, 'white rice': 130, 'brown rice': 111,
        'pasta': 131, 'spaghetti': 131, 'noodles': 138,
        'bread': 265, 'flour': 364, 'wheat flour': 364,
        'oats': 389, 'quinoa': 120, 'couscous': 112,
        
        # Vegetables
        'potato': 77, 'potatoes': 77, 'sweet potato': 86,
        'tomato': 18, 'tomatoes': 18, 'onion': 40, 'onions': 40,
        'garlic': 149, 'carrot': 41, 'carrots': 41,
        'broccoli': 34, 'spinach': 23, 'lettuce': 15,
        'bell pepper': 31, 'mushroom': 22, 'mushrooms': 22,
        'cucumber': 15, 'zucchini': 17, 'eggplant': 25,
        'cauliflower': 25, 'cabbage': 25, 'kale': 49,
        
        # Fruits
        'apple': 52, 'banana': 89, 'orange': 47,
        'strawberry': 32, 'blueberry': 57, 'mango': 60,
        'avocado': 160, 'lemon': 29, 'lime': 30,
        
        # Oils & Fats
        'oil': 884, 'olive oil': 884, 'vegetable oil': 884,
        'coconut oil': 862, 'ghee': 900,
        
        # Nuts & Seeds
        'almond': 579, 'almonds': 579, 'peanut': 567,
        'cashew': 553, 'walnut': 654, 'sesame': 573,
        
        # Condiments & Spices
        'salt': 0, 'pepper': 251, 'sugar': 387,
        'honey': 304, 'soy sauce': 53, 'vinegar': 18,
        'ketchup': 112, 'mayonnaise': 680, 'mustard': 66,
        
        # Legumes
        'beans': 127, 'black beans': 132, 'kidney beans': 127,
        'lentils': 116, 'chickpeas': 164, 'peas': 81,
        
        # Common ingredients
        'water': 0, 'stock': 10, 'broth': 10,
        'wine': 85, 'beer': 43, 'coconut milk': 230,
    }
    
    # Common measurement conversions to grams (approximate)
    MEASUREMENT_CONVERSIONS = {
        'cup': 240, 'cups': 240,
        'tablespoon': 15, 'tablespoons': 15, 'tbsp': 15,
        'teaspoon': 5, 'teaspoons': 5, 'tsp': 5,
        'ounce': 28, 'ounces': 28, 'oz': 28,
        'pound': 454, 'pounds': 454, 'lb': 454, 'lbs': 454,
        'gram': 1, 'grams': 1, 'g': 1,
        'kilogram': 1000, 'kilograms': 1000, 'kg': 1000,
        'piece': 100, 'pieces': 100,  # Assume 100g per piece
        'clove': 3, 'cloves': 3,  # Garlic clove
    }
    
    @staticmethod
    def extract_quantity(ingredient_line):
        """
        Extract quantity from ingredient line
        Returns: (quantity_in_grams, cleaned_ingredient_name)
        """
        import re
        
        line = ingredient_line.lower().strip()
        
        # Pattern to match number + measurement + ingredient
        # e.g., "2 cups rice", "3 tablespoons butter", "500g chicken"
        pattern = r'(\d+\.?\d*)\s*([a-z]+)?\s+(.+)'
        match = re.match(pattern, line)
        
        if match:
            quantity = float(match.group(1))
            measurement = match.group(2) if match.group(2) else 'gram'
            ingredient = match.group(3).strip()
            
            # Convert to grams
            conversion_factor = CalorieEstimator.MEASUREMENT_CONVERSIONS.get(
                measurement, 100  # Default to 100g if unknown
            )
            quantity_in_grams = quantity * conversion_factor
            
            return quantity_in_grams, ingredient
        
        # If no quantity found, assume standard serving (100g)
        return 100, line
    
    @staticmethod
    def find_ingredient_match(ingredient_name):
        """
        Find the best match for an ingredient in the database
        Uses keyword matching for flexibility
        """
        ingredient_lower = ingredient_name.lower()
        
        # Direct match
        if ingredient_lower in CalorieEstimator.CALORIE_DATABASE:
            return CalorieEstimator.CALORIE_DATABASE[ingredient_lower]
        
        # Partial match - check if any database key is in the ingredient
        for key, calories in CalorieEstimator.CALORIE_DATABASE.items():
            if key in ingredient_lower or ingredient_lower in key:
                return calories
        
        # No match found - return average calorie value
        return 150  # Average of common ingredients
    
    @staticmethod
    def estimate_calories(ingredients_list):
        """
        Main method to estimate total calories from ingredients list
        Returns: dictionary with total calories and breakdown
        """
        total_calories = 0
        breakdown = []
        
        for ingredient in ingredients_list:
            if not ingredient.strip():
                continue
            
            # Extract quantity and ingredient name
            quantity_grams, ingredient_name = CalorieEstimator.extract_quantity(ingredient)
            
            # Find calorie value per 100g
            calories_per_100g = CalorieEstimator.find_ingredient_match(ingredient_name)
            
            # Calculate calories for this ingredient
            ingredient_calories = (calories_per_100g * quantity_grams) / 100
            total_calories += ingredient_calories
            
            breakdown.append({
                'ingredient': ingredient.strip(),
                'estimated_grams': round(quantity_grams, 1),
                'calories': round(ingredient_calories, 1)
            })
        
        return {
            'total_calories': round(total_calories),
            'breakdown': breakdown,
            'servings_estimate': max(1, len(ingredients_list) // 3)  # Rough estimate
        }