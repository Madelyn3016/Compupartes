from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)

# Conexión a MongoDB
mongo_uri = ""
client = MongoClient(mongo_uri)
db = client["compupartes"]
partes_collection = db["partespc"]
clientes_collection = db["clientes"]
facturas_collection = db["facturas"]

# Rutas CRUD
@app.route("/")
def index():
    return render_template("inicio.html")

@app.route("/partespc")
def partespc():
    query = {}
    q = request.args.get("q", "").strip()
    marca = request.args.get("marca", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()
    min_quantity = request.args.get("min_quantity", "").strip()
    max_quantity = request.args.get("max_quantity", "").strip()

    if q:
        query["$or"] = [
            {"nombre": {"$regex": q, "$options": "i"}},
            {"referencia": {"$regex": q, "$options": "i"}},
            {"S/N": {"$regex": q, "$options": "i"}}
        ]
    if marca:
        query["marca"] = marca
    if min_price:
        query.setdefault("valor", {})["$gte"] = float(min_price)
    if max_price:
        query.setdefault("valor", {})["$lte"] = float(max_price)
    if min_quantity:
        query.setdefault("cantidad", {})["$gte"] = int(min_quantity)
    if max_quantity:
        query.setdefault("cantidad", {})["$lte"] = int(max_quantity)

    partes_pc = list(partes_collection.find(query))
    marcas = partes_collection.distinct("marca")
    return render_template(
        "partespc.html", 
        partes=partes_pc, 
        marcas=marcas,
        search_params={
            "q": q,
            "marca": marca,
            "min_price": min_price,
            "max_price": max_price,
            "min_quantity": min_quantity,
            "max_quantity": max_quantity
        }
    )


@app.route("/añadirpartes", methods=["GET", "POST"])
def add_parte():
    if request.method == "POST":
        parte = {
            "S/N": request.form["sn"],
            "nombre": request.form["nombre"],
            "referencia": request.form["referencia"],
            "cantidad": int(request.form["cantidad"]),
            "marca": request.form["marca"],
            "valor": float(request.form["valor"])
        }
        partes_collection.insert_one(parte)
        return redirect(url_for("partespc"))
    return render_template("añadirpartes.html")

@app.route("/editarpartes/<id>", methods=["GET", "POST"])
def edit_parte(id):
    if request.method == "POST":
        partes_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "S/N": request.form["sn"],
                "nombre": request.form["nombre"],
                "referencia": request.form["referencia"],
                "cantidad": int(request.form["cantidad"]),
                "marca": request.form["marca"],
                "valor": float(request.form["valor"])
            }}
        )
        return redirect(url_for("partespc"))
    parte = partes_collection.find_one({"_id": ObjectId(id)})
    return render_template("editarpartes.html", parte=parte)

@app.route("/delete_parte/<id>")
def delete_parte(id):
    partes_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("partespc"))

@app.route("/clientes")
def clientes_view():
    query = {}
    q = request.args.get("q", "").strip()
    min_nit = request.args.get("min_nit", "").strip()
    max_nit = request.args.get("max_nit", "").strip()

    if q:
        query["$or"] = [
            {"Nombres": {"$regex": q, "$options": "i"}},
            {"Apellidos": {"$regex": q, "$options": "i"}},
            {"Nro.Nit/CC": {"$regex": q, "$options": "i"}},
            {"Direccion": {"$regex": q, "$options": "i"}}
        ]
    if min_nit:
        query.setdefault("Nro.Nit/CC", {})["$gte"] = min_nit
    if max_nit:
        query.setdefault("Nro.Nit/CC", {})["$lte"] = max_nit

    clientes_lista = list(clientes_collection.find(query))
    return render_template(
        "clientes.html", 
        clientes=clientes_lista,
        search_params={
            "q": q,
            "min_nit": min_nit,
            "max_nit": max_nit
        }
    )


@app.route("/añadircliente", methods=["GET", "POST"])
def add_cliente():
    if request.method == "POST":
        cliente = {
            "Nro.Nit/CC": request.form["no.nit"],
            "Nombres": request.form["nombre"],
            "Apellidos": request.form["apellido"],
            "Direccion": request.form["direccion"],
            "e-mail": request.form["email"],
            "celular": request.form["celular"]
        }
        clientes_collection.insert_one(cliente)
        return redirect(url_for("clientes_view"))
    return render_template("añadircliente.html")

@app.route("/editarcliente/<id>", methods=["GET", "POST"])
def edit_cliente(id):
    if request.method == "POST":
        clientes_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "Nro.Nit/CC": request.form["no.nit"],
                "Nombres": request.form["nombre"],
                "Apellidos": request.form["apellido"],
                "Direccion": request.form["direccion"],
                "e-mail": request.form["email"],
                "celular": request.form["celular"]
            }}
        )
        return redirect(url_for("clientes_view"))
    cliente = clientes_collection.find_one({"_id": ObjectId(id)})
    return render_template("editarcliente.html", cliente=cliente)

@app.route("/delete_cliente/<id>")
def delete_cliente(id):
    clientes_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("clientes_view"))

@app.route("/facturas")
def facturas_view():
    query = {}
    q = request.args.get("q", "").strip()
    min_date = request.args.get("min_date", "").strip()
    max_date = request.args.get("max_date", "").strip()
    min_total = request.args.get("min_total", "").strip()
    max_total = request.args.get("max_total", "").strip()

    if q:
        query["$or"] = [
            {"Nro.Factura": {"$regex": q, "$options": "i"}},
            {"cliente": {"$regex": q, "$options": "i"}},
            {"forma de pago": {"$regex": q, "$options": "i"}}
        ]
    if min_date:
        query.setdefault("fecha", {})["$gte"] = min_date
    if max_date:
        query.setdefault("fecha", {})["$lte"] = max_date
    if min_total:
        query.setdefault("valor total", {})["$gte"] = float(min_total)
    if max_total:
        query.setdefault("valor total", {})["$lte"] = float(max_total)

    facturas_lista = list(facturas_collection.find(query))
    return render_template(
        "facturas.html", 
        facturas=facturas_lista,
        search_params={
            "q": q,
            "min_date": min_date,
            "max_date": max_date,
            "min_total": min_total,
            "max_total": max_total
        }
    )

@app.route("/añadirfactura", methods=["GET", "POST"])
def add_factura():
    if request.method == "POST":
        factura = {
            "Nro.Factura": request.form["no.factura"],
            "fecha": request.form["fecha"],
            "cliente": request.form["cliente"],
            "direccion": request.form["direccion"],
            "telefono": request.form["telefono"],
            "e-mail": request.form["email"],
            "forma de pago": request.form["forma_pago"],
            "valor total": float(request.form["valor_total"])
        }
        facturas_collection.insert_one(factura)
        return redirect(url_for("facturas_view"))
    return render_template("añadirfactura.html")

@app.route("/editarfactura/<id>", methods=["GET", "POST"])
def edit_factura(id):
    if request.method == "POST":
        facturas_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "Nro.Factura": request.form["no.factura"],
                "fecha": request.form["fecha"],
                "cliente": request.form["cliente"],
                "direccion": request.form["direccion"],
                "telefono": request.form["telefono"],
                "e-mail": request.form["email"],
                "forma de pago": request.form["forma_pago"],
                "valor total": float(request.form["valor_total"])
            }}
        )
        return redirect(url_for("facturas_view"))
    factura = facturas_collection.find_one({"_id": ObjectId(id)})
    return render_template("editarfactura.html", factura=factura)

@app.route("/delete_factura/<id>")
def delete_factura(id):
    facturas_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("facturas_view"))

if __name__ == "__main__":
    app.run(debug=True)