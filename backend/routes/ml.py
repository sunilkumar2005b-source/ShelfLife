"""
FastAPI Routes for Machine Learning Prediction & Synchronization (Section 8)
"""

from fastapi import APIRouter, HTTPException, status
from schemas.ml import (
    DemandPredictionRequest,
    DemandPredictionResponse,
    SpoilagePredictionRequest,
    SpoilagePredictionResult,
    MLSyncResponse,
    MLStatusResponse,
)
from services.ml_service import (
    get_ml_status,
    predict_product_demand,
    predict_batch_spoilage,
    sync_database_predictions,
)

router = APIRouter(prefix="/ml", tags=["Machine Learning & Predictions"])


@router.get("/status", response_model=MLStatusResponse)
def get_model_status():
    """
    Returns metadata, training sample sizes, champion model architectures,
    and test evaluation metrics for all active ML models.
    """
    try:
        return get_ml_status()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to read ML model status: {str(error)}"
        )


@router.post("/predict/demand", response_model=DemandPredictionResponse)
def predict_demand_endpoint(request: DemandPredictionRequest):
    """
    Generate real-time demand forecast for a specified product ID or arbitrary product features
    using the champion Ridge Regression model.
    """
    try:
        return predict_product_demand(request)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demand forecasting inference failed: {str(error)}"
        )


@router.post("/predict/spoilage", response_model=SpoilagePredictionResult)
def predict_spoilage_endpoint(request: SpoilagePredictionRequest):
    """
    Generate real-time spoilage risk tier and continuous probability for an inventory batch
    using the champion Logistic Regression model.
    """
    try:
        return predict_batch_spoilage(request)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Spoilage prediction inference failed: {str(error)}"
        )


@router.post("/sync-predictions", response_model=MLSyncResponse)
def sync_predictions_endpoint():
    """
    Executes live ML batch inference across all products and active inventory in the database,
    replacing synthetic demo seeds with genuine trained ML predictions.
    """
    try:
        return sync_database_predictions()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ML synchronization failed: {str(error)}"
        )
