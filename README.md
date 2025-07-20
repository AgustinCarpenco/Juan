## Análisis y limpieza inicial de datos (1ra evaluación)

**Objetivo:**
Cargar e inspeccionar el archivo `data/1ra evaluación.xlsx` para entender su estructura y detectar problemas de calidad de datos.

**Comandos implementados en limpieza.py:**
- `cargar_excel(path)`: Carga el archivo Excel y maneja errores.
- `inspeccion_inicial(df)`: Muestra dimensiones, columnas, tipos, nulos, duplicados y ejemplos de datos.

**Uso básico:**
```bash
python limpieza.py
```

**Resultados esperados:**
- Información sobre dimensiones, columnas, tipos de datos, valores nulos, duplicados y ejemplos de datos.
- Identificación de posibles problemas (columnas irrelevantes, nulos, formatos inconsistentes, etc.).

**Próximos pasos:**
- Definir plan de limpieza según hallazgos (eliminar/renombrar columnas, tratar nulos, normalizar formatos, etc.).
- Documentar cada transformación relevante.

---
