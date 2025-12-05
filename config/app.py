import os
from flask import Flask, jsonify, request, json
from flask_cors import CORS
from flask_migrate import Migrate
from models.models import db, Trabajadores, Usuarios
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv
import mercadopago

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Subimos un nivel (a /API)
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')

app = Flask(__name__,
            static_folder=STATIC_DIR,
            static_url_path='/static')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:UdlMFndRgqAmfwYFIZfMnbieiXwNEkDG@switchback.proxy.rlwy.net:37016/servilocal'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/servilocal'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_predeterminada_segura')

sdk = mercadopago.SDK("TEST-3761858260575889-112610-d264e25c8a0e52f3e8aa5a83551c2a48-618206464")

CORS(app, resources={r"/*": {"origins": "*"}})
db.init_app(app)
migrate = Migrate(app, db)

@app.route("/preferencemp", methods=['GET'])
def crear_preferencia():

    preference_data = {
        "items": [
            {
                "title": "Nombre de producto",
                "quantity": 1,
                "unit_price": 100.00
            }
        ],
        "back_urls": {
            "success": "https://carpiteriareyna.com/success",
            "failure": "https://carpiteriareyna.com/failure",
            "pending": "https://carpiteriareyna.com/pending"
        },
       # "auto_return": "approved",
    }

    #crear preferencia
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    
    data = {
        "id": preference["id"],
        "init_point": preference["init_point"],
        "sandbox_init_point": preference["sandbox_init_point"]
    }

    respuesta = {
        "mensaje" : "Mensaje de exito",
        "status" : "success",
        "data" : data
    }

    return jsonify(respuesta),200

@app.route('/processpayment', methods=['POST'])
def process_payment():
    """
    Procesa un pago utilizando la API de Mercado Pago.
    """
    parameters = request.get_json(silent=True)

    if not parameters:
        return jsonify({"error": "Datos JSON inválidos o faltantes"}), 400

    payment_data_form = parameters.get('formdata')
    # id_carrito = parameters.get('idfoliocarrito') # Variable no utilizada
    id_device = parameters.get('iddevice')

    if not payment_data_form or not payment_data_form.get('token'):
        return jsonify({"error": "Faltan datos obligatorios (token o formdata)"}), 400

    # PROCESAR LA COMPRA Y REGISTRAR O MODIFICAR LA BASE DE DATO
    # DE ACUERDO A LA LOGICA DE NEGOCIO

    amount = payment_data_form.get('transaction_amount')
    email = payment_data_form.get('payer').get('email')

    payment_intent_data = {
        "transaction_amount": float(amount),
        "token": payment_data_form.get('token'),
        "payment_method_id": payment_data_form.get('payment_method_id'),
        "issuer_id": payment_data_form.get('issuer_id'),
        "description": "Descripcion del pago a Realizar",
        "installments": 1,  # pago en una sola exhibición
        "statement_descriptor": 'Description',
        "payer": {
            "first_name": 'Jonathan',
            "last_name": "Guevara",
            "email": email,
        },
        "additional_info": {
            "items": [
                {
                    "title": "Nombre del Producto",
                    "quantity": 1,
                    "unit_price": float(amount)
                }
            ]
        },
        "capture": True,
        "binary_mode": False,  # evita pagos pendientes: solo aprueba o rechaza
        # "device_id": id_device
    }

    request_options = RequestOptions()

    idempotency_key = str(uuid.uuid4())

    request_options.custom_headers = {
        "X-Idempotency-Key": idempotency_key,
        "X-meli-session-id": id_device
    }

    result = sdk.payment().create(payment_intent_data, request_options)
    payment_response = result.get("response", {})

    if (payment_response.get("status") == 'approved' and
            payment_response.get('status_detail') == 'accredited'):
        # PROCESAR SUS DATOS EN LA BD O LO QUE TENGAN QUE HACER
        # DAR RESPUESTA
        respuesta = {
            "mensaje": "Mensaje de Exito",
            "status": "success",
            'data': payment_response
        }
        return jsonify(respuesta), 200
    else:
        respuesta = {
            "mensaje": "Mensaje de Error",
            "status": "error",
            'data': payment_response
        }
        return jsonify(respuesta), 400

@app.route("/main/token", methods=['GET'])
def getToken():
    correo = request.args.get('correo')
    
    data = {
        "nombre": "",
        "apellido": "", 
        "correo": correo}
    
    return jsonify({"mensaje": "", "status": "success", "data": data}), 200


@app.route('/site/main', methods=['GET'])
def getTrabajadores():
    trabajadores = Trabajadores.query.all()
    lista_trabajadores = []
    for trabajador in trabajadores:
        lista_trabajadores.append(trabajador.to_dict())
        
        respuesta ={
            "mensaje": "mensaje de exito",
            "status": "success",
            "lista_trabajadores": lista_trabajadores
        }

    return jsonify(respuesta), 200
    

@app.route('/workers/information/<int:id_trabajador>', methods=['GET'])
def get_datos(id_trabajador):
    trabajador = Trabajadores.query.get(id_trabajador)

    if not trabajador:
        return jsonify({
            "mensaje": "Trabajador no encontrado",
            "status": "error"
        }), 404

    respuesta = {
        "mensaje": "Trabajador encontrado",
        "status": "success",
        "trabajador": trabajador.to_dict()
    }

    return jsonify(respuesta), 200


@app.route('/upload_foto/<int:trabajador_id>', methods=['POST'])
def upload_foto(trabajador_id):
    if 'foto_trabajador' not in request.files:
        return jsonify({"mensaje": "No se envió ninguna imagen"}), 400

    file = request.files['foto_trabajador']
    if file.filename == '':
        return jsonify({"mensaje": "Nombre de archivo vacío"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    trabajador = Trabajadores.query.get(trabajador_id)
    if not trabajador:
        return jsonify({"mensaje": "Trabajador no encontrado"}), 404

    trabajador.foto_trabajador = f'static/uploads/{filename}'
    db.session.commit()

    return jsonify({
        "mensaje": "Foto subida correctamente",
        "ruta_foto": filepath
    }), 200

def generar_token(data):
    token = jwt.encode({
        **data,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    return token

def token_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token requerido"}), 401
        try:
            jwt.decode(token.split(" ")[1], app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({"error": "Token inválido o expirado"}), 401
        return f(*args, **kwargs)
    return decorador

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    tipo = data.get('tipo')
    correo = data.get('correo')
    contrasena = data.get('contrasena')

    if tipo == 'usuario':
        user = Usuarios.query.filter_by(correo=correo).first()
    else:
        user = Trabajadores.query.filter_by(correo_trabajador=correo).first()

    if not user:
        return jsonify({"error": "Correo no encontrado"}), 404

    contrasena_correcta = check_password_hash(
        user.contrasena,
        contrasena
    )
    
    '''if user.contrasena.startswith('pbkdf2:sha256') else user.contrasena == contrasena'''

    if not contrasena_correcta:
        return jsonify({"error": "Contraseña incorrecta"}), 401

    token = generar_token({"correo": correo, "tipo": tipo})
    return jsonify({"token": token, "tipo": tipo}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    tipo = data.get('tipo')

    if tipo == 'usuario':
        nuevo = Usuarios(
            nombre=data['nombre'],
            apellidos=data['apellidos'],
            correo=data['correo'],
            direccion=data['direccion'],
            telefono=data['telefono'],
            contrasena=generate_password_hash(data['contrasena'], method='pbkdf2:sha256')
        )
    else:
        nuevo = Trabajadores(
            nombre=data['nombre'],
            descripcion_trabajo=data['descripcion_trabajo'],
            correo_trabajador=data['correo'],
            telefono_trabajador=data['telefono'],
            contrasena=generate_password_hash(data['contrasena']),
            foto_trabajador=data.get('foto_trabajador', None)
        )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({"mensaje": f"{tipo.capitalize()} registrado con éxito"}), 201


if __name__ == '__main__':
    app.run(debug=True)