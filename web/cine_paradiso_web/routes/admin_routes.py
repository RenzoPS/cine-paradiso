from flask import Blueprint, render_template

from cine_paradiso_web.services.auth_service import admin_requerido

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/', methods=['GET'])
@admin_bp.route('/dashboard', methods=['GET'])
@admin_requerido
def index():
    return render_template('admin/dashboard.html')
