#!/usr/bin/env bash
set -euo pipefail

PLUGIN_NAME="ICRA"
BUILD_DIR="build"
PACKAGE_DIR="${BUILD_DIR}/${PLUGIN_NAME}"
ZIP_FILE="${BUILD_DIR}/${PLUGIN_NAME}.zip"
QGIS_PLUGIN_DIR="/mnt/c/Users/jpueyo/AppData/Roaming/QGIS/QGIS4/profiles/default/python/plugins/${PLUGIN_NAME}"

echo "==> Cleaning build"
rm -rf "${BUILD_DIR}"
mkdir -p "${PACKAGE_DIR}"

echo "==> Copying plugin files"

cp ICRA.py "${PACKAGE_DIR}/"
cp ICRA_provider.py "${PACKAGE_DIR}/"
cp README.md "${PACKAGE_DIR}/"
cp __init__.py "${PACKAGE_DIR}/"
cp metadata.txt "${PACKAGE_DIR}/"
cp LICENSE "${PACKAGE_DIR}"

mkdir -p "${PACKAGE_DIR}/algs"
mkdir -p "${PACKAGE_DIR}/algs/utils"
mkdir -p "${PACKAGE_DIR}/algs/dataset"
mkdir -p "${PACKAGE_DIR}/algs/tests"
mkdir -p "${PACKAGE_DIR}/icons"

cp algs/buildings2sewertAlgorithm.py "${PACKAGE_DIR}/algs/"
cp algs/utils/check_extent.py "${PACKAGE_DIR}/algs/utils/"
cp algs/utils/z_sampling.py "${PACKAGE_DIR}/algs/utils/"
cp algs/tests/test_building2sewer.py "${PACKAGE_DIR}/algs/tests/"

cp algs/dataset/buildings2sewer.gpkg "${PACKAGE_DIR}/algs/dataset/"
cp algs/dataset/dem.tif "${PACKAGE_DIR}/algs/dataset/"
cp algs/dataset/dem.tif.aux.xml "${PACKAGE_DIR}/algs/dataset/"

cp icons/buildings2sewer.png "${PACKAGE_DIR}/icons/"
cp icons/icra_icon.png "${PACKAGE_DIR}/icons/"

echo "==> Package tree"
tree "${PACKAGE_DIR}" || find "${PACKAGE_DIR}" -print

echo "==> Creating zip"
rm -f "${ZIP_FILE}"
(
  cd "${BUILD_DIR}"
  zip -r "${PLUGIN_NAME}.zip" "${PLUGIN_NAME}"
)

echo "==> Deploying to local QGIS plugins dir"
rm -rf "${QGIS_PLUGIN_DIR}"
mkdir -p "$(dirname "${QGIS_PLUGIN_DIR}")"
cp -r "${PACKAGE_DIR}" "${QGIS_PLUGIN_DIR}"

echo "==> Done"
echo "Local plugin: ${QGIS_PLUGIN_DIR}"
echo "Zip package:  ${ZIP_FILE}"