# Herramientas de Calidad de Datos - IAvH

**Python 3.8+ | Licencia MIT | QGIS 3.34+**

Conjunto de scripts Python para validación y reorganización de datos de biodiversidad bajo el estándar Darwin Core (DwC), desarrollados durante la pasantía código 25-167 en el Instituto de Investigación de Recursos Biológicos Alexander von Humboldt.

## Descripción

Este repositorio contiene dos herramientas principales:

### 1. **Unpivot de Extensiones DwC** 
Script para reorganizar extensiones de mediciones (measurementType, measurementUnit, measurementValue) desde formato wide (múltiples columnas) a formato long (normalizado), facilitando el procesamiento y validación de datos de biodiversidad.

### 2. **Validación Geográfica con PyQGIS**
Sistema automatizado de validación de coordenadas geográficas mediante spatial joins con capas de referencia oficiales (municipios políticos y buffer de 530m), implementado con PyQGIS en modo headless.

---

## Inicio Rápido

### Unpivot de Extensiones
```bash
cd unpivot
python unpivot.py
```

### Validación Geográfica
```bash
cd "CoordenadasPyQGIS v1.0"
./run_validation.sh data/input/tu_archivo.csv
```

---

## Instalación

### Requisitos Generales
- Python 3.8+
- Entorno con PyQGIS configurado

### Unpivot
```bash
pip install pandas numpy
```

### Validación Geográfica
**Requisitos adicionales:**
- QGIS 3.34+ instalado
- PyQGIS configurado
- Capas de referencia (incluidas en `data/reference/`)

**Instalación de QGIS en Ubuntu:**
```bash
sudo apt update
sudo apt install qgis python3-qgis
```

Consulte la [Guía de Validación Geográfica](docs/validacion_geografica_guide.md) para configuración detallada del script ubicado en `CoordenadasPyQGIS v1.0/`.

---

## Documentación

- [Guía de Unpivot](docs/unpivot_guide.md) - Uso detallado del script de reorganización
- [Guía de Validación Geográfica](docs/validacion_geografica_guide.md) - Configuración y uso del validador




## Uso

### Unpivot de Extensiones DwC

**Entrada:** CSV con extensiones en formato wide
```csv
occurrenceID,measurementType1,measurementUnit1,measurementValue1,measurementType2,...
1,Altura,cm,150,Peso,...
```

**Salida:** CSV normalizado en formato long
```csv
occurrenceID,measurementType,measurementUnit,measurementValue
1,Altura,cm,150
1,Peso,kg,65
```

**Ejecución:**
```bash
cd unpivot
# Editar ruta del archivo en unpivot.py (línea 32)
python unpivot.py
```

### Validación Geográfica

**Entrada:** CSV con coordenadas DwC
```csv
occurrenceID,decimalLongitude,decimalLatitude,county,stateProvince
1,-74.0,4.6,Bogotá,Cundinamarca
```

**Salida:** CSV con campos de validación
```csv
occurrenceID,decimalLongitude,decimalLatitude,county,stateProvince,suggestedC,suggestedS,valiCount,valiStat,valiBuffer
1,-74.0,4.6,Bogotá,Cundinamarca,Bogotá,Cundinamarca,1,1,1
```

**Ejecución:**
```bash
cd "CoordenadasPyQGIS v1.0"
./run_validation.sh data/input/coordenadas.csv
# Resultado en: data/output/coordenadas_validado.csv
```

---

## Campos de Validación

| Campo | Descripción | Valores |
|-------|-------------|---------|
| `valiCount` | Coincidencia con municipio político | 1 = válido, 0 = inválido, NULL = no documentado |
| `valiStat` | Coincidencia con departamento | 1 = válido, 0 = inválido, NULL = no documentado |
| `valiBuffer` | Coincidencia dentro de buffer 530m | 1 = válido, 0 = inválido, NULL = no documentado |

---

## Capas de Referencia

Las capas geográficas utilizadas se encuentran en `CoordenadasPyQGIS v1.0/data/reference/`:

- **MGN_MPIO_POLITICO_2020.shp** - División política municipal de Colombia (DANE 2020)
- **MGN_MPIO_2020_Buffer_530m.shp** - Buffer de 530m sobre municipios

**Nota:** Las capas actuales son del año 2020. Para divisiones políticas más recientes, actualice los shapefiles en la carpeta `data/reference/` y ajuste las rutas en `scripts/validacion_geografica.py` (clase Config, líneas 49-50).


---

## Cómo Citar

Si utiliza estas herramientas en su investigación, por favor cite:

```
Ruiz Cortés, M. D. (2025). Herramientas de Calidad de Datos - Validación y 
Reorganización de Datos Darwin Core. Pasantía código 25-167. Instituto de 
Investigación de Recursos Biológicos Alexander von Humboldt. 
https://github.com/PEM-Humboldt/data-quality-tools
```

---

## Licencia

Este proyecto está bajo la Licencia MIT - consulte el archivo [LICENSE](LICENSE) para más detalles.

---

## Autor

**Michael David Ruiz Cortés**  
Pasantía código 25-167  
Instituto de Investigación de Recursos Biológicos Alexander von Humboldt

---

## Institución

[Instituto de Investigación de Recursos Biológicos Alexander von Humboldt](http://www.humboldt.org.co/)

Línea de Integración de Datos

---

## Notas Importantes

- **Unpivot:** Revise el archivo antes de ejecutar. Ajuste los nombres de columnas si difieren del estándar DwC.
- **Validación Geográfica:** Requiere pyQGIS instalado. Compatible con WSL 
- **Capas de Referencia:** Actualice los shapefiles si necesita divisiones políticas posteriores a 2020.
