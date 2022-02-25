from utils import shell_cmd, file_exists, co_flag, plotting


def test_timeseries():
    plot_name = 'timeseries'

    # Check if co flag is working
    co_flag(plot_name)

    # Check if plotting works
    config_files = ['config_all_opt', 'config_no_opt', 'config_coord']
    input_files = ['my_exp1_atm_3d_ml_20180921T000000Z']
    plotting(plot_name, config_files, input_files)
