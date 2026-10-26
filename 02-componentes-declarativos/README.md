# Fase 2: Componentes Declarativos — El Contrato de Mensajería

## 2.1 ¿Por qué componentes declarativos?

En una arquitectura tradicional, cambiar el broker de mensajería (de Redis a Kafka, o de RabbitMQ a Azure Service Bus) requiere:

1. Reescribir el código de la aplicación para usar el nuevo SDK
2. Gestionar la autenticación y configuración propietaria de cada broker
3. Modificar los pipelines de CI/CD y las variables de entorno

Con Dapr, el código de la aplicación **nunca referencia el broker directamente**. En su lugar, declara un `Component` que es el único artefacto que cambia en una migración de broker.

### El flujo de datos en Dapr Pub/Sub

```
Publisher App  →  Dapr Sidecar  →  Component YAML  →  Redis/Kafka/RabbitMQ
                      ↑
              (traduce la llamada HTTP
               estándar al protocolo
               del broker concreto)

Subscriber App  ←  Dapr Sidecar  ←  Component YAML  ←  Redis/Kafka/RabbitMQ
                      ↑
              (recibe el evento del broker,
               lo envuelve en CloudEvents 1.0
               y lo reenvía a la app)
```

### Anatomía de un Component YAML

| Campo | Descripción |
|---|---|
| `metadata.name` | Nombre lógico con el que la app referencia este componente |
| `spec.type` | Tipo de building block + implementación concreta (ej: `pubsub.redis`) |
| `spec.version` | Versión del componente |
| `spec.metadata` | Configuración específica del broker subyacente |

### Referencias esenciales

- 📖 [Components — Documentación oficial](https://docs.dapr.io/concepts/components-concept/)
- 📖 [Pub/Sub Redis Component](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-redis-pubsub/)
- 📖 [Todos los brokers soportados](https://docs.dapr.io/reference/components-reference/supported-pubsub/)

---

## 2.2 Instalar Redis en el Clúster Kind

Redis actúa como el broker de mensajería subyacente. Para el estudiante y el código de la app, su existencia es **transparente** — solo la vemos aquí, en el nivel de configuración de infraestructura.

```bash
# Agregar el repositorio de Bitnami
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Instalar Redis en el namespace redis (sin contraseña para simplificar)
helm install redis bitnami/redis \
  --namespace redis \
  --create-namespace \
  --set auth.enabled=false \
  --set replica.replicaCount=0 \
  --wait

# Verificar que Redis está corriendo
kubectl get pods -n redis
```

```bash
# Verificar el nombre del Service de Redis (lo necesitarás para el TODO 1)
kubectl get svc -n redis
```

---

## 2.3 Aplicar el Componente Pub/Sub

El archivo `pubsub-redis.yaml` define el componente de mensajería. **Tiene un TODO que debes completar antes de aplicarlo.**

Una vez completado el TODO, aplícalo:

```bash
kubectl apply -f 02-componentes-declarativos/pubsub-redis.yaml

# Verificar que Dapr registró el componente
kubectl get components.dapr.io
```

Deberías ver:

```
NAME           AGE
order-pubsub   10s
```

---

## 2.4 Actividades TODO

### TODO 1: Completar el `redisHost` con el DNS de Kubernetes

Abre el archivo `02-componentes-declarativos/pubsub-redis.yaml`.

El campo `redisHost` está vacío. Debes completarlo con la dirección correcta del Service de Redis dentro del clúster.

**Pista:** En Kubernetes, los Services son accesibles mediante el patrón de DNS interno:
```
<service-name>.<namespace>.svc.cluster.local:<port>
```

Usa el comando del paso anterior para descubrir el nombre exacto del Service y el namespace. El puerto de Redis es `6379`.

Una vez completado, aplica el componente y verifica que aparece con:
```bash
kubectl get components.dapr.io -o yaml
```

---

### TODO 2: Análisis de la Abstracción

En el archivo `02-componentes-declarativos/analisis-abstraccion.md`, responde:

1. **Migración de broker:** Si la empresa decide migrar de Redis a Apache Kafka mañana, ¿qué archivos del repositorio habría que modificar? ¿Cambiaría el código Python del subscriber o del publisher?

2. **Inventario de brokers soportados:** Consulta la [documentación de componentes Pub/Sub de Dapr](https://docs.dapr.io/reference/components-reference/supported-pubsub/). Lista **5 brokers distintos** que Dapr soporta como implementación. ¿Qué campo en el YAML cambia para apuntar a cada uno?

3. **Secretos en producción:** El valor `redisPassword: ""` funciona para el lab, pero en producción nunca se deben poner contraseñas en texto plano en un YAML de Git. ¿Qué mecanismo ofrece Dapr para referenciar secretos de forma segura? (Pista: busca "Dapr Secret Store component reference")

---

*Continúa con → [Fase 3: Aplicaciones Pub/Sub](../03-aplicaciones/README.md)*
