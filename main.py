import os
import json
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from datetime import datetime
import time

# --- CONFIGURATION ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
text_model = genai.GenerativeModel('gemini-1.5-pro-latest')

# --- HELPER FUNCTIONS ---

def load_strategy(filepath="strategy.json"):
    """Loads the marketing strategy from a JSON file."""
    print("✅ Loading marketing strategy...")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_post_ideas(strategy, num_posts=30):
    """Generates a list of post ideas using the Gemini API."""
    print(f"🧠 Generating {num_posts} post ideas...")
    
    prompt = f"""
    Based on the following marketing strategy for an app called '{strategy['appName']}', generate a list of exactly {num_posts} engaging social media post ideas.
    The target audience is: {strategy['targetAudience']}.
    The content should revolve around these pillars: {', '.join(strategy['contentPillars'])}.
    
    Return the response as a numbered list of one-sentence ideas. For example:
    1. A quick tip on how teachers can use technology in the classroom.
    2. Explaining the importance of parent-teacher meetings.
    """
    
    try:
        response = text_model.generate_content(prompt)
        # Simple parsing for a numbered list
        ideas = [line.strip().split('. ', 1)[1] for line in response.text.strip().split('\n') if '. ' in line]
        print(f"💡 Got {len(ideas)} ideas!")
        return ideas
    except Exception as e:
        print(f"❌ Error generating ideas: {e}")
        return []

def generate_caption(strategy, idea):
    """Generates a social media caption for a given idea."""
    print(f"✍️ Writing caption for: '{idea[:30]}...'")

    prompt = f"""
    You are the social media manager for '{strategy['appName']}'. Your brand voice is: '{strategy['brandVoice']}'.
    Write a complete, engaging social media caption based on this idea: "{idea}".
    
    The caption should be clear, helpful, and directly address the target audience: {strategy['targetAudience']}.
    Include relevant hashtags. Do not include the original idea in the response.
    """
    try:
        response = text_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error generating caption: {e}")
        return "Error: Could not generate caption."


def generate_image(image_prompt, post_number):
    """
    Generates an image and saves it.
    *** THIS IS A PLACEHOLDER - REPLACE WITH YOUR IMAGE GENERATION API ***
    """
    print(f"🎨 Generating image for post {post_number}...")
    
    # In a real scenario, you would call your image generation API here.
    # For example, using Stability AI, DALL-E, or another service.
    # For now, we'll use a placeholder image service.
    
    try:
        # Replace this URL with your actual API call.
        # This placeholder creates a simple image with text.
        image_url = f"https://placehold.co/600x400/1E90FF/FFFFFF?text=Image+for+Post+{post_number}"
        # In a real implementation, you'd download the image bytes from the API response.
        return image_url
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        return "https://placehold.co/600x400/FF0000/FFFFFF?text=Image+Error"


def generate_dashboard(posts, output_path="dashboard.html"):
    """Generates an HTML dashboard from the created content."""
    print(f"📊 Generating review dashboard...")
    
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('dashboard.html')
    
    current_date = datetime.now()
    month_name = current_date.strftime("%B %Y")
    generation_date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")

    html_content = template.render(
        posts=posts, 
        month=month_name,
        generation_date=generation_date_str
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"🎉 Dashboard created successfully! Open '{output_path}' in your browser.")

# --- MAIN EXECUTION ---

def main():
    """Main function to run the AI Co-Pilot."""
    strategy = load_strategy()
    if not strategy:
        return

    ideas = generate_post_ideas(strategy, num_posts=10) # Using 10 to run faster for testing
    if not ideas:
        return
        
    all_posts = []
    
    for i, idea in enumerate(ideas, 1):
        caption = generate_caption(strategy, idea)
        
        # Create a detailed prompt for the image generation model
        image_prompt = f"Create an image for a social media post about '{idea}'. The visual style should be: '{strategy['visualStyle']}'"
        
        # Call the image generation function
        image_path = generate_image(image_prompt, i)
        
        all_posts.append({
            "idea": idea,
            "caption": caption,
            "image_path": image_path
        })
        time.sleep(1) # Add a small delay to avoid hitting API rate limits

    generate_dashboard(all_posts)


if __name__ == "__main__":
    main()
