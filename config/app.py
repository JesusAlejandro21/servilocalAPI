import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from models.models import db, Trabajadores

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Subimos un nivel (a /API)
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')

app = Flask(__name__,
            static_folder=STATIC_DIR,
            static_url_path='/static')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/servilocal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, resources={r"/*": {"origins": "*"}})
db.init_app(app)
migrate = Migrate(app, db)

@app.route("/main/token", methods=['GET'])
def getToken():
    correo = request.args.get('correo')
    
    data = {
        "nombre": "",
        "apellido": "", 
        "correo": correo}
    
    return jsonify({"mensaje": "", "status": "success", "data": data}), 200


@app.route('/workers/workers', methods=['GET'])
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

@app.route('/static/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)