# Guía de Uso - Unpivot de variables de extension de medidas y hechos Darwin Core

## Descripción

Script Python para reorganizar extensiones de mediciones en formato Darwin Core desde una estructura "wide" (múltiples columnas) a una estructura "long" (normalizada). Este proceso facilita el análisis, validación y publicación de datos de biodiversidad.

## Requisitos

- Python 3.8 o superior
- Librerías Python:
  - pandas >= 1.3.0
  - numpy >= 1.21.0

## Instalación

```bash
pip install pandas numpy
```

## Estructura de Datos

### Entrada (Formato Wide)

Archivo CSV con múltiples columnas de extensiones numeradas:

```csv
occurrenceID,measurementType1,measurementUnit1,measurementValue1,measurementType2,measurementUnit2,measurementValue2
1,Altura,cm,150,Peso,kg,65
2,Longitud,mm,25,Ancho,mm,10
```

### Salida (Formato Long)

Archivo CSV normalizado con tres columnas estándar:

```csv
occurrenceID,measurementType,measurementUnit,measurementValue
1,Altura,cm,150
1,Peso,kg,65
2,Longitud,mm,25
2,Ancho,mm,10
```

## Configuración Previa

### 1. Preparar el archivo de entrada

**Ubicación:** Coloque su archivo CSV en la misma carpeta que el script.

**Verificaciones críticas:**

#### A. Nombres de columnas únicos

El script requiere que cada valor de `measurementType` sea único. Si hay duplicados entre extensiones, debe renombrarlos antes de ejecutar.

**Ejemplo de problema:**
```csv
measurementType1,measurementType13,measurementType16
INTERPRETACION,INTERPRETACION,INTERPRETACION
```

**Solución:** Renombre en OpenRefine o Excel:
```csv
measurementType1,measurementType13,measurementType16
INTERPRETACION1,INTERPRETACION13,INTERPRETACION16
```

#### B. Formato de nombres de columnas

Las columnas deben seguir el patrón:
- `measurementType1`, `measurementType2`, ..., `measurementTypeN`
- `measurementUnit1`, `measurementUnit2`, ..., `measurementUnitN`
- `measurementValue1`, `measurementValue2`, ..., `measurementValueN`

**Nota:** El script también reconoce variantes sin número (ej. `measurementType` sin número).

### 2. Editar la ruta del archivo

Abra `unpivot.py` y modifique la línea 32:

```python
# Línea 32
df = pd.read_csv('NOMBRE_DE_SU_ARCHIVO.csv')
```

Reemplace `'NOMBRE_DE_SU_ARCHIVO.csv'` con el nombre exacto de su archivo.

## Ejecución

### Paso 1: Ejecutar el script

```bash
cd unpivot
python unpivot.py
```

### Paso 2: Revisar la salida en consola

El script muestra información detallada en cada fase:

#### Verificación inicial
```
=== VERIFICACIÓN INICIAL ===
Shape del dataset: (100, 45)
Total de filas: 100
Total de columnas: 45

Columnas encontradas:
  1. occurrenceID
  2. measurementType1
  3. measurementUnit1
  ...
```

#### Reporte de nulos
```
=== REPORTE DE NULOS ===
Extensiones encontradas: 15
Total de nulos en todas las extensiones: 1250

Extensión #1:
  measurementType1              → Nulos: 0
  measurementUnit1              → Nulos: 10
  measurementValue1             → Nulos: 5
```

#### Debug de valores únicos
```
=== DEBUG: VALORES ÚNICOS DENTRO DE CADA COLUMNA ===

Extensión #1:
  Columna: measurementType1
  Valores únicos dentro: 1
    - 'Altura'
```

**IMPORTANTE:** Si "Valores únicos dentro" es mayor a 1, **DETENGA** el proceso. Esto indica que hay valores diferentes en la misma columna de extensión, lo cual causará problemas. Revise y corrija el dataset.

#### Unpivot completado
```
=== REALIZANDO UNPIVOT ===
✓ Extensión #1 procesada
✓ Extensión #2 procesada
...

✓ Unpivot completado
  Filas originales: 100
  Filas finales: 1500
  Columnas finales: 4
```

#### Limpieza de datos
```
=== ELIMINANDO FILAS VACÍAS ===
 Filas antes de limpiar: 1500
 Filas eliminadas: 200
 Filas después de limpiar: 1300
 Porcentaje de datos conservados: 86.7%
```

### Paso 3: Obtener el resultado

El archivo `resultado_unpivot.csv` se crea en la misma carpeta del script.

## Opciones de Limpieza Adicional

El script incluye una sección opcional (Parte 4.7) para eliminar filas con solo una columna llena:

```python
# PARTE 4.7: ELIMINAR FILAS CON SOLO UNA COLUMNA LLENA
# Descomente la línea correspondiente según su criterio
```

### Opción 1: Eliminar filas con solo Type lleno

```python
# Descomente esta línea:
df_final = df_final[~((df_final['measurementType'].notnull()) & (df_final['measurementUnit'].isnull()) & (df_final['measurementValue'].isnull()))]
```

### Opción 2: Eliminar filas con solo Unit lleno

```python
# Descomente esta línea:
df_final = df_final[~((df_final['measurementType'].isnull()) & (df_final['measurementUnit'].notnull()) & (df_final['measurementValue'].isnull()))]
```

### Opción 3: Eliminar filas con solo Value lleno

```python
# Descomente esta línea:
df_final = df_final[~((df_final['measurementType'].isnull()) & (df_final['measurementUnit'].isnull()) & (df_final['measurementValue'].notnull()))]
```

**Después de descomentar, ejecute:**
```python
df_final = df_final.reset_index(drop=True)
```

## Solución de Problemas

### Error: "File not found"

**Causa:** El nombre del archivo en línea 32 no coincide con el archivo real.

**Solución:**
```python
# Verifique el nombre exacto
ls  # En la terminal
# Luego actualice la línea 32 con el nombre correcto
```

### Error: "KeyError: 'measurementType1'"

**Causa:** Las columnas no siguen el patrón esperado.

**Solución:**
1. Ejecute la última sección del script (Debug de nombres):
```python
# Al final del script, revise:
=== DEBUG: NOMBRES EXACTOS DE COLUMNAS ===
  measurementtype1    # ← minúsculas
  MeasurementType1    # ← mayúsculas mezcladas
```

2. Corrija los nombres de columnas en el CSV para que sean exactamente:
   - `measurementType1`, `measurementUnit1`, `measurementValue1`
   - Sin espacios, con mayúsculas/minúsculas exactas

### Valores únicos > 1 en una extensión

**Problema:**
```
Extensión #5:
  Valores únicos dentro: 3
    - 'Peso'
    - 'Longitud'
    - 'Altura'
```

**Causa:** La misma columna tiene diferentes tipos de mediciones.

**Solución:** 
Este es un problema de estructura de datos. Revise el dataset original. Probablemente necesita:
1. Reorganizar manualmente en Excel/OpenRefine
2. Asignar cada tipo de medición a su propia extensión numerada

### Muchas filas eliminadas en limpieza

Si el porcentaje de datos conservados es muy bajo (< 50%):

1. Revise el dataset original
2. Verifique que las extensiones tengan datos reales
3. Considere si realmente necesita todas las extensiones numeradas

## Validación Post-Unpivot

Después de ejecutar el script:

1. **Abra el archivo de salida en Excel/OpenRefine**
2. **Verifique:**
   - Número de filas es correcto (original × número de extensiones)
   - No hay valores perdidos inesperadamente
   - Los tipos de medición son correctos
   - Las unidades corresponden a sus tipos

## Caso de Uso: Datos con EventID

Si sus datos usan `eventID` en lugar de (o además de) `occurrenceID`:

1. Abra `unpivot.py`
2. Busque la línea 125:
```python
df_temp['occurrenceID'] = df['occurrenceID']
#df_temp['eventID'] = df['eventID'] #llave eventos, descomentar cuando sea así.
```
3. Descomente la segunda línea:
```python
df_temp['occurrenceID'] = df['occurrenceID']
df_temp['eventID'] = df['eventID']
```

## Próximos Pasos

Una vez completado el unpivot:

1. **OpenRefine:** Para validaciones adicionales y limpieza de datos
2. **Validación Darwin Core:** Verificar que cumple con el estándar DwC
3. **Publicación:** Preparar para GBIF, SiB Colombia, u otros repositorios

## Referencia de Columnas

### Columnas de entrada (ejemplo)
- `occurrenceID`: Identificador único del registro
- `measurementType1...N`: Tipo de medición (ej. "Altura", "Peso")
- `measurementUnit1...N`: Unidad de medida (ej. "cm", "kg")
- `measurementValue1...N`: Valor numérico o categórico

### Columnas de salida
- `occurrenceID`: Mantenido del original
- `measurementType`: Tipo de medición consolidado
- `measurementUnit`: Unidad de medida consolidada
- `measurementValue`: Valor consolidado

## Contacto

Para reportar problemas o sugerir mejoras, contacte al autor o abra un issue en el repositorio.
