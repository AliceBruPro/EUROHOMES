import os
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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




def cargar_inmuebles():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_inmuebles(inmuebles):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(inmuebles, f, ensure_ascii=False, indent=4)

inmuebles = cargar_inmuebles()

@app.route('/')
def index():
    lang = request.args.get('lang', 'es')
    ciudad = request.args.get('ciudad', '').strip().lower()
    operacion = request.args.get('operacion', '').strip().lower()
    pais = request.args.get('pais', '').strip().lower()
    precio_min = request.args.get('precio_min', '').strip()
    precio_max = request.args.get('precio_max', '').strip()
    tipo_inmueble = request.args.get('tipo_inmueble', '').strip().lower()


    resultados = inmuebles

    if pais:
        resultados = [i for i in resultados if i.get('pais', '').lower() == pais]
    if ciudad:
        resultados = [i for i in resultados if i.get('ciudad', '').lower() == ciudad]
    if operacion:
        resultados = [i for i in resultados if i.get('operacion', '').lower() == operacion]
    if tipo_inmueble:
        resultados = [i for i in resultados if i.get('tipo', '').lower() == tipo_inmueble]



    # Filtrar por precio mínimo
    if precio_min:
        try:
            precio_min_val = float(precio_min)
            resultados = [i for i in resultados if float(i.get('precio', 0)) >= precio_min_val]
        except ValueError:
            pass

    # Filtrar por precio máximo
    if precio_max:
        try:
            precio_max_val = float(precio_max)
            resultados = [i for i in resultados if float(i.get('precio', 0)) <= precio_max_val]
        except ValueError:
            pass

    textos = TRADUCCIONES.get(lang, TRADUCCIONES['es'])

    return render_template(
        'index.html',
        inmuebles=resultados,
        ciudad=ciudad,
        operacion=operacion,
        pais=pais,
        tipo_inmueble=tipo_inmueble,
        lang=lang,
        textos=textos,
        precio_min=precio_min,
        precio_max=precio_max
    )


@app.route('/detalle/<int:id>')
def detalle(id):
    lang = request.args.get('lang', 'es')
    textos = TRADUCCIONES.get(lang, TRADUCCIONES['es'])

    # Cargar los datos del archivo JSON en este momento
    inmuebles = cargar_inmuebles()

    # Buscar el inmueble por su ID
    inmueble = next((i for i in inmuebles if i['id'] == id), None)

    if inmueble:
        return render_template('detalle.html', inmueble=inmueble, lang=lang, textos=textos)
    
    # Redirigir si no se encuentra el inmueble
    return redirect(url_for('index', lang=lang))

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    lang = request.args.get('lang', 'es')
    textos = TRADUCCIONES.get(lang, TRADUCCIONES['es'])

    if request.method == 'POST':
        imagen = request.files['imagen']
        imagen_filename = ''
        if imagen and imagen.filename:
            imagen_filename = imagen.filename
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename))

        nuevo_inmueble = {
            'id': len(inmuebles) + 1,
            'titulo': request.form['titulo'],
            'operacion': request.form['operacion'],
            'pais': request.form['pais'],
            'ciudad': request.form['ciudad'],
            'moneda': request.form['moneda'],
            'precio': request.form['precio'],
            'descripcion': request.form['descripcion'],
            'tipo': request.form.get('tipo', ''),
            'imagen': imagen_filename
        }

        inmuebles.append(nuevo_inmueble)
        guardar_inmuebles(inmuebles)
        return redirect(url_for('index', lang=lang))

    return render_template('nuevo.html', lang=lang, textos=textos)


import os


