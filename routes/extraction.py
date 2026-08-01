import json

from fastapi import HTTPException
from fastapi import APIRouter, Request
from pydantic import BaseModel

# Fix 1: Alias the imported function to avoid the name conflict
from ai.extraction import extract_claim as extract_claim
from ai.reasoning import reasoning
from search.tavily import TavilySearch

verification_router = APIRouter(prefix="/verify", tags=["verify"])

class ClaimExtractionRequest(BaseModel):
    claim: str

@verification_router.post("")
async def verify_claim(claim_extraction_request: ClaimExtractionRequest):
    """Extract entities and claims from a given text using GroqLLM"""
    try:
        text_to_process = claim_extraction_request.claim
        if not text_to_process:
            raise HTTPException(status_code=400, detail="No claim provided")
            
        # Fix 2: Call the aliased AI function here
        claims = extract_claim(text_to_process)
        
        if not claims:
            raise HTTPException(status_code=400, detail="No claims extracted")

        # 1. Convert the JSON string into a Python dictionary
        claims_data = json.loads(claims)
            
        # 2. Extract the list using the "claims" key and loop
        for claim in claims_data.get("claims", []):
            # 3. Use dictionary bracket/get syntax instead of dot notation
            if claim.get("confidence", 0) > 0.5:
                claim_text = claim.get("claim")
                evidence = TavilySearch().search(claim_text, max_results=5, search_depth="advanced", include_domains=["who.int", "niddk.nih.gov", "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov", "cdc.gov", "nhs.uk", "cochranelibrary.com", "ncdc.gov.ng"])
                context = reasoning(claim_text, evidence)
                return json.loads(context)
                
        return None
    except HTTPException:
        # Re-raise HTTP exceptions so FastAPI handles them correctly 
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse
import httpx
from config.settings import Settings

class TTSRequest(BaseModel):
    text: str
    voice: str = "Idera"

@verification_router.post("/tts")
async def generate_tts(request: TTSRequest):
    """Secure proxy to YarnGPT TTS to hide API keys from the frontend client."""
    try:
        url = "https://yarngpt.ai/api/v1/tts"
        api_key = Settings().yarngpt_api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": request.text,
            "voice": request.voice,
            "response_format": "mp3"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=60.0)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"YarnGPT TTS API failed: {response.text}")
            
            return StreamingResponse(
                response.iter_bytes(),
                media_type="audio/mpeg"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
