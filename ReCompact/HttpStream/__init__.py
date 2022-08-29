import os
import re
import mimetypes
from wsgiref.util import FileWrapper
import gridfs
from django.http.response import StreamingHttpResponse
range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
from gridfs import GridFSBucket
def file_iterator(f:gridfs.grid_file.GridOut, chunk_size=1024*1024*2, offset=0, length=None):
    f.seek(offset, os.SEEK_SET)
    remaining = length
    while True:
      bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
      data = f.read(bytes_length)
      if not data or data.__len__()==0:
        break
      if remaining:
        remaining -= len(data)
      yield data
def stream_video(request, path,f:gridfs.grid_file.GridOut):
  """Responding to the video file by streaming media"""
  range_header = request.META.get('HTTP_RANGE', '').strip()
  range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
  range_match = range_re.match(range_header)
  size = f.length
  content_type, encoding = mimetypes.guess_type(path)
  content_type = content_type or 'application/octet-stream'
  if range_match:
    first_byte, last_byte = range_match.groups()
    first_byte = int(first_byte) if first_byte else 0
    last_byte = first_byte + 1024 * 1024 * 8    # 8M Each piece, the maximum volume of the response body
    if last_byte >= size:
      last_byte = size - 1
    length = last_byte - first_byte + 1
    resp = StreamingHttpResponse(FileWrapper(f, offset=first_byte, length=length), status=206, content_type=content_type)
    resp['Content-Length'] = str(length)
    resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
  else:
    # When it is not obtained by video stream, the entire file is returned by generator to save memory
    resp = StreamingHttpResponse(FileWrapper(f), content_type=content_type, status=206)
    resp['Content-Length'] = str(size)
  resp['Accept-Ranges'] = 'bytes'
  return resp
class RangeFileWrapper(object):
    import gridfs
    def __init__(self, filelike, blksize=8192*4, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize


    def close(self):
        if hasattr(self.filelike, 'close'):
            return self.filelike.close
    def __getitem__(self,key):
        self.filelike = GridFSBucket(self.db)
        fs = self.filelike

        data = self.filelike.read(self.blksize)

        fs.close()
        if data:
            return data
        raise IndexError
    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.

            data = self.filelike.read(self.blksize)

            if data:
                return data
            # raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))

            # if not data:
            #     raise StopIteration()
            self.remaining -= len(data)
            return data
def streaming_mongo_db_fs(request,file:gridfs.grid_file.GridOut):

    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    size = file.length
    content_type, encoding = mimetypes.guess_type(file.filename)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        # last_byte = int(last_byte) if last_byte else size - 1
        "rat quan trong"
        last_byte = first_byte + 1024 * 1024 * 24
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(RangeFileWrapper(file, offset=first_byte, length=length), status=206,
                                     content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(file),  content_type=content_type)
        resp['Content-Length'] = str(size)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (0, size, size)
    resp['Accept-Ranges'] = 'bytes'
    return resp