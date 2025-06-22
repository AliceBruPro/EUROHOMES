import os
from dotenv import load_dotenv
load_dotenv()  # Esto carga las variables definidas en el archivo .env
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para flash()

# Configuración para PostgreSQL (Render define DATABASE_URL automáticamente)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Carpeta para subir imágenes
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# 🔧 Esto crea todas las tablas si no existen
with app.app_context():
    db.create_all()


# Modelo de datos
class Inmueble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    operacion = db.Column(db.String(50))
    pais = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    moneda = db.Column(db.String(20))
    precio = db.Column(db.Float)
    descripcion = db.Column(db.Text)
    tipo = db.Column(db.String(100))
    imagen = db.Column(db.String(200))
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)

# Traducciones multilenguaje
TRADUCCIONES = {
    'es': {
        "inmuebles_disponibles": "Inmuebles disponibles",
        "nuevo_inmueble": "Nuevo inmueble",
        "buscar": "Buscar",
        "pais": "País",
        "ciudad": "Ciudad",
        "operacion": "Operación",
        "precio": "Precio",
        "precio_min": "Precio mínimo",
        "precio_max": "Precio máximo",
        "volver": "Volver",
        "contactar": "Contactar",
        "sin_descripcion": "No hay descripción disponible.",
        "venta": "Venta",
        "alquiler": "Alquiler",
        "tipo_inmueble_label": "Tipo de inmueble",
        "tipo_inmueble": {
            "apartamento": "Apartamento",
            "casa": "Casa",
            "chalet": "Chalet",
            "estudio": "Estudio",
            "atico": "Ático",
            "piso": "Piso",
            "duplex": "Dúplex",
            "local_comercial": "Local comercial",
            "oficina": "Oficina",
            "terreno": "Terreno"
        }
    },
    'en': {
        "inmuebles_disponibles": "Available Properties",
        "nuevo_inmueble": "New Property",
        "buscar": "Search",
        "pais": "Country",
        "ciudad": "City",
        "operacion": "Operation",
        "precio": "Price",
        "precio_min": "Minimum price",
        "precio_max": "Maximum price",
        "volver": "Back",
        "contactar": "Contact",
        "sin_descripcion": "No description available.",
        "venta": "For sale",
        "alquiler": "For rent",
        "tipo_inmueble_label": "Property type",
        "tipo_inmueble": {
            "apartamento": "Apartment",
            "casa": "House",
            "chalet": "Villa",
            "estudio": "Studio",
            "atico": "Penthouse",
            "piso": "Flat",
            "duplex": "Duplex",
            "local_comercial": "Commercial Space",
            "oficina": "Office",
            "terreno": "Land"
        }
    },
    'fr': {
        "inmuebles_disponibles": "Biens disponibles",
        "nuevo_inmueble": "Nouveau bien",
        "buscar": "Rechercher",
        "pais": "Pays",
        "ciudad": "Ville",
        "operacion": "Opération",
        "precio": "Prix",
        "precio_min": "Prix minimum",
        "precio_max": "Prix maximum",
        "volver": "Retour",
        "contactar": "Contacter",
        "sin_descripcion": "Pas de description disponible.",
        "venta": "À vendre",
        "alquiler": "À louer",
        "tipo_inmueble_label": "Type de bien",
        "tipo_inmueble": {
            "apartamento": "Appartement",
            "casa": "Maison",
            "chalet": "Chalet",
            "estudio": "Studio",
            "atico": "Penthouse",
            "piso": "Logement",
            "duplex": "Duplex",
            "local_comercial": "Local commercial",
            "oficina": "Bureau",
            "terreno": "Terrain"
        }
    },
    'de': {
        "inmuebles_disponibles": "Verfügbare Immobilien",
        "nuevo_inmueble": "Neue Immobilie",
        "buscar": "Suchen",
        "pais": "Land",
        "ciudad": "Stadt",
        "operacion": "Transaktion",
        "precio": "Preis",
        "precio_min": "Mindestpreis",
        "precio_max": "Höchstpreis",
        "volver": "Zurück",
        "contactar": "Kontaktieren",
        "sin_descripcion": "Keine Beschreibung verfügbar.",
        "venta": "Zu verkaufen",
        "alquiler": "Zu vermieten",
        "tipo_inmueble_label": "Immobilienart",
        "tipo_inmueble": {
            "apartamento": "Wohnung",
            "casa": "Haus",
            "chalet": "Chalet",
            "estudio": "Studio",
            "atico": "Penthouse",
            "piso": "Etagenwohnung",
            "duplex": "Maisonette",
            "local_comercial": "Gewerbeimmobilie",
            "oficina": "Büro",
            "terreno": "Grundstück"
        }
    }
}

# Página principal con filtros
@app.route('/')
def index():
    lang = request.args.get('lang', 'es')
    ciudad = request.args.get('ciudad', '').strip().lower()
    operacion = request.args.get('operacion', '').strip().lower()
    pais = request.args.get('pais', '').strip().lower()
    precio_min = request.args.get('precio_min', '').strip()
    precio_max = request.args.get('precio_max', '').strip()
    tipo_inmueble = request.args.get('tipo_inmueble', '').strip().lower()

    resultados = Inmueble.query

    if pais:
        resultados = resultados.filter(Inmueble.pais.ilike(pais))
    if ciudad:
        resultados = resultados.filter(Inmueble.ciudad.ilike(ciudad))
    if operacion:
        resultados = resultados.filter(Inmueble.operacion.ilike(operacion))
    if tipo_inmueble:
        resultados = resultados.filter(Inmueble.tipo.ilike(tipo_inmueble))
    if precio_min:
        try:
            resultados = resultados.filter(Inmueble.precio >= float(precio_min))
        except ValueError:
            pass
    if precio_max:
        try:
            resultados = resultados.filter(Inmueble.precio <= float(precio_max))
        except ValueError:
            pass

    textos = TRADUCCIONES.get(lang, TRADUCCIONES['es'])

    return render_template(
        'index.html',
        inmuebles=resultados.all(),
        ciudad=ciudad,
        operacion=operacion,
        pais=pais,
        tipo_inmueble=tipo_inmueble,
        lang=lang,
        textos=textos,
        precio_min=precio_min,
        precio_max=precio_max
    )

# Detalle del inmueble
@app.route('/detalle/<int:id>')
def detalle(id):
    lang = request.args.get('lang', 'es')
    textos = TRADUCCIONES.get(lang, TRADUCCIONES['es'])
    inmueble = Inmueble.query.get_or_404(id)
    return render_template('detalle.html', inmueble=inmueble, lang=lang, textos=textos)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    inmueble = Inmueble.query.get_or_404(id)
    lang = request.args.get('lang', 'es')
    textos = TRADUCCIONES.get(lang, TRADUCCIONES['es'])

    if request.method == 'POST':
        inmueble.titulo = request.form['titulo']
        inmueble.tipo = request.form['tipo']
        inmueble.operacion = request.form['operacion']
        inmueble.pais = request.form['pais']
        inmueble.ciudad = request.form['ciudad']
        inmueble.moneda = request.form['moneda']
        inmueble.precio = float(request.form['precio']) if request.form['precio'] else None
        inmueble.descripcion = request.form['descripcion']
        inmueble.latitud = float(request.form['latitud']) if request.form['latitud'] else None
        inmueble.longitud = float(request.form['longitud']) if request.form['longitud'] else None

        db.session.commit()
        return redirect(url_for('detalle', id=inmueble.id, lang=lang))

    return render_template('editar.html', inmueble=inmueble, lang=lang, textos=textos)


# Nuevo inmueble
@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    lang = request.args.get('lang', 'es')
    textos = TRADUCCIONES.get(lang, TRADUCCIONES['es'])

    if request.method == 'POST':
        # Datos del formulario
        titulo = request.form['titulo']
        tipo = request.form['tipo']
        operacion = request.form['operacion']
        pais = request.form.get('pais', '')
        ciudad = request.form.get('ciudad', '')
        moneda = request.form.get('moneda', 'EUR')
        precio = float(request.form.get('precio', 0))
        descripcion = request.form.get('descripcion', '')

        # Imagen (opcional)
        imagen_file = request.files.get('imagen')
        imagen_filename = None

        if imagen_file and imagen_file.filename != '':
            imagen_filename = secure_filename(imagen_file.filename)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
            imagen_file.save(ruta)

        # Crear y guardar inmueble
        inmueble = Inmueble(
            titulo=titulo,
            tipo=tipo,
            operacion=operacion,
            pais=pais,
            ciudad=ciudad,
            moneda=moneda,
            precio=precio,
            descripcion=descripcion,
            imagen=imagen_filename
        )

        db.session.add(inmueble)
        db.session.commit()

        flash(textos.get('inmueble_creado', 'Inmueble creado exitosamente.'), 'success')
        return redirect(url_for('index', lang=lang))

    return render_template('nuevo.html', lang=lang, textos=textos)

# Punto de entrada
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


