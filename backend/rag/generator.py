import os
import markdown
from openai import OpenAI
from typing import List, Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

class GPTOSSGenerator:
    """Generator using gpt-oss-20b via Hugging Face Inference API."""
    
    def __init__(self, api_key: str, base_url: str = "https://router.huggingface.co/v1", model: str = "openai/gpt-oss-20b"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client for Hugging Face Inference API."""
        try:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            logger.info("Initialized gpt-oss-20b client successfully")
        except Exception as e:
            logger.error(f"Error initializing gpt-oss-20b client: {e}")
            raise
    
    def format_rag_prompt(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Format the RAG prompt with retrieved context and question."""
        # Build context section
        context_section = "Relevant Australian Immigration Law Documents:\n\n"
        
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk.get("metadata", {}).get("source", "Unknown")
            section = chunk.get("metadata", {}).get("section", "Unknown")
            content = chunk.get("content", "")
            
            context_section += f"Document {i} - {source}, Section {section}:\n{content}\n\n"
        
        # Build the complete prompt
        prompt = f"""{context_section}

Based on the above Australian immigration law documents, please answer the following question:

Question: {question}

Instructions:
- Provide a clear, accurate answer based on the provided documents
- If the answer is not found in the documents, state that clearly
- Include relevant citations to specific documents and sections
- Focus on Australian immigration law and procedures
- Be concise but comprehensive
- Use proper markdown formatting for better readability:
  - Use **bold** for emphasis and key terms
  - Use *italics* for legal references when appropriate
  - Use proper paragraph breaks for structure
  - Use bullet points (-) for lists when helpful
  - Use line breaks for better text flow

Answer:"""
        
        return prompt
    
    def generate_response(self, question: str, context_chunks: List[Dict[str, Any]], 
                         max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate a response using gpt-oss-20b with retrieved context."""
        try:
            # Format the prompt
            prompt = self.format_rag_prompt(question, context_chunks)
            
            # Make API call
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            # Extract and format response
            raw_answer = response.choices[0].message.content
            formatted_answer = self.format_markdown_response(raw_answer)

            # Prepare result
            result = {
                "answer": formatted_answer,
                "raw_answer": raw_answer,  # Keep raw version for debugging
                "question": question,
                "context_chunks": context_chunks,
                "metadata": {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "latency_seconds": latency,
                    "tokens_used": response.usage.total_tokens if response.usage else None,
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                    "completion_tokens": response.usage.completion_tokens if response.usage else None
                }
            }
            
            logger.info(f"Generated response in {latency:.2f}s using {response.usage.total_tokens if response.usage else 'unknown'} tokens")
            return result
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def generate_streaming_response(self, question: str, context_chunks: List[Dict[str, Any]], 
                                  max_tokens: int = 512, temperature: float = 0.7):
        """Generate a streaming response using gpt-oss-20b."""
        try:
            # Format the prompt
            prompt = self.format_rag_prompt(question, context_chunks)
            
            # Make streaming API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            # Yield chunks as they arrive
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error generating streaming response: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test the connection to the gpt-oss-20b API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10,
                temperature=0.1
            )
            
            if response.choices[0].message.content:
                logger.info("gpt-oss-20b API connection test successful")
                return True
            else:
                logger.error("gpt-oss-20b API connection test failed - no response")
                return False
                
        except Exception as e:
            logger.error(f"gpt-oss-20b API connection test failed: {e}")
            return False
    
    def format_markdown_response(self, text: str) -> str:
        """Convert markdown text to HTML with proper formatting and security."""
        if not text or not isinstance(text, str):
            return text or ""

        try:
            # Configure markdown with safe extensions
            md = markdown.Markdown(extensions=[
                'extra',  # For tables, code blocks, etc.
                'codehilite',  # For code highlighting
                'toc',  # For table of contents if needed
                'meta',  # For metadata
                'nl2br',  # Convert newlines to <br>
                'sane_lists'  # For better list handling
            ], extension_configs={
                'codehilite': {
                    'linenums': False,  # No line numbers for cleaner look
                    'guess_lang': False,  # Don't guess language
                }
            })

            # Convert markdown to HTML
            html_output = md.convert(text)

            # Clean up any potential security issues (though markdown is generally safe)
            # Remove any script tags that might have been inserted
            html_output = html_output.replace('<script', '&lt;script').replace('</script>', '&lt;/script&gt;')

            logger.debug(f"Converted markdown to HTML: {len(html_output)} characters")
            return html_output

        except Exception as e:
            logger.error(f"Error formatting markdown response: {e}")
            # Return original text if markdown conversion fails
            return text

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model being used."""
        return {
            "model": self.model,
            "base_url": self.base_url,
            "api_type": "huggingface_inference",
            "description": "OpenAI gpt-oss-20b via Hugging Face Inference API"
        }
