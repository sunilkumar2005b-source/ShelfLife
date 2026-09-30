from typing import Dict
from pydantic import BaseModel, Field


class RuleConfig(BaseModel):
    """
    Configurable parameters for the heuristic Inventory Intelligence rule engine.
    Eliminates magic numbers by centralizing all decision boundaries,
    scoring weights, and environmental factor thresholds.
    """

    # Expiry thresholds (days)
    expiry_critical_days: int = Field(
        default=2,
        ge=0,
        le=15,
        description="Batches expiring within this number of days trigger urgent action"
    )
    expiry_warning_days: int = Field(
        default=5,
        ge=1,
        le=30,
        description="Batches expiring within this window require monitoring"
    )
    expiry_safe_days: int = Field(
        default=10,
        ge=3,
        le=60,
        description="Batches with more remaining shelf life receive full expiry scores"
    )

    # Spoilage probability thresholds (0.0 - 1.0)
    spoilage_high_threshold: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
        description="Probability threshold for High spoilage risk classification"
    )
    spoilage_medium_threshold: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Probability threshold for Medium spoilage risk classification"
    )

    # Stock-to-demand ratio thresholds
    reorder_buffer_multiplier: float = Field(
        default=1.0,
        ge=0.5,
        le=3.0,
        description="Stock level below predicted_demand * multiplier triggers Reorder"
    )
    stock_excess_multiplier: float = Field(
        default=2.0,
        ge=1.1,
        le=5.0,
        description="Stock level exceeding predicted_demand * multiplier considered excess"
    )

    # Health score component weights (Sum = 1.0)
    weight_stock: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Weight of stock coverage in final health score"
    )
    weight_expiry: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Weight of days-to-expiry in final health score"
    )
    weight_spoilage: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Weight of spoilage probability in final health score"
    )

    # Environmental thresholds
    dairy_max_temp: float = Field(
        default=5.0,
        description="Maximum recommended storage temperature for dairy (°C)"
    )
    ambient_high_temp: float = Field(
        default=30.0,
        description="High ambient temperature threshold accelerating degradation (°C)"
    )
    high_humidity_threshold: float = Field(
        default=78.0,
        description="Relative humidity (%) above which microbial mold growth accelerates"
    )


# Active in-memory singleton configuration instance
_active_config = RuleConfig()


def get_rule_config() -> RuleConfig:
    """Return the active rule engine configuration."""
    return _active_config


def update_rule_config(new_config: RuleConfig) -> RuleConfig:
    """Update the active rule engine configuration."""
    global _active_config
    _active_config = new_config
    return _active_config
