from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------------------------------------------------------------------
# Endpoint de descubrimiento de suscripciones
# ---------------------------------------------------------------------------
# Dapr llama a GET /dapr/subscribe al iniciar el sidecar para saber
# a qué tópicos debe suscribirse esta aplicación.
#
# Retorna una lista de suscripciones indicando:
#   - pubsubname: nombre del componente Dapr definido en el YAML
#   - topic:      nombre del tópico a escuchar
#   - route:      ruta HTTP de este servicio donde se entregarán los mensajes
# ---------------------------------------------------------------------------
@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    subscriptions = [
        {
            "pubsubname": "order-pubsub",
            "topic":      "orders",
            "route":      "/orders"
        }
    ]
    logging.info("Dapr solicitó las suscripciones: %s", subscriptions)
    return jsonify(subscriptions)


# ---------------------------------------------------------------------------
# Endpoint receptor de mensajes del tópico 'orders'
# ---------------------------------------------------------------------------
# Dapr envuelve el payload original en un sobre CloudEvents 1.0 antes
# de enviarlo a esta ruta. La estructura recibida es:
#
#   {
#     "specversion":     "1.0",
#     "id":              "<uuid generado por Dapr>",
#     "source":          "<app-id del publisher>",
#     "type":            "com.dapr.event.sent",
#     "datacontenttype": "application/json",
#     "traceparent":     "<W3C Trace Context>",
#     "data": {
#       "orderId": "1001",
#       "status":  "created"
#     }
#   }
#
# Retorna {"status": "SUCCESS"} con HTTP 200 para confirmar la recepción.
# Si el sidecar recibe un código distinto, reintentará la entrega.
# ---------------------------------------------------------------------------
@app.route('/orders', methods=['POST'])
def receive_order():
    cloud_event = request.get_json()

    # Atributos del sobre CloudEvents (metadatos de infraestructura)
    event_id      = cloud_event.get("id", "N/A")
    event_source  = cloud_event.get("source", "N/A")
    event_type    = cloud_event.get("type", "N/A")
    traceparent   = cloud_event.get("traceparent", "N/A")

    # Payload de negocio (lo que publicó el publisher)
    data = cloud_event.get("data", {})

    logging.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logging.info("📨 CloudEvent recibido")
    logging.info("   id          : %s", event_id)
    logging.info("   source      : %s", event_source)
    logging.info("   type        : %s", event_type)
    logging.info("   traceparent : %s", traceparent)
    logging.info("   data        : %s", data)
    logging.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return jsonify({"status": "SUCCESS"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
