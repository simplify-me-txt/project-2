/**
 * Frontend JavaScript for Cooking Recipe Analyzer
 * Handles form submission, API communication, and UI updates
 */

// Configuration
const API_BASE_URL = 'http://localhost:5005/api';
const HISTORY_KEY = 'recipe_analysis_history';
const THEME_KEY = 'recipe_analyzer_theme';

// DOM Elements
const recipeForm = document.getElementById('recipeForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const loadSampleBtn = document.getElementById('loadSampleBtn');
const downloadBtn = document.getElementById('downloadBtn');
const themeToggle = document.getElementById('themeToggle');
const resultCard = document.getElementById('resultCard');
const resultContent = document.getElementById('resultContent');
const historyCard = document.getElementById('historyCard');
const historyContent = document.getElementById('historyContent');

// State
let currentAnalysis = null;

/**
 * Initialize the application
 */
function init() {
    // Load theme preference
    loadTheme();
    
    // Load history
    loadHistory();
    
    // Event listeners
    recipeForm.addEventListener('submit', handleFormSubmit);
    clearBtn.addEventListener('click', clearForm);
    loadSampleBtn.addEventListener('click', loadSampleRecipe);
    downloadBtn.addEventListener('click', downloadResults);
    themeToggle.addEventListener('click', toggleTheme);
}

/**
 * Handle form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Get form data
    const recipeName = document.getElementById('recipeName').value.trim();
    const ingredientsText = document.getElementById('ingredients').value.trim();
    const steps = document.getElementById('steps').value.trim();
    
    // Parse ingredients (split by newline)
    const ingredients = ingredientsText.split('\n').filter(line => line.trim());
    
    // Validate
    if (!recipeName || ingredients.length === 0 || !steps) {
        showError('Please fill in all fields');
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    
    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipe_name: recipeName,
                ingredients: ingredients,
                steps: steps
            })
        });
        
        // Check if response is ok
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Store current analysis
            currentAnalysis = data;
            
            // Display results
            displayResults(data);
            
            // Generate and display charts (without blocking)
            generateCharts(data).catch(err => console.log('Charts optional:', err));
            
            // Save to history
            saveToHistory(data);
            
            // Scroll to results
            resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            showError(data.message || 'Analysis failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to analyze recipe. Please check if the backend is running on port 5005.');
    } finally {
        setLoadingState(false);
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    const { recipe_name, analysis } = data;
    
    let html = `
        <div class="result-section">
            <h3>📊 Overview</h3>
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-label">Total Calories</div>
                    <div class="stat-value">${analysis.calories.total} <span class="stat-unit">kcal</span></div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Per Serving</div>
                    <div class="stat-value">${analysis.calories.per_serving} <span class="stat-unit">kcal</span></div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Servings</div>
                    <div class="stat-value">${analysis.calories.servings}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Cooking Time</div>
                    <div class="stat-value">${analysis.time.display}</div>
                </div>
            </div>
        </div>
        
        <div class="result-section">
            <h3>🎯 Difficulty Level</h3>
            <div>
                <span class="badge badge-${analysis.difficulty.level.toLowerCase()}">${analysis.difficulty.level}</span>
                <p style="margin-top: 10px; color: var(--text-secondary);">${analysis.difficulty.description}</p>
            </div>
            <ul class="info-list mt-2">
                ${analysis.difficulty.factors.map(factor => `<li>📌 ${factor}</li>`).join('')}
            </ul>
            ${analysis.difficulty.techniques.length > 0 ? `
                <div style="margin-top: 15px;">
                    <strong>Techniques detected:</strong>
                    ${analysis.difficulty.techniques.map(t => `<span class="badge">${t}</span>`).join('')}
                </div>
            ` : ''}
        </div>
        
        <div class="result-section">
            <h3>⏱️ Time Estimate</h3>
            <div>
                <span class="badge badge-${analysis.time.category.toLowerCase()}">${analysis.time.category}</span>
                <p style="margin-top: 10px; color: var(--text-secondary);">${analysis.time.description}</p>
            </div>
            ${analysis.time.methods.length > 0 ? `
                <div style="margin-top: 15px;">
                    <strong>Cooking methods:</strong>
                    ${analysis.time.methods.map(m => `<span class="badge">${m}</span>`).join('')}
                </div>
            ` : ''}
        </div>
        
        <div class="result-section">
            <h3>🍽️ Dietary Information</h3>
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-label">Diet Type</div>
                    <div class="stat-value" style="font-size: 1.3rem;">${analysis.suggestions.diet_type}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Best For</div>
                    <div class="stat-value" style="font-size: 1.3rem;">${analysis.suggestions.meal_type}</div>
                </div>
            </div>
            <p style="margin-top: 15px; padding: 15px; background: var(--bg-primary); border-radius: 8px;">
                💡 <strong>Quick Tip:</strong> ${analysis.suggestions.quick_tip}
            </p>
        </div>
        
        <div class="result-section">
            <h3>💪 Healthy Alternatives</h3>
            <ul class="info-list">
                ${analysis.suggestions.healthy_alternatives.map(alt => `<li>🥗 ${alt}</li>`).join('')}
            </ul>
        </div>
        
        <div class="result-section">
            <h3>🌶️ Spice Recommendations</h3>
            <div>
                ${analysis.suggestions.spice_recommendations.map(spice => `<span class="badge">${spice}</span>`).join('')}
            </div>
        </div>
        
        <div class="result-section">
            <h3>👨‍🍳 Serving Tips</h3>
            <ul class="info-list">
                ${analysis.suggestions.serving_tips.map(tip => `<li>✨ ${tip}</li>`).join('')}
            </ul>
        </div>
        
        <div class="result-section">
            <h3>🔍 Calorie Breakdown</h3>
            <div style="max-height: 300px; overflow-y: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: var(--bg-tertiary);">
                            <th style="padding: 10px; text-align: left;">Ingredient</th>
                            <th style="padding: 10px; text-align: right;">Amount (g)</th>
                            <th style="padding: 10px; text-align: right;">Calories</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${analysis.calories.breakdown.map(item => `
                            <tr style="border-bottom: 1px solid var(--border-color);">
                                <td style="padding: 10px;">${item.ingredient}</td>
                                <td style="padding: 10px; text-align: right;">${item.estimated_grams}</td>
                                <td style="padding: 10px; text-align: right; font-weight: 600;">${item.calories}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    resultContent.innerHTML = html;
    resultCard.style.display = 'block';
}

/**
 * Generate and display charts
 */
async function generateCharts(data) {
    try {
        const response = await fetch(`${API_BASE_URL}/visualize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            console.error('Visualization failed');
            return;
        }
        
        const chartData = await response.json();
        
        if (chartData.status === 'success' && chartData.charts) {
            // Add charts to the results
            let chartsHtml = `
                <div class="result-section">
                    <h3>📊 Visual Analytics</h3>
                    
                    <div class="chart-container">
                        <h4>Calorie Breakdown</h4>
                        <img src="${chartData.charts.calorie_breakdown}" alt="Calorie Chart">
                    </div>
                    
                    <div class="chart-container">
                        <h4>Analysis Summary</h4>
                        <img src="${chartData.charts.summary_dashboard}" alt="Summary Chart">
                    </div>
                    
                    <div class="chart-container">
                        <h4>Nutrition Distribution</h4>
                        <img src="${chartData.charts.nutrition_pie}" alt="Nutrition Pie Chart">
                    </div>
                </div>
            `;
            
            // Append charts to results
            resultContent.innerHTML += chartsHtml;
        }
    } catch (error) {
        console.error('Chart generation error:', error);
        // Don't show error to user, charts are optional
    }
}

/**
 * Save analysis to local storage history
 */
function saveToHistory(data) {
    let history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    
    // Add new entry
    history.unshift({
        recipe_name: data.recipe_name,
        timestamp: new Date().toISOString(),
        data: data
    });
    
    // Keep only last 10 entries
    history = history.slice(0, 10);
    
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    loadHistory();
}

/**
 * Load and display history
 */
function loadHistory() {
    const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    
    if (history.length === 0) {
        historyCard.style.display = 'none';
        return;
    }
    
    historyCard.style.display = 'block';
    
    let html = '';
    history.forEach((item, index) => {
        const date = new Date(item.timestamp);
        html += `
            <div class="history-item" onclick="loadFromHistory(${index})">
                <div>
                    <div class="history-name">🍳 ${item.recipe_name}</div>
                    <div class="history-date">${date.toLocaleDateString()} ${date.toLocaleTimeString()}</div>
                </div>
                <span>📋</span>
            </div>
        `;
    });
    
    historyContent.innerHTML = html;
}

/**
 * Load recipe from history
 */
function loadFromHistory(index) {
    const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    const item = history[index];
    
    if (item) {
        currentAnalysis = item.data;
        displayResults(item.data);
        resultCard.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Download results as text file
 */
function downloadResults() {
    if (!currentAnalysis) return;
    
    const { recipe_name, analysis } = currentAnalysis;
    
    let text = `RECIPE ANALYSIS REPORT\n`;
    text += `${'='.repeat(50)}\n\n`;
    text += `Recipe: ${recipe_name}\n`;
    text += `Date: ${new Date().toLocaleString()}\n\n`;
    
    text += `OVERVIEW\n${'-'.repeat(50)}\n`;
    text += `Total Calories: ${analysis.calories.total} kcal\n`;
    text += `Per Serving: ${analysis.calories.per_serving} kcal\n`;
    text += `Servings: ${analysis.calories.servings}\n`;
    text += `Cooking Time: ${analysis.time.display}\n\n`;
    
    text += `DIFFICULTY\n${'-'.repeat(50)}\n`;
    text += `Level: ${analysis.difficulty.level}\n`;
    text += `${analysis.difficulty.description}\n`;
    text += `Factors: ${analysis.difficulty.factors.join(', ')}\n\n`;
    
    text += `DIETARY INFO\n${'-'.repeat(50)}\n`;
    text += `Diet Type: ${analysis.suggestions.diet_type}\n`;
    text += `Meal Type: ${analysis.suggestions.meal_type}\n\n`;
    
    text += `SUGGESTIONS\n${'-'.repeat(50)}\n`;
    text += `Healthy Alternatives:\n`;
    analysis.suggestions.healthy_alternatives.forEach(alt => {
        text += `  - ${alt}\n`;
    });
    text += `\nSpice Recommendations: ${analysis.suggestions.spice_recommendations.join(', ')}\n\n`;
    
    text += `Serving Tips:\n`;
    analysis.suggestions.serving_tips.forEach(tip => {
        text += `  - ${tip}\n`;
    });
    
    // Create and download file
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${recipe_name.replace(/[^a-z0-9]/gi, '_')}_analysis.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Clear form
 */
function clearForm() {
    recipeForm.reset();
    resultCard.style.display = 'none';
    currentAnalysis = null;
}

/**
 * Load sample recipe
 */
function loadSampleRecipe() {
    document.getElementById('recipeName').value = 'Creamy Chicken Pasta';
    document.getElementById('ingredients').value = `500g chicken breast
300g pasta
2 tablespoons olive oil
1 cup heavy cream
2 cloves garlic
1 onion
1 cup parmesan cheese
Salt and pepper to taste
Fresh basil for garnish`;
    
    document.getElementById('steps').value = `1. Bring a large pot of salted water to boil and cook pasta according to package directions
2. While pasta cooks, heat olive oil in a large skillet over medium-high heat
3. Season chicken with salt and pepper, add to skillet and cook for 6-7 minutes per side until golden brown
4. Remove chicken and set aside, add chopped onion and garlic to the same skillet
5. Sauté for 3 minutes until fragrant
6. Pour in heavy cream and bring to a simmer
7. Add parmesan cheese and stir until melted
8. Slice chicken and return to the skillet
9. Add drained pasta and toss everything together
10. Simmer for 2-3 minutes until sauce thickens
11. Garnish with fresh basil and serve hot`;
}

/**
 * Toggle theme
 */
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem(THEME_KEY, isDark ? 'dark' : 'light');
    themeToggle.querySelector('.theme-icon').textContent = isDark ? '☀️' : '🌙';
}

/**
 * Load theme preference
 */
function loadTheme() {
    const theme = localStorage.getItem(THEME_KEY);
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
        themeToggle.querySelector('.theme-icon').textContent = '☀️';
    }
}

/**
 * Set loading state
 */
function setLoadingState(isLoading) {
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoading = analyzeBtn.querySelector('.btn-loading');
    
    analyzeBtn.disabled = isLoading;
    btnText.style.display = isLoading ? 'none' : 'inline';
    btnLoading.style.display = isLoading ? 'inline' : 'none';
}

/**
 * Show error message
 */
function showError(message) {
    alert(`❌ Error: ${message}`);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

// Make loadFromHistory available globally
window.loadFromHistory = loadFromHistory;
