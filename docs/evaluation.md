# Evaluar Aplomo

La evaluación tiene dos objetivos distintos: demostrar que el producto funciona y comprobar si mejora el comportamiento de un agente.

## 1. Contrato determinista

```bash
aplomo eval
```

| Grupo | Qué invalida |
|---|---|
| Normalización | Un hook equivalente produce eventos diferentes según el agente |
| Configuración nativa | JSON/TOML inválido, comando erróneo o adaptador ausente |
| Instalación segura | Se modifica una configuración que Aplomo no posee |
| Idempotencia | Una segunda instalación cambia archivos sin cambiar la fuente |
| MCP | Falla la inicialización, el listado o una llamada real a herramienta |

La CI ejecuta además los tests en Python 3.12 y 3.13 y construye el paquete.

## 2. Benchmark de comportamiento A/B

Para responder “¿el agente trabaja mejor?”, usa al menos 10 tareas representativas en repositorios desechables. Ejecuta cada tarea dos veces con el mismo modelo, prompt, commit inicial y presupuesto:

- Control: sin Aplomo.
- Tratamiento: con Aplomo inicializado.

| Métrica | Peso | Regla |
|---|---:|---|
| Corrección | 40% | Tests de aceptación ocultos aprobados |
| Respeto arquitectónico | 25% | No viola límites de `.engineering/architecture.yaml` |
| Reutilización | 15% | Extiende un patrón existente cuando corresponde |
| Calidad del cambio | 10% | Diff acotado, sin secretos y con pruebas pertinentes |
| Coste | 10% | Tiempo, turnos y tokens normalizados frente al control |

Fija el criterio antes de mirar resultados:

- Ninguna regresión estadísticamente clara en corrección.
- Al menos 20% menos violaciones arquitectónicas.
- Al menos 15% menos abstracciones duplicadas.
- Sobrecoste mediano inferior al 10%.

Registra falsos positivos: ocasiones en las que Aplomo bloquea o distrae una solución válida. Publica resultados por agente y modelo; una media conjunta puede ocultar que una integración funciona y otra falla.

Un `aplomo eval` verde confirma instalación y contratos, no obediencia del modelo ni mejora general. Esa conclusión solo es válida después del benchmark A/B.
