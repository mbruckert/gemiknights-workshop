
from google import genai
from google.genai import types
import os
import dotenv

# Load environment variables


# Initialize Gemini client


def get_difference_detection_function():
    """
        Define the json schema for the ai to return
        differences: array of objects, required: all fields
            - label: string
            - box_2d: array of numbers [ymin, xmin, ymax, xmax]
            - confidence: number between 0 and 1
        required: differences
    """
    return {}


def create_detection_prompt():
    return """"""


def detect_differences_with_ai(image1, image2):
    """
    1. Define the json schema for the ai to return
    2. Craft prompt to tell that ai what we want it to do
    3. Define the tools from the json schema we created
    4. Create the generate content config, providing it the tools, the tools config, and the thinking config
    5. Generate the content, providing it the prompt, the images, and the config
    6. Process the response, checking if the ai returned a function call
    7. If the ai returned a function call, return the differences
    8. If the ai did not return a function call, return an empty list
    9. If there is an error, return an empty list
    """
