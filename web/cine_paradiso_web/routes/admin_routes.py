from flask import Blueprint, render_template

from cine_paradiso_web.seguridad import verificar_administrador

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/', methods=['GET'])
@admin_bp.route('/dashboard', methods=['GET'])
def index():
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    return render_template('admin/dashboard.html')
