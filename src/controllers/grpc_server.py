import grpc
import grpc.aio

from proto import rag_pb2, rag_pb2_grpc
from services.document_extractor import extract_document
from services.chunking import chunk_text
from services.storage_service import store_chunks
from services.llm_service import answer_query


class RagServicer(rag_pb2_grpc.RagServiceServicer):
    async def UploadDocument(self, request, context):
        content = bytes(request.content)

        text = extract_document(request.filename, content)
        chunks = chunk_text(text, metadata={"filename": request.filename})
        result = await store_chunks(chunks, request.filename)

        print(
            f"Stored {result['chunks_created']} chunks, document_id={result['document_id']}"
        )

        return rag_pb2.DocumentResponse(
            document_id=result["document_id"],
            chunks_created=result["chunks_created"],
            status=result["status"],
        )

    async def GetAnswer(self, request, context):
        result = await answer_query(request.query)
        return rag_pb2.QueryResponse(answer=result["answer"], sources=result["sources"])


async def serve():
    server = grpc.aio.server()
    rag_pb2_grpc.add_RagServiceServicer_to_server(RagServicer(), server)

    server.add_insecure_port("[::]:50051")
    await server.start()
    print("[gRPC] Listening on [::]:50051")
    await server.wait_for_termination()
