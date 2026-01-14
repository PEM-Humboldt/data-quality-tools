# Capas de Referencia Geográfica

Este directorio contiene los shapefiles utilizados para la validación geográfica de coordenadas.

## Capas Incluidas

### MGN_MPIO_POLITICO_2020
- **Descripción:** División política municipal de Colombia
- **Fuente:** DANE (Departamento Administrativo Nacional de Estadística)
- **Año:** 2020
- **CRS:** EPSG:4326 (WGS84)
- **Archivos:**
  - MGN_MPIO_POLITICO_2020.shp
  - MGN_MPIO_POLITICO_2020.shx
  - MGN_MPIO_POLITICO_2020.dbf
  - MGN_MPIO_POLITICO_2020.prj
  - MGN_MPIO_POLITICO_2020.cpg

**Campos principales:**
- `DPTO_CNMBR`: Nombre del departamento
- `MPIO_CNMBR`: Nombre del municipio
- `suggestedS`: Nombre sugerido del departamento (usado en validación)
- `suggestedC`: Nombre sugerido del municipio (usado en validación)

### MGN_MPIO_2020_Buffer_530m
- **Descripción:** Buffer de 530 metros sobre la división municipal
- **Fuente:** Generado a partir de MGN_MPIO_POLITICO_2020
- **Año:** 2020
- **CRS:** EPSG:4326 (WGS84)
- **Propósito:** Permite validar coordenadas con margen de error GPS

**Campos principales:**
- `BUFF_DIST`: Distancia del buffer (530 metros)
- `ORIG_FID`: ID de la característica original
- `suggestedC_2`: Nombre del municipio dentro del buffer (usado en validación)

## Uso en el Script

Estas capas se cargan automáticamente en `scripts/validacion_geografica.py`:

```python
LAYER_POLITICO = REFERENCE_DIR / "MGN_MPIO_POLITICO_2020.shp"
LAYER_BUFFER = REFERENCE_DIR / "MGN_MPIO_2020_Buffer_530m.shp"
```

## Actualización de Capas

Para usar divisiones políticas más recientes:

1. Descargue los shapefiles actualizados del DANE o fuente oficial
2. Asegúrese de que contengan los campos `DPTO_CNMBR` y `MPIO_CNMBR`
3. Renombre o cree los campos `suggestedS` y `suggestedC` si es necesario
4. Reemplace los archivos en este directorio
5. Actualice las rutas en `scripts/validacion_geografica.py` si cambió los nombres


## Licencia de Datos

Las capas de división política son datos abiertos del DANE.
