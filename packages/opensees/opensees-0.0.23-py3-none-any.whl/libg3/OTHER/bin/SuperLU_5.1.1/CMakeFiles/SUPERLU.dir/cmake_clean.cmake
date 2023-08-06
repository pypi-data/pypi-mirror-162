file(REMOVE_RECURSE
  "libSUPERLU.a"
  "libSUPERLU.pdb"
)

# Per-language clean rules from dependency scanning.
foreach(lang C)
  include(CMakeFiles/SUPERLU.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
