from fastapi import HTTPException, Request, status
from fastapi.responses import StreamingResponse
import mimetypes
def _get_range_header(range_header: str, file_size: int):
    def _invalid_range():
        return HTTPException(
            status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"Invalid request range (Range:{range_header!r})",
        )

    try:
        h = range_header.replace("bytes=", "").split("-")
        start = int(h[0]) if h[0] != "" else 0
        end = int(h[1]) if h[1] != "" else file_size - 1
    except ValueError:
        raise _invalid_range()

    if start > end or start < 0 or end > file_size - 1:
        raise _invalid_range()
    return start, end


async def __send_bytes_range_requests__(
        file_obj, start: int, end: int, chunk_size: int = 10_000
):
    """Send a file in chunks using Range Requests specification RFC7233

    `start` and `end` parameters are inclusive due to specification
    """

    file_obj.seek(start)
    data = [1]
    pos = file_obj.tell()
    while len(data) > 0:
        read_size = min(chunk_size, end + 1 - pos)
        data = await file_obj.read(read_size)
        yield data


async def streaming(fsg,request,content_type,streaming_buffering=1024 *  8*4):
    """
    Streaming content
    :param fsg: mongodb gridOut
    :param request: client request
    :param content_type: mime_type
    :param streaming_buffering: support 4k
    :return:
    """
    file_size = fsg.length
    range_header = request.headers.get("range")
    headers = {
        "content-type": content_type,
        "accept-ranges": "bytes",
        "content-encoding": "identity",
        "content-length": str(file_size),
        "access-control-expose-headers": (
            "content-type, accept-ranges, content-length, "
            "content-range, content-encoding"
        ),
    }
    start = 0
    end = file_size - 1
    status_code = 200

    if range_header is not None:
        start, end = _get_range_header(range_header, file_size)
        size = end - start + 1
        headers["content-length"] = str(size)
        headers["content-range"] = f"bytes {start}-{end}/{file_size}"
        status_code = status.HTTP_206_PARTIAL_CONTENT

    return StreamingResponse(
        __send_bytes_range_requests__(fsg, start, end, streaming_buffering),
        headers=headers,
        status_code=status_code,
    )
