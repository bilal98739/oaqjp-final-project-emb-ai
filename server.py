"""
Flask web server for Emotion Detection Application
Provides routes to render HTML page and detect emotions using the emotion_detector function.
"""

from flask import Flask, request, render_template
from EmotionDetection import emotion_detector

app = Flask(__name__)

@app.route("/")
def index():
    """
    Render the main HTML page.

    Returns:
        str: Rendered HTML page (index.html)
    """
    return render_template("index.html")


@app.route("/emotionDetector", methods=["POST"])
def detect_emotion():
    """
    API route to detect emotions from user input.

    Returns:
        str: Formatted emotion response or error message for blank input
    """
    text_to_analyze = request.form["text"].strip()
    response = emotion_detector(text_to_analyze)

    # Error handling for blank input or None-dominant emotion
    if response.get('status_code') == 400 or response['dominant_emotion'] is None:
        return "Invalid text! Please try again!"

    return (
        f"For the given statement, the system response is 'anger': {response['anger']}, "
        f"'disgust': {response['disgust']}, 'fear': {response['fear']}, "
        f"'joy': {response['joy']} and 'sadness': {response['sadness']}. "
        f"The dominant emotion is {response['dominant_emotion']}."
    )


if __name__ == "__main__":
    """
    Run the Flask web server.
    """
    app.run(host="0.0.0.0", port=5000)
