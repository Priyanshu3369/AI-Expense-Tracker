from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime , timedelta
import re
from app.models.expense import Expense
from app.extensions import db
from statistics import mean, stdev
from app.models.budget import Budget


ai_bp = Blueprint("ai_insights", __name__, url_prefix="/api/ai")

# Simple parser for NLP input like: "Spent ₹500 on groceries yesterday"
@ai_bp.route("/parse-expense", methods=["POST"])
@jwt_required()
def parse_expense():
    user_id = get_jwt_identity()
    data = request.get_json()
    text = data.get("text", "")

    # Simple regex + NLP-like parsing
    amount_match = re.search(r"₹?(\d+(\.\d+)?)", text)
    category_match = re.search(r"on\s+(\w+)", text)
    date_match = "today"
    if "yesterday" in text.lower():
        date_match = (datetime.utcnow().date() - timedelta(days=1)).isoformat()
    else:
        date_match = datetime.utcnow().date().isoformat()

    if not amount_match or not category_match:
        return jsonify({"error": "Could not parse the input text"}), 400

    amount = float(amount_match.group(1))
    category = category_match.group(1).capitalize()

    expense = Expense(
        user_id=user_id,
        amount=amount,
        category=category,
        description=text,
        date=date_match,
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify({
        "message": "Expense added from natural language input",
        "data": {
            "amount": amount,
            "category": category,
            "date": date_match,
            "description": text,
        }
    }), 201


@ai_bp.route("/predict-category", methods=["POST"])
@jwt_required()
def predict_category():
    data = request.get_json()
    description = data.get("description", "").lower()

    # TEMP: Rule-based stub — ML model will be integrated later
    if "grocery" in description:
        predicted = "Groceries"
    elif "fuel" in description:
        predicted = "Transport"
    elif "pizza" in description or "food" in description:
        predicted = "Dining"
    else:
        predicted = "Other"

    return jsonify({
        "predicted_category": predicted
    })

@ai_bp.route('/detect-anomalies', methods=['GET'])
@jwt_required()
def detect_anomalies():
    user_id = get_jwt_identity()

    # Get last 30 days of expenses
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=30)

    expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date <= today
    ).all()

    # Group by category
    category_map = {}
    for e in expenses:
        category_map.setdefault(e.category, []).append(e)

    anomalies = []

    for category, exps in category_map.items():
        if len(exps) < 5:
            continue  # Not enough data to analyze

        amounts = [e.amount for e in exps]
        avg = mean(amounts)
        std = stdev(amounts)

        for e in exps:
            if e.amount > avg + 2 * std:
                anomalies.append({
                    "id": e.id,
                    "amount": e.amount,
                    "category": e.category,
                    "description": e.description,
                    "date": e.date.isoformat(),
                    "reason": f"Unusually high compared to others in {category}"
                })

    return jsonify({"anomalies": anomalies})

@ai_bp.route('/budget-alerts', methods=['GET'])
@jwt_required()
def budget_alerts():
    user_id = get_jwt_identity()
    today = datetime.utcnow().date()
    current_month = today.strftime('%Y-%m')

    budgets = Budget.query.filter_by(user_id=user_id, month=current_month).all()

    alerts = []

    for b in budgets:
        total_spent = db.session.query(
            db.func.sum(Expense.amount)
        ).filter_by(user_id=user_id, category=b.category).filter(
            db.func.strftime('%Y-%m', Expense.date) == current_month
        ).scalar() or 0

        if total_spent >= b.amount:
            alerts.append({
                "category": b.category,
                "status": "Exceeded",
                "budget": b.amount,
                "spent": total_spent
            })
        elif total_spent >= 0.9 * b.amount:
            alerts.append({
                "category": b.category,
                "status": "Warning",
                "budget": b.amount,
                "spent": total_spent
            })

    return jsonify({"alerts": alerts})