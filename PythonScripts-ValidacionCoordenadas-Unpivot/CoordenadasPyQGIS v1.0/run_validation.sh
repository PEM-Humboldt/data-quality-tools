#!/usr/bin/env bash
# ==============================================================
#  Script : validacion_geografica_qgis.sh
#  Proyecto: Integración de Datos (I2D)
#  Entidad : Instituto de Investigación de Recursos Biológicos
#            Alexander von Humboldt
#
#  Descripción:
#    Script wrapper para la validación de coordenadas geográficas
#    utilizando PyQGIS en entorno Linux. Configura el entorno
#    necesario para ejecutar QGIS en modo no interactivo.
#
#  Requisitos:
#    - QGIS instalado
#    - Python 3
#
#  Uso:
#    ./validacion_geografica_qgis.sh <entrada.csv> [salida.csv]
#
# ==============================================================


# ----------------------------------------------------------------
# Configuración de colores para salida en terminal
# ----------------------------------------------------------------
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'   # No Color

# ----------------------------------------------------------------
# Funciones de formato
# ----------------------------------------------------------------
print_centered() {
    local text="$1"
    local width
    width=$(tput cols)
    printf "%*s\n" $(((${#text} + width) / 2)) "$text"
}

# ----------------------------------------------------------------
# Encabezado informativo
# ----------------------------------------------------------------
echo -e "${GREEN}$(printf '=%.0s' $(seq 1 $(tput cols)))${NC}"

print_centered "I2D - Integración de Datos"
print_centered "Instituto de Investigación de Recursos Biológicos"
print_centered "Alexander von Humboldt"
echo ""
print_centered "VALIDACIÓN GEOGRÁFICA CON PyQGIS"
echo ""
print_centered "AUTOR : PASANTE 2025-2 - MICHAEL RUIZ"

echo -e "${GREEN}$(printf '=%.0s' $(seq 1 $(tput cols)))${NC}"
echo ""


# ----------------------------------------------------------------
# Verificación de dependencias
# ----------------------------------------------------------------
if ! command -v qgis &> /dev/null; then
    echo -e "${RED}ERROR: QGIS no está instalado.${NC}"
    echo "Instale QGIS con:"
    echo "  sudo apt install qgis"
    exit 1
fi

echo -e "${YELLOW}QGIS detectado:${NC}"
qgis --version
echo ""


# ----------------------------------------------------------------
# Configuración del entorno PyQGIS
# ----------------------------------------------------------------
export PYTHONPATH="/usr/share/qgis/python:/usr/share/qgis/python/plugins:/usr/lib/python3/dist-packages:$PYTHONPATH"
export LD_LIBRARY_PATH="/usr/lib:$LD_LIBRARY_PATH"
export QGIS_PREFIX_PATH="/usr"
export QT_QPA_PLATFORM=offscreen   # Ejecución sin interfaz gráfica


# ----------------------------------------------------------------
# Verificación de Python
# ----------------------------------------------------------------
PYTHON_CMD="python3"
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 no encontrado.${NC}"
    exit 1
fi

echo -e "${YELLOW}Python:${NC} $($PYTHON_CMD --version)"
echo ""


# ----------------------------------------------------------------
# Validación de argumentos
# ----------------------------------------------------------------
if [ $# -eq 0 ]; then
    echo -e "${RED}ERROR: No se proporcionó archivo de entrada.${NC}"
    echo ""
    echo "Uso:"
    echo "  $0 <archivo.csv> [salida.csv]"
    echo ""
    exit 1
fi

if [ ! -f "$1" ]; then
    echo -e "${RED}ERROR: El archivo '$1' no existe.${NC}"
    exit 1
fi

echo -e "${GREEN}Archivo de entrada:${NC} $1"
if [ $# -eq 2 ]; then
    echo -e "${GREEN}Archivo de salida:${NC}  $2"
fi
echo ""


# ----------------------------------------------------------------
# Ejecución del script principal
# ----------------------------------------------------------------
echo -e "${YELLOW}Iniciando proceso de validación...${NC}"
echo ""

$PYTHON_CMD scripts/Validacion_qgis.py "$@"
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}--------------------------------------------------${NC}"
    echo -e "${GREEN}Proceso finalizado correctamente.${NC}"
    echo -e "${GREEN}--------------------------------------------------${NC}"
else
    echo -e "${RED}--------------------------------------------------${NC}"
    echo -e "${RED}El proceso finalizó con errores (código: $EXIT_CODE).${NC}"
    echo -e "${RED}--------------------------------------------------${NC}"
fi

exit $EXIT_CODE

