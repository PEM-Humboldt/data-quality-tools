# Guía de Uso - Validación Geográfica con PyQGIS

## Descripción

Sistema automatizado de validación de coordenadas geográficas mediante spatial joins (uniones espaciales) con capas de referencia oficiales. El script compara las coordenadas documentadas con la ubicación geográfica real según divisiones políticas de Colombia.

## Requisitos del Sistema

### Software Requerido
- **QGIS:** Versión 3.34 o superior
- **Python:** 3.8+ (incluido con QGIS)

### Capas de Referencia
Incluidas en `data/reference/`:
- `MGN_MPIO_POLITICO_2020.shp` - División municipal DANE 2020
- `MGN_MPIO_2020_Buffer_530m.shp` - Buffer de 530m sobre municipios

## Instalación

### 1. Instalar QGIS en Ubuntu

```bash
sudo apt update
sudo apt install qgis python3-qgis
```

**Verificar instalación:**
```bash
qgis --version
# Salida esperada: QGIS 3.34.x-Prizren 'Prizren'
```

### 2. Clonar o descargar el repositorio

```bash
git clone https://github.com/PEM-Humboldt/data-quality-tools.git
cd data-quality-tools/PythonScripts-ValidacionCoordenadas-Unpivot/CoordenadasPyQGIS\ v1.0
```

### 3. Verificar estructura

```bash
ls -la
# Debe mostrar:
# - run_validation.sh
# - scripts/
# - data/
# - logs/
```

### 4. Hacer ejecutable el wrapper

```bash
chmod +x run_validation.sh
```

## Preparación de Datos

### Requisitos del CSV de Entrada

Su archivo CSV **debe** contener estas columnas exactas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `decimalLongitude` | Longitud en grados decimales | -74.0721 |
| `decimalLatitude` | Latitud en grados decimales | 4.7110 |
| `county` | Municipio documentado | Bogotá |
| `stateProvince` | Departamento documentado | Cundinamarca |

**Ejemplo de archivo válido:**
```csv
occurrenceID,decimalLongitude,decimalLatitude,county,stateProvince
1,-74.0721,4.7110,Bogotá,Cundinamarca
2,-75.5636,6.2476,Medellín,Antioquia
3,-76.5225,3.4516,Cali,Valle del Cauca
```

### Verificaciones Previas

1. **Sistema de coordenadas:** WGS84 (EPSG:4326)
2. **Formato decimal:** No usar grados-minutos-segundos
3. **Sin espacios extras:** En nombres de municipios/departamentos
4. **Encoding:** UTF-8 recomendado

## Uso Básico

### Colocar el archivo de entrada

```bash
cp /ruta/a/su/archivo.csv data/input/
```

### Ejecutar la validación

```bash
./run_validation.sh data/input/archivo.csv
```

**Con ruta de salida personalizada:**
```bash
./run_validation.sh data/input/archivo.csv data/output/resultado_custom.csv
```

## Proceso de Validación

El script ejecuta 6 pasos automáticamente:

### Paso 1: Inicialización de QGIS
```
[INFO] Inicializando QGIS...
[OK] QGIS inicializado correctamente
```

### Paso 2: Carga del CSV
```
[INFO] Cargando CSV y creando capa de puntos...
[OK] Capa de puntos creada: 100 registros
```

### Paso 3: Spatial Join con Municipios
```
[INFO] Realizando spatial join con MGN_MPIO_POLITICO_2020...
[OK] Join completado: 100 registros
```

**Campos agregados:**
- `DPTO_CNMBR`: Nombre oficial del departamento
- `MPIO_CNMBR`: Nombre oficial del municipio
- `suggestedS`: Departamento sugerido (para validación)
- `suggestedC`: Municipio sugerido (para validación)

### Paso 4: Spatial Join con Buffer
```
[INFO] Realizando spatial join con MGN_MPIO_2020_Buffer_530m...
[OK] Join completado: 100 registros
```

**Campos agregados:**
- `BUFF_DIST`: Distancia del buffer (530m)
- `suggestedC_2`: Municipio dentro del buffer

### Paso 5: Cálculo de Validaciones
```
[INFO] Calculando campos de validación...
  > Calculando valiCount...
  > Calculando valiStat...
  > Calculando valiBuffer...
[OK] Campos de validación calculados
```

### Paso 6: Exportación
```
[INFO] Exportando resultados a CSV...
[OK] Archivo exportado: data/output/archivo_validado.csv
```

### Estadísticas Finales
```
[INFO] ESTADÍSTICAS DE VALIDACIÓN:
 > Total de registros: 100
 > valiCount: 85/100 (85.0% válidos)
 > valiStat: 92/100 (92.0% válidos)
 > valiBuffer: 88/100 (88.0% válidos)
```

## Interpretación de Resultados

### Campos de Validación

| Campo | Validación | Interpretación |
|-------|-----------|----------------|
| `valiCount` | ¿`county` = `suggestedC`? | Municipio documentado coincide con el político exacto |
| `valiStat` | ¿`stateProvince` = `suggestedS`? | Departamento documentado coincide |
| `valiBuffer` | ¿`county` = `suggestedC_2`? | Municipio está dentro del buffer de 530m |

### Valores Posibles

| Valor | Significado |
|-------|-------------|
| `1` | **Válido** - Coincidencia exacta |
| `0` | **Inválido** - No coincide (error de documentación) |
| `NULL` | **No documentado** - Campo original estaba vacío |

### Ejemplos de Interpretación

#### Caso 1: Datos perfectos
```csv
county,stateProvince,suggestedC,suggestedS,valiCount,valiStat,valiBuffer
Bogotá,Cundinamarca,Bogotá,Cundinamarca,1,1,1
```
**Interpretación:** Coordenadas y documentación 100% correctas.

#### Caso 2: Error de tipeo
```csv
county,stateProvince,suggestedC,suggestedS,valiCount,valiStat,valiBuffer
Bogota,Cundinamarca,Bogotá,Cundinamarca,0,1,1
```
**Interpretación:** Falta tilde en "Bogotá". Coordenadas correctas, documentación tiene error menor.

#### Caso 3: Coordenada incorrecta
```csv
county,stateProvince,suggestedC,suggestedS,valiCount,valiStat,valiBuffer
Bogotá,Cundinamarca,Medellín,Antioquia,0,0,0
```
**Interpretación:** Las coordenadas apuntan a Medellín, no a Bogotá. Error grave en coordenadas.

#### Caso 4: Punto en límite municipal
```csv
county,stateProvince,suggestedC,suggestedS,valiCount,valiStat,valiBuffer
Soacha,Cundinamarca,Bogotá,Cundinamarca,0,1,1
```
**Interpretación:** Punto cerca del límite. `valiBuffer=1` indica que está dentro del margen de error GPS (530m).

## Configuración Avanzada

### Cambiar Capas de Referencia

Si necesita actualizar las capas (ej. divisiones 2024):

1. Descargue nuevos shapefiles del DANE
2. Colóquelos en `data/reference/`
3. Edite `scripts/validacion_geografica.py`:

```python
# Líneas 49-50
LAYER_POLITICO = REFERENCE_DIR / "MGN_MPIO_POLITICO_2024.shp"
LAYER_BUFFER = REFERENCE_DIR / "MGN_MPIO_2024_Buffer_530m.shp"
```

### Cambiar Nombres de Campos

Si sus columnas tienen nombres diferentes:

Edite `scripts/validacion_geografica.py`:

```python
# Líneas 55-58
FIELD_LONGITUDE = "longitude"      # Cambiar si su columna se llama distinto
FIELD_LATITUDE = "latitude"        # Cambiar si su columna se llama distinto
FIELD_COUNTY = "municipio"         # Cambiar si su columna se llama distinto
FIELD_STATE = "departamento"       # Cambiar si su columna se llama distinto
```

### Modificar Buffer

Para cambiar la distancia del buffer:

1. Genere nuevo buffer en QGIS:
   - Abra `MGN_MPIO_POLITICO_2020.shp`
   - Vector → Herramientas de geoproceso → Buffer
   - Distancia: `X` metros
   - Guardar como: `MGN_MPIO_2020_Buffer_Xm.shp`

2. Actualice la ruta en `scripts/validacion_geografica.py`

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'processing'"

**Causa:** PyQGIS no está en el PYTHONPATH

**Solución:** Use el wrapper `run_validation.sh` en lugar de ejecutar el Python directamente:
```bash
# Incorrecto:
python3 scripts/validacion_geografica.py archivo.csv

# Correcto:
./run_validation.sh data/input/archivo.csv
```

### Error: "NO SE PUDO CARGAR EL CSV COMO CAPA DE PUNTOS"

**Causas posibles:**
1. El CSV no tiene las columnas `decimalLongitude` y `decimalLatitude`
2. Las coordenadas no son numéricas
3. El archivo está corrupto

**Solución:**
```bash
# Verificar columnas
head -1 data/input/archivo.csv

# Debe contener:
# ...,decimalLongitude,decimalLatitude,...
```

### Error: "NO SE PUDO CARGAR [shapefile]"

**Causa:** Archivos de referencia faltantes o corruptos

**Solución:**
```bash
# Verificar que existan todos los archivos
ls -la data/reference/MGN_MPIO_POLITICO_2020.*

# Debe mostrar:
# .shp .shx .dbf .prj .cpg
```

### Proceso muy lento

**Causa:** Archivo CSV muy grande (> 10,000 registros)

**Solución:**
- Divida el archivo en lotes más pequeños
- Use una máquina con más RAM
- Ejecute en servidor en lugar de laptop

### Coordenadas fuera de Colombia

Si tiene registros internacionales:

**Comportamiento esperado:**
- `valiCount`, `valiStat`, `valiBuffer` = `NULL` o `0`
- `suggestedC` y `suggestedS` = vacío

**Nota:** El script solo valida para Colombia. Para otros países, necesita capas de referencia diferentes.

## Casos de Uso

### 1. Validación de Colección Biológica

```bash
# Dataset de 500 especímenes
./run_validation.sh data/input/coleccion_botanica.csv

# Resultado: 
# - 450 con coordenadas válidas (90%)
# - 30 con errores menores de tipeo (6%)
# - 20 con coordenadas incorrectas (4%)
```

**Acción:** Corregir los 50 registros con errores antes de publicar.

### 2. Control de Calidad Pre-GBIF

```bash
# Antes de publicar en GBIF
./run_validation.sh data/input/dataset_publicacion.csv

# Filtrar solo registros válidos:
# En Excel/R: Filtrar donde valiCount=1 AND valiStat=1
```

### 3. Migración de Datos Históricos

```bash
# Datos digitalizados de etiquetas antiguas
./run_validation.sh data/input/datos_historicos.csv

# Identificar registros con coordenadas sospechosas
# valiCount=0 AND valiBuffer=0 → Revisar manualmente
```

## Limitaciones

1. **Solo funciona en Linux:** No soportado en Windows nativo (use WSL)
2. **Requiere QGIS instalado:** No se puede ejecutar en servidores sin QGIS
3. **Solo Colombia:** Las capas actuales son solo para Colombia
4. **Año 2020:** Divisiones políticas hasta 2020, actualizar para años posteriores
5. **Memoria RAM:** Archivos muy grandes (> 100,000 registros) requieren 8GB+ RAM

## Mejoras Futuras

Contribuciones bienvenidas para:
- [ ] Soporte para otros países
- [ ] Validación con múltiples años de divisiones políticas
- [ ] Interfaz gráfica (GUI)
- [ ] Generación de reportes en PDF
- [ ] Visualización de puntos problemáticos en mapa

## Flujo de Trabajo Recomendado

```
1. Preparar CSV con coordenadas
   ↓
2. Ejecutar validación geográfica
   ↓
3. Revisar estadísticas
   ↓
4. Filtrar registros con valiCount=0 o valiStat=0
   ↓
5. Verificar manualmente los registros problemáticos
   ↓
6. Corregir coordenadas o documentación
   ↓
7. Re-ejecutar validación
   ↓
8. Publicar cuando valiCount ≥ 95%
```

## Referencias

- **Darwin Core:** https://dwc.tdwg.org/
- **QGIS Documentation:** https://docs.qgis.org/
- **DANE Geodatos:** https://geoportal.dane.gov.co/

## Contacto

Para preguntas técnicas o reportar problemas, contacte al autor o abra un issue en el repositorio de GitHub.
