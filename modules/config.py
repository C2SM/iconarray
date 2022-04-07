# Load modules
import configparser
import sys
from pathlib import Path
import numpy as np


def get_several_input(config, sect, opt, f=False, i=False):
    var = config.get(sect, opt)
    var = var.replace(', ', ',')
    var = var.split(',')
    if f:
        var = list(map(float, var))
    if i:
        var = list(map(int, var))
    return var


def read_config(config_path):
    # Check if config_path is a file
    configPath = Path(config_path)
    if not configPath.is_file():
        sys.exit(config_path + ' is not a file')

    # Check if config_path is a config file
    config = configparser.ConfigParser(inline_comment_prefixes='#')
    try:
        config.read(config_path)
    except Exception as e:
        sys.exit("Please provide a valid config file")

    # Read information regarding the variable
    var = {}
    if config.has_option('var', 'name'):
        var['name'] = config.get('var', 'name')
    else:
        sys.exit("No variable name given")
    if config.has_option('var', 'zname'):
        var['zname'] = config.get('var', 'zname')
    else:
        var['zname'] = 'height'
    if config.has_option('var', 'varlim'):
        var['varlim'] = get_several_input(config, 'var', 'varlim', f=True)
    if config.has_option('var', 'grid_file'):
        var['grid_file'] = config.get('var', 'grid_file')
    if config.has_option('var', 'time'):
        var['time'] = get_several_input(config, 'var', 'time', i=True)
    else:
        var['time'] = [0]
    if config.has_option('var', 'height'):
        var['height'] = get_several_input(config, 'var', 'height', i=True)
    else:
        var['height'] = [0]
    if config.has_option('var', 'unc'):
        var['unc'] = config.get('var', 'unc')

    # Read information regarding the map
    map = {}
    if config.has_option('map', 'lonmin'):
        map['lonmin'] = config.getfloat('map', 'lonmin')
    if config.has_option('map', 'lonmax'):
        map['lonmax'] = config.getfloat('map', 'lonmax')
    if config.has_option('map', 'latmin'):
        map['latmin'] = config.getfloat('map', 'latmin')
    if config.has_option('map', 'latmax'):
        map['latmax'] = config.getfloat('map', 'latmax')
    if config.has_option('map', 'add_grid'):
        map['add_grid'] = config.getboolean('map', 'add_grid')
    if config.has_option('map', 'projection'):
        map['projection'] = config.get('map', 'projection')
    if config.has_option('map', 'title'):
        map['title'] = config.get('map', 'title')
    if config.has_option('map', 'clabel'):
        map['clabel'] = config.get('map', 'clabel')
    if config.has_option('map', 'sig'):
        map['sig'] = config.getint('map', 'sig')
    else:
        map['sig'] = 0
    if config.has_option('map', 'alpha'):
        map['alpha'] = config.getfloat('map', 'alpha')
    else:
        map['alpha'] = 0.05
    if config.has_option('map', 'cmap'):
        map['cmap'] = config.get('map', 'cmap')
    if config.has_option('map', 'diff'):
        map['diff'] = config.get('map', 'diff')
    else:
        map['diff'] = 'abs'
    if config.has_option('map', 'col'):
        map['col'] = config.get('map', 'col')
    else:
        map['col'] = 'k'
    if config.has_option('map', 'marker'):
        map['marker'] = config.get('map', 'marker')
    else:
        map['marker'] = '.'
    if config.has_option('map', 'markersize'):
        map['markersize'] = config.getfloat('map', 'markersize')
    else:
        map['markersize'] = 0.5

    # Read information regarding coordinates
    coord = {}
    if config.has_section('coord'):
        if config.has_option('coord', 'name'):
            coord['name'] = get_several_input(config, 'coord', 'name')
        if config.has_option('coord', 'lon'):
            coord['lon'] = get_several_input(config, 'coord', 'lon', f=True)
        if config.has_option('coord', 'lat'):
            coord['lat'] = get_several_input(config, 'coord', 'lat', f=True)
        if config.has_option('coord', 'marker'):
            coord['marker'] = get_several_input(config, 'coord', 'marker')
        else:
            coord['marker'] = ['*']
        if len(coord['marker']) < len(coord['lon']):
            coord['marker'] = np.repeat(coord['marker'][0], len(coord['lon']))
        if config.has_option('coord', 'marker_size'):
            coord['marker_size'] = get_several_input(config,
                                                     'coord',
                                                     'marker_size',
                                                     f=True)
        else:
            coord['marker_size'] = [10]
        if len(coord['marker_size']) < len(coord['lon']):
            coord['marker_size'] = np.repeat(coord['marker_size'][0],
                                             len(coord['lon']))
        if config.has_option('coord', 'col'):
            coord['col'] = get_several_input(config, 'coord', 'col')
        else:
            coord['col'] = ['r']
        if len(coord['col']) < len(coord['lon']):
            coord['col'] = np.repeat(coord['col'][0], len(coord['lon']))
        if config.has_option('coord', 'name'):
            coord['name'] = get_several_input(config, 'coord', 'name')
            if len(coord['name']) < len(coord['lon']):
                coord['name'] = np.repeat(coord['name'][0], len(coord['lon']))

    #Read information regarding plot
    plot = {}
    if config.has_option('plot', 'xlabel'):
        plot['xlabel'] = config.get('plot', 'xlabel')
    if config.has_option('plot', 'ylabel'):
        plot['ylabel'] = config.get('plot', 'ylabel')
    if config.has_option('plot', 'xlim'):
        plot['xlim'] = get_several_input(config, 'plot', 'xlim', f=True)
    if config.has_option('plot', 'ylim'):
        plot['ylim'] = get_several_input(config, 'plot', 'ylim', f=True)
    if config.has_option('plot', 'title'):
        plot['title'] = config.get('plot', 'title')
    if config.has_option('plot', 'date_format'):
        plot['date_format'] = config.get('plot', 'date_format')
    else:
        plot['date_format'] = '%Y-%m-%d %H:%M'

    return [var, map, coord, plot]
