from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.expense import Expense
from app.extensions import db
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')

@expenses_bp.route('/', methods=['POST'])
@jwt_required()
def add_expense():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    expense = Expense(
        user_id=user_id,
        amount=data['amount'],
        category=data['category'],
        description=data.get('description'),
        date=datetime.strptime(data['date'], '%Y-%m-%d') if 'date' in data else datetime.utcnow()
    )

    db.session.add(expense)
    db.session.commit()
    return jsonify({'message': 'Expense added successfully'}), 201

@expenses_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            'id': e.id,
            'amount': e.amount,
            'category': e.category,
            'description': e.description,
            'date': e.date.strftime('%Y-%m-%d')
        } for e in expenses
    ])

@expenses_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_expense(id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()
    
    expense.amount = data.get('amount', expense.amount)
    expense.category = data.get('category', expense.category)
    expense.description = data.get('description', expense.description)
    if 'date' in data:
        expense.date = datetime.strptime(data['date'], '%Y-%m-%d')
    
    db.session.commit()
    return jsonify({'message': 'Expense updated successfully'})

@expenses_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_expense(id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Expense deleted successfully'})
