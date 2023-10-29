import grpc
from . import app_pb2 as pb2
from . import app_pb2_grpc as pb2_grpc
from pyramid.response import Response
import logging

def get_detail_product(request):
    try:
        # Set up a gRPC channel to connect to the gRPC server
        logging.info(request.json.get('product_id'))
        channel = grpc.insecure_channel('localhost:50051')  # Replace with the appropriate address
        stub = pb2_grpc.ProductServiceStub(channel)

        # Call the gRPC method
        
        response = stub.GetProductDetails(pb2_grpc.ProductDetailsRequest(product_id=request.json.get('product_id')))
        logging.info(response)
        # Process the gRPC response
        if response:
            # Return the response as needed
            return Response({
                'product_id': response.id,
                'name': response.name,
                'description': response.description,
                'price': response.price,
                'stock': response.stock,
            })
        else:
            return Response({'message': 'Product not found'}, status=404)
    except Exception as e:
        # Handle exceptions here
        return Response({'message': 'An error occurred: ' + str(e)}, status=500)

if __name__ == '__main__':
    get_detail_product()
