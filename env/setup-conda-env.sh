#!/bin/bash

function check_python {
    python_version_l=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    python_version_maj=$(python -c 'import sys; print(".".join(map(str, sys.version_info[0:1])))')
    python_version_min=$(python -c 'import sys; print(".".join(map(str, sys.version_info[1:2])))')
    python_lib=$(python --version | tr '[:upper:]' '[:lower:]' | sed 's/ //g' | sed 's/\.[^.]*$//')

    min_required_maj=3
    min_required_min=6
    if [[ $(echo $python_version_maj'>='$min_required_maj | bc -l) == 1  ]]  && [[ $(echo $python_version_min'>='$min_required_min | bc -l) == 1  ]] ; then
        echo "Python version: $python_version_l"
    else
        echo -e "\e[31mPython version: $python_version_l\e[0m"
        echo -e "\e[31mPlease check your Python version >= 3.6 and make sure that the appropriate Conda env is activated.\e[0m"
        exit $1
    fi
    if [[ -d "$CONDA_PREFIX/lib/$python_lib" ]]; then
        echo "Found $python_lib within Conda environment."
    else
        echo -e "\e[31mPlease check your Python binary path and make sure that the appropriate Conda environment is activated.\e[0m"
        exit $1
    fi
}

function set_grib_definition_path {

    cosmo_eccodes=$(spack find --format "{prefix}" cosmo-eccodes-definitions@2.19.0.7%gcc | head -n1)
    if [[ -d "$cosmo_eccodes" ]]; then
        echo 'Cosmo eccodes-definitions were successfully retrieved.'
    else
        echo -e "\e[31mCosmo eccodes-definitions could not be set properly. Please check your Spack setup.\e[0m"
        exit $1
    fi

    eccodes=$(spack find --format "{prefix}" eccodes@2.19.0%gcc \~aec | head -n1)
    if [[ -d "$eccodes" ]]; then
        echo 'Eccodes definitions were successfully retrieved.'
    else
        echo -e "\e[31mEccodes retrieval failed. Please check your Spack setup.\e[0m"
        exit $1
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

elif [[ $(hostname -s) == *'nid'* ]]; then

    check_python

    if [[ -z $(command -v spack) ]]; then
        echo -e "\e[31mSpack could not be found in your PATH.\e[0m"
        echo -e "\e[31mBalfrin has no global system installation of Spack.\e[0m"
        echo -e "\e[34mFollow the instructions below to install your own Spack instance:\e[0m"
        echo -e "\e[34mhttps://github.com/C2SM/spack-c2sm/tree/dev_v0.18.1\e[0m"
        echo -e "\e[34mThen install the latest eccodes and cosmo-eccodes with Spack before re-running this script:\e[0m"
        echo -e "\e[34m$ spack install cosmo-eccodes-definitions@2.19.0.7 ^eccodes@2.19.0\e[0m"
        exit $1
    fi

    set_grib_definition_path
fi

# ---- required for fieldextra ------

if [[ $(hostname -s) == *'tsa'* ]]; then

    echo 'Setting FIELDEXTRA_PATH for tsa'
    conda env config vars set FIELDEXTRA_PATH=/project/s83c/fieldextra/tsa/bin/fieldextra_gnu_opt_omp

elif [[ $(hostname -s) == *'daint'* ]]; then

    echo 'Setting FIELDEXTRA_PATH for daint'
    conda env config vars set FIELDEXTRA_PATH=/project/s83c/fieldextra/daint/bin/fieldextra_gnu_opt_omp

elif [[ $(hostname -s) == *'nid'* ]]; then

    echo 'Setting FIELDEXTRA_PATH for balfrin'
    conda env config vars set FIELDEXTRA_PATH=/users/oprusers/osm/bin/fieldextra
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
