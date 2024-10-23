import openai
import os
from typing import Optional, List, Dict

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.
        Args:
            api_key (str, optional): OpenAI API key. If not provided, will look for OPENAI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided either directly or through OPENAI_API_KEY environment variable")
        
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_text(self, 
                     prompt: str,
                     model: str = "gpt-3.5-turbo",
                     max_tokens: int = 150,
                     temperature: float = 0.7) -> str:
        """
        Generate text using OpenAI's chat models.
        
        Args:
            prompt (str): The input prompt for generation
            model (str): The model to use (default: gpt-3.5-turbo)
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Controls randomness (0.0-1.0)
            
        Returns:
            str: Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating text: {str(e)}")
            return ""

    def create_image(self,
                    prompt: str,
                    size: str = "1024x1024",
                    quality: str = "standard",
                    n: int = 1) -> List[str]:
        """
        Generate images using DALL-E.
        
        Args:
            prompt (str): The image description
            size (str): Image size (1024x1024, 512x512, or 256x256)
            quality (str): Image quality (standard or hd)
            n (int): Number of images to generate
            
        Returns:
            List[str]: List of image URLs
        """
        try:
            response = self.client.images.generate(
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            return [image.url for image in response.data]
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    # Initialize the client
    client = OpenAIClient()  # Make sure OPENAI_API_KEY is set in environment variables
    
    # Example text generation
    prompt = "Write a short poem about artificial intelligence."
    response = client.generate_text(prompt)
    print("Generated Text:")
    print(response)
    print("\n" + "="*50 + "\n")
    
    # Example image generation
    image_prompt = "A futuristic city with flying cars"
    image_urls = client.create_image(image_prompt)
    print("Generated Image URLs:")
    for url in image_urls:
        print(url) 
