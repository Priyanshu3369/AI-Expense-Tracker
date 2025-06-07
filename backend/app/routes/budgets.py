from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.budget import Budget

budgets_bp = Blueprint('budgets', __name__, url_prefix='/api/budgets')

@budgets_bp.route('/', methods=['POST'])
@jwt_required()
def set_budget():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    budget = Budget.query.filter_by(
        user_id=user_id,
        category=data['category'],
        month=data['month']
    ).first()

    if budget:
        budget.amount = data['amount']  # Update
    else:
        budget = Budget(
            user_id=user_id,
            amount=data['amount'],
            category=data['category'],
            month=data['month']
        )
        db.session.add(budget)

    db.session.commit()
    return jsonify({'message': 'Budget set/updated successfully'}), 200

@budgets_bp.route('/', methods=['GET'])
@jwt_required()
def get_budgets():
    user_id = get_jwt_identity()
    month = request.args.get('month')  # e.g., ?month=2025-06

    query = Budget.query.filter_by(user_id=user_id)
    if month:
        query = query.filter_by(month=month)

    budgets = query.all()
    return jsonify([
        {
            'id': b.id,
            'category': b.category,
            'amount': b.amount,
            'month': b.month
        } for b in budgets
    ])
