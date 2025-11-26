# Skincare Expert System

An AI-powered web application that provides personalized skincare recommendations using a rule-based expert system with MYCIN-style certainty factors.

## Features

- **Goal-Based Interface**: Select skincare concerns (acne, anti-aging, pigmentation, etc.)
- **Goal-Specific Symptoms**: Input symptoms tailored to your selected concern
- **Expert System Inference**: Forward and backward chaining algorithms
- **Certainty Factors**: MYCIN-style confidence scoring for recommendations
- **Full Analysis Mode**: Comprehensive symptom input for all skin conditions
- **Modern UI**: Responsive, clean interface with smooth interactions

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd expertsys
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open in browser:
```
http://localhost:5000
```

### Prerequisites
- Vercel account (free at https://vercel.com)
- Git repository (GitHub, GitLab, or Bitbucket)

### Steps

1. **Push to Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

2. **Deploy on Vercel**
   - Go to https://vercel.com/new
   - Select your Git repository
   - Vercel will auto-detect Flask and configure the build
   - Click "Deploy"

3. **Alternative: Vercel CLI**
   ```bash
   npm i -g vercel
   vercel
   ```
   Follow the prompts and your app will be deployed!

### Configuration

The `vercel.json` file contains the deployment configuration:
- Python runtime version: 3.11
- Build command: Installs dependencies
- All routes route to app.py for Flask routing

### Environment Variables

If needed, add environment variables in Vercel dashboard:
- Project Settings → Environment Variables
- Common ones: `FLASK_ENV=production`, `DEBUG=False`

## Project Structure

```
expertsys/
├── app.py                 # Flask application
├── expert_system.py       # Expert system engine
├── skincare.json          # Knowledge base (200 rules)
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment config
├── build.json            # Build configuration
└── templates/
    ├── landing.html      # Goal selection page
    ├── goal-symptoms.html # Goal-specific symptom input
    └── index.html        # Full analysis page
```

## API Endpoints

### GET `/`
Landing page with goal cards

### GET `/goal-symptoms`
Goal-specific symptom input page (query param: `goal`)

### GET `/analysis`
Full analysis page with all symptoms

### GET `/api/symptoms`
Returns available symptoms organized by category

### GET `/api/goals`
Returns all possible treatment goals

### POST `/api/diagnose`
Analyzes symptoms and returns recommendations
- Request body:
  ```json
  {
    "symptoms": {"Symptom1": 0.9, "Symptom2": 0.7},
    "method": "forward",
    "threshold": 0.3
  }
  ```

## Knowledge Base

The system uses 200+ rules with:
- If-Then logic expressions
- Certainty factors (0-1 range)
- Priority-based conflict resolution
- Forward and backward chaining inference

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## License

MIT

## Contributing

Feel free to submit issues and enhancement requests!

## Support

For issues or questions, please open an issue on the repository.
#
