import grpc
import grpc.aio

from proto import rag_pb2, rag_pb2_grpc
from services.document_extractor import extract_document


class RagServicer(rag_pb2_grpc.RagServiceServicer):
    async def UploadDocument(self, request, context):
        content = bytes(request.content)

        text = extract_document(request.filename, content)
        return rag_pb2.DocumentResponse(text=text)


async def serve():
    server = grpc.aio.server()
    rag_pb2_grpc.add_RagServiceServicer_to_server(RagServicer(), server)

    server.add_insecure_port("[::]:50051")
    await server.start()
    print("[gRPC] Listening on [::]:50051")
    await server.wait_for_termination()
