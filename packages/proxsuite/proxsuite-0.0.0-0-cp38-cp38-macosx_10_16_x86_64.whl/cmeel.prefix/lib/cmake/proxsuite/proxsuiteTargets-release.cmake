#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "proxsuite::instructionset" for configuration "Release"
set_property(TARGET proxsuite::instructionset APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(proxsuite::instructionset PROPERTIES
  IMPORTED_COMMON_LANGUAGE_RUNTIME_RELEASE ""
  IMPORTED_LOCATION_RELEASE "${PACKAGE_PREFIX_DIR}/lib/python3.8/site-packages/proxsuite/instructionset.so"
  IMPORTED_NO_SONAME_RELEASE "TRUE"
  )

list(APPEND _cmake_import_check_targets proxsuite::instructionset )
list(APPEND _cmake_import_check_files_for_proxsuite::instructionset "${PACKAGE_PREFIX_DIR}/lib/python3.8/site-packages/proxsuite/instructionset.so" )

# Import target "proxsuite::proxsuite_pywrap" for configuration "Release"
set_property(TARGET proxsuite::proxsuite_pywrap APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(proxsuite::proxsuite_pywrap PROPERTIES
  IMPORTED_COMMON_LANGUAGE_RUNTIME_RELEASE ""
  IMPORTED_LOCATION_RELEASE "${PACKAGE_PREFIX_DIR}/lib/python3.8/site-packages/proxsuite/proxsuite_pywrap.so"
  IMPORTED_NO_SONAME_RELEASE "TRUE"
  )

list(APPEND _cmake_import_check_targets proxsuite::proxsuite_pywrap )
list(APPEND _cmake_import_check_files_for_proxsuite::proxsuite_pywrap "${PACKAGE_PREFIX_DIR}/lib/python3.8/site-packages/proxsuite/proxsuite_pywrap.so" )

# Import target "proxsuite::proxsuite_pywrap_avx2" for configuration "Release"
set_property(TARGET proxsuite::proxsuite_pywrap_avx2 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(proxsuite::proxsuite_pywrap_avx2 PROPERTIES
  IMPORTED_COMMON_LANGUAGE_RUNTIME_RELEASE ""
  IMPORTED_LOCATION_RELEASE "${PACKAGE_PREFIX_DIR}/lib/python3.8/site-packages/proxsuite/proxsuite_pywrap_avx2.so"
  IMPORTED_NO_SONAME_RELEASE "TRUE"
  )

list(APPEND _cmake_import_check_targets proxsuite::proxsuite_pywrap_avx2 )
list(APPEND _cmake_import_check_files_for_proxsuite::proxsuite_pywrap_avx2 "${PACKAGE_PREFIX_DIR}/lib/python3.8/site-packages/proxsuite/proxsuite_pywrap_avx2.so" )

# Import target "proxsuite::proxsuite_pywrap_avx512" for configuration "Release"
set_property(TARGET proxsuite::proxsuite_pywrap_avx512 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(proxsuite::proxsuite_pywrap_avx512 PROPERTIES
  IMPORTED_COMMON_LANGUAGE_RUNTIME_RELEASE ""
  IMPORTED_LOCATION_RELEASE "${PACKAGE_PREFIX_DIR}/lib/python3.8/site-packages/proxsuite/proxsuite_pywrap_avx512.so"
  IMPORTED_NO_SONAME_RELEASE "TRUE"
  )

list(APPEND _cmake_import_check_targets proxsuite::proxsuite_pywrap_avx512 )
list(APPEND _cmake_import_check_files_for_proxsuite::proxsuite_pywrap_avx512 "${PACKAGE_PREFIX_DIR}/lib/python3.8/site-packages/proxsuite/proxsuite_pywrap_avx512.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
