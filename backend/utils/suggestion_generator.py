"""
Suggestion Generator Module
Provides helpful cooking suggestions based on recipe analysis
"""

class SuggestionGenerator:
    # Ingredient categorization
    MEAT_INGREDIENTS = [
        'chicken', 'beef', 'pork', 'lamb', 'turkey', 'duck',
        'fish', 'salmon', 'tuna', 'shrimp', 'prawn', 'crab',
        'bacon', 'ham', 'sausage', 'meat'
    ]
    
    VEG_INGREDIENTS = [
        'tofu', 'paneer', 'beans', 'lentils', 'chickpeas',
        'mushroom', 'eggplant', 'jackfruit'
    ]
    
    HIGH_CALORIE_INGREDIENTS = [
        'butter', 'cream', 'cheese', 'oil', 'mayonnaise',
        'bacon', 'sugar', 'chocolate', 'nuts'
    ]
    
    HEALTHY_ALTERNATIVES = {
        'butter': 'olive oil or avocado',
        'cream': 'Greek yogurt or coconut cream',
        'white rice': 'brown rice or quinoa',
        'pasta': 'whole wheat pasta or zucchini noodles',
        'sugar': 'honey or maple syrup',
        'oil': 'cooking spray or broth',
        'mayonnaise': 'Greek yogurt or avocado',
        'sour cream': 'Greek yogurt',
        'ground beef': 'ground turkey or lean beef',
        'bacon': 'turkey bacon',
        'cheese': 'reduced-fat cheese',
        'bread': 'whole grain bread',
    }
    
    SPICE_SUGGESTIONS = {
        'chicken': ['paprika', 'thyme', 'rosemary', 'garlic powder'],
        'beef': ['black pepper', 'garlic', 'rosemary', 'oregano'],
        'fish': ['lemon', 'dill', 'parsley', 'caper'],
        'pasta': ['basil', 'oregano', 'garlic', 'parmesan'],
        'rice': ['cumin', 'turmeric', 'bay leaf', 'cardamom'],
        'vegetables': ['garlic', 'onion', 'herbs', 'chili flakes'],
        'soup': ['bay leaf', 'thyme', 'black pepper', 'parsley'],
    }
    
    @staticmethod
    def detect_diet_type(ingredients_list):
        """
        Detect if recipe is vegetarian, non-vegetarian, or vegan
        """
        ingredients_lower = ' '.join(ingredients_list).lower()
        
        is_non_veg = any(meat in ingredients_lower for meat in SuggestionGenerator.MEAT_INGREDIENTS)
        
        dairy_items = ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'ghee', 'egg']
        has_dairy = any(item in ingredients_lower for item in dairy_items)
        
        if is_non_veg:
            return 'Non-Vegetarian'
        elif has_dairy:
            return 'Vegetarian'
        else:
            return 'Vegan'
    
    @staticmethod
    def generate_healthy_alternatives(ingredients_list):
        """
        Suggest healthier alternatives for high-calorie ingredients
        """
        alternatives = []
        ingredients_lower = ' '.join(ingredients_list).lower()
        
        for ingredient, alternative in SuggestionGenerator.HEALTHY_ALTERNATIVES.items():
            if ingredient in ingredients_lower:
                alternatives.append(f"Replace {ingredient} with {alternative}")
        
        return alternatives[:3]  # Return top 3 suggestions
    
    @staticmethod
    def suggest_spices(ingredients_list):
        """
        Suggest complementary spices based on main ingredients
        """
        ingredients_lower = ' '.join(ingredients_list).lower()
        suggested_spices = set()
        
        for ingredient_key, spices in SuggestionGenerator.SPICE_SUGGESTIONS.items():
            if ingredient_key in ingredients_lower:
                suggested_spices.update(spices)
        
        if not suggested_spices:
            # Default suggestions
            suggested_spices = ['salt', 'black pepper', 'garlic', 'herbs']
        
        return list(suggested_spices)[:4]
    
    @staticmethod
    def generate_serving_tips(difficulty, total_calories, servings):
        """
        Generate serving and presentation tips
        """
        tips = []
        
        # Based on difficulty
        if difficulty == 'Beginner':
            tips.append("Great recipe to start your cooking journey!")
        elif difficulty == 'Advanced':
            tips.append("Take your time and follow each step carefully")
        
        # Based on calories
        calories_per_serving = total_calories / servings if servings > 0 else total_calories
        
        if calories_per_serving > 600:
            tips.append("This is a hearty meal - consider serving smaller portions")
        elif calories_per_serving < 300:
            tips.append("Light meal - perfect for lunch or as a side dish")
        
        # General tips
        tips.extend([
            "Taste and adjust seasoning before serving",
            "Prepare ingredients (mise en place) before cooking",
            "Let the dish rest for a few minutes before serving"
        ])
        
        return tips[:3]
    
    @staticmethod
    def generate_suggestions(ingredients_list, steps_text, difficulty, total_calories, servings):
        """
        Main method to generate all suggestions
        Returns: dictionary with various suggestions
        """
        # Detect diet type
        diet_type = SuggestionGenerator.detect_diet_type(ingredients_list)
        
        # Generate healthy alternatives
        healthy_alternatives = SuggestionGenerator.generate_healthy_alternatives(ingredients_list)
        
        # Suggest spices
        spice_suggestions = SuggestionGenerator.suggest_spices(ingredients_list)
        
        # Generate serving tips
        serving_tips = SuggestionGenerator.generate_serving_tips(
            difficulty, total_calories, servings
        )
        
        # Meal type suggestion based on ingredients
        ingredients_lower = ' '.join(ingredients_list).lower()
        if any(word in ingredients_lower for word in ['egg', 'pancake', 'cereal', 'toast']):
            meal_type = 'Breakfast'
        elif any(word in ingredients_lower for word in ['salad', 'sandwich', 'soup']):
            meal_type = 'Lunch'
        elif any(word in ingredients_lower for word in ['steak', 'roast', 'casserole']):
            meal_type = 'Dinner'
        else:
            meal_type = 'Any time'
        
        return {
            'diet_type': diet_type,
            'meal_type': meal_type,
            'healthy_alternatives': healthy_alternatives if healthy_alternatives else ['Recipe looks healthy!'],
            'spice_suggestions': spice_suggestions,
            'serving_tips': serving_tips,
            'quick_tip': f"This is a {diet_type.lower()} {meal_type.lower()} recipe"
        }