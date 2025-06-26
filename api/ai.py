
from google import genai
from google.genai import types
import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))


def get_difference_detection_function():
    return {
        "name": "report_image_differences",
        "description": "Reports all differences found between two images with precise bounding box coordinates and detailed descriptions.",
        "parameters": {
            "type": "object",
            "properties": {
                "differences": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": "Detailed description of the specific difference found"
                            },
                            "box_2d": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Bounding box coordinates in format [ymin, xmin, ymax, xmax] normalized to 0-1000. IT'S VERY IMPORTANT THAT YOU DRAW THE CORRECT BOUNDING BOXES!!"
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0.1,
                                "maximum": 1.0,
                                "description": "Confidence score for this difference detection"
                            }
                        },
                        "required": ["label", "box_2d", "confidence"]
                    },
                    "description": "Array of all differences found between the two images"
                }
            },
            "required": ["differences"]
        }
    }


def create_detection_prompt():
    return """
    You are an expert at spot-the-difference puzzles. Carefully examine these two images pixel by pixel and identify ALL differences between them, no matter how small or subtle.

    Look for these types of differences:
    - Objects added, removed, or moved
    - Color changes (even slight variations)
    - Size changes (objects made bigger/smaller)
    - Orientation changes (rotated, flipped)
    - Text changes
    - Number of items changed (more/fewer objects)

    For each difference found, use the report_image_differences function to provide:
    1. A detailed descriptive label explaining exactly what changed
    2. The bounding box coordinates in the format [ymin, xmin, ymax, xmax] normalized to 0-1000. IT'S VERY IMPORTANT THAT YOU DRAW THE CORRECT BOUNDING BOXES!!
    3. A confidence score between 0.1 and 1.0

    Be exhaustive and thorough - find every single difference possible! Only report differences that you are 100% sure are actual differences.
    """


def detect_differences_with_ai(image1, image2):
    """
    Use Gemini AI to detect differences between two images.

    Args:
        image1: PIL Image object of the first image
        image2: PIL Image object of the second image

    Returns:
        list: List of differences found, each containing label, box_2d, and confidence
    """
    try:
        # Get the function declaration for structured output
        detect_differences_function = get_difference_detection_function()

        # Get the prompt that tells the AI what to do
        prompt = create_detection_prompt()

        # Configure the AI tools and function calling
        tools = types.Tool(function_declarations=[detect_differences_function])
        config = types.GenerateContentConfig(
            tools=[tools],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode='ANY')
            ),
            thinking_config=types.ThinkingConfig(thinking_budget=3000)
        )

        # Make the API call to Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image1, image2],
            config=config
        )

        # Process the AI's response
        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call

            if function_call.name == "report_image_differences":
                differences = function_call.args.get("differences", [])

                # Log the results for debugging
                print(f"AI found {len(differences)} differences")
                for i, diff in enumerate(differences):
                    print(f"Difference {i+1}: {diff.get('label', 'No label')}")

                return differences
            else:
                print(f"Unexpected function call: {function_call.name}")
                return []
        else:
            print("No function call found in AI response")
            return []

    except Exception as e:
        print(f"Error in AI difference detection: {str(e)}")
        return []
