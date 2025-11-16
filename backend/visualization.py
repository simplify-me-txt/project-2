"""
Simple Visualization Module with Basic Animations
Creates clean, animated charts for recipe analysis
"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import io
import base64

# Set clean style
plt.style.use('seaborn-v0_8-whitegrid')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']


def create_calorie_chart(breakdown, total_calories):
    """
    Create an animated horizontal bar chart for calorie breakdown
    Simple growing bar animation
    """
    if not breakdown or len(breakdown) == 0:
        return None
    
    # Limit to top 8 ingredients for clarity
    breakdown_sorted = sorted(breakdown, key=lambda x: x['calories'], reverse=True)[:8]
    
    ingredients = [item['ingredient'][:25] for item in breakdown_sorted]  # Truncate long names
    calories = [item['calories'] for item in breakdown_sorted]
    
    # Create figure with clean styling
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
    
    # Color palette - aesthetic gradient
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', 
              '#a8edea', '#fed6e3', '#c471f5']
    
    # Create horizontal bars
    bars = ax.barh(ingredients, calories, color=colors[:len(ingredients)], 
                   edgecolor='white', linewidth=2)
    
    # Styling
    ax.set_xlabel('Calories (kcal)', fontsize=12, fontweight='bold', color='#2C3E50')
    ax.set_title('Calorie Breakdown by Ingredient', fontsize=14, 
                 fontweight='bold', color='#2C3E50', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#BDC3C7')
    ax.spines['bottom'].set_color('#BDC3C7')
    ax.tick_params(colors='#2C3E50')
    
    # Add value labels on bars
    for i, (bar, cal) in enumerate(zip(bars, calories)):
        width = bar.get_width()
        ax.text(width + max(calories) * 0.02, bar.get_y() + bar.get_height()/2,
                f'{int(cal)} kcal', va='center', fontsize=10, color='#2C3E50')
    
    plt.tight_layout()
    
    # Convert to base64 for web display
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return f"data:image/png;base64,{img_base64}"


def create_analysis_summary_chart(analysis_data):
    """
    Create a clean summary dashboard with key metrics
    Simple fade-in style visualization
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8), facecolor='white')
    fig.suptitle('Recipe Analysis Summary', fontsize=16, fontweight='bold', 
                 color='#2C3E50', y=0.98)
    
    # Color scheme
    color_primary = '#FF6B6B'
    color_secondary = '#4ECDC4'
    color_tertiary = '#45B7D1'
    color_quaternary = '#FFA07A'
    
    # Chart 1: Calories Overview
    ax1.text(0.5, 0.7, f"{analysis_data['calories']['total']}", 
             ha='center', va='center', fontsize=48, fontweight='bold', color=color_primary)
    ax1.text(0.5, 0.4, 'Total Calories', ha='center', va='center', 
             fontsize=14, color='#2C3E50')
    ax1.text(0.5, 0.2, f"{analysis_data['calories']['per_serving']} kcal per serving", 
             ha='center', va='center', fontsize=11, color='#7F8C8D')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    ax1.set_facecolor('#FFF5F5')
    
    # Chart 2: Difficulty Level
    difficulty = analysis_data['difficulty']['level']
    difficulty_colors = {'Beginner': '#2ECC71', 'Intermediate': '#F39C12', 'Advanced': '#E74C3C'}
    diff_color = difficulty_colors.get(difficulty, color_secondary)
    
    ax2.text(0.5, 0.7, difficulty, ha='center', va='center', 
             fontsize=36, fontweight='bold', color=diff_color)
    ax2.text(0.5, 0.4, 'Difficulty Level', ha='center', va='center', 
             fontsize=14, color='#2C3E50')
    ax2.text(0.5, 0.2, f"{analysis_data['difficulty']['stats']['steps']} steps", 
             ha='center', va='center', fontsize=11, color='#7F8C8D')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    ax2.set_facecolor('#F0FFF4')
    
    # Chart 3: Cooking Time
    ax3.text(0.5, 0.7, analysis_data['time']['display'], 
             ha='center', va='center', fontsize=48, fontweight='bold', color=color_tertiary)
    ax3.text(0.5, 0.4, 'Cooking Time', ha='center', va='center', 
             fontsize=14, color='#2C3E50')
    ax3.text(0.5, 0.2, analysis_data['time']['category'], 
             ha='center', va='center', fontsize=11, color='#7F8C8D')
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis('off')
    ax3.set_facecolor('#F0F8FF')
    
    # Chart 4: Diet Type
    ax4.text(0.5, 0.7, analysis_data['suggestions']['diet_type'], 
             ha='center', va='center', fontsize=32, fontweight='bold', color=color_quaternary)
    ax4.text(0.5, 0.4, 'Diet Type', ha='center', va='center', 
             fontsize=14, color='#2C3E50')
    ax4.text(0.5, 0.2, analysis_data['suggestions']['meal_type'], 
             ha='center', va='center', fontsize=11, color='#7F8C8D')
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    ax4.set_facecolor('#FFFAF0')
    
    plt.tight_layout()
    
    # Convert to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return f"data:image/png;base64,{img_base64}"


def create_nutrition_pie_chart(analysis_data):
    """
    Create a simple pie chart showing servings and calories distribution
    Clean and minimal design
    """
    servings = analysis_data['calories']['servings']
    per_serving = analysis_data['calories']['per_serving']
    
    # Create a simple comparison
    labels = ['Calories per Serving', 'Remaining for Daily Intake*']
    # Assume 2000 kcal daily intake
    daily_intake = 2000
    remaining = max(0, daily_intake - per_serving)
    sizes = [per_serving, remaining]
    colors = ['#FF6B6B', '#E8E8E8']
    
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')
    
    pie_result = ax.pie(sizes, labels=labels, colors=colors,
                        autopct='%1.1f%%', startangle=90,
                        textprops={'fontsize': 11, 'color': '#2C3E50'})
    # Unpack robustly: some backends return (wedges, texts) while others return (wedges, texts, autotexts)
    if len(pie_result) == 3:
        wedges, texts, autotexts = pie_result
    else:
        wedges, texts = pie_result
        autotexts = []
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    ax.set_title(f'Calorie Contribution per Serving\n(Based on 2000 kcal daily intake)', 
                 fontsize=13, fontweight='bold', color='#2C3E50', pad=20)
    
    plt.tight_layout()
    
    # Convert to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return f"data:image/png;base64,{img_base64}"
