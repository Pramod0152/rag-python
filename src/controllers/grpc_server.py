import asyncio

import grpc
import grpc.aio

from proto import rag_pb2, rag_pb2_grpc
from services.document_extractor import extract_document
from services.chunking import chunk_text
from services.storage_service import store_chunks
from services.llm_service import answer_query


def _log_progress(step: str, message: str, percent: int) -> None:
    print(f"[upload:{step}] ({percent}%) {message}")


def _progress_event(
    step: str,
    message: str,
    percent: int,
    result: rag_pb2.DocumentResponse | None = None,
) -> rag_pb2.UploadProgress:
    _log_progress(step, message, percent)
    return rag_pb2.UploadProgress(
        step=step,
        message=message,
        progress_percent=percent,
        result=result or rag_pb2.DocumentResponse(),
    )


class RagServicer(rag_pb2_grpc.RagServiceServicer):
    async def UploadDocument(self, request, context):
        filename = request.filename
        content = bytes(request.content)
        size_kb = len(content) / 1024

        yield _progress_event(
            "received",
            f"Received {filename} ({size_kb:.1f} KB)",
            5,
        )

        try:
            yield _progress_event(
                "extracting",
                f"Extracting text from {filename}...",
                15,
            )
            text = await asyncio.to_thread(extract_document, filename, content)
            yield _progress_event(
                "extracting",
                f"Extracted {len(text):,} characters from {filename}",
                25,
            )

            yield _progress_event(
                "chunking",
                "Splitting text into chunks...",
                30,
            )
            chunks = await asyncio.to_thread(
                chunk_text, text, metadata={"filename": filename}
            )
            yield _progress_event(
                "chunking",
                f"Created {len(chunks)} chunks",
                40,
            )

            progress_queue: asyncio.Queue[rag_pb2.UploadProgress] = asyncio.Queue()

            async def on_progress(step: str, message: str, percent: int) -> None:
                await progress_queue.put(_progress_event(step, message, percent))

            store_task = asyncio.create_task(
                store_chunks(chunks, filename, on_progress=on_progress)
            )

            while not store_task.done() or not progress_queue.empty():
                try:
                    update = progress_queue.get_nowait()
                except asyncio.QueueEmpty:
                    if store_task.done():
                        break
                    await asyncio.sleep(0.05)
                    continue
                yield update

            result = store_task.result()

            yield _progress_event(
                "complete",
                f"Upload complete: {result['chunks_created']} chunks stored",
                100,
                result=rag_pb2.DocumentResponse(
                    document_id=result["document_id"],
                    chunks_created=result["chunks_created"],
                    status=result["status"],
                ),
            )
        except Exception as exc:
            yield _progress_event("error", str(exc), 0)
            await context.abort(grpc.StatusCode.INTERNAL, str(exc))

    async def GetAnswer(self, request, context):
        result = await answer_query(request.query)
        return rag_pb2.QueryResponse(answer=result["answer"], sources=result["sources"])


MAX_MESSAGE_SIZE = 50 * 1024 * 1024  # 50MB

GRPC_SERVER_OPTIONS = [
    ("grpc.max_send_message_length", MAX_MESSAGE_SIZE),
    ("grpc.max_receive_message_length", MAX_MESSAGE_SIZE),
]


async def serve():
    server = grpc.aio.server(options=GRPC_SERVER_OPTIONS)
    rag_pb2_grpc.add_RagServiceServicer_to_server(RagServicer(), server)

    server.add_insecure_port("[::]:50051")
    await server.start()
    print("[gRPC] Listening on [::]:50051")
    await server.wait_for_termination()
