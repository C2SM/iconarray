#!/bin/bash

if [[ $(hostname -s) == *'tsa'* ]]; then
    echo 'Setting GRIB_DEFINITION_PATH for cfgrib engine'
    errormessage=$(module load python)
    if [ -z "$errormessage" ]; then
        echo 'EasyBuild loaded the python module successfully.'
    else
        echo 'EasyBuild was not able to load the python module.'
        return $1
    fi
    source /project/g110/spack/user/admin-tsa/spack/share/spack/setup-env.sh

    cosmo_eccodes=$(spack find --format "{prefix}" cosmo-eccodes-definitions@2.19.0.7%gcc | head -n1)
    eccodes=$(spack find --format "{prefix}" eccodes@2.19.0%gcc \~aec | head -n1)
    export GRIB_DEFINITION_PATH=${cosmo_eccodes}/cosmoDefinitions/definitions/:${eccodes}/share/eccodes/definitions/
    export OMPI_MCA_pml="ucx"
    export OMPI_MCA_osc="ucx"
    echo 'GRIB_DEFINITION_PATH: '${GRIB_DEFINITION_PATH}
    conda env config vars set GRIB_DEFINITION_PATH=${GRIB_DEFINITION_PATH}

elif [[ $(hostname -s) == *'daint'* ]]; then
    echo 'Setting GRIB_DEFINITION_PATH for cfgrib engine'
    errormessage=$(module load cray-python)
    if [ -z "$errormessage"]; then
        echo 'EasyBuild loaded the python module successfully.'
    else
        echo 'EasyBuild was not able to load the python module.'
        return $1
    fi
    source /project/g110/spack/user/admin-daint/spack/share/spack/setup-env.sh

    cosmo_eccodes=$(spack find --format "{prefix}" cosmo-eccodes-definitions@2.19.0.7%gcc | head -n1)
    eccodes=$(spack find --format "{prefix}" eccodes@2.19.0%gcc \~aec | head -n1)
    export GRIB_DEFINITION_PATH=${cosmo_eccodes}/cosmoDefinitions/definitions/:${eccodes}/share/eccodes/definitions/
    export OMPI_MCA_pml="ucx"
    export OMPI_MCA_osc="ucx"
    echo 'GRIB_DEFINITION_PATH: ' ${GRIB_DEFINITION_PATH}
    conda env config vars set GRIB_DEFINITION_PATH=${cosmo_eccodes}/cosmoDefinitions/definitions/:${eccodes}/share/eccodes/definitions/
fi

# ---- required for fieldextra ------

if [[ $(hostname -s) == *'tsa'* ]]; then

    echo 'Setting FIELDEXTRA_PATH for tsa'
    conda env config vars set FIELDEXTRA_PATH=/project/s83c/fieldextra/tsa/bin/fieldextra_gnu_opt_omp

elif [[ $(hostname -s) == *'daint'* ]]; then

    echo 'Setting FIELDEXTRA_PATH for daint'
    conda env config vars set FIELDEXTRA_PATH=/project/s83c/fieldextra/daint/bin/fieldextra_gnu_opt_omp

fi

# ---- required for cartopy ------

python_version=$(python --version | tr '[:upper:]' '[:lower:]' | sed 's/ //g' | sed 's/\.[^.]*$//')
vpython=$(ls --color=never -d $CONDA_PREFIX/lib/$python_version)
if cp env/siteconfig.py ${vpython}/site-packages/cartopy; then
    echo -e 'The setup script completed successfully! \n' \
        'Make sure to deactivate your environment completely before reactivating it by running "conda deactivate" twice.'
else
    echo -e 'Enable cartopy to modify cartopy.config by placing the env/siteconfig.py file into cartopy package source folder. \n' \
        'Please make sure that you are in the parent directory of the iconarray folder while executing this setup script.'
fi
