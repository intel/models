#!/bin/bash

#set -x

BASE_REF=${BASE_REF:-"r3.4"}
NEW_RELEASE_REF=${NEW_RELEASE_REF:-"r3.4.1"}
AIRM_ROOT="../../"
FILE_TYPES=("requirements.txt" "poetry.lock")
ONE_BOM_DIR="$(pwd)"
UPDATED_3PC="updated"
NEW_3PC="new"
UPDATED_3PC_DIR="${ONE_BOM_DIR}/${UPDATED_3PC}_components"
NEW_3PC_DIR="${ONE_BOM_DIR}/${NEW_3PC}_components"
UNIQUE_COMPONENTS_CSV="unique_new_component_versions.csv"
UNIQUE_COMPONENT_PURLS_CSV="unique_new_component_purls.csv"
NEW_3PC_VERSIONS=("Component Name,Version")
IT_REQUEST_CSV="IT-request.csv"
echo "name,version_external,pURL" > "${IT_REQUEST_CSV}"

IT_PURL_LIST_CSV="existing-purls.csv"
NEW_3PC_REQUEST_PURLS="new-3pc-request-purls.csv"

collect_csv_files() {
  local pattern=${1}
  local target_dir=${2}
  echo "UPdated components can be found in ${target_dir}. "
  rm -rf ${target_dir}
  mkdir -p "${target_dir}"

  for i in $(find . -name "*${pattern}.csv") 
  do
    flat_name=$(echo ${i:2} | tr '/' '-')
    echo "${flat_name}"
    mv $i "${target_dir}/${flat_name}"
  done
  ls -la "${target_dir}"

}

find-airm-root() {
  # Start from the current directory
  current_dir=${ONE_BOM_DIR}

  # Traverse up the directory tree to find the .github directory
  while [ "$current_dir" != "/" ]; do
    if [ -d "$current_dir/.github" ]; then
      # Change to the parent directory of .github
      AIRM_ROOT="$current_dir"
      break
    fi
      # Move up one directory
      current_dir=$(dirname "$current_dir")
  done

  if [ "$current_dir" == "/" ]
  then
    echo ".github directory not found in the current path."
  fi
}

parse_changes(){
  echo $1
  echo "$1"
  local awk_ret="${1}"
  local csv_file="${2}"
  local lines=()
  if [[ "${awk_ret}" != "" ]]
  then
    echo "AWK_RET: ${awk_ret}"
    IFS=$'\n' read -r -d '' -a lines <<< "${awk_ret}"
    for line in "${lines[@]}"
    do 
      echo "LINE: ${line}"
      echo "${line}" >> "${i}.${csv_file}.csv"
      NEW_3PC_VERSIONS+=("${line}")
    done
  fi

}

# I'm not going to add the "removed 3PC use case because it 
# is not valid any more

get-new-3PCs() {
  local file_type="${FILE_TYPES[$1]}"
  pushd $AIRM_ROOT
  echo "Get $file_type differences from $(pwd)"
  local awk_ret=""

  for i in $(git diff ${BASE_REF} ${NEW_RELEASE_REF} --name-only **/"${file_type}")
    do 
      echo "Changes in ${i}:"
      new_file=$(git diff "${BASE_REF}" "${NEW_RELEASE_REF}" -- "${i}" | grep "new file mode 100644")
      if [[ "${new_file}" == "new file mode 100644" ]] ;
      then
        echo "$i is a new file"
        continue
      fi
      deleted_file=$(git diff "${BASE_REF}" "${NEW_RELEASE_REF}" -- "${i}" | grep "deleted file mode 100644")
      if [[ "${deleted_file}" == "deleted file mode 100644" ]] ;
      then
        echo "$i was deleted"
        continue
      fi
      
      echo "Format ${i} output as CSV"
      if [[ "$1" == "0" ]] ; 
      then
        echo "Not Implemented"
      elif [[ "$1" == "1" ]] ; 
      then
        # This will give us the components with new versions

        git diff r3.4 r3.4.1 -- ${i} | grep "+version = " -B3 > "${i}.versions.debug.log"
        awk_ret=$(cat "${i}.versions.debug.log" | awk '
          BEGIN { name = ""; new_version = ""; }
          {
              if ($0 ~ /^ name = /) {
                  match($0, /"([^"]+)"/, arr);
                  name = arr[1];
              }
              if ($0 ~ /^\+version = /) {
                  match($0, /\+version = "([^"]+)"/, arr);
                  new_version = arr[1];
                  if (name != "" && new_version != "") {
                      print name "_pypi," new_version;
                      name = ""; new_version = "";  # Reset for next package
                  }
              }
          }
          ')
        echo "Create ${i}.${UPDATED_3PC}.csv"
        echo "Package Name,Version" > "${i}.${UPDATED_3PC}.csv"
        parse_changes "${awk_ret}" "${UPDATED_3PC}"

        awk_ret=""
        git diff r3.4 r3.4.1 -- ${i} | grep "+\[\[package\]\]" -A2 > "${i}.new.debug.log"
        awk_ret=$(cat "${i}.new.debug.log" | awk '
          BEGIN { name = ""; version = ""; }
          {
              if ($0 ~ /^\+name = /) {
                  match($0, /"([^"]+)"/, arr);
                  name = arr[1];
              }
              if ($0 ~ /^\+version = /) {
                  match($0, /\+version = "([^"]+)"/, arr);
                  version = arr[1];
                  if (name != "" && version != "") {
                      print name "_pypi," version;
                      name = ""; version = "";  # Reset for next package
                  }
              }
          }
          ')
        # This will give us the new components
        echo "Create ${i}.${NEW_3PC}.csv"
        echo "Package Name,Version" > "${i}.${NEW_3PC}.csv"
        parse_changes "${awk_ret}" "${NEW_3PC}"

      else
        echo "Invalid File Type index"
        exit -1
      fi
    done

  collect_csv_files ${UPDATED_3PC} ${UPDATED_3PC_DIR}
  collect_csv_files ${NEW_3PC} ${NEW_3PC_DIR}

  for j in "${NEW_3PC_VERSIONS[@]}" ;
  do
    echo "J = $j"
  done
  popd

}


find-airm-root

#get-new-3PC-versions 0

get-new-3PCs 1
# turn the new_elements array into a set
declare -A new_3pc_set
for element in "${NEW_3PC_VERSIONS[@]}"
do
  echo "Element = ${element}"
  new_3pc_set["${element}"]="1"
done

#output the set to the unique new elements file
echo "Component Name,Version,pURL" > ${UNIQUE_COMPONENTS_CSV}
rm -f ${UNIQUE_COMPONENT_PURLS_CSV}
sorted_keys=($(printf "%s\n" "${!new_3pc_set[@]}" | sort))
for key in "${sorted_keys[@]}"
do
  echo "Unique Element=${key}"

  pURL=$(echo "pkg:pypi/$key" | tr ',' '@')
  echo "${key},${pURL}" >> "${UNIQUE_COMPONENTS_CSV}"
  echo "${pURL}" >> "${UNIQUE_COMPONENT_PURLS_CSV}"
done


# compare with the existing 3PCs in IPX and include only the ones that aren't already there
sort "${UNIQUE_COMPONENT_PURLS_CSV}" > "sorted-${UNIQUE_COMPONENT_PURLS_CSV}"
sort "${IT_PURL_LIST_CSV}" > "sorted-${IT_PURL_LIST_CSV}"

comm -13 "sorted-${IT_PURL_LIST_CSV}" "sorted-${UNIQUE_COMPONENT_PURLS_CSV}" > "${NEW_3PC_REQUEST_PURLS}"
cat "${NEW_3PC_REQUEST_PURLS}"

# now walk through the list of unique components and remove the lines that dont exist in the request PURLs
mapfile -t new_purls < "${NEW_3PC_REQUEST_PURLS}"
for purl in "${new_purls[@]}"; 
do 
  ret_val=$(cat ${UNIQUE_COMPONENTS_CSV} | grep "${purl}")
  echo "${ret_val}"
  if [[ "${ret_val}" == *"${purl}" ]] 
  then
    echo "${ret_val}" >> "${IT_REQUEST_CSV}"
  fi
done