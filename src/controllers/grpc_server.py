import grpc
import grpc.aio

from proto import rag_pb2, rag_pb2_grpc
from services.document_extractor import extract_document
from services.chunking import chunk_text


class RagServicer(rag_pb2_grpc.RagServiceServicer):
    async def UploadDocument(self, request, context):
        content = bytes(request.content)

        text = extract_document(request.filename, content)
        chunks = chunk_text(text, metadata={"filename": request.filename})
        return rag_pb2.DocumentResponse(text=chunks)


async def serve():
    server = grpc.aio.server()
    rag_pb2_grpc.add_RagServiceServicer_to_server(RagServicer(), server)

    server.add_insecure_port("[::]:50051")
    await server.start()
    print("[gRPC] Listening on [::]:50051")
    await server.wait_for_termination()
