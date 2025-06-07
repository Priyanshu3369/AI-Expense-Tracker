from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.expense import Expense
from app.extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_dashboard_summary():
    user_id = get_jwt_identity()
    month = request.args.get('month')  # Format: 'YYYY-MM'

    query = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter_by(user_id=user_id)

    if month:
        year, mon = map(int, month.split('-'))
        query = query.filter(
            func.strftime('%Y', Expense.date) == str(year),
            func.strftime('%m', Expense.date) == f"{mon:02}"
        )

    category_totals = query.group_by(Expense.category).all()

    total_spent = sum([total for _, total in category_totals])

    return jsonify({
        'total_spent': total_spent,
        'category_breakdown': [
            {'category': cat, 'amount': total}
            for cat, total in category_totals
        ]
    })
