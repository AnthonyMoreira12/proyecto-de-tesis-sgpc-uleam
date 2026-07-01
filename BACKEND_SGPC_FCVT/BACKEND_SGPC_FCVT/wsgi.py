import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BACKEND_SGPC_FCVT.settings')

application = get_wsgi_application()

# ==============================================================================
# INICIALIZACIÓN DE OPENTELEMETRY
# ==============================================================================
from django.conf import settings

if getattr(settings, 'ENABLE_TELEMETRY', False):
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.django import DjangoInstrumentor

    # 1. Configurar el proveedor de trazas
    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()

    # 2. Configurar el exportador (envía los datos a un colector como Jaeger o Azure)
    # Por defecto usará http://localhost:4317 si no se le pasa otra variable de entorno
    otlp_exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # 3. (Opcional) Si quieres ver las trazas en tu terminal también, descomenta la siguiente línea:
    # tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # 4. Inyectar la instrumentación en el núcleo de Django
    DjangoInstrumentor().instrument()