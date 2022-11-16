#!/bin/bash

function check_python {
    python_version=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    python_version_l=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    python_lib=$(python --version | tr '[:upper:]' '[:lower:]' | sed 's/ //g' | sed 's/\.[^.]*$//')
    min_required_version=3.5
    if [ $(echo $python_version'>'$min_required_version | bc -l) == 1 ]; then
        echo "Python version: $python_version_l"
    else
        echo -e "\e[31mPython version: $python_version_l\e[0m"
        echo -e "\e[31mPlease check your Python version >= 3.6 and make sure that the appropriate Conda env is activated.\e[0m"
        exit $1
    fi
    if [ -d "$CONDA_PREFIX/lib/$python_lib" ]; then
        echo "Found $python_lib within Conda environment."
    else
        echo -e "\e[31mPlease check your Python binary path and make sure that the appropriate Conda environment is activated.\e[0m"
        exit $1
    fi
}

function set_grib_definition_path {

    if cosmo_eccodes=$(spack find --format "{prefix}" cosmo-eccodes-definitions@2.19.0.7%gcc | head -n1); then
        echo 'Cosmo eccodes-definitions were successfully retrieved.'
    else
        echo -e "\e[31mCosmo eccodes-definitions could not be set properly. Please check your Spack setup.\e[0m"
        return $1
    fi

    if eccodes=$(spack find --format "{prefix}" eccodes@2.19.0%gcc \~aec | head -n1); then
        echo 'Eccodes definitions were successfully retrieved.'
    else
        echo -e "\e[31mEccodes retrieval failed. Please check your Spack setup.\e[0m"
        return $1
    fi

    export GRIB_DEFINITION_PATH=${cosmo_eccodes}/cosmoDefinitions/definitions/:${eccodes}/share/eccodes/definitions/
    export OMPI_MCA_pml="ucx"
    export OMPI_MCA_osc="ucx"
    conda env config vars set GRIB_DEFINITION_PATH=${cosmo_eccodes}/cosmoDefinitions/definitions/:${eccodes}/share/eccodes/definitions/
}


if [[ $(hostname -s) == *'tsa'* ]]; then

    check_python
    source /project/g110/spack/user/admin-tsa/spack/share/spack/setup-env.sh
    set_grib_definition_path

elif [[ $(hostname -s) == *'daint'* ]]; then

    check_python
    source /project/g110/spack/user/admin-daint/spack/share/spack/setup-env.sh
    set_grib_definition_path
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

if cp env/siteconfig.py $CONDA_PREFIX/lib/$python_lib/site-packages/cartopy; then
    echo 'Cartopy configuration completed successfully.'
else
    echo -e "\e[31mEnable cartopy to modify cartopy.config by placing the env/siteconfig.py file into cartopy package source folder.\n\e[0m"\
        "\e[31mPlease make sure that you are in the parent directory of the iconarray folder while executing this setup script.\e[0m"
    exit $1
fi

echo -e "\n "\
 "Variables saved to environment: \n "\
 " "

conda env config vars list

echo -e "\n "\
    "\e[32mThe setup script completed successfully! \n \e[0m" \
    "\e[32mMake sure to deactivate your environment completely before reactivating it by running conda deactivate twice: \n \e[0m" \
    "\n "\
    "\e[32m            conda deactivate  \n \e[0m"\
    " "

