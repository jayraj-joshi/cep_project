# Install required packages if not already installed
# Run these in your terminal:
# pip install flask google-generativeai flask-cors

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import base64

app = Flask(__name__)
CORS(app)  # Allow all origins

# Configure the Gemini API key
API_KEY = "AIzaSyDkFtj3edbzUiyn6O2hViakpQSWgJkdQQc"  # Replace with your actual Gemini API key
genai.configure(api_key=API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-pro')

# Helper function to encode image to base64
def load_image_to_base64(image_file):
    image_data = image_file.read()
    return base64.b64encode(image_data).decode('utf-8')

# Endpoint: Analyze image and return nutrition advice
@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    try:
        # Check if image is in the request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Encode image
        image_base64 = load_image_to_base64(image_file)

        # Prompt for Gemini model
        prompt = """ 
        You are a professional nutritionist who advises whether to consume a foodstuff or not by analyzing ingredients and nutritional information.
        Give a rating of 0-5 to foodstuff.
        Give the answer in JSON format.
        The JSON format should be like this:
        {
            "rating": 0-5,
            "reason": "reason for rating",
            "advice": "advice to consume or not"
        }
        """

        content = [
            {
                "mime_type": image_file.mimetype,
                "data": image_base64
            },
            {"text": prompt}
        ]

        # Get Gemini response
        response = model.generate_content(content)
        raw_output = response.text.strip()

        # Remove markdown wrapping like ```json ... ```
        if raw_output.startswith("```json") and raw_output.endswith("```"):
            cleaned_output = raw_output[7:-3].strip()
        elif raw_output.startswith("```") and raw_output.endswith("```"):
            cleaned_output = raw_output[3:-3].strip()
        else:
            cleaned_output = raw_output

        # Return clean JSON string
        return jsonify({
            "status": "success",
            "analysis": cleaned_output
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Run the app
if __name__ == '__main__':
    app.run()

