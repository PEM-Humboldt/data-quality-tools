#!/usr/bin/env python3
"""
Script de Validación Geográfica con PyQGIS
Automatiza el proceso de validación de coordenadas usando capas de referencia
"""

import sys
from pathlib import Path

# ============================================================================
# IMPORTACIÓN DE QGIS
# ============================================================================
# PyQGIS requiere importar el entorno de QGIS antes de importar sus módulos
from qgis.core import (
    QgsApplication,           # Aplicación principal de QGIS
    QgsVectorLayer,          # Para manejar capas vectoriales (shapefiles, CSV)
    QgsProject,              # Maneja el proyecto QGIS
    QgsCoordinateReferenceSystem,  # Sistema de coordenadas
    QgsVectorFileWriter,     # Para exportar capas a archivos
    QgsField,                # Para definir campos en tablas
    QgsProcessing,           # Motor de procesamiento
    QgsProcessingFeedback    # Para logs del procesamiento
)

from qgis.analysis import QgsNativeAlgorithms  # Algoritmos nativos de QGIS
from PyQt5.QtCore import QVariant  # Tipos de datos para campos

import processing  # Motor de procesamiento de QGIS

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================
class Config:
    """Configuración centralizada de rutas y parámetros"""
    
    # Rutas base
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    REFERENCE_DIR = DATA_DIR / "reference"
    INPUT_DIR = DATA_DIR / "input"
    OUTPUT_DIR = DATA_DIR / "output"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Capas de referencia (shapefiles)
    LAYER_POLITICO = REFERENCE_DIR / "MGN_MPIO_POLITICO_2020.shp"
    LAYER_BUFFER = REFERENCE_DIR / "MGN_MPIO_2020_Buffer_530m.shp"
    
    # Sistema de coordenadas (WGS84)
    CRS_EPSG = "EPSG:4326"
    
    # Nombres de campos en el CSV de entrada
    FIELD_LONGITUDE = "decimalLongitude"
    FIELD_LATITUDE = "decimalLatitude"
    FIELD_COUNTY = "county"
    FIELD_STATE = "stateProvince"
    
    @classmethod
    def create_directories(cls):
        """Crea los directorios necesarios si no existen"""
        for directory in [cls.OUTPUT_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# ============================================================================
# CLASE PRINCIPAL: VALIDADOR GEOGRÁFICO
# ============================================================================
class ValidadorGeografico:
    """
    Automatiza el proceso de validación geográfica de coordenadas
    
    Flujo del proceso:
    1. Inicializa QGIS (sin interfaz gráfica - modo headless)
    2. Carga el CSV con coordenadas
    3. Convierte coordenadas en geometrías de puntos
    4. Hace spatial join con capa de municipios políticos
    5. Hace spatial join con capa de buffer 530m
    6. Calcula las 3 validaciones (valiCount, valiStat, valiBuffer)
    7. Exporta el resultado a CSV
    """
    
    def __init__(self, csv_input_path: str, csv_output_path: str = None):
        """
        Inicializa el validador
        
        Args:
            csv_input_path: Ruta al CSV con coordenadas a validar
            csv_output_path: Ruta donde guardar el resultado (opcional)
        """
        self.csv_input_path = Path(csv_input_path)
        self.csv_output_path = Path(csv_output_path) if csv_output_path else None
        
        # Si no se especifica output, genera nombre automático
        if not self.csv_output_path:
            output_name = f"{self.csv_input_path.stem}_validado.csv"
            self.csv_output_path = Config.OUTPUT_DIR / output_name
        
        # Variables para las capas que crearemos
        self.capa_puntos = None
        self.capa_join1 = None
        self.capa_join2 = None
        self.capa_final = None
        
       
        print(f"> Archivo de entrada: {self.csv_input_path}")
        print(f"> Archivo de salida: {self.csv_output_path}")
    
    
    def inicializar_qgis(self):
        """
        PASO 1: Inicializa QGIS en modo headless (sin interfaz gráfica)
        
        Este método prepara el entorno de QGIS para ejecutar operaciones
    	de procesamiento espacial sin requerir interfaz gráfica. Configura
    	la aplicación base y registra los algoritmos nativos necesarios
    	para operaciones de spatial join y cálculos de campos.
        
        Explicación:
        - QgsApplication.setPrefixPath(): Le dice a QGIS dónde están sus recursos
        - initQgis(): Inicializa todo el sistema de QGIS
        - QgsApplication.processingRegistry(): Registra los algoritmos de procesamiento
        """
        print("\n[INFO]: INICIALIZANDO QGIS...")
        
        # Crear aplicación QGIS ([] = sin argumentos de línea de comandos)
        self.qgs = QgsApplication([], False)
        
        # Inicializar QGIS
        self.qgs.initQgis()
        
        # Registrar los algoritmos de procesamiento nativos
        # Esto es necesario para poder usar processing.run()
        self.qgs.processingRegistry().addProvider(QgsNativeAlgorithms())
        
        print("[OK]: QGIS INICIALIZADO CORRECTAMENTE")
    
    
    def cargar_capa_csv(self):
        """
        PASO 2:  Carga el CSV como una capa vectorial de puntos en memoria.
        
    
    	Construye un URI especial que especifica:
    	
        - Ubicación del archivo CSV
        - Delimitador (coma)
        - Campos de coordenadas X (longitud) e Y (latitud)
        - Sistema de referencia de coordenadas (CRS)
    
        
        - QgsVectorLayer crea la capa en memoria
        - isValid() verifica que se cargó correctamente
        
        
        """
        print("\n[INFO]: CARGANDO CSV Y CREANDO CAPA DE PUNTOS")
        
        # Construir URI para la capa delimitada
        # Formato: file:///path?delimiter=,&xField=lon&yField=lat&crs=EPSG:4326
        uri = (
            f"file:///{self.csv_input_path.absolute()}?"
            f"delimiter=,&"
            f"xField={Config.FIELD_LONGITUDE}&"
            f"yField={Config.FIELD_LATITUDE}&"
            f"crs={Config.CRS_EPSG}"
        )
        
        # Crear la capa vectorial
        self.capa_puntos = QgsVectorLayer(uri, "puntos_csv", "delimitedtext")
        
        # Verificar que se cargó correctamente
        if not self.capa_puntos.isValid():
            raise Exception("[ERROR]: NO SE PUDO CARGAR EL CSV COMO CAPA DE PUNTOS [Verifique campos DwC de las coordenadas]")
        
        num_features = self.capa_puntos.featureCount()
        print(f"[OK]: CAPA CREADA > {num_features} registros")
        
        return self.capa_puntos
    
    
    def spatial_join(self, capa_input, capa_join, nombre_output, prefijo=""):
        """
        PASO 3 y 4: Realiza un spatial join (unión espacial)
        
        Explicación:
        - Un spatial join une dos capas basándose en su relación espacial
        - En este caso: "¿En qué polígono (municipio) cae cada punto?"
        - processing.run() ejecuta algoritmos de QGIS desde Python
        
        Parámetros del algoritmo 'native:joinattributesbylocation':
        - INPUT: Capa de puntos
        - JOIN: Capa de polígonos (municipios)
        - PREDICATE: [0] = 'intersects' (el punto intersecta el polígono)
        - JOIN_FIELDS: [] = copiar TODOS los campos del polígono al punto
        - METHOD: 0 = "crear features separadas" (one-to-one join)
        - PREFIX: prefijo para los campos copiados
        - OUTPUT: 'TEMPORARY_OUTPUT' = capa temporal en memoria
        
        Args:
            capa_input: Capa con los puntos
            capa_join: Capa con la que hacer el join (municipios o buffer)
            nombre_output: Nombre para la capa resultante
            prefijo: Prefijo para los campos unidos
        
        Returns:
            Capa resultante del join
        """
        print(f"\n[INFO]: REALIZANDO SPATIAL JOIN CON {nombre_output}...")
        
        # Cargar la capa de referencia (shapefile)
        capa_referencia = QgsVectorLayer(str(capa_join), nombre_output, "ogr")
        
        if not capa_referencia.isValid():
            raise Exception(f"[ERROR]: NO SE PUDO CARGAR {capa_join}")
        
        # Ejecutar el algoritmo de join espacial
        resultado = processing.run("native:joinattributesbylocation", {
            'INPUT': capa_input,                    # Capa de entrada (puntos)
            'JOIN': capa_referencia,                # Capa para unir (polígonos)
            'PREDICATE': [0],                       # 0 = intersects
            'JOIN_FIELDS': [],                      # [] = todos los campos
            'METHOD': 0,                            # 0 = one-to-one
            'DISCARD_NONMATCHING': False,           # Mantener puntos sin match
            'PREFIX': prefijo,                      # Prefijo para campos
            'OUTPUT': 'TEMPORARY_OUTPUT'            # Salida temporal
        })
        
        # Obtener la capa resultante
        capa_resultado = resultado['OUTPUT']
        num_features = capa_resultado.featureCount()
        
        print(f"[OK]: JOIN COMPLETADO > {num_features} registros")
        
        return capa_resultado
    
    
    def calcular_validaciones(self, capa):
        """
        PASO 5: Calcula los 3 campos de validación
        
        Explicación:
        - Agregamos 3 nuevos campos a la capa (tipo entero: 0 o 1)
        - Usamos la calculadora de campos de QGIS
        - Las expresiones son equivalentes a las que usabas manualmente
        
        Lógica de validación:
        - valiCount: ¿El campo 'county' coincide con 'suggestedC'?
        - valiStat: ¿El campo 'stateProvince' coincide con 'suggestedS'?  
        - valiBuffer: ¿El campo 'county' coincide con 'suggestedC_2'?
        
        Nota: Si el campo original es NULL, el resultado es NULL (no 0)
        
        Args:
            capa: Capa con los datos unidos
        
        Returns:
            Capa con los campos de validación agregados
        """
        print("\n[INFO]: CALCULANDO CAMPOS DE VALIDACIÓN")
        
        # Definir los 3 nuevos campos
        campos_validacion = [
            ('valiCount', f'CASE WHEN "{Config.FIELD_COUNTY}" IS NULL THEN NULL '
                         f'WHEN "{Config.FIELD_COUNTY}" = "suggestedC" THEN 1 ELSE 0 END'),
            
            ('valiStat', f'CASE WHEN "{Config.FIELD_STATE}" IS NULL THEN NULL '
                        f'WHEN "{Config.FIELD_STATE}" = "suggestedS" THEN 1 ELSE 0 END'),
            
            ('valiBuffer', f'CASE WHEN "{Config.FIELD_COUNTY}" IS NULL THEN NULL '
                          f'WHEN "{Config.FIELD_COUNTY}" = "suggestedC_2" THEN 1 ELSE 0 END')
        ]
        
        # Agregar cada campo usando la calculadora de campos
        for nombre_campo, expresion in campos_validacion:
            print(f"  > CALCULANDO {nombre_campo}...")
            
            resultado = processing.run("native:fieldcalculator", {
                'INPUT': capa,
                'FIELD_NAME': nombre_campo,
                'FIELD_TYPE': 1,                    # 1 = Integer
                'FIELD_LENGTH': 1,
                'FORMULA': expresion,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            
            capa = resultado['OUTPUT']
        
        print("[OK]: CAMPOS DE VALIDACIÓN CALCULADOS")
        
        return capa
    
    
    def exportar_a_csv(self, capa, ruta_salida):
        """
        PASO 6: Exporta la capa final a CSV
        
        Explicación:
        - QgsVectorFileWriter.writeAsVectorFormat() convierte cualquier capa a archivo
        - Especificamos formato CSV y encoding UTF-8
        
        Args:
            capa: Capa a exportar
            ruta_salida: Ruta donde guardar el CSV
        """
        print(f"\n[INFO]: EXPORTANDO RESULTADOS A CSV")
        
        # Escribir el archivo usando la API más simple y compatible
        error = QgsVectorFileWriter.writeAsVectorFormat(
            capa,
            str(ruta_salida),
            "UTF-8",
            capa.crs(),  # Usar el CRS de la capa
            "CSV"
        )
        
        # En QGIS 3.34, writeAsVectorFormat devuelve una tupla (error_code, error_message)
        error_code = error[0] if isinstance(error, tuple) else error
        
        if error_code == QgsVectorFileWriter.NoError:
            print(f"[OK]: ARCHIVO EXPORTADO EXITOSAMENTE: {ruta_salida}")
        else:
            error_msg = error[1] if isinstance(error, tuple) else str(error)
            raise Exception(f"[ERROR]: Al exportar CSV: código {error_code}, mensaje: {error_msg}")
    
    
    def ejecutar_validacion(self):
        """
        ORQUESTADOR: Ejecuta todo el proceso de validación
        
        Este es el método principal que coordina todos los pasos
        """
        try:
            # PASO 1: Inicializar QGIS
            self.inicializar_qgis()
            
            # PASO 2: Cargar CSV como capa de puntos
            self.capa_puntos = self.cargar_capa_csv()
            
            # PASO 3: Primer spatial join con MGN_MPIO_POLITICO
            self.capa_join1 = self.spatial_join(
                self.capa_puntos,     ## CAPA INPUT ###
                Config.LAYER_POLITICO,## CAPA JOIN ##
                "MGN_MPIO_POLITICO_2020",  ## Nombre output ##
                prefijo=""      ## Prefijo ###
            )
            
            # PASO 4: Segundo spatial join con MGN_MPIO_Buffer_530m
            self.capa_join2 = self.spatial_join(
                self.capa_join1,
                Config.LAYER_BUFFER,
                "MGN_MPIO_2020_Buffer_530m",
                prefijo=""
            )
            
            # PASO 5: Calcular campos de validación
            self.capa_final = self.calcular_validaciones(self.capa_join2)
            
            # PASO 6: Exportar resultado a CSV
            self.exportar_a_csv(self.capa_final, self.csv_output_path)
            
            print("\n" + "="*60)
            print("[OK]: VALIDACIÓN COMPLETADA EXITOSAMENTE")
            print("="*60)
            
            # Mostrar estadísticas básicas
            self.mostrar_estadisticas()
            
        except Exception as e:
            print(f"\n[ERROR]: {str(e)}")
            raise
        
        finally:
            # Siempre cerrar QGIS al terminar
            self.cerrar_qgis()
    
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas básicas de la validación"""
        if not self.capa_final:
            return
        
        print("\n[INFO]: ESTADÍSTICAS DE VALIDACIÓN:")
        print(f" > Total de registros: {self.capa_final.featureCount()}")
        
        # Contar validaciones exitosas
        campos = ['valiCount', 'valiStat', 'valiBuffer']
        for campo in campos:
            idx = self.capa_final.fields().indexFromName(campo)
            if idx >= 0:
                exitosos = sum(1 for f in self.capa_final.getFeatures() 
                             if f[campo] == 1)
                total = self.capa_final.featureCount()
                porcentaje = (exitosos / total * 100) if total > 0 else 0
                print(f"  > {campo}: {exitosos}/{total} ({porcentaje:.1f}% válidos)")
    
    
    def cerrar_qgis(self):
        """Cierra QGIS y libera recursos"""
        print("\n[INFO]: Cerrando QGIS")
        self.qgs.exitQgis()


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def main():
    """Punto de entrada del script"""
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("[ERROR]: Debes proporcionar la ruta del archivo CSV")
        print("\nUso:")
        print(f"  python {sys.argv[0]} <archivo.csv> [salida.csv]")
        print("\nEjemplo:")
        print(f"  python {sys.argv[0]} data/input/coordenadas.csv")
        sys.exit(1)
    
    # Obtener rutas de los argumentos
    csv_input = sys.argv[1]
    csv_output = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Crear directorios necesarios
    Config.create_directories()
    
    # Ejecutar validación
    validador = ValidadorGeografico(csv_input, csv_output)
    validador.ejecutar_validacion()


if __name__ == "__main__":
    main()
