# Fase 1: Arquitectura Sidecar — Clúster y Plano de Control Dapr

## 1.1 ¿Qué es Dapr?

**Dapr (Distributed Application Runtime)** es un runtime de código abierto que implementa capacidades de infraestructura distribuida como un **sidecar** —un contenedor auxiliar que corre junto a tu aplicación y asume la complejidad de red, mensajería, service discovery y observabilidad.

La idea central es poderosa: **tu código de negocio no habla con Redis, Kafka ni ningún broker directamente. Habla con el sidecar de Dapr a través de HTTP o gRPC estándar.**

### Conceptos clave que debes dominar

| Concepto | Descripción |
|---|---|
| **Sidecar** | Contenedor auxiliar inyectado junto a la app que expone las APIs de Dapr |
| **Building Block** | Capacidad de infraestructura abstraída (Pub/Sub, State Store, Secrets, etc.) |
| **Component** | Archivo YAML declarativo que configura qué tecnología concreta implementa cada Building Block |
| **Control Plane** | Conjunto de servicios de Dapr que corren en `dapr-system` y gestionan el ciclo de vida de los sidecars |
| **CloudEvents 1.0** | Estándar CNCF de envoltura de eventos que Dapr aplica automáticamente en Pub/Sub |

### Componentes del plano de control de Dapr en Kubernetes

| Pod | Función |
|---|---|
| `dapr-operator` | Reconcilia los objetos `Component` de Kubernetes y los distribuye a los sidecars |
| `dapr-sidecar-injector` | Webhook de Kubernetes que inyecta el contenedor `daprd` cuando detecta la anotación `dapr.io/enabled: "true"` |
| `dapr-placement` | Servicio de distribución de actores (necesario aunque no usemos actores) |
| `dapr-sentinels` | Servicio de health y coordinación del plano de control |

### Referencias esenciales

- 📖 [Conceptos: Dapr Sidecar](https://docs.dapr.io/concepts/dapr-services/sidecar/)
- 📖 [Building Block: Pub/Sub](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- 📖 [CloudEvents 1.0 Specification](https://cloudevents.io/)
- 📖 [Anotaciones del Sidecar de Dapr](https://docs.dapr.io/reference/arguments-annotations-overview/)

---

## 1.2 Crear el Clúster Kind

```bash
# Crear un clúster Kind con nombre dapr-lab
kind create cluster --name dapr-lab

# Verificar que el contexto apunta al nuevo clúster
kubectl config current-context
# Debe mostrar: kind-dapr-lab
```

---

## 1.3 Instalar Dapr en Kubernetes con Helm

```bash
# Agregar el repositorio oficial de Dapr
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Instalar Dapr en el namespace dapr-system
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --wait

# Verificar la instalación
kubectl get pods -n dapr-system
```

Deberías ver algo similar a:

```
NAME                                     READY   STATUS    RESTARTS   AGE
dapr-dashboard-...                       1/1     Running   0          2m
dapr-operator-...                        1/1     Running   0          2m
dapr-placement-server-...                1/1     Running   0          2m
dapr-sidecar-injector-...                1/1     Running   0          2m
dapr-sentinels-...                       1/1     Running   0          2m
```

```bash
# Verificar los CRDs que Dapr instala (los Component, Subscription, etc.)
kubectl get crds | grep dapr
```

---

## 1.4 Actividades TODO

### TODO 1: Análisis del Plano de Control

**Objetivo:** Comprender qué hace cada componente del plano de control de Dapr antes de usarlo.

Ejecuta el siguiente comando y examina la salida:

```bash
kubectl get pods -n dapr-system -o wide
kubectl describe pod -n dapr-system -l app=dapr-sidecar-injector
```

Responde en un archivo `01-arquitectura-sidecar/analisis-control-plane.md`:

1. ¿Qué tipo de objeto de Kubernetes es el `dapr-sidecar-injector`? ¿Por qué necesita ser un **MutatingWebhookConfiguration**?
2. ¿Cuántas réplicas del `dapr-operator` están corriendo? ¿Por qué el plano de control de Dapr es más liviano que el de Istio?
3. Describe con tus palabras el flujo de inyección del sidecar: ¿qué ocurre desde que `kubectl apply` un Deployment con `dapr.io/enabled: "true"` hasta que el sidecar está corriendo?

---

### TODO 2: Exploración de los CRDs de Dapr

**Objetivo:** Entender el modelo de extensibilidad de Dapr a través de Custom Resource Definitions.

```bash
# Listar los CRDs instalados por Dapr
kubectl get crds | grep dapr.io
```

Responde en `01-arquitectura-sidecar/analisis-control-plane.md`:

4. ¿Qué CRDs instala Dapr? Lista al menos 4 y describe brevemente para qué sirve cada uno.
5. ¿Cómo se relaciona el CRD `components.dapr.io` con el concepto de "Building Block"? ¿Es el componente la abstracción o la implementación concreta?

---

*Continúa con → [Fase 2: Componentes Declarativos](../02-componentes-declarativos/README.md)*
