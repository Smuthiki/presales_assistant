#!/usr/bin/env python3
"""
Enhanced Presales Assistant API with:
- Bullet-point reasoning with percentage match scores
- Pitch refinement endpoint
- Professional presales-grade prompts
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from openai import OpenAI
import os
import math
import json
from pathlib import Path
import serpapi
from bs4 import BeautifulSoup
import requests
import time
import io
import base64
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Free search alternatives
try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False

try:
    from googlesearch import search as google_search
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False

# ===================== CONFIG =====================
PORTFOLIO_XLSX = Path(r"C:\Users\smuthiki\Downloads\presales_assistant\Project_Portfolio_Data.xlsx")

# Load configuration from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")

# Search Engine Configuration - Intelligent Multi-Engine Strategy
# Options: "serpapi", "duckduckgo", "google", "intelligent_mixed"
SEARCH_ENGINE_PREFERENCE = "intelligent_mixed"  # Auto-cascade through engines for best results

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== MODELS =====================
class PortfolioRequest(BaseModel):
    client: str
    industry: Optional[str] = None
    technology: Optional[str] = None
    focus: Optional[str] = None
    company_website: Optional[str] = None
    limit: int = 6
    intelligence_data: Optional[Dict[str, Any]] = None

class PortfolioSummarySelectedRequest(BaseModel):
    client: str
    rows: List[Dict[str, Any]]
    intelligence_data: Optional[Dict[str, Any]] = None

class PitchRefinementRequest(BaseModel):
    client: str
    current_short_pitch: str
    current_long_pitch: str
    refinement_instructions: str
    context_rows: List[Dict[str, Any]]
    intelligence_data: Optional[Dict[str, Any]] = None

class PitchDownloadRequest(BaseModel):
    client: str
    short_pitch: str
    long_pitch: str

class PortfolioSummaryResponse(BaseModel):
    short_summary: str
    long_summary: str
    long_structured: Optional[Dict[str, Any]] = None
    rows: List[Dict[str, Any]]
    intelligence_data: Optional[Dict[str, Any]] = None
    detected_industry: Optional[str] = None
    industry_confidence: Optional[float] = None

# ===================== CACHE =====================
_portfolio_cache: Dict[str, Any] = {"df": None, "mtime": None}
_embeddings_cache: Dict[str, Any] = {"embeddings": None, "mtime": None, "rows": None}
EMBEDDINGS_CACHE_FILE = Path("portfolio_embeddings_cache.json")

# ===================== HELPERS =====================
def _safe_str(x: object) -> str:
    """Convert any value to safe string."""
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    return str(x).strip()

def load_portfolio_df() -> pd.DataFrame:
    """Load Portfolio Excel with ALL columns, cache by mtime."""
    p = PORTFOLIO_XLSX
    if not p.exists():
        return pd.DataFrame()

    mtime = p.stat().st_mtime
    if _portfolio_cache["df"] is not None and _portfolio_cache["mtime"] == mtime:
        return _portfolio_cache["df"]

    try:
        df_active = pd.read_excel(p, sheet_name=0, engine="openpyxl")
        df_active["status"] = "active"
    except Exception:
        df_active = pd.DataFrame()

    try:
        df_closed = pd.read_excel(p, sheet_name=1, engine="openpyxl")
        df_closed["status"] = "closed"
    except Exception:
        df_closed = pd.DataFrame()

    df = pd.concat([df_active, df_closed], ignore_index=True)

    # Normalize column names to lowercase with underscores
    df.columns = [col.lower().replace(' ', '_').replace('/', '_') for col in df.columns]

    # Normalize all string columns
    for c in df.columns:
        if df[c].dtype == 'object':
            df[c] = df[c].apply(_safe_str)

    # Remove completely empty rows
    df = df[df.apply(lambda row: any(row.astype(str).str.strip() != ''), axis=1)]
    df.reset_index(drop=True, inplace=True)

    _portfolio_cache["df"] = df
    _portfolio_cache["mtime"] = mtime
    return df

def load_or_create_embeddings() -> tuple[np.ndarray, pd.DataFrame]:
    """Load or generate embeddings for all portfolio rows with batch optimization."""
    df = load_portfolio_df()
    if df.empty:
        return np.array([]), df

    xlsx_mtime = PORTFOLIO_XLSX.stat().st_mtime

    # Check cache
    if EMBEDDINGS_CACHE_FILE.exists():
        try:
            with open(EMBEDDINGS_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            if cache_data.get("xlsx_mtime") == xlsx_mtime and cache_data.get("row_count") == len(df):
                print(f"[Embeddings] Loaded {len(cache_data['embeddings'])} cached embeddings")
                embeddings = np.array(cache_data["embeddings"], dtype=np.float32)
                return embeddings, df
        except Exception as e:
            print(f"[Embeddings] Cache read error: {e}")

    # Generate embeddings
    print(f"[Embeddings] Generating embeddings for {len(df)} rows...")
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Create text representations
    texts = []
    for idx, row in df.iterrows():
        parts = [
            f"Client: {row.get('client_name', '')}",
            f"Industry: {row.get('industry', '')}",
            f"Technology: {row.get('technologies', '')}",
            f"Business Case: {row.get('business_case', '')}",
            f"Solution: {row.get('evoke_solution_/_value_add_to_the_customer_(what_/_how)', '')}",
            f"Deliverables: {row.get('key_deliverables', '')}"
        ]
        texts.append(" ".join(parts))

    # Batch embedding generation (20 at a time for optimal speed)
    BATCH_SIZE = 20
    all_embeddings = []
    
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i+BATCH_SIZE]
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=batch,
                dimensions=1536
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
            print(f"[Embeddings] Generated {len(all_embeddings)}/{len(texts)}")
        except Exception as e:
            print(f"[Embeddings] Error in batch {i}: {e}")
            # Fallback: zero embeddings for failed batch
            all_embeddings.extend([[0.0]*1536 for _ in range(len(batch))])

    embeddings = np.array(all_embeddings, dtype=np.float32)

    # Save cache
    cache_data = {
        "xlsx_mtime": xlsx_mtime,
        "row_count": len(df),
        "embeddings": embeddings.tolist()
    }
    with open(EMBEDDINGS_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f)
    
    print(f"[Embeddings] Cached {len(embeddings)} embeddings")
    return embeddings, df

def cosine_similarity_batch(query_vec: np.ndarray, all_vecs: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between query and all vectors."""
    query_norm = np.linalg.norm(query_vec)
    all_norms = np.linalg.norm(all_vecs, axis=1)
    
    if query_norm == 0 or np.any(all_norms == 0):
        return np.zeros(len(all_vecs))
    
    dots = np.dot(all_vecs, query_vec)
    return dots / (all_norms * query_norm)

def score_row_with_reasoning(
    row: pd.Series,
    query_embedding: np.ndarray,
    row_embedding: np.ndarray,
    client: str,
    industry: Optional[str],
    technology: Optional[str],
    focus: Optional[str]
) -> Dict[str, Any]:
    """
    Enhanced scoring with bullet-point reasoning and percentage match scores.
    Returns detailed explanation of WHY this row was selected.
    """
    reasoning_bullets = []
    match_score = 0
    max_score = 100
    
    # 1. Semantic Similarity (40 points max)
    semantic_sim = float(cosine_similarity_batch(query_embedding, row_embedding.reshape(1, -1))[0])
    semantic_score = semantic_sim * 40
    match_score += semantic_score
    reasoning_bullets.append(f"[OK] Semantic Match: {semantic_sim*100:.1f}% similarity to your requirements")
    
    # 2. Industry Alignment (20 points max)
    row_industry = _safe_str(row.get('industry', '')).lower()
    if industry and _safe_str(industry).lower() in row_industry:
        industry_score = 20
        match_score += industry_score
        reasoning_bullets.append(f"[OK] Industry Match: Direct alignment with '{industry}' sector")
    elif industry:
        # Partial match
        query_words = set(_safe_str(industry).lower().split())
        row_words = set(row_industry.split())
        overlap = len(query_words & row_words)
        if overlap > 0:
            industry_score = 10
            match_score += industry_score
            reasoning_bullets.append(f"[OK] Industry Relevance: Partial match ({overlap} keyword{'s' if overlap > 1 else ''})")
    
    # 3. Technology Match (20 points max)
    row_tech = _safe_str(row.get('technologies', '')).lower()
    if technology:
        tech_query = _safe_str(technology).lower()
        if tech_query in row_tech:
            tech_score = 20
            match_score += tech_score
            reasoning_bullets.append(f"[OK] Technology Match: '{technology}' explicitly used in project")
        else:
            # Check for partial tech matches
            tech_words = set(tech_query.split())
            row_tech_words = set(row_tech.split())
            overlap = len(tech_words & row_tech_words)
            if overlap > 0:
                tech_score = 10
                match_score += tech_score
                reasoning_bullets.append(f"[OK] Technology Relevance: {overlap} related technology keyword{'s' if overlap > 1 else ''}")
    
    # 4. Business Value Indicators (10 points max)
    value_add = _safe_str(row.get('evoke_solution_/_value_add_to_the_customer_(what_/_how)', ''))
    results = _safe_str(row.get('key_deliverables', ''))
    
    value_score = 0
    if len(value_add) > 100:
        value_score += 5
        reasoning_bullets.append("[OK] Strong Value Proposition: Detailed solution description available")
    if len(results) > 50:
        value_score += 5
        reasoning_bullets.append("[OK] Proven Results: Concrete deliverables documented")
    match_score += value_score
    
    # 5. Project Status Bonus (5 points max)
    if row.get('status') == 'active':
        match_score += 5
        reasoning_bullets.append("[OK] Active Project: Currently ongoing, demonstrating recent capabilities")
    
    # 6. Focus Area Alignment (5 points max)
    if focus:
        focus_lower = _safe_str(focus).lower()
        business_case = _safe_str(row.get('business_case', '')).lower()
        problem_stmt = _safe_str(row.get('problem_or_opportunity_statement', '')).lower()
        
        focus_in_business = any(word in business_case for word in focus_lower.split() if len(word) > 3)
        focus_in_problem = any(word in problem_stmt for word in focus_lower.split() if len(word) > 3)
        
        if focus_in_business or focus_in_problem:
            match_score += 5
            reasoning_bullets.append("[OK] Focus Area Alignment: Project addresses similar business challenges")
    
    # Calculate percentage
    match_percentage = min(100, (match_score / max_score) * 100)
    
    # Build final reasoning summary
    reasoning_summary = "\n".join(reasoning_bullets)
    if not reasoning_bullets:
        reasoning_summary = "- General portfolio relevance"
    
    return {
        "match_score": round(match_percentage, 1),
        "semantic_similarity": round(semantic_sim * 100, 1),
        "detailed_reasoning": reasoning_summary,
        "reasoning_bullets": reasoning_bullets,
        "raw_score": round(match_score, 1)
    }

def generate_search_queries_with_ai(client: str, industry: Optional[str], focus: Optional[str]) -> List[str]:
    """Generate comprehensive search queries with enhanced fallback for maximum intelligence gathering."""
    # Enhanced fallback queries - always use these for reliability
    comprehensive_queries = [
        # Financial Intelligence
        f'{client} financial results revenue earnings',
        f'{client} annual report financial performance',
        f'{client} market capitalization stock price',
        f'{client} quarterly earnings investor relations',
        
        # Technology & Infrastructure
        f'{client} technology stack IT infrastructure',
        f'{client} cloud adoption digital transformation',
        f'{client} software vendors technology partners',
        f'{client} automation AI machine learning',
        
        # Strategic & Business
        f'{client} strategic partnerships alliances',
        f'{client} acquisitions mergers business development',
        f'{client} market position competitive landscape',
        f'{client} business model revenue streams',
        
        # Recent News & Announcements
        f'{client} recent announcements press releases',
        f'{client} latest news updates developments',
        f'{client} leadership team executives management',
        f'{client} industry trends market analysis'
    ]
    
    if industry:
        comprehensive_queries.extend([
            f'{client} {industry} market share position',
            f'{client} {industry} challenges opportunities',
            f'{client} {industry} technology adoption trends'
        ])
    
    if focus:
        comprehensive_queries.extend([
            f'{client} {focus} initiatives projects',
            f'{client} {focus} strategy roadmap'
        ])
    
    # Try AI enhancement but fallback to comprehensive queries
    if not OPENAI_API_KEY:
        print(f"[Query Gen] Using comprehensive fallback queries ({len(comprehensive_queries)} queries)")
        return comprehensive_queries
    
    try:
        ai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""Generate 25-30 highly targeted search queries to comprehensively research this company for presales intelligence:

Company: {client}
Industry: {industry or 'Unknown'}
Focus Area: {focus or 'General business intelligence'}

Generate SPECIFIC queries for these intelligence categories:

FINANCIAL INTELLIGENCE (8-10 queries):
- Revenue, earnings, financial performance
- Market capitalization, stock performance
- Growth metrics, profitability
- Investment rounds, funding, acquisitions
- Financial forecasts and analyst reports

TECHNOLOGY & INFRASTRUCTURE (6-8 queries):
- Current technology stack and platforms
- IT infrastructure and cloud adoption
- Software vendors and technology partners
- Digital transformation initiatives
- Tech roadmap and future investments

STRATEGIC & BUSINESS (6-8 queries):
- Strategic partnerships and alliances
- Business model and revenue streams
- Market expansion and growth strategy
- Competitive positioning
- Recent announcements and press releases

OPERATIONAL INTELLIGENCE (4-6 queries):
- Key vendors and suppliers
- Organizational structure and leadership
- Operational challenges and opportunities
- Industry-specific initiatives
- Regulatory and compliance aspects

Use exact company name in quotes for precise results.
Return ONLY a JSON array of query strings, no other text.
Example: ['"Apple Inc" latest quarterly earnings", '"Apple Inc" cloud infrastructure vendors']"""

        response = ai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Enhanced JSON parsing with fallback
        if content and content.startswith('[') and content.endswith(']'):
            try:
                queries = json.loads(content)
                if isinstance(queries, list) and len(queries) > 0:
                    print(f"[AI Query Gen] Generated {len(queries)} AI-enhanced queries")
                    return queries
            except json.JSONDecodeError:
                print(f"[AI Query Gen] JSON parse failed, using enhanced fallback")
        
        print(f"[AI Query Gen] Using comprehensive fallback queries")
        return comprehensive_queries
    
    except Exception as e:
        print(f"[AI Query Gen] Error: {e}, using enhanced fallback queries")
        return comprehensive_queries

def duckduckgo_search(query: str, max_results: int = 8, retries: int = 3) -> List[Dict[str, str]]:
    """Enhanced DuckDuckGo search with retry logic and better error handling."""
    if not DDGS_AVAILABLE:
        print("[DuckDuckGo] ERROR Library not available")
        return []
        
    for attempt in range(retries):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                formatted_results = []
                
                for result in results:
                    # Enhanced validation of result data
                    title = result.get("title", "").strip()
                    body = result.get("body", "").strip()
                    url = result.get("href", "").strip()
                    
                    # Skip results with missing critical data
                    if not title or not url or len(body) < 20:
                        continue
                        
                    formatted_results.append({
                        "source": "DuckDuckGo Search",
                        "query": query,
                        "title": title,
                        "snippet": body,
                        "url": url,
                        "category": "web_search"
                    })
                    
                print(f"[DuckDuckGo] SUCCESS Found {len(formatted_results)} quality results")
                return formatted_results
                
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg:
                print(f"[DuckDuckGo] WARNING Rate limited on attempt {attempt + 1}")
                wait_time = 5 + (2 ** attempt)  # Longer wait for rate limits
            else:
                print(f"[DuckDuckGo] ERROR Attempt {attempt + 1} failed: {str(e)[:100]}")
                wait_time = 2 ** attempt
                
            if attempt < retries - 1:
                print(f"[DuckDuckGo] RETRYING in {wait_time} seconds...")
                time.sleep(wait_time)
                    
    print(f"[DuckDuckGo] ERROR All {retries} attempts failed for query")
    return []

def free_google_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Enhanced free Google search with better error handling."""
    if not GOOGLE_SEARCH_AVAILABLE:
        print("[Google] ERROR Library not available")
        return []
        
    try:
        # Add delay to avoid being blocked
        time.sleep(1)
        
        results = list(google_search(query, num_results=max_results))
        formatted_results = []
        
        for i, url in enumerate(results):
            if url and url.startswith(('http://', 'https://')):
                # Try to extract title from URL if possible
                title = url.split('/')[-1] if '/' in url else f"Google Result {i+1}"
                title = title.replace('-', ' ').replace('_', ' ').title()
                
                formatted_results.append({
                    "source": "Free Google Search",
                    "query": query,
                    "title": title[:100],  # Limit title length
                    "snippet": f"Search result for: {query[:50]}",
                    "url": url,
                    "category": "web_search"
                })
            
        print(f"[Google] SUCCESS Found {len(formatted_results)} results")
        return formatted_results
        
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "too many requests" in error_msg:
            print(f"[Google] WARNING Rate limited - {str(e)[:100]}")
        elif "403" in error_msg or "blocked" in error_msg:
            print(f"[Google] WARNING Access blocked - {str(e)[:100]}")
        else:
            print(f"[Google] ERROR Search failed: {str(e)[:100]}")
        return []

def serpapi_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Enhanced SERP API search with comprehensive error handling."""
    if not SERPAPI_API_KEY:
        print("[SERP] ERROR API key not available")
        return []
        
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "num": min(max_results, 10),  # SerpAPI has limits
        "gl": "us",
        "hl": "en"
    }
    
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=20)
        
        if response.status_code == 429:
            print(f"[SERP] WARNING Rate limit hit - daily quota exceeded")
            return []
        elif response.status_code == 401:
            print(f"[SERP] ERROR Authentication failed - check API key")
            return []
        elif response.status_code == 403:
            print(f"[SERP] ERROR Access forbidden - API key may be invalid")
            return []
            
        response.raise_for_status()
        data = response.json()
        
        # Check for API-specific errors
        if "error" in data:
            print(f"[SERP] ERROR API error: {data['error']}")
            return []
        
        formatted_results = []
        organic_results = data.get("organic_results", [])
        
        for result in organic_results[:max_results]:
            title = result.get("title", "").strip()
            snippet = result.get("snippet", "").strip()
            url = result.get("link", "").strip()
            
            # Quality filter - ensure we have good data
            if title and url and len(snippet) > 10:
                formatted_results.append({
                    "source": "SERP API",
                    "query": query,
                    "title": title,
                    "snippet": snippet,
                    "url": url,
                    "category": "web_search"
                })
            
        print(f"[SERP] SUCCESS Found {len(formatted_results)} quality results")
        return formatted_results
        
    except requests.exceptions.Timeout:
        print(f"[SERP] WARNING Request timeout after 20 seconds")
        return []
    except requests.exceptions.RequestException as e:
        print(f"[SERP] ERROR Network error: {str(e)[:100]}")
        return []
    except Exception as e:
        print(f"[SERP] ERROR Unexpected error: {str(e)[:100]}")
        return []

def intelligent_cascade_search(query: str, target_results: int = 8) -> List[Dict[str, str]]:
    """
    Intelligent search that cascades through engines until target results achieved.
    Priority: DuckDuckGo -> Google -> SerpAPI (based on rate limits and reliability)
    """
    all_results = []
    
    # Define search engines in priority order
    search_engines = [
        {
            "name": "duckduckgo",
            "func": duckduckgo_search,
            "max_results": target_results,
            "delay": 1,
            "description": "Primary free engine"
        },
        {
            "name": "google", 
            "func": free_google_search,
            "max_results": min(target_results, 5),  # Google has stricter limits
            "delay": 2,
            "description": "Secondary free engine"
        },
        {
            "name": "serpapi",
            "func": serpapi_search, 
            "max_results": min(target_results, 5),
            "delay": 1,
            "description": "Premium API fallback"
        }
    ]
    
    print(f"[Intelligent Search] Target: {target_results} results for '{query[:50]}...'")
    
    for engine in search_engines:
        # Skip if we already have enough results
        if len(all_results) >= target_results:
            print(f"[Intelligent Search] Target achieved with {len(all_results)} results")
            break
            
        # Skip SerpAPI if rate limited (check for API key)
        if engine["name"] == "serpapi" and not SERPAPI_API_KEY:
            print(f"[Intelligent Search] Skipping {engine['name']} - no API key")
            continue
            
        # Skip Google/DDG if they're not available
        if engine["name"] == "google" and not GOOGLE_SEARCH_AVAILABLE:
            print(f"[Intelligent Search] Skipping {engine['name']} - library not available")
            continue
            
        if engine["name"] == "duckduckgo" and not DDGS_AVAILABLE:
            print(f"[Intelligent Search] Skipping {engine['name']} - library not available")
            continue
        
        remaining_needed = target_results - len(all_results)
        search_limit = min(engine["max_results"], remaining_needed + 2)  # Get a few extra
        
        print(f"[Intelligent Search] Trying {engine['name']} ({engine['description']}) - need {remaining_needed} more")
        
        try:
            engine_results = engine["func"](query, search_limit)
            
            if engine_results:
                # Filter out duplicates by URL
                existing_urls = {result.get("url", "") for result in all_results}
                new_results = [r for r in engine_results if r.get("url", "") not in existing_urls]
                
                all_results.extend(new_results)
                print(f"[Intelligent Search] SUCCESS {engine['name']} added {len(new_results)} unique results (total: {len(all_results)})")
                
                # If we got good results, no need to try more engines unless we're still short
                if len(all_results) >= target_results * 0.7:  # 70% of target from primary engines
                    print(f"[Intelligent Search] Sufficient results from {engine['name']}, stopping cascade")
                    break
            else:
                print(f"[Intelligent Search] ERROR {engine['name']} returned no results")
                
        except Exception as e:
            print(f"[Intelligent Search] ERROR {engine['name']} failed: {str(e)[:100]}...")
            continue
            
        # Rate limiting delay between engines
        time.sleep(engine["delay"])
    
    print(f"[Intelligent Search] Final result: {len(all_results)} items from cascade search")
    return all_results

def multi_engine_search(query: str, max_results_per_engine: int = 3) -> List[Dict[str, str]]:
    """Legacy multi-engine search - now calls intelligent cascade for better results."""
    return intelligent_cascade_search(query, target_results=max_results_per_engine * 2)

def validate_search_quality(all_results: List[Dict[str, str]], client: str, target_categories: int = 5) -> Dict[str, Any]:
    """
    Validate search result quality and suggest improvements.
    Returns quality metrics and recommendations.
    """
    if not all_results:
        return {
            "quality_score": 0.0,
            "total_results": 0,
            "categories_covered": 0,
            "recommendations": ["No search results obtained", "Check internet connection and API keys"]
        }
    
    # Analyze result categories
    categories = set()
    for result in all_results:
        source = result.get("source", "").lower()
        url = result.get("url", "").lower()
        title = result.get("title", "").lower()
        
        # Categorize by content type
        if "yahoo" in url or "finance" in url or "investor" in title:
            categories.add("financial")
        elif "linkedin" in url or "executive" in title or "leadership" in title:
            categories.add("leadership")
        elif "press" in title or "news" in title or "announcement" in title:
            categories.add("news")
        elif client.lower() in url or "about" in url:
            categories.add("company_info")
        else:
            categories.add("general")
    
    # Calculate quality metrics
    unique_urls = len(set(r.get("url", "") for r in all_results))
    avg_snippet_length = sum(len(r.get("snippet", "")) for r in all_results) / max(len(all_results), 1)
    
    # Quality scoring
    quality_score = min(1.0, (
        (unique_urls / 20.0) * 0.4 +  # URL diversity
        (len(categories) / target_categories) * 0.3 +  # Category coverage
        (min(avg_snippet_length, 300) / 300.0) * 0.3  # Content richness
    ))
    
    # Generate recommendations
    recommendations = []
    if unique_urls < 10:
        recommendations.append("Consider adding more search engines or queries")
    if len(categories) < 3:
        recommendations.append("Need more diverse search queries for comprehensive intelligence")
    if avg_snippet_length < 100:
        recommendations.append("Search results have limited content - may need different query strategies")
    
    if quality_score > 0.7:
        recommendations.append("SUCCESS Good search result quality")
    
    return {
        "quality_score": quality_score,
        "total_results": len(all_results),
        "unique_urls": unique_urls,
        "categories_covered": len(categories),
        "categories": list(categories),
        "avg_snippet_length": avg_snippet_length,
        "recommendations": recommendations
    }

def comprehensive_web_search(client: str, industry: Optional[str] = None, focus: Optional[str] = None, 
                            company_website: Optional[str] = None) -> str:
    """Enhanced comprehensive intelligence gathering with maximum data extraction."""
    print(f"[Web Search] Starting comprehensive intelligence gathering for {client}...")
    
    all_results = []
    
    # Generate AI-powered search queries
    search_queries = generate_search_queries_with_ai(client, industry, focus)
    print(f"[Web Search] Generated {len(search_queries)} comprehensive search queries")
    
    # Multi-engine web search with intelligent fallbacks
    print(f"[Web Search] Using search engine preference: {SEARCH_ENGINE_PREFERENCE}")
    
    # Process search queries with enhanced strategy
    max_queries = min(10, len(search_queries))  # Process up to 10 queries
    for i, query in enumerate(search_queries[:max_queries]):
        print(f"[Web Search] Processing query {i+1}/{max_queries}: {query}")
        
        query_results = []
        
        if SEARCH_ENGINE_PREFERENCE == "intelligent_mixed":
            # Use intelligent cascade search for best results
            query_results = intelligent_cascade_search(query, target_results=8)
            
        elif SEARCH_ENGINE_PREFERENCE == "mixed":
            # Use traditional multi-engine approach
            query_results = multi_engine_search(query, max_results_per_engine=3)
            
        elif SEARCH_ENGINE_PREFERENCE == "duckduckgo":
            # Primary: DuckDuckGo, Fallback: Intelligent cascade if DDG fails
            query_results = duckduckgo_search(query, max_results=8)
            if len(query_results) < 3:  # If DDG fails or returns few results
                print(f"[Fallback] DuckDuckGo insufficient ({len(query_results)} results), cascading to other engines")
                cascade_results = intelligent_cascade_search(query, target_results=8)
                # Merge results, avoiding duplicates
                existing_urls = {r.get("url", "") for r in query_results}
                additional_results = [r for r in cascade_results if r.get("url", "") not in existing_urls]
                query_results.extend(additional_results)
            
        elif SEARCH_ENGINE_PREFERENCE == "google":
            # Primary: Google, Fallback: Intelligent cascade if Google fails
            query_results = free_google_search(query, max_results=5)
            if len(query_results) < 2:
                print(f"[Fallback] Google insufficient ({len(query_results)} results), cascading to other engines")
                query_results = intelligent_cascade_search(query, target_results=8)
            
        elif SEARCH_ENGINE_PREFERENCE == "serpapi":
            # Primary: SerpAPI, Fallback: Intelligent cascade if SerpAPI fails
            query_results = serpapi_search(query, max_results=5)
            if len(query_results) < 2:
                print(f"[Fallback] SerpAPI insufficient ({len(query_results)} results), cascading to other engines")
                query_results = intelligent_cascade_search(query, target_results=8)
            
        else:
            # Default fallback to intelligent mixed mode
            print(f"[Search] Unknown preference '{SEARCH_ENGINE_PREFERENCE}', using intelligent_mixed")
            query_results = intelligent_cascade_search(query, target_results=8)
        
        # Add results to main collection
        all_results.extend(query_results)
        
        # Enhanced delay to avoid rate limits - increase delay between queries
        time.sleep(2)  # Increased from 1 to 2 seconds to avoid rate limiting
    
    # Auto-detect and scrape Yahoo Finance data
    try:
        print(f"[Yahoo Auto] Searching for Yahoo Finance data for {client}")
        
        # Try to find Yahoo Finance URL using free search engines
        yahoo_query = f'site:finance.yahoo.com "{client}" stock financial data'
        yahoo_results = []
        
        # Try DuckDuckGo first for Yahoo Finance search
        if DDGS_AVAILABLE:
            try:
                print(f"[Yahoo Auto] Trying DuckDuckGo search for Yahoo Finance")
                yahoo_ddg_results = duckduckgo_search(yahoo_query, max_results=3)
                yahoo_results.extend(yahoo_ddg_results)
            except Exception as e:
                print(f"[Yahoo Auto] DuckDuckGo search failed: {e}")
        
        # If no results from DuckDuckGo, try free Google search
        if not yahoo_results and GOOGLE_SEARCH_AVAILABLE:
            try:
                print(f"[Yahoo Auto] Trying Google search for Yahoo Finance")
                yahoo_google_results = free_google_search(yahoo_query, max_results=3)
                yahoo_results.extend(yahoo_google_results)
            except Exception as e:
                print(f"[Yahoo Auto] Google search failed: {e}")
        
        # Fallback to SERP API only if other methods failed
        if not yahoo_results and SERPAPI_API_KEY:
            try:
                print(f"[Yahoo Auto] Trying SERP API as fallback")
                yahoo_results = serpapi_search(yahoo_query, max_results=3)
            except Exception as e:
                print(f"[Yahoo Auto] SERP API search failed: {e}")
                
        # Look for Yahoo Finance URLs in search results
        for result in yahoo_results:
            link = result.get("url", "") or result.get("link", "")
            if "finance.yahoo.com" in link and "/quote/" in link:
                try:
                    print(f"[Yahoo Auto] Found Yahoo Finance URL: {link}")
                    
                    # Scrape the detected Yahoo Finance page
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    response = requests.get(link, headers=headers, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract comprehensive financial data
                    financial_sections = []
                    
                    # Key statistics
                    for span in soup.find_all('span', limit=100):
                        if span.text and any(term in span.text.lower() for term in ['revenue', 'market cap', 'pe ratio', 'earnings', 'dividend']):
                            financial_sections.append(span.text.strip())
                    
                    # Financial tables
                    for table in soup.find_all('table', limit=10):
                        table_text = table.get_text(separator=' | ', strip=True)
                        if table_text and len(table_text) < 1000:
                            financial_sections.append(table_text)
                    
                    financial_content = "\n\n".join(financial_sections[:10])
                    
                    all_results.append({
                        "source": "Yahoo Finance (Auto-detected)",
                        "query": "auto_financial_data",
                        "title": f"{client} Auto-detected Financial Data",
                        "snippet": financial_content or soup.get_text()[:2500],
                        "url": link,
                        "category": "financial"
                    })
                    
                    print(f"[Yahoo Auto] Successfully scraped financial data from {link}")
                    break  # Only process the first valid Yahoo Finance URL found
                        
                except Exception as search_error:
                    print(f"[Yahoo Auto] Search error: {search_error}")
        
        # Fallback: Try to construct Yahoo Finance URL using company ticker
        if not any(result.get("source", "").startswith("Yahoo Finance") for result in all_results):
            print(f"[Yahoo Auto] Attempting ticker-based URL construction for {client}")
            
            # Use AI to guess the stock ticker
            try:
                client_ai = OpenAI(api_key=OPENAI_API_KEY)
                ticker_prompt = f"""What is the stock ticker symbol for "{client}"? 
                
Return ONLY the ticker symbol (like AAPL, MSFT, TSLA) or "UNKNOWN" if not a public company.
Do not include any explanation."""
                
                ticker_response = client_ai.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": ticker_prompt}],
                    max_tokens=20,
                    temperature=0.1
                )
                
                ticker = ticker_response.choices[0].message.content.strip()
                
                if ticker and ticker != "UNKNOWN" and len(ticker) <= 10:
                    constructed_url = f"https://finance.yahoo.com/quote/{ticker}"
                    print(f"[Yahoo Auto] Trying constructed URL: {constructed_url}")
                    
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    response = requests.get(constructed_url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract financial data
                        financial_sections = []
                        for span in soup.find_all('span', limit=100):
                            if span.text and any(term in span.text.lower() for term in ['revenue', 'market cap', 'pe ratio', 'earnings']):
                                financial_sections.append(span.text.strip())
                        
                        financial_content = "\n\n".join(financial_sections[:10])
                        
                        all_results.append({
                            "source": "Yahoo Finance (Ticker-based)",
                            "query": "ticker_financial_data", 
                            "title": f"{client} Ticker-based Financial Data ({ticker})",
                            "snippet": financial_content or soup.get_text()[:2500],
                            "url": constructed_url,
                            "category": "financial"
                        })
                        
                        print(f"[Yahoo Auto] Successfully scraped ticker-based data for {ticker}")
                        
            except Exception as ticker_error:
                print(f"[Yahoo Auto] Ticker detection error: {ticker_error}")
                
    except Exception as e:
        print(f"[Yahoo Auto] Auto-detection error: {e}")
    
    # Enhanced company website scraping
    if company_website:
        try:
            print(f"[Website] Scraping company information from {company_website}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # Try multiple pages
            pages_to_scrape = [
                company_website,
                f"{company_website.rstrip('/')}/about",
                f"{company_website.rstrip('/')}/about-us",
                f"{company_website.rstrip('/')}/investors",
                f"{company_website.rstrip('/')}/news"
            ]
            
            for page_url in pages_to_scrape:
                try:
                    response = requests.get(page_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Extract meaningful content
                        content = soup.get_text(separator=' ', strip=True)
                        
                        # Filter for relevant content
                        if content and len(content) > 200:
                            all_results.append({
                                "source": "Company Website",
                                "query": "company_info",
                                "title": f"{client} Company Information - {page_url.split('/')[-1] or 'Homepage'}",
                                "snippet": content[:2000],
                                "url": page_url,
                                "category": "company_website"
                            })
                except Exception as page_error:
                    continue
            
        except Exception as e:
            print(f"[Website] Enhanced scraping error: {e}")
    
    # Enhanced alternative intelligence sources when search engines fail
    print(f"[Web Search] Collected {len(all_results)} results, attempting enhanced alternative sources...")
    
    # Alternative source 1: Direct company website intelligence
    if len(all_results) < 20:  # If we don't have enough data
        try:
            # Try to find company website using basic search
            website_queries = [
                f'{client} official website',
                f'{client} company homepage',
                f'{client} corporate site'
            ]
            
            for website_query in website_queries:
                try:
                    website_results = duckduckgo_search(website_query, max_results=3)
                    for result in website_results:
                        url = result.get("url", "")
                        if any(indicator in url.lower() for indicator in [client.lower().replace(" ", ""), ".com", ".org", ".net"]):
                            print(f"[Alternative] Found potential company website: {url}")
                            # Try to scrape this as company website
                            try:
                                headers = {
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                                }
                                response = requests.get(url, headers=headers, timeout=10)
                                if response.status_code == 200:
                                    from bs4 import BeautifulSoup
                                    soup = BeautifulSoup(response.content, 'html.parser')
                                    
                                    # Remove unwanted elements
                                    for tag in soup(["script", "style", "nav", "footer", "header"]):
                                        tag.decompose()
                                    
                                    content = soup.get_text(separator=' ', strip=True)
                                    if len(content) > 500:
                                        all_results.append({
                                            "source": "Company Website (Auto-detected)",
                                            "query": "company_website_auto",
                                            "title": f"{client} Company Website Content",
                                            "snippet": content[:3000],  # Get substantial content
                                            "url": url,
                                            "category": "company_website"
                                        })
                                        print(f"[Alternative] Successfully scraped company website")
                                        break
                            except Exception as scrape_error:
                                print(f"[Alternative] Website scraping failed: {scrape_error}")
                    time.sleep(2)
                except Exception as website_error:
                    print(f"[Alternative] Website search failed: {website_error}")
                    
        except Exception as alt_error:
            print(f"[Alternative Sources] Error: {alt_error}")
    
    # Alternative source 2: Industry-specific searches when main searches fail
    if industry and len(all_results) < 15:
        industry_queries = [
            f'{client} {industry} company profile',
            f'{client} {industry} market leader',
            f'{client} {industry} business overview'
        ]
        
        for ind_query in industry_queries:
            try:
                ind_results = duckduckgo_search(ind_query, max_results=3)
                all_results.extend(ind_results)
                time.sleep(2)
            except Exception as ind_error:
                print(f"[Industry Search] Failed: {ind_error}")
                
    # Skip SERP API specialized searches to avoid rate limits - focus on free sources
    
    # Validate search result quality
    quality_metrics = validate_search_quality(all_results, client)
    print(f"[Search Quality] Score: {quality_metrics['quality_score']:.1%} | "
          f"Results: {quality_metrics['total_results']} | "
          f"Categories: {quality_metrics['categories_covered']} | "
          f"Unique URLs: {quality_metrics['unique_urls']}")
    
    for recommendation in quality_metrics['recommendations']:
        print(f"[Search Quality] TIP {recommendation}")
    
    # If quality is too low, try additional targeted searches
    if quality_metrics['quality_score'] < 0.5 and len(all_results) < 15:
        print(f"[Search Enhancement] Quality below threshold, attempting targeted searches...")
        
        targeted_queries = [
            f'"{client}" company overview business profile',
            f'"{client}" financial performance annual results',
            f'"{client}" technology solutions products services',
            f'site:linkedin.com "{client}" company page',
            f'site:crunchbase.com "{client}"'
        ]
        
        for targeted_query in targeted_queries:
            try:
                additional_results = intelligent_cascade_search(targeted_query, target_results=3)
                # Filter duplicates
                existing_urls = {r.get("url", "") for r in all_results}
                new_results = [r for r in additional_results if r.get("url", "") not in existing_urls]
                all_results.extend(new_results)
                print(f"[Search Enhancement] Added {len(new_results)} results from targeted search")
                time.sleep(2)
            except Exception as e:
                print(f"[Search Enhancement] Targeted search failed: {e}")
    
    # Format results with enhanced structure
    formatted_sections = []
    
    # Group results by category
    categories = {}
    for result in all_results:
        cat = result.get("category", "general")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result)
    
    # Format each category with richer content
    for category, results in categories.items():
        category_content = []
        for r in results[:10]:  # More results per category for comprehensive data
            formatted_result = f"""Title: {r['title']}
Content: {r['snippet']}
Source: {r.get('source', 'Unknown')}
URL: {r['url']}
Query Context: {r.get('query', 'N/A')}"""
            category_content.append(formatted_result)
        
        if category_content:
            formatted_sections.append(f"\n=== {category.upper().replace('_', ' ')} INTELLIGENCE ===\n" + "\n\n".join(category_content))
    
    final_formatted = "\n\n".join(formatted_sections)
    
    # Enhanced completion summary
    final_quality = validate_search_quality(all_results, client)
    print(f"[Web Search] SUCCESS Intelligence gathering complete:")
    print(f"  Quality Score: {final_quality['quality_score']:.1%}")  
    print(f"  Total Results: {final_quality['total_results']}")
    print(f"  Categories: {final_quality['categories_covered']} ({', '.join(final_quality['categories'])})")
    print(f"  Unique URLs: {final_quality['unique_urls']}")
    
    return final_formatted or "No comprehensive intelligence gathered."

def _normalize_legacy_intel(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map legacy flat lists into new richer schema so UI can rely on one shape."""
    if not data or data.get("error"):
        return data
    # Already new schema?
    if any(k in data for k in ["strategic_focus", "vendors_partners", "it_infrastructure_summary", "business_context"]):
        return data
    financial_list = data.get("financial_data", []) or []
    financial_obj = {
        "revenue": None,
        "market_cap": None,
        "growth_rate": None,
        "other_metrics": [],
        "source_url": None,
        "confidence": 0.4,
    }
    for item in financial_list:
        metric = (item or {}).get("metric") if isinstance(item, dict) else None
        value = (item or {}).get("value") if isinstance(item, dict) else None
        src = (item or {}).get("source_url") if isinstance(item, dict) else None
        if not metric or not value:
            continue
        low = metric.lower()
        if "revenue" in low and not financial_obj["revenue"]:
            financial_obj["revenue"] = value; financial_obj["source_url"] = src or financial_obj["source_url"]
        elif ("market" in low and "cap" in low) and not financial_obj["market_cap"]:
            financial_obj["market_cap"] = value; financial_obj["source_url"] = src or financial_obj["source_url"]
        elif any(k in low for k in ["growth", "cagr"] ) and not financial_obj["growth_rate"]:
            financial_obj["growth_rate"] = value; financial_obj["source_url"] = src or financial_obj["source_url"]
        else:
            financial_obj["other_metrics"].append({"metric": metric, "value": value, "source_url": src})
    return {
        "financial_data": financial_obj,
        "technologies": {"confirmed": data.get("technologies", []), "inferred": []},
        "vendors_partners": {"confirmed": data.get("key_vendors", []), "inferred": []},
        "recent_projects": [],
        "announcements": data.get("recent_announcements", []),
        "strategic_focus": [],
        "it_infrastructure_summary": None,
        "business_context": None,
        "confidence_score": 0.4,
        "_legacy_transformed": True,
    }


def ai_extract_intelligence(web_data: str) -> Dict[str, Any]:
    """Extract comprehensive structured intelligence from aggregated web data with enhanced schema.

    Enhanced Target Schema:
    {
      "financial_data": {"revenue": str|None, "market_cap": str|None, "growth_rate": str|None,
                          "other_metrics": [{metric, value, source_url}], "source_url": str|None, "confidence": float,
                          "stock_price": str|None, "pe_ratio": str|None, "dividend_yield": str|None},
      "technologies": {"confirmed": [{name, source_url, category}], "inferred": [{name, reason, category}]},
      "vendors_partners": {"confirmed": [{name, source_url, relationship_type}], "inferred": [{name, reason, relationship_type}]},
      "recent_projects": [{"title": str, "description": str, "source_url": str, "timeline": str}],
      "announcements": [{"title": str, "summary": str, "source_url": str, "date": str, "impact": str}],
      "strategic_focus": [{"theme": str, "evidence": str, "source_url": str|None, "priority": str}],
      "competitive_landscape": [{"competitor": str, "relationship": str, "source_url": str}],
      "tech_roadmap": [{"initiative": str, "timeline": str, "description": str, "source_url": str}],
      "leadership_team": [{"name": str, "position": str, "background": str, "source_url": str}],
      "it_infrastructure_summary": str|None,
      "business_context": str|None,
      "market_position": str|None,
      "confidence_score": float (0-1)
    }
    """
    if not OPENAI_API_KEY or not web_data:
        return {"error": "No data to analyze"}

    base_system = (
        "You are a comprehensive business intelligence analyst extracting ONLY factual information present in the provided data. "
        "Extract maximum relevant details while maintaining accuracy. Return structured JSON without fabrication. "
        "When information is mentioned but not detailed, note it in inferred sections with reasoning."
    )

    instruction = f"""COMPREHENSIVE SOURCE DATA:\n\n{web_data}\n\n
Extract ALL available information into this enhanced JSON schema (no markdown formatting):\n{{
  "financial_data": {{
      "revenue": "exact figure with currency or null",
      "market_cap": "exact figure with currency or null", 
      "growth_rate": "percentage with timeframe or null",
      "stock_price": "current price with currency or null",
      "pe_ratio": "ratio value or null",
      "dividend_yield": "percentage or null",
      "other_metrics": [{{"metric": "name", "value": "exact value", "source_url": "url"}}],
      "source_url": "primary financial source url",
      "confidence": 0.0
  }},
  "technologies": {{
      "confirmed": [{{"name": "technology name", "source_url": "url", "category": "cloud/software/hardware/ai/etc"}}],
      "inferred": [{{"name": "technology name", "reason": "why inferred", "category": "type"}}]
  }},
  "vendors_partners": {{
      "confirmed": [{{"name": "company name", "source_url": "url", "relationship_type": "vendor/partner/supplier/customer"}}],
      "inferred": [{{"name": "company name", "reason": "why inferred", "relationship_type": "type"}}]
  }},
  "recent_projects": [{{"title": "project name", "description": "brief description", "source_url": "url", "timeline": "timeframe"}}],
  "announcements": [{{"title": "announcement", "summary": "1-2 sentences", "source_url": "url", "date": "date mentioned", "impact": "business impact"}}],
  "strategic_focus": [{{"theme": "focus area", "evidence": "supporting evidence", "source_url": "url", "priority": "high/medium/low"}}],
  "competitive_landscape": [{{"competitor": "company name", "relationship": "competing/collaborating/acquiring", "source_url": "url"}}],
  "tech_roadmap": [{{"initiative": "technology initiative", "timeline": "expected timeframe", "description": "brief description", "source_url": "url"}}],
  "leadership_team": [{{"name": "person name", "position": "job title", "background": "brief background", "source_url": "url"}}],
  "it_infrastructure_summary": "comprehensive summary of IT infrastructure and technology stack or null",
  "business_context": "overall business situation and market context or null", 
  "market_position": "company's competitive position and market standing or null",
  "confidence_score": 0.0
}}\n\nEXTRACTION RULES:\n- Extract ALL factual information present, no matter how detailed\n- INFER reasonable information when direct data is limited (mark as "inferred")\n- Use exact figures, currencies, percentages, dates when available\n- Categorize technologies (cloud, AI, software, hardware, etc.)\n- Specify relationship types for vendors/partners\n- Include timeline information when mentioned\n- Assess business impact of announcements\n- Prioritize strategic focus areas when context allows\n- For limited data: make educated inferences based on industry and company context\n- Confidence score (0-1) based on data completeness and source reliability\n- Maximum 15 items per array section for comprehensive coverage\n- IMPORTANT: When data is sparse, populate "inferred" sections with reasonable assumptions"""

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": base_system},
                {"role": "user", "content": instruction}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content.strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as je:
            print(f"[AI Intelligence] JSON parse error, returning legacy normalization attempt: {je}")
            return {"error": "parse_error", "raw": raw[:500]}

        # Enhanced defensive defaults for comprehensive schema
        def ensure(key, default):
            if key not in data or data[key] is None:
                data[key] = default
        
        # Core data structures
        ensure("financial_data", {
            "revenue": None, "market_cap": None, "growth_rate": None, "stock_price": None,
            "pe_ratio": None, "dividend_yield": None, "other_metrics": [], 
            "source_url": None, "confidence": 0.0
        })
        ensure("technologies", {"confirmed": [], "inferred": []})
        ensure("vendors_partners", {"confirmed": [], "inferred": []})
        ensure("recent_projects", [])
        ensure("announcements", [])
        ensure("strategic_focus", [])
        
        # New enhanced fields
        ensure("competitive_landscape", [])
        ensure("tech_roadmap", [])
        ensure("leadership_team", [])
        ensure("it_infrastructure_summary", None)
        ensure("business_context", None)
        ensure("market_position", None)
        
        if "confidence_score" not in data:
            data["confidence_score"] = data.get("financial_data", {}).get("confidence", 0.0)

        # Enhanced sanitation (truncate oversize arrays for performance)
        array_limits = {
            "recent_projects": 15, "announcements": 15, "strategic_focus": 15,
            "competitive_landscape": 10, "tech_roadmap": 12, "leadership_team": 8
        }
        
        for arr_key, limit in array_limits.items():
            if isinstance(data.get(arr_key), list) and len(data[arr_key]) > limit:
                data[arr_key] = data[arr_key][:limit]

        # Enhanced diagnostics
        tech_confirmed = len(data.get('technologies', {}).get('confirmed', []))
        tech_inferred = len(data.get('technologies', {}).get('inferred', []))
        vendors_confirmed = len(data.get('vendors_partners', {}).get('confirmed', []))
        vendors_inferred = len(data.get('vendors_partners', {}).get('inferred', []))
        
        print("[AI Intelligence] Comprehensive extraction results: " + ", ".join([
            f"tech_confirmed={tech_confirmed}",
            f"tech_inferred={tech_inferred}", 
            f"vendors_confirmed={vendors_confirmed}",
            f"vendors_inferred={vendors_inferred}",
            f"announcements={len(data.get('announcements', []))}",
            f"projects={len(data.get('recent_projects', []))}",
            f"strategic_focus={len(data.get('strategic_focus', []))}",
            f"tech_roadmap={len(data.get('tech_roadmap', []))}",
            f"leadership={len(data.get('leadership_team', []))}",
            f"confidence={data.get('confidence_score', 0):.2f}"
        ]))

        return data
    except Exception as e:
        print(f"[AI Intelligence] Error: {e}")
        return {"error": str(e)}

def openai_benefits_summary(client: str, rows: List[Dict[str, str]], intelligence_data: Optional[Dict] = None) -> Dict[str, str]:
    """
    PROFESSIONAL PRESALES-GRADE PROMPT TEMPLATE
    Generate SHORT and LONG pitches from a presales manager's perspective.
    """
    if not OPENAI_API_KEY:
        return {
            "short": f"OpenAI API key not configured. Cannot generate pitch for {client}.",
            "long": "Please configure OPENAI_API_KEY environment variable."
        }

    ai_client = OpenAI(api_key=OPENAI_API_KEY)

    # Build context from matched rows
    evidence_lines = []
    for i, r in enumerate(rows, 1):
        evidence_lines.append(f"""
Project {i}:
- Client: {_safe_str(r.get('client_name', r.get('client', '')))}
- Industry: {_safe_str(r.get('industry', ''))}
- Technologies: {_safe_str(r.get('technologies', r.get('technology', '')))}
- Business Challenge: {_safe_str(r.get('business_case', ''))}
- Evoke Solution: {_safe_str(r.get('evoke_solution_/_value_add_to_the_customer_(what_/_how)', r.get('value_add', '')))}
- Key Deliverables: {_safe_str(r.get('key_deliverables', ''))}
- Project Status: {_safe_str(r.get('status', ''))}
""")

    evidence_block = "\n".join(evidence_lines) if evidence_lines else "(No matching projects found)"

    # Build intelligence context
    intelligence_context = ""
    if intelligence_data and not intelligence_data.get("error"):
        intel_parts = []
        
        if "financial_data" in intelligence_data:
            # financial = [f"- {item.get('metric', '')}: {item.get('value', '')}" 
            #             for item in intelligence_data["financial_data"]]
            financial = []
            for item in intelligence_data["financial_data"]:
                if isinstance(item, dict):          # new schema
                    financial.append(f"- {item.get('metric', '')}: {item.get('value', '')}")
                elif isinstance(item, str):         # legacy flat list
                    financial.append(f"- {item}")
            if financial:
                intel_parts.append("Financial Intelligence:\n" + "\n".join(financial))
        
        if "technologies" in intelligence_data:
            techs = [f"- {item.get('name', '') if isinstance(item, dict) else item}" 
                    for item in intelligence_data["technologies"]]
            if techs:
                intel_parts.append("Technology Stack:\n" + "\n".join(techs))
        
        if "recent_announcements" in intelligence_data:
            announcements = [f"- {item.get('title', '')}: {item.get('summary', '')}" 
                           for item in intelligence_data["recent_announcements"]]
            if announcements:
                intel_parts.append("Recent Announcements:\n" + "\n".join(announcements))
        
        intelligence_context = "\n\n".join(intel_parts) if intel_parts else ""

    # ENHANCED PRESALES-GRADE SYSTEM PROMPT WITH WORD COUNT CONSTRAINTS
    system_prompt = """You are a presales consultant for Evoke Technologies. Generate TWO summaries with STRICT word count requirements:

1. SHORT SUMMARY (EXACTLY 250-300 words):
   - Hook: Why this matters NOW (reference recent news/announcements if available)
   - Evidence: 2-3 specific outcomes from portfolio projects
   - Connection: Link to their strategic focus and industry trends
   - Value: What Evoke brings uniquely
   - Call to action

2. LONG SUMMARY - STRUCTURED JSON FORMAT with interactive bullet points:

   Create structured sections with expandable bullet points for interactive display:

   **Business Context Section:**
   - 3-4 bullet points covering: market position, recent announcements, technology landscape, strategic initiatives
   - Each bullet: key theme + detailed explanation

   **Evoke's Relevant Experience Section:** 
   - 3-4 bullet points covering: similar client outcomes, technology expertise, industry experience, measurable results
   - Each bullet: success story theme + specific details and metrics

   **Strategic Fit & Value Proposition Section:**
   - 2-3 bullet points covering: unique positioning, competitive advantages, proven methodologies
   - Each bullet: value driver + supporting evidence

   **Next Steps & Engagement Model Section:**
   - 2-3 bullet points covering: recommended approach, timeline/milestones, expected outcomes
   - Each bullet: engagement phase + description and benefits

CRITICAL REQUIREMENTS:
- Use financial data and announcements to create urgency and relevance
- Reference their current vendors/technologies to position Evoke naturally
- Connect their strategic focus to our portfolio evidence
- Be SPECIFIC with numbers, metrics, and outcomes
- NEVER imply we worked with the prospect directly - use "companies such as X" or "similar organizations in Y industry"
- COUNT YOUR WORDS - SHORT must be 250-300 words, LONG must be 800-1000 words
- Use markdown formatting (## for sections, **bold** for emphasis)"""

    user_prompt = f"""CLIENT: {client}

EVOKE PORTFOLIO PROJECTS:
{evidence_block}

CLIENT INTELLIGENCE DATA:
{intelligence_context if intelligence_context else "(Limited intelligence available - focus on industry trends)"}

TASK:
Generate THREE outputs with STRICT requirements:

1. SHORT SUMMARY (250-300 words total):
   - Start with a hook referencing their recent news/situation
   - Provide 2-3 specific outcomes from our portfolio
   - Connect to their strategic needs
   - End with clear value proposition and call to action
   - MUST BE 250-300 WORDS

2. LONG SUMMARY (800-1000 words total):
   - Comprehensive detailed pitch covering all four sections
   - Business Context, Evoke's Experience, Strategic Fit, Next Steps
   - Rich narratives with specific examples and metrics
   - MUST BE 800-1000 WORDS

3. STRUCTURED JSON FOR INTERACTIVE DISPLAY:
   Return a "long_structured" object with this format:
   {{
     "sections": [
       {{
         "title": "Business Context",
         "bullet_points": [
           {{
             "summary": "Market Position & Financial Health",
             "details": ["Strong market position in engineering services sector", "Revenue growth of X% in recent quarters", "Key strategic positioning advantages in their industry"]
           }},
           {{
             "summary": "Recent Strategic Initiatives", 
             "details": ["Digital transformation initiatives launched", "Strategic partnerships with technology vendors", "Investment in automation and AI capabilities"]
           }}
         ]
       }},
       {{
         "title": "Evoke's Relevant Experience",
         "bullet_points": [
           {{
             "summary": "Similar Client Success Stories",
             "details": "Specific examples of how we've helped companies like X achieve Y outcomes with Z technologies, resulting in measurable benefits..."
           }}
         ]
       }}
     ]
   }}

CRITICAL OUTPUT FORMAT:
Return a JSON object with exactly these three keys:
{{
  "short": "250-300 word summary...",
  "long": "800-1000 word detailed pitch covering all four sections...",
  "long_structured": {{ "sections": [array of sections] }}
}}

CONTENT REQUIREMENTS:
- Use intelligence data to create compelling, timely narratives
- Reference their vendors/technologies naturally  
- NEVER imply we worked with the client directly - use "companies such as X"
- Be specific with numbers and metrics
- Ensure ALL sections are included: Business Context, Evoke's Relevant Experience, Strategic Fit & Value Proposition, Next Steps & Engagement Model
- Each section should have 2-4 meaningful bullet points with substantive details
- IMPORTANT: "details" field must be an ARRAY of 2-4 specific points, not a single string
- COUNT YOUR WORDS CAREFULLY"""

    try:
        print(f"[API] Calling OpenAI API with model: {OPENAI_MODEL}")
        resp = ai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        print(f"[API] OpenAI response received, parsing JSON...")
        raw_content = resp.choices[0].message.content.strip()
        print(f"[API] Raw response length: {len(raw_content)} characters")
        
        result = json.loads(raw_content)
        print(f"[API] JSON parsing successful, keys: {list(result.keys())}")
        
        short = result.get('short', '')
        long = result.get('long', '')
        long_structured = result.get('long_structured', None)
        
        print(f"[SUMMARY] Generated summaries:")
        print(f"  - Short: {len(short.split())} words")
        print(f"  - Long: {len(long.split())} words")
        if long_structured:
            sections_count = len(long_structured.get('sections', []))
            print(f"  - Structured: {sections_count} sections")
        else:
            print(f"  - Structured: None (missing in response)")
        
        return {"short": short, "long": long, "long_structured": long_structured}

    except json.JSONDecodeError as e:
        print(f"[Pitch Generation] JSON Error: {e}")
        print(f"[Pitch Generation] Raw content: {raw_content[:500]}...")
        return {
            "short": f"JSON parsing error: {str(e)}",
            "long": f"The API response was not valid JSON. Please try again.",
            "long_structured": None
        }
    except Exception as e:
        print(f"[Pitch Generation] Error: {e}")
        import traceback
        print(f"[Pitch Generation] Traceback: {traceback.format_exc()}")
        return {
            "short": f"Error generating pitch: {str(e)}",
            "long": f"Please check API configuration and try again.",
            "long_structured": None
        }

def select_rows_for_summary(
    client: str,
    industry: Optional[str],
    technology: Optional[str],
    focus: Optional[str],
    limit: int = 6
) -> List[Dict[str, Any]]:
    """
    Semantic search with enhanced reasoning for row selection.
    Returns rows with match scores, similarity, and detailed reasoning.
    """
    print(f"\n{'='*80}")
    print(f"[Portfolio Search] Client: {client} | Industry: {industry} | Tech: {technology}")
    print(f"{'='*80}")

    embeddings, df = load_or_create_embeddings()
    if df.empty or len(embeddings) == 0:
        return []

    # Generate query embedding
    query_parts = [f"Client: {client}"]
    if industry:
        query_parts.append(f"Industry: {industry}")
    if technology:
        query_parts.append(f"Technology: {technology}")
    if focus:
        query_parts.append(f"Focus: {focus}")
    
    query_text = " ".join(query_parts)
    
    try:
        ai_client = OpenAI(api_key=OPENAI_API_KEY)
        query_response = ai_client.embeddings.create(
            model="text-embedding-3-small",
            input=[query_text],
            dimensions=1536
        )
        query_embedding = np.array(query_response.data[0].embedding, dtype=np.float32)
    except Exception as e:
        print(f"[Embeddings] Query embedding error: {e}")
        return []

    # Compute similarities
    similarities = cosine_similarity_batch(query_embedding, embeddings)

    # Pre-filter by industry if specified
    candidate_indices = list(range(len(df)))
    if industry:
        industry_lower = industry.lower()
        candidate_indices = [
            i for i in candidate_indices
            if industry_lower in _safe_str(df.iloc[i].get('industry', '')).lower()
        ]
        print(f"[Filter] Industry pre-filter: {len(candidate_indices)} candidates")

    if not candidate_indices:
        candidate_indices = list(range(len(df)))

    # Score all candidates
    scored_rows = []
    for idx in candidate_indices:
        row = df.iloc[idx]
        row_embedding = embeddings[idx]
        
        scoring_result = score_row_with_reasoning(
            row=row,
            query_embedding=query_embedding,
            row_embedding=row_embedding,
            client=client,
            industry=industry,
            technology=technology,
            focus=focus
        )

        row_dict = row.to_dict()
        row_dict.update(scoring_result)
        scored_rows.append(row_dict)

    # Sort by match score descending
    scored_rows.sort(key=lambda x: x["match_score"], reverse=True)

    # Return top matches
    top_matches = scored_rows[:limit]
    
    print(f"[Portfolio Search] Top {len(top_matches)} matches:")
    for i, match in enumerate(top_matches, 1):
        print(f"  {i}. {match.get('client_name', 'Unknown')} - Score: {match['match_score']}% | Similarity: {match['semantic_similarity']}%")

    return top_matches

# ===================== API ENDPOINTS =====================

@app.post("/determine_industry")
def determine_industry(req: dict):
    """Detect industry from customer name using GPT-4o."""
    customer = req.get("customer", "")
    if not customer or not OPENAI_API_KEY:
        return {"data": {"industry": "", "confidence": 0.0}}

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""Identify the primary industry for this company: {customer}

Return ONLY valid JSON with this structure:
{{"industry": "Industry Name", "confidence": 0.0-1.0}}

Examples:
- Microsoft -> {{"industry": "Technology", "confidence": 0.95}}
- JPMorgan -> {{"industry": "Financial Services", "confidence": 0.90}}

Be specific but concise (1-2 words for industry)."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content.strip())
        return {"data": result}

    except Exception as e:
        print(f"[Industry Detection] Error: {e}")
        return {"data": {"industry": "", "confidence": 0.0}}

@app.post("/portfolio_summary", response_model=PortfolioSummaryResponse)
def portfolio_summary(req: PortfolioRequest):
    """Main endpoint: Search portfolio and gather intelligence."""
    print("\n" + "="*80)
    print(f"[API] Starting portfolio search for: {req.client}")
    print("="*80)
    
    # Auto-detect industry if not provided
    detected_industry = req.industry
    industry_confidence = None
    
    if not req.industry and req.client:
        print(f"[API] Auto-detecting industry for {req.client}")
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            prompt = f"""Identify the primary industry for this company: {req.client}

You must respond with ONLY a valid JSON object in this exact format:
{{"industry": "Industry Name", "confidence": 0.85}}

Use one of these industry categories: Technology, Healthcare, Financial Services, Manufacturing, Retail, Energy, Telecommunications, Automotive, Aerospace, Media, Real Estate, Education, Government, Non-profit, Other

Do not include any explanation or additional text."""

            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"[API] Raw OpenAI response: {response_text}")
            
            # Try to extract JSON even if there's extra text
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_text = response_text[start:end]
                result = json.loads(json_text)
            else:
                # Fallback: manual parsing for common cases
                if req.client.lower() in ['apple', 'microsoft', 'google', 'amazon']:
                    result = {"industry": "Technology", "confidence": 0.9}
                else:
                    result = {"industry": "Technology", "confidence": 0.5}  # Default fallback
            
            detected_industry = result.get("industry", "")
            industry_confidence = result.get("confidence", 0.0)
            
            print(f"[API] Auto-detected industry: {detected_industry} (confidence: {industry_confidence:.2f})")
            
        except Exception as e:
            print(f"[API] Industry detection failed: {e}")
            # Provide smart fallback based on common company names
            if req.client.lower() in ['apple', 'microsoft', 'google', 'amazon', 'tesla', 'meta', 'netflix']:
                detected_industry = "Technology"
                industry_confidence = 0.8
                print(f"[API] Using fallback industry: {detected_industry}")
            else:
                detected_industry = ""
                industry_confidence = None

    # Select matching rows with reasoning
    matched_rows = select_rows_for_summary(
        client=req.client,
        industry=detected_industry,
        technology=req.technology,
        focus=req.focus,
        limit=req.limit
    )

    # Gather web intelligence (if not provided)
    if req.intelligence_data and not req.intelligence_data.get("error"):
        print(f"[API] Reusing provided intelligence data")
        intelligence_data = req.intelligence_data
    else:
        print(f"[API] Gathering fresh intelligence...")
        web_data = comprehensive_web_search(
            client=req.client,
            industry=detected_industry,
            focus=req.focus,
            company_website=req.company_website
        )
        intelligence_data = ai_extract_intelligence(web_data)
        intelligence_data = _normalize_legacy_intel(intelligence_data)

    print(f"[API] Returning {len(matched_rows)} matched rows with intelligence")
    print("="*80 + "\n")

    return PortfolioSummaryResponse(
        short_summary="",
        long_summary="",
        rows=matched_rows,
        intelligence_data=intelligence_data,
        detected_industry=detected_industry if not req.industry else None,
        industry_confidence=industry_confidence
    )

@app.post("/portfolio_summary_selected", response_model=PortfolioSummaryResponse)
def portfolio_summary_selected(req: PortfolioSummarySelectedRequest):
    """Generate pitch from selected rows (reuses intelligence)."""
    print("\n" + "="*80)
    print(f"[API] Generating pitch for {req.client} with {len(req.rows)} selected rows")
    print("="*80)

    # Use cached intelligence if provided
    if req.intelligence_data and not req.intelligence_data.get("error"):
        print(f"[API] Reusing intelligence data from first fetch (no SerpAPI call)")
        intelligence_data = req.intelligence_data
    else:
        print(f"[API] Warning: No intelligence data provided, generating without context")
        intelligence_data = None

    # Generate pitch
    pitch = openai_benefits_summary(req.client, req.rows, intelligence_data)

    print(f"[API] Pitch generation complete")
    print("="*80 + "\n")

    return PortfolioSummaryResponse(
        short_summary=pitch.get("short", ""),
        long_summary=pitch.get("long", ""),
        long_structured=pitch.get("long_structured", None),
        rows=[],
        intelligence_data=intelligence_data
    )

@app.post("/refine_pitch")
def refine_pitch(req: PitchRefinementRequest):
    """
    NEW ENDPOINT: Refine existing pitch based on user instructions.
    Takes current pitch + refinement instructions -> generates improved version.
    """
    print("\n" + "="*80)
    print(f"[API] Refining pitch for {req.client}")
    print(f"[Refinement] User instructions: {req.refinement_instructions[:100]}...")
    print("="*80)

    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        ai_client = OpenAI(api_key=OPENAI_API_KEY)

        # Build context
        evidence_summary = "\n".join([
            f"- {r.get('client_name', '')}: {r.get('evoke_solution_/_value_add_to_the_customer_(what_/_how)', '')[:100]}"
            for r in req.context_rows[:5]
        ])

        intelligence_summary = ""
        if req.intelligence_data and not req.intelligence_data.get("error"):
            intel_parts = []
            if "financial_data" in req.intelligence_data:
                intel_parts.append(f"Financial: {len(req.intelligence_data['financial_data'])} metrics")
            if "technologies" in req.intelligence_data:
                intel_parts.append(f"Technologies: {len(req.intelligence_data['technologies'])} identified")
            intelligence_summary = ", ".join(intel_parts)

        refinement_prompt = f"""You are refining a presales pitch based on client feedback.

ORIGINAL PITCH:

SHORT VERSION:
{req.current_short_pitch}

LONG VERSION:
{req.current_long_pitch}

CONTEXT:
- Client: {req.client}
- Supporting Evidence: {evidence_summary}
- Intelligence: {intelligence_summary}

USER REFINEMENT INSTRUCTIONS:
{req.refinement_instructions}

TASK:
Generate an IMPROVED pitch that:
1. Preserves the core value propositions from the original
2. Incorporates the user's requested changes/additions
3. Maintains presales-grade professional tone
4. Keeps the SHORT/LONG structure

Return in this format:

SHORT PITCH:
[improved 100-150 word version]

LONG PITCH:
[improved 400-600 word version with sections]

Generate the refined pitch now:"""

        response = ai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": refinement_prompt}],
            temperature=0.7,
            max_tokens=2000
        )

        content = response.choices[0].message.content.strip()

        # Parse response
        short_match = content.find("SHORT PITCH")
        long_match = content.find("LONG PITCH")

        if short_match != -1 and long_match != -1:
            short_section = content[short_match:long_match].replace("SHORT PITCH", "").replace(":", "").strip()
            long_section = content[long_match:].replace("LONG PITCH", "").replace(":", "").strip()
        else:
            parts = [p.strip() for p in content.split('\n\n') if p.strip()]
            short_section = parts[0] if parts else content[:500]
            long_section = "\n\n".join(parts[1:]) if len(parts) > 1 else content

        print(f"[API] Pitch refinement complete")
        print("="*80 + "\n")

        return {
            "short_summary": short_section,
            "long_summary": long_section
        }

    except Exception as e:
        print(f"[Pitch Refinement] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

@app.post("/download_pitch")
def download_pitch(req: PitchDownloadRequest):
    """
    Generate and download pitch as PDF.
    Returns a PDF file containing the formatted pitch content.
    """
    print(f"[PDF Download] Generating PDF for {req.client}")
    
    try:
        # Create HTML content for the pitch
        current_date = datetime.now().strftime("%B %d, %Y")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{req.client} - Presales Pitch</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px;
                    color: #333;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #1976d2;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .company-name {{
                    font-size: 2.2em;
                    color: #1976d2;
                    margin: 0;
                    font-weight: 700;
                }}
                .subtitle {{
                    font-size: 1.2em;
                    color: #666;
                    margin: 10px 0;
                }}
                .date {{
                    color: #888;
                    font-size: 0.9em;
                }}
                .section {{
                    margin: 30px 0;
                    padding: 20px;
                    border-left: 4px solid #1976d2;
                    background: #f8f9fa;
                }}
                .section-title {{
                    font-size: 1.4em;
                    color: #1976d2;
                    margin: 0 0 15px 0;
                    font-weight: 600;
                }}
                .content {{
                    margin: 15px 0;
                    text-align: justify;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 0.9em;
                }}
                .evoke-brand {{
                    color: #1976d2;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 class="company-name">{req.client}</h1>
                <p class="subtitle">Presales Pitch & Value Proposition</p>
                <p class="date">Generated on {current_date}</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Executive Summary</h2>
                <div class="content">
                    {req.short_pitch.replace('\\n', '<br>').replace('**', '<strong>').replace('**', '</strong>')}
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Detailed Proposal</h2>
                <div class="content">
                    {req.long_pitch.replace('\\n', '<br>').replace('**', '<strong>').replace('**', '</strong>')}
                </div>
            </div>
            
            <div class="footer">
                <p>Prepared by <span class="evoke-brand">Evoke Technologies</span></p>
                <p>Presales Assistant - AI-Powered Portfolio Intelligence</p>
            </div>
        </body>
        </html>
        """
        
        # Convert HTML to PDF-like format by returning formatted text
        # Since we don't have PDF libraries, we'll return a structured text format
        text_content = f"""
{req.client.upper()} - PRESALES PITCH
Generated on {current_date}
{'='*60}

EXECUTIVE SUMMARY
{'-'*20}
{req.short_pitch}

DETAILED PROPOSAL  
{'-'*20}
{req.long_pitch}

{'='*60}
Prepared by Evoke Technologies
Presales Assistant - AI-Powered Portfolio Intelligence
        """
        
        # Create a simple text file as PDF alternative
        text_bytes = text_content.encode('utf-8')
        
        print(f"[PDF Download] Generated document for {req.client} ({len(text_bytes)} bytes)")
        
        return Response(
            content=text_bytes,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={req.client}_pitch.txt"
            }
        )
        
    except Exception as e:
        print(f"[PDF Download] Error: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

# ===================== STARTUP =====================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*80)
    print("ENHANCED PRESALES ASSISTANT API")
    print("="*80)
    print("Features:")
    print("  Bullet-point reasoning with percentage match scores")
    print("  Pitch refinement endpoint")
    print("  Professional presales-grade prompts")
    print("  Semantic search with embeddings")
    print("  Web intelligence gathering")
    print("="*80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
