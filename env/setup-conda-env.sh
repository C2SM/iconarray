#!/bin/bash

if [[ $(hostname -s) == *'tsa'* ]]; then
    echo 'Setting GRIB_DEFINITION_PATH for cfgrib engine'
    if module load python; then
        echo '"module load python" was successful.'
    else
        echo '"module load python" was NOT successful. Please contact your system admin.'
        return $1
    fi
    source /project/g110/spack/user/admin-tsa/spack/share/spack/setup-env.sh

    if cosmo_eccodes=$(spack find --format "{prefix}" cosmo-eccodes-definitions@2.19.0.7%gcc | head -n1); then
        echo 'Cosmo eccodes-definitions were set successfully.'
    else
        echo 'Cosmo eccodes-definitions could not be set properly. Please check your Spack setup.'
        return $1
    fi

    if eccodes=$(spack find --format "{prefix}" eccodes@2.19.0%gcc \~aec | head -n1); then
        echo 'Eccodes were successfully retrieved.'
    else
        echo 'Eccodes retrieval failed. Please check your Spack setup.'
        return $1
    fi

    export GRIB_DEFINITION_PATH=${cosmo_eccodes}/cosmoDefinitions/definitions/:${eccodes}/share/eccodes/definitions/
    export OMPI_MCA_pml="ucx"
    export OMPI_MCA_osc="ucx"
    echo 'GRIB_DEFINITION_PATH: '${GRIB_DEFINITION_PATH}
    conda env config vars set GRIB_DEFINITION_PATH=${GRIB_DEFINITION_PATH}

elif [[ $(hostname -s) == *'daint'* ]]; then
    echo 'Setting GRIB_DEFINITION_PATH for cfgrib engine'
    if module load cray-python; then
        echo '"module load cray-python" was successful.'
    else
        echo '"module load cray-python" was NOT successful. Please contact your system admin.'
        return $1
    fi
    source /project/g110/spack/user/admin-daint/spack/share/spack/setup-env.sh

    if cosmo_eccodes=$(spack find --format "{prefix}" cosmo-eccodes-definitions@2.19.0.7%gcc | head -n1); then
        echo 'Cosmo eccodes-definitions were set successfully.'
    else
        echo 'Cosmo eccodes-definitions could not be set properly. Please check your Spack setup.'
        return $1
    fi

    if eccodes=$(spack find --format "{prefix}" eccodes@2.19.0%gcc \~aec | head -n1); then
        echo 'Eccodes were successfully retrieved.'
    else
        echo 'Eccodes retrieval failed. Please check your Spack setup.'
        return $1
    fi

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

if python_version=$(python --version | tr '[:upper:]' '[:lower:]' | sed 's/ //g' | sed 's/\.[^.]*$//'); then
    echo $python_version
else
    echo "Please check your Python version and make sure that the appropriate Conda env is activated."
    return $1
fi
if vpython=$(ls --color=never -d $CONDA_PREFIX/lib/$python_version); then
    echo $vpython
else
    echo "Please check your Python binary path and make sure that the appropriate Conda env is activated."
    return $1
fi
if cp env/siteconfig.py ${vpython}/site-packages/cartopy; then
    echo 'Cartopy configuration completed successfully.'
else
    echo -e 'Enable cartopy to modify cartopy.config by placing the env/siteconfig.py file into cartopy package source folder. \n' \
        'Please make sure that you are in the parent directory of the iconarray folder while executing this setup script.'
    return $1
fi

echo -e 'The setup script completed successfully! \n' \
    'Make sure to deactivate your environment completely before reactivating it by running "conda deactivate" twice.'
