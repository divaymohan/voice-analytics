import os
import aiohttp
import openai
from typing import Dict, Any
from fastapi import HTTPException
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


class AnalyseFileService:
    def __init__(self):
        # Get API key from environment
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable is required")
        
        self.base_url = "https://api.deepgram.com/v1/listen"
        self.open_ai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def transcribe_audio_file(self, audio_file: bytes, filename: str) -> Dict[str, Any]:
        """
        Transcribe an audio file using Deepgram REST API
        
        Args:
            audio_file: Audio file bytes
            filename: Name of the uploaded file
            
        Returns:
            Dict containing transcription results
        """
        try:
            # Determine content type based on file extension
            file_extension = filename.lower().split('.')[-1]
            content_type_map = {
                'wav': 'audio/wav',
                'mp3': 'audio/mpeg',
                'm4a': 'audio/mp4',
                'flac': 'audio/flac',
                'ogg': 'audio/ogg',
                'webm': 'audio/webm',
                'mp4': 'audio/mp4'
            }
            content_type = content_type_map.get(file_extension, 'audio/wav')
            
            # Prepare headers
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": content_type
            }
            
            # Prepare query parameters
            params = {
                "model": "nova-3",
                "smart_format": "true",
                "language": "multi"
            }
            
            # Make the API request with binary data
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    params=params,
                    data=audio_file
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Deepgram API error: {error_text}"
                        )
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Transcription failed: {str(e)}"
            )
    


    async def review_transcript(self, transcript: str, language: str = "auto"):
        prompt = f"""
            You are a professional sales communication coach.

            The following is a transcript of a sales call in language: {language}.
            Evaluate the conversation based on the following five criteria:
            1. Start of the conversation
            2. Pitching of the product
            3. Understanding the customer’s problem
            4. Collecting required information
            5. Ending the call

            For each point, give:
            - A rating from 1 to 5
            - What was done well
            - Suggestions for improvement

            Always respond in English regardless of the transcript language.

            Transcript:
            \"\"\"
            {transcript}
            \"\"\"
      """

        response = self.open_ai_client.chat.completions.create(
            model="gpt-4",  # You can use gpt-3.5-turbo if needed
            messages=[
                {"role": "system", "content": "You are an expert sales communication coach."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )

        return {"review": response.choices[0].message.content}
    
