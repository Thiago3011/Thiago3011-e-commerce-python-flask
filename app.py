# Importações para utilização do Flask e Flask_sqlalchemy
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user

# Instânciamento do Flask para uso
app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = "minha_chave_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

# Configuração sistema de login + BD
login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelação
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=True)
    cart = db.relationship('CartItem', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    

# Autenticação

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas
@app.route('/login', methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    
    if user and data.get("password") == user.password:
        login_user(user)
        return jsonify({"message": "Logged in sucessfully"})
         
    return jsonify({"message": "Unauthorized. Invalid credentials"}), 401
    
@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout sucessfully"})

    
@app.route('/api/products/add', methods=["POST"])
@login_required
def add_product():
    data = request.json
    
    if "name" in data and "price" in data:
        # data["CHAVE"] -> retorna o valor da chave, porém se não encontrar, da erro
        # data.get("CHAVE", "VALOR CASO NAO ENCONTRE") -> retorna o valor da chave, porém se não encontrar, substitui por outro valor escolhido
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        
        db.session.add(product)
        db.session.commit()
    
        return jsonify({"message": "Product added sucessfully"})
    return jsonify({"message": "Invalid product data"}), 400

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({"message": "Product deleted sucessfully"})
    return jsonify({"message": "Product not found"}), 404
    
@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        })
        
    return jsonify({"message": "Product not found"}), 404
    
@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    data = request.json
    
    if "name" in data:
        product.name = data["name"] 
    
    if "price" in data:
        product.price = data["price"]
        
    if "description" in data:
        product.description = data["description"]
        
    db.session.commit()
        
    return jsonify({"message": "Product updated sucessfully"})

@app.route('/api/products', methods=["GET"])
def get_products():
    products = Product.query.all()
    
    product_list = []
    
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
        }
        
        product_list.append(product_data)

    return jsonify(product_list)

# Execução do servidor Flask
@app.route('/')
def hello_world():
    return 'Hello World!'

# Checagem para saber se o arquivo está sendo usado diretamento ou importado por uma outra API
if __name__ == "__main__":
    app.run(debug=True)