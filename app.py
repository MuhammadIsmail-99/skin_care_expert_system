"""
Flask Web Application for Skincare Expert System
Run with: python app.py
Access at: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from expert_system import ExpertSystem
import os

app = Flask(__name__)
app.secret_key = 'skincare_expert_system_2024'

# Initialize expert system
es = None

def init_expert_system():
    """Initialize or reset the expert system."""
    global es
    es = ExpertSystem('skincare.json')
    return es


@app.route('/')
def landing():
    """Landing page with goal cards."""
    return render_template('landing.html')


@app.route('/goal-symptoms')
def goal_symptoms():
    """Goal-specific symptom input page."""
    return render_template('goal-symptoms.html')


@app.route('/analysis')
def analysis():
    """Full analysis page with all symptoms."""
    return render_template('index.html')


@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """Get list of available symptoms/facts."""
    symptoms = {
        "Skin Type": [
            "OilySkin", "DrySkin", "CombinationSkin", "SensitiveSkin",
            "Dehydrated", "NormalSkin"
        ],
        "Acne & Blemishes": [
            "HasAcne", "HasBlackheads", "HasWhiteheads", "CysticAcne",
            "HormonalAcne", "FungalAcne", "HasAcneScars", "PostInflammatoryMarks",
            "PainfulNodules"
        ],
        "Aging Concerns": [
            "HasWrinkles", "FineLines", "SaggingSkin", "LossOfElasticity",
            "CrowsFeet", "NasolabialFolds", "ForeheadWrinkles", "NeckWrinkles",
            "AgeOver40", "DecolletageLines", "SmileLines", "MarionetteLines"
        ],
        "Pigmentation": [
            "HasDarkSpots", "HasHyperpigmentation", "HasMelasma", 
            "SunSpots", "AgeSpots", "UnevenSkinTone", "Blotchiness",
            "HormonalDarkPatches", "Photoaging", "FrecklesIncrease"
        ],
        "Texture & Pores": [
            "HasLargePores", "RoughTexture", "BumpySkin", "DullSkin",
            "LackOfGlow", "ClosedComedones", "CloggedPores", "OilyTZone",
            "ShinyNose", "GreasyFeel", "ShineAllDay"
        ],
        "Redness & Sensitivity": [
            "HasRedness", "FacialFlushing", "HasRosacea", "HasIrritation",
            "BurningSensation", "AllergicReaction", "ContactDermatitis"
        ],
        "Dryness & Hydration": [
            "SkinFeelsTight", "Flaking", "PeelingSkin"
        ],
        "Medical Conditions": [
            "HasEczema", "HasDermatitis", "HasPsoriasis", "AtopicDermatitis",
            "SeborrheicDermatitis", "PerioralDermatitis", "KeratosisPilaris",
            "ChickenSkin", "TineaVersicolor", "FungalPatches"
        ],
        "Body Concerns": [
            "ChestAcne", "BackAcne", "StretchMarks", "Striae",
            "HasCellulite", "DimpledSkin", "IngrownHairs", "RazorBumps"
        ],
        "Eye Area": [
            "UnderEyeBags", "DarkCircles", "CrowsFeet"
        ],
        "Lifestyle Factors": [
            "DailySunExposure", "UsesSPF", "SmokingHabit", "HighStress",
            "PoorSleep", "PollutionExposure", "UrbanEnvironment",
            "BlueLightExposure", "HighScreenTime", "IsPregnant",
            "InMenopause", "HotFlashes"
        ],
        "Seasons & Environment": [
            "WinterSeason", "ColdWeather", "SummerSeason", "HighHumidity",
            "AirConditioning", "IndoorDryness"
        ],
        "Other Symptoms": [
            "TiredAppearance", "PuffyFace", "MorningSwelling",
            "Maskne", "MaskRelatedBreakouts", "ChronicItching",
            "LipDryness", "ChappedLips", "Sunburn", "UVDamage"
        ]
    }
    return jsonify(symptoms)


@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Process symptoms and return diagnosis."""
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', {})
        method = data.get('method', 'forward')
        goal = data.get('goal', '')
        threshold = float(data.get('threshold', 0.3))
        
        # Initialize new expert system
        es = init_expert_system()
        
        # Set all symptoms
        for symptom, cf in symptoms.items():
            if cf > 0:
                es.set_fact(symptom, float(cf))
        
        # Run inference
        if method == 'backward' and goal:
            goal_cf = es.backward_chaining(goal, threshold=threshold)
            result = {
                'method': 'backward',
                'goal': goal,
                'goal_cf': round(goal_cf, 3),
                'success': goal_cf >= threshold
            }
        else:
            es.forward_chaining(threshold=threshold)
            result = {
                'method': 'forward'
            }
        
        # Get working memory
        working_memory = {}
        for symbol, cf in es.working_memory.items():
            working_memory[str(symbol)] = round(cf, 3)
        
        # Get fired rules
        fired_rules = es.fired_rules
        
        # Extract recommendations and conditions
        recommendations = {}
        conditions = {}
        
        treatment_prefixes = [
            'Use', 'Consult', 'Take', 'Avoid', 'Stop', 'Reduce',
            'Increase', 'Switch', 'Extend', 'Consider', 'Change',
            'Keep', 'Disinfect', 'Clean', 'Shower', 'Discard',
            'Simplify', 'Separate', 'Continue', 'Carry', 'Double', 'No'
        ]
        
        for symbol_str, cf in working_memory.items():
            if cf >= threshold:
                is_treatment = any(symbol_str.startswith(prefix) for prefix in treatment_prefixes)
                
                if is_treatment:
                    recommendations[symbol_str] = cf
                elif symbol_str not in symptoms:
                    conditions[symbol_str] = cf
        
        result.update({
            'working_memory': working_memory,
            'conditions': conditions,
            'recommendations': recommendations,
            'fired_rules': fired_rules,
            'num_rules_fired': len(fired_rules)
        })
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/goals', methods=['GET'])
def get_goals():
    """Get list of possible treatment goals for backward chaining."""
    goals = [
        "UseSalicylicAcidCleanser",
        "UseHyaluronicAcidSerum",
        "UseRetinolTreatment",
        "UseVitaminCSerum",
        "UseNiacinamideSerum",
        "UseBHAExfoliant",
        "UseAHAExfoliant",
        "UseBroadSpectrumSPF50",
        "UseCeramideCream",
        "UsePeptideSerum",
        "UseAzelaic AcidCream",
        "ConsultDermatologist",
        "UseBenzoylPeroxideBodyWash",
        "UseGlycerinMoisturizer",
        "UseCentellaToner",
        "UseAlphaArbutinSerum",
        "UseCaffeineEyeCream",
        "UseKojicAcidSerum",
        "UseBakuchiolSerum"
    ]
    return jsonify(sorted(goals))


if __name__ == '__main__':
    if not os.path.exists('skincare.json'):
        print("Error: skincare.json not found!")
        print("Please make sure the knowledge base file is in the same directory.")
        exit(1)
    
    print("=" * 70)
    print("SKINCARE EXPERT SYSTEM - WEB INTERFACE")
    print("=" * 70)
    print("\nStarting Flask server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    print("=" * 70)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)