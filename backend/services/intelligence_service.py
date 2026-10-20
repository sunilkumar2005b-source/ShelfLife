from datetime import date
from typing import Optional, Tuple
from .rule_config import RuleConfig, get_rule_config


def days_until_expiry(expiry_date) -> int:
    """
    Calculate the number of integer days remaining until expiry.
    Returns 0 if already expired or if expiry_date is today.
    """
    if expiry_date is None:
        return 0

    if isinstance(expiry_date, str):
        expiry_date = date.fromisoformat(expiry_date[:10])

    return max((expiry_date - date.today()).days, 0)


def calculate_health_score(
    current_stock: float,
    predicted_demand: float,
    days_remaining: int,
    spoilage_probability: float,
    storage_temp: Optional[float] = None,
    category: Optional[str] = None,
    config: Optional[RuleConfig] = None,
) -> int:
    """
    Calculate a normalized Inventory Health Score from 0 to 100.
    Explicitly a deterministic heuristic rule calculation, NOT a trained ML model.

    Score Breakdown:
    - Stock Coverage Score (configurable weight)
    - Shelf Life Expiry Score (configurable weight)
    - Spoilage Resistance Score (configurable weight)
    - Environmental / Storage temperature penalty modifier
    """
    if config is None:
        config = get_rule_config()

    # 1. Stock Coverage Score (0 - 100)
    if predicted_demand <= 0:
        stock_score = 100.0
    else:
        stock_ratio = current_stock / predicted_demand
        if stock_ratio >= config.stock_excess_multiplier:
            # Overstocked - potential capital lockup
            stock_score = 85.0
        elif stock_ratio >= 1.2:
            # Ideal stock buffer
            stock_score = 100.0
        elif stock_ratio >= config.reorder_buffer_multiplier:
            stock_score = 80.0
        elif stock_ratio >= 0.75:
            stock_score = 55.0
        elif stock_ratio >= 0.50:
            stock_score = 35.0
        else:
            # Critically understocked
            stock_score = 15.0

    # 2. Expiry Score (0 - 100)
    if days_remaining <= 0:
        expiry_score = 0.0
    elif days_remaining <= 1:
        expiry_score = 15.0
    elif days_remaining <= config.expiry_critical_days:
        expiry_score = 35.0
    elif days_remaining <= config.expiry_warning_days:
        expiry_score = 65.0
    elif days_remaining <= config.expiry_safe_days:
        expiry_score = 85.0
    else:
        expiry_score = 100.0

    # 3. Spoilage Resistance Score (0 - 100)
    prob = max(0.0, min(float(spoilage_probability), 1.0))
    spoilage_score = (1.0 - prob) * 100.0

    # Weighted composite score
    base_score = (
        stock_score * config.weight_stock
        + expiry_score * config.weight_expiry
        + spoilage_score * config.weight_spoilage
    )

    # 4. Storage temperature penalty
    penalty = 0.0
    if storage_temp is not None and category:
        cat_lower = category.lower()
        if "dairy" in cat_lower and storage_temp > config.dairy_max_temp:
            # Cold-chain violation penalty for dairy
            excess_deg = storage_temp - config.dairy_max_temp
            penalty += min(excess_deg * 3.0, 15.0)

    final_score = max(0, min(100, round(base_score - penalty)))
    return final_score


def health_status(score: int) -> str:
    """
    Categorize health score into an operational status.
    """
    if score >= 75:
        return "Healthy"
    if score >= 50:
        return "Needs Attention"
    return "Critical"


def get_spoilage_risk(probability: float, config: Optional[RuleConfig] = None) -> str:
    """
    Convert spoilage probability to a categorical risk tier.
    """
    if config is None:
        config = get_rule_config()

    prob = float(probability)
    if prob >= config.spoilage_high_threshold:
        return "High"
    if prob >= config.spoilage_medium_threshold:
        return "Medium"
    return "Low"


def get_recommendation(
    current_stock: float,
    predicted_demand: float,
    days_remaining: int,
    spoilage_probability: float,
    storage_temp: Optional[float] = None,
    category: Optional[str] = None,
    ambient_temp: Optional[float] = None,
    humidity: Optional[float] = None,
    config: Optional[RuleConfig] = None,
) -> Tuple[str, str]:
    """
    Deterministic rule engine that produces a high-confidence recommendation
    and an interpretable natural language explanation.

    Possible Recommendations:
    - Clearance Action (or Urgent Clearance)
    - Sell Quickly
    - Reorder
    - Monitor
    - Sufficient Stock
    """
    if config is None:
        config = get_rule_config()

    prob = float(spoilage_probability)
    prob_percent = round(prob * 100, 1)

    # Environmental / storage warning suffix
    env_notes = []
    if storage_temp is not None and category and "dairy" in category.lower():
        if storage_temp > config.dairy_max_temp:
            env_notes.append(
                f"Storage temperature of {storage_temp}°C exceeds recommended dairy limit ({config.dairy_max_temp}°C)."
            )

    if ambient_temp is not None and ambient_temp >= config.ambient_high_temp:
        env_notes.append(f"High ambient temperature ({ambient_temp}°C) accelerates perishable decay.")

    if humidity is not None and humidity >= config.high_humidity_threshold:
        env_notes.append(f"Elevated relative humidity ({humidity}%) increases moisture-related spoilage risk.")

    env_explanation = " " + " ".join(env_notes) if env_notes else ""

    # RULE 1: URGENT CLEARANCE
    # Trigger: Expiring within critical window (<=2 days), or <=3 days with high spoilage risk (>=60%), or excessive stock facing imminent expiry
    if (
        (days_remaining <= config.expiry_critical_days)
        or (days_remaining <= 3 and prob >= config.spoilage_high_threshold)
        or (days_remaining <= config.expiry_critical_days and current_stock > predicted_demand * config.stock_excess_multiplier)
    ):
        recommendation = "Urgent Clearance"
        explanation = (
            f"Product expires in {days_remaining} day(s) with an elevated spoilage probability of {prob_percent}%. "
            f"Current stock of {int(current_stock)} units cannot be absorbed before shelf life lapses. "
            f"Execute an immediate promotional clearance discount to prevent total stock loss.{env_explanation}"
        )
        return recommendation, explanation

    # RULE 2: SELL QUICKLY
    # Trigger: Expiry approaching within warning window (3-5 days) with medium or high spoilage risk (>=30%)
    if (
        days_remaining <= config.expiry_warning_days
        and prob >= config.spoilage_medium_threshold
    ):
        recommendation = "Sell Quickly"
        explanation = (
            f"Inventory holds {int(current_stock)} units with {days_remaining} day(s) remaining and {prob_percent}% spoilage probability. "
            f"Prioritize front-of-shelf positioning, first-expiry-first-out (FEFO) rotation, or bundle promotions to accelerate sell-through.{env_explanation}"
        )
        return recommendation, explanation

    # RULE 3: REORDER
    # Trigger: Stock is below demand buffer AND remaining shelf life is safe (> warning window) with low spoilage risk
    if (
        current_stock < predicted_demand * config.reorder_buffer_multiplier
        and days_remaining > config.expiry_warning_days
        and prob < config.spoilage_medium_threshold
    ):
        reorder_qty = max(round(predicted_demand * 1.2 - current_stock), 1)
        recommendation = "Reorder"
        explanation = (
            f"Current stock of {int(current_stock)} units is insufficient for predicted demand of {int(predicted_demand)} units. "
            f"Batch shelf life is stable ({days_remaining} days left, {prob_percent}% spoilage risk). Place a replenishment purchase order for approximately {reorder_qty} unit(s).{env_explanation}"
        )
        return recommendation, explanation

    # RULE 4: MONITOR STOCK
    # Trigger: Shelf life in intermediate window (<=10 days) or moderate spoilage risk or adequate buffer
    if (
        days_remaining <= config.expiry_safe_days
        or prob >= 0.10
        or current_stock >= predicted_demand * config.stock_excess_multiplier
    ):
        recommendation = "Monitor Stock"
        explanation = (
            f"Inventory holds {int(current_stock)} units with {days_remaining} day(s) until expiry and {prob_percent}% spoilage probability. "
            f"Stock is currently sufficient; track shelf life progression and storage temperature closely.{env_explanation}"
        )
        return recommendation, explanation

    # RULE 5: SUFFICIENT STOCK
    # Default healthy state with long shelf life and low risk
    recommendation = "Sufficient Stock"
    explanation = (
        f"Available stock of {int(current_stock)} units adequately covers predicted demand ({int(predicted_demand)} units). "
        f"Shelf life is comfortable ({days_remaining} days remaining) with low spoilage probability ({prob_percent}%).{env_explanation}"
    )
    return recommendation, explanation
