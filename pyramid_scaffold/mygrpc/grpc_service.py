import grpc
from . import app_pb2 as pb2
from . import app_pb2_grpc as pb2_grpc
from pyramid_scaffold.models import DBSession, Product
from concurrent import futures
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPInternalServerError

class ProductGRPCService(pb2_grpc.ProductServiceServicer):
    def CalculateTotalPrice(self, request, context):
        # Implementasi perhitungan total harga produk
        total_price = 0.0
        # Lakukan perhitungan sesuai kebutuhan
        response = pb2.CalculateTotalResponse(total_price=total_price)
        return response

    def GetProductDetails(self, request, context):
        session = DBSession()
        product_id = request.product_id
        product = session.query(Product).filter(Product.id == product_id).first()

        if product:
            return pb2.Product(
                id=product.id,
                name=product.name,
                description=product.description,
                price=product.price,
                stock=product.stock,
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return pb2.Product()

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ProductServiceServicer_to_server(ProductGRPCService(), server)
    server.add_insecure_port('[::]:5005')
    server.start()

    server.wait_for_termination()

if __name__ == '__main__':
    serve_grpc()
