import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logging_config import get_access_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in ('/api/v1/health', '/', '/metrics'):
            return await call_next(request)

        start_time = time.time()
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))

        request.state.request_id = request_id
        request.state.start_time = start_time

        user_id = '-'
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                from app.auth import decode_jwt_token
                token = auth_header[7:]
                payload = decode_jwt_token(token)
                if payload:
                    user_id = payload.get('sub', payload.get('name', '-'))
        except Exception:
            pass

        request.state.user_id = user_id

        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = request_id
            record.trace_id = request_id
            record.user_id = user_id
            return record

        logging.setLogRecordFactory(record_factory)

        access_logger = get_access_logger()

        access_logger.info(
            f"{request.method} {request.url.path}",
            extra={
                'method': request.method,
                'path': request.url.path,
                'query_params': str(request.query_params) if request.query_params else '',
                'client_ip': request.client.host if request.client else '-',
                'user_agent': request.headers.get('user-agent', '-'),
                'event': 'request_start',
            },
        )

        try:
            response = await call_next(request)

            process_time = (time.time() - start_time) * 1000
            status_code = response.status_code

            if request.url.path.startswith('/uploads/') or request.url.path.startswith('/api/v1/files/'):
                response.headers['Cache-Control'] = 'public, max-age=31536000'
            elif '/export/' in request.url.path:
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            elif request.url.path.startswith('/api/'):
                response.headers['Cache-Control'] = 'public, max-age=60'

            response.headers['X-Request-ID'] = request_id
            response.headers['X-Trace-ID'] = request_id
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'
            if request.url.scheme == 'https':
                response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'

            access_logger.info(
                f"{request.method} {request.url.path} - {status_code} - {process_time:.2f}ms",
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'status_code': status_code,
                    'process_time_ms': round(process_time, 2),
                    'client_ip': request.client.host if request.client else '-',
                    'event': 'request_end',
                },
            )

            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            access_logger.error(
                f"{request.method} {request.url.path} - EXCEPTION - {process_time:.2f}ms",
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'process_time_ms': round(process_time, 2),
                    'exception': str(e),
                    'client_ip': request.client.host if request.client else '-',
                    'event': 'request_error',
                },
                exc_info=True,
            )
            raise
        finally:
            logging.setLogRecordFactory(old_factory)
