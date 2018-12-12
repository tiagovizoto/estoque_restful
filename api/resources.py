from main import api, db
from flask import jsonify
from flask_restful import Resource, reqparse, abort
from flask_security.decorators import roles_required, roles_accepted, auth_token_required
from models import Product, Shopping, Score, Output

parser_product = reqparse.RequestParser()
parser_shopping = reqparse.RequestParser()
parser_score = reqparse.RequestParser()
parser_output = reqparse.RequestParser()


parser_product.add_argument('name', type=str, help="Informe o nome do produto")
parser_product.add_argument('description', type=str, help="Descrição do produto")
parser_product.add_argument('amount_min', type=int, help="Informe a quantidade minima do produto")
parser_product.add_argument('amount_total', type=int, help="Quantidade total do produto")
parser_product.add_argument('created_by', type=int, help="Quem é o autor deste post?")

parser_shopping.add_argument('amount', type=str, help='Informe a quantidade da compra do produto')
parser_shopping.add_argument('product', type=int, help='Informe o produto comprado')
parser_shopping.add_argument('created_by', type=int, help="Quem é o autor deste post?")

parser_score.add_argument('amount', type=str, help='Informe a quantidade do produto no estoque')
parser_score.add_argument('product', type=int, help='Informe o produto da contagem')
parser_score.add_argument('created_by', type=int, help="Quem é o autor deste post?")

parser_score.add_argument('amount', type=str, help='Informe a quantidade do produto no estoque')
parser_score.add_argument('product', type=int, help='Informe o produto da contagem')
parser_score.add_argument('created_by', type=int, help="Quem é o autor deste post?")

parser_output.add_argument('amount', type=str, help='Informe a quantidade do produto que será estirado')
parser_output.add_argument('product', type=int, help='Informe o produto da saída')
parser_output.add_argument('created_by', type=int, help="Quem é o autor deste post?")


class BaseUserRole:
    decorators = ['admin', 'estoquista', 'gerente', 'supervisor']


class BaseAdminRole:
    decorators = ['admin', 'gerente']


class BaseListResource(Resource):
    model = None

    @auth_token_required
    def get(self):
        model = self.model.query.all()
        data = []
        columns = self.model.__table__.columns.keys()

        for idx, m in enumerate(model):

            data.append({})
            for c in columns:
                data[idx][c] = getattr(m, c)
        return jsonify({self.model.__tablename__: data})

    def post(self):
        pass


class BaseResource(Resource):
    model = None

    @auth_token_required
    def get(self, id):
        data = {}
        model = self.model.query.filter_by(id=id).first()
        if model is None:
            return abort(404, message=f"Not Found {self.model.__tablename__}")
        columns = model.__table__.columns.keys()
        for c in columns:
            data[c] = getattr(model, c)
        return jsonify({model.__tablename__: data})

    @auth_token_required
    def delete(self, id):
        result = self.model.query.filter_by(id=id).first()
        if result is None:
            return abort(404, message=f"Not Found <{self.model.__tablename__} {id}>")
        db.session.delete(result)
        db.session.commit()

    @auth_token_required
    def put(self, id):
        result = self.model.query.filter_by(id=id).first()
        if result is None:
            return abort(404, message=f"Not Found <{self.model.__tablename__} {id}>")
        db.session.commit()


class ProductListView(BaseListResource):
    model = Product

    def __init__(self):
        super(ProductListView, self).__init__()

    @auth_token_required
    def post(self):
        args = parser_product.parse_args()
        product = Product(name=args['name'], description=args['description'], amount_min=args['amount_min'],
                          amount_total=args['amount_total'], created_by=args["created_by"])
        db.session.add(product)
        db.session.commit()
        return "", 201


class ProductView(BaseResource):
    model = Product

    def __init__(self):
        super(ProductView, self).__init__()


class ShoppingListView(BaseListResource):
    model = Shopping

    def __init__(self):
        super(ShoppingListView, self).__init__()

    def post(self):
        pass


class ShoppingView(BaseResource):
    model = Shopping

    def __int__(self):
        super(ShoppingView, self).__int__()


class OutputListView(BaseListResource):
    model = Output

    def __init__(self):
        super(OutputListView, self).__init__()

    def post(self):
        pass


class OutputView(BaseResource):
    model = Output

    def __init__(self):
        super(OutputView, self).__init__()


class ScoreListView(BaseListResource):
    model = Score

    def __init__(self):
        super(ScoreListView, self).__init__()

    def post(self):
        pass


class ScoreView(BaseResource):
    model = Score

    def __init__(self):
        super(ScoreView, self).__init__()


api.add_resource(ProductListView, '/product/')
api.add_resource(ProductView, '/product/<int:id>')
api.add_resource(ShoppingListView, '/shopping/')
api.add_resource(ShoppingView, '/shopping/<int:id>')
api.add_resource(OutputListView, '/output/')
api.add_resource(OutputView, '/output/<int:id>')
api.add_resource(ScoreListView,'/score/')
api.add_resource(ScoreView,'/score/<int:id>')
