"""
Flask Backend for Cooking Recipe Analyzer
Main application file - Serves both API and Frontend
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.calorie_estimator import CalorieEstimator
from utils.difficulty_analyzer import DifficultyAnalyzer
from utils.time_predictor import TimePredictor
from utils.suggestion_generator import SuggestionGenerator

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for frontend communication

# Configure app
app.config['JSON_SORT_KEYS'] = False


# ===== FRONTEND ROUTES =====

@app.route('/')
def serve_frontend():
    """Serve the main HTML file"""
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve CSS, JS, and other static files"""
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    return send_from_directory(frontend_dir, path)
    return send_from_directory(app.static_folder, path)


# ===== API ROUTES =====

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Cooking Recipe Analyzer API is running',
        'version': '1.0.0',
        'port': 5002
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_recipe():
    """
    Main endpoint to analyze a recipe
    Expects JSON body with: recipe_name, ingredients (array), steps (string)
    """
    try:
        # Get data from request
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        recipe_name = data.get('recipe_name', 'Untitled Recipe')
        ingredients = data.get('ingredients', [])
        steps = data.get('steps', '')
        
        # Validate ingredients and steps
        if not ingredients or len(ingredients) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Please provide at least one ingredient'
            }), 400
        
        if not steps or steps.strip() == '':
            return jsonify({
                'status': 'error',
                'message': 'Please provide cooking steps'
            }), 400
        
        # Filter empty ingredients
        ingredients = [ing.strip() for ing in ingredients if ing.strip()]
        
        # 1. Estimate Calories
        calorie_data = CalorieEstimator.estimate_calories(ingredients)
        
        # 2. Analyze Difficulty
        difficulty_data = DifficultyAnalyzer.analyze_difficulty(ingredients, steps)
        
        # 3. Predict Cooking Time
        time_data = TimePredictor.predict_time(steps, difficulty_data['step_count'])
        
        # 4. Generate Suggestions
        suggestions = SuggestionGenerator.generate_suggestions(
            ingredients,
            steps,
            difficulty_data['difficulty'],
            calorie_data['total_calories'],
            calorie_data['servings_estimate']
        )
        
        # Compile response
        response = {
            'status': 'success',
            'recipe_name': recipe_name,
            'analysis': {
                # Calorie Information
                'calories': {
                    'total': calorie_data['total_calories'],
                    'per_serving': round(
                        calorie_data['total_calories'] / calorie_data['servings_estimate']
                    ),
                    'servings': calorie_data['servings_estimate'],
                    'breakdown': calorie_data['breakdown']
                },
                
                # Difficulty Information
                'difficulty': {
                    'level': difficulty_data['difficulty'],
                    'description': difficulty_data['description'],
                    'score': difficulty_data['score'],
                    'factors': difficulty_data['factors'],
                    'techniques': difficulty_data['techniques_found'],
                    'stats': {
                        'ingredients': difficulty_data['ingredient_count'],
                        'steps': difficulty_data['step_count']
                    }
                },
                
                # Time Information
                'time': {
                    'category': time_data['category'],
                    'total_minutes': time_data['total_minutes'],
                    'display': time_data['time_display'],
                    'description': time_data['description'],
                    'methods': time_data['methods_detected']
                },
                
                # Suggestions
                'suggestions': {
                    'diet_type': suggestions['diet_type'],
                    'meal_type': suggestions['meal_type'],
                    'healthy_alternatives': suggestions['healthy_alternatives'],
                    'spice_recommendations': suggestions['spice_suggestions'],
                    'serving_tips': suggestions['serving_tips'],
                    'quick_tip': suggestions['quick_tip']
                }
            }
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }), 500


@app.route('/api/ingredients', methods=['GET'])
def get_ingredient_database():
    """
    Optional endpoint to get list of known ingredients
    Useful for autocomplete features
    """
    try:
        ingredients = list(CalorieEstimator.CALORIE_DATABASE.keys())
        return jsonify({
            'status': 'success',
            'count': len(ingredients),
            'ingredients': sorted(ingredients)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/visualize', methods=['POST'])
def visualize_recipe():
    """
    Generate visualization charts for recipe analysis
    Expects the same data as /api/analyze endpoint
    """
    try:
        from visualization import (create_calorie_chart, 
                                   create_analysis_summary_chart,
                                   create_nutrition_pie_chart)
        
        # Get analysis data from request
        data = request.get_json()
        
        if not data or 'analysis' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Analysis data required'
            }), 400
        
        analysis = data['analysis']
        
        # Generate charts
        calorie_chart = create_calorie_chart(
            analysis['calories']['breakdown'],
            analysis['calories']['total']
        )
        
        summary_chart = create_analysis_summary_chart(analysis)
        
        nutrition_pie = create_nutrition_pie_chart(analysis)
        
        return jsonify({
            'status': 'success',
            'charts': {
                'calorie_breakdown': calorie_chart,
                'summary_dashboard': summary_chart,
                'nutrition_pie': nutrition_pie
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Visualization error: {str(e)}'
        }), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


# Run the application
if __name__ == '__main__':
    print("=" * 60)
    print("🍳 Cooking Recipe Analyzer - Starting...")
    print("=" * 60)
    print(f"🌐 Application running on: http://localhost:5005")
    print(f"📱 Open in browser: http://localhost:5005")
    print(f"📡 API endpoint: http://localhost:5005/api/analyze")
    print("=" * 60)
    print("✅ Server is ready! Press CTRL+C to stop.")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5005)
