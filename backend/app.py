import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from backend.config.settings import get_settings
from backend.src.services.review_service import get_review_service, ReviewService

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("backend.app")

settings = get_settings()


# =====================================================================
# PYDANTIC REQUEST & RESPONSE SCHEMAS
# =====================================================================

class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Customer review text string to analyze", example="The sound quality is fantastic and battery lasts long.")

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Review text must not be blank.")
        return value


class SentimentResponse(BaseModel):
    sentiment: str = Field(..., description="Predicted sentiment class ('Positive', 'Neutral', 'Negative')")
    confidence: float = Field(..., description="Prediction confidence score (0.0 to 1.0)")
    probabilities: Dict[str, float] = Field(..., description="Class probability breakdown")
    preprocessed_text: str = Field(..., description="Normalized text used for inference")


class AskAIRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="User question about customer reviews", example="What battery problems are customers reporting?")
    product: Optional[str] = Field(None, description="Optional product filter")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of reviews to retrieve for context")

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question must not be blank.")
        return value


class AskAIResponse(BaseModel):
    question: str
    answer: str
    retrieved_reviews: List[Dict[str, Any]]
    review_count: int
    model_used: str


class CompareProductsRequest(BaseModel):
    product_a: str = Field(..., description="Name of Product A")
    product_b: str = Field(..., description="Name of Product B")

    @field_validator("product_a", "product_b")
    @classmethod
    def validate_product_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Product name must not be blank.")
        return value


# =====================================================================
# LIFESPAN & APPLICATION INITIALIZATION
# =====================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager: Pre-warms models and database connections on startup.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    try:
        service = get_review_service()
        logger.info("Pre-warming analytics data and shared service configuration...")
        _ = service.get_dashboard()
        logger.info("All components initialized successfully. Server ready for requests.")
    except Exception as e:
        logger.error(f"Error during application startup pre-warming: {e}")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade AI Platform for Customer Review Intelligence, Sentiment Analysis, RAG Semantic Search, and Analytics.",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# API ENDPOINTS
# =====================================================================

@app.get("/", tags=["Health Check"])
async def root():
    """
    Root API health check endpoint.
    """
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
    }


@app.post(
    "/predict-sentiment",
    response_model=SentimentResponse,
    tags=["Sentiment Analysis"],
    summary="Predict Sentiment for Review Text",
)
async def predict_sentiment(
    request: SentimentRequest,
    service: ReviewService = Depends(get_review_service),
):
    """
    Predicts sentiment classification ('Positive', 'Neutral', 'Negative'), confidence score,
    and class probability breakdown using TF-IDF + Logistic Regression.
    """
    try:
        result = service.predict_sentiment(text=request.text)
        return result
    except Exception:
        logger.exception("Error predicting sentiment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to predict sentiment at this time.",
        )


@app.post(
    "/ask-ai",
    response_model=AskAIResponse,
    tags=["AI Review Assistant (RAG)"],
    summary="Ask Questions About Reviews using RAG + Gemini AI",
)
async def ask_ai(
    request: AskAIRequest,
    service: ReviewService = Depends(get_review_service),
):
    """
    Answers natural language questions about customer reviews using RAG:
    Query Expansion -> ChromaDB Vector Retrieval -> Gemini AI Generation.
    """
    try:
        result = service.ask_ai(
            question=request.question,
            product=request.product,
            top_k=request.top_k or 5,
        )
        return result
    except Exception:
        logger.exception("Error processing AI question")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the AI review question at this time.",
        )


@app.get(
    "/dashboard",
    tags=["Analytics"],
    summary="Executive Dashboard Metrics & Overview",
)
async def get_dashboard(
    service: ReviewService = Depends(get_review_service),
):
    """
    Returns aggregate executive dashboard metrics:
    Total Reviews, Total Products, Average Rating, Sentiment Percentages, Star Distribution, and Featured Reviews.
    """
    try:
        return service.get_dashboard()
    except Exception:
        logger.exception("Error retrieving dashboard metrics")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve dashboard analytics at this time.",
        )


@app.get(
    "/products",
    tags=["Products"],
    summary="List All Products with Aggregate Metrics",
)
async def get_products(
    search: str = Query("", description="Optional search term to filter products"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of products to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: ReviewService = Depends(get_review_service),
):
    """
    Returns list of products with review counts and average ratings.
    """
    try:
        return service.get_products(search=search, limit=limit, offset=offset)
    except Exception:
        logger.exception("Error listing products")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to list products at this time.",
        )


@app.get(
    "/product/{product_name:path}",
    tags=["Products"],
    summary="Get Detailed Product Analytics & AI Summary",
)
async def get_product_details(
    product_name: str,
    service: ReviewService = Depends(get_review_service),
):
    """
    Returns detailed product statistics, rating distributions, top complaints,
    top positive reviews, and AI-generated product summary.
    """
    try:
        result = service.get_product_by_name(product_name=product_name)
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"],
            )
        return result
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error fetching product details for '%s'", product_name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve product analytics at this time.",
        )


@app.get(
    "/reviews",
    tags=["Review Explorer"],
    summary="Explore & Search Customer Reviews",
)
async def explore_reviews(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query("", description="Search term or semantic query"),
    product: str = Query("", description="Filter by product name"),
    sentiment: str = Query("", description="Filter by sentiment ('Positive', 'Neutral', 'Negative')"),
    rating: Optional[float] = Query(None, description="Filter by exact star rating"),
    is_semantic: bool = Query(False, description="Enable semantic vector search via ChromaDB"),
    service: ReviewService = Depends(get_review_service),
):
    """
    Explores customer reviews with support for keyword search, metadata filters,
    pagination, and semantic vector search.
    """
    try:
        return service.explore_reviews(
            page=page,
            page_size=page_size,
            search=search,
            product=product,
            sentiment=sentiment,
            rating=rating,
            is_semantic=is_semantic,
        )
    except Exception:
        logger.exception("Error exploring reviews")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to explore reviews at this time.",
        )


@app.get(
    "/analytics",
    tags=["Analytics"],
    summary="Comprehensive Analytics Overview",
)
async def get_analytics(
    service: ReviewService = Depends(get_review_service),
):
    """
    Returns full platform analytics data for charts and dashboards.
    """
    try:
        return service.get_dashboard()
    except Exception:
        logger.exception("Error fetching analytics")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve analytics at this time.",
        )


@app.post(
    "/compare-products",
    tags=["Product Intelligence"],
    summary="Compare Two Products Head-to-Head using AI",
)
async def compare_products(
    request: CompareProductsRequest,
    service: ReviewService = Depends(get_review_service),
):
    """
    Compares two products head-to-head using analytics and Gemini AI comparative summaries.
    """
    if request.product_a.casefold() == request.product_b.casefold():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Choose two different products to compare.",
        )

    try:
        return service.compare_products(
            product_a=request.product_a,
            product_b=request.product_b,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except Exception:
        logger.exception("Error comparing products")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to compare products at this time.",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
