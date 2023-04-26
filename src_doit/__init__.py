from pathlib import Path
import functools
import subprocess

import mako.lookup
import mako.template

from hat.doit import common


__all__ = ['task_clean_all',
           'task_build',
           'task_html',
           'task_sass',
           'task_static',
           'task_node_modules']


build_dir = Path('build')
src_html_dir = Path('src_html')
src_scss_dir = Path('src_scss')
src_static_dir = Path('src_static')


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [build_dir])]}


def task_build():
    """Build"""
    return {'actions': None,
            'task_dep': ['html',
                         'sass',
                         'static']}


def task_html():
    """Build html"""
    for src_path, dst_path in _get_html_mappings():
        yield {'name': str(dst_path),
               'actions': [(_build_mako, [src_html_dir, src_path, dst_path])],
               'targets': [dst_path]}


def task_sass():
    """Build sass"""
    for src_path, dst_path in _get_scss_mappings():
        yield {'name': str(dst_path),
               'actions': [(_build_scss, [src_path, dst_path])],
               'targets': [dst_path],
               'task_dep': ['node_modules']}


def task_static():
    """Copy static files"""
    for src_path, dst_path in _get_static_mappings():
        yield {'name': str(dst_path),
               'actions': [functools.partial(dst_path.parent.mkdir,
                                             parents=True, exist_ok=True),
                           (common.cp_r, [src_path, dst_path])],
               'targets': [dst_path]}


def task_node_modules():
    """Install node_modules"""
    return {'actions': ['yarn install --silent']}


def _build_mako(tmpl_dir, src_path, dst_path, params={}):
    tmpl_lookup = mako.lookup.TemplateLookup(directories=[str(tmpl_dir)],
                                             input_encoding='utf-8')
    tmpl_uri = tmpl_lookup.filename_to_uri(str(src_path))
    tmpl = tmpl_lookup.get_template(tmpl_uri)
    output = tmpl.render(**params)

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text(output)


def _build_scss(src_path, dst_path):
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['node_modules/.bin/sass', '--no-source-map',
                    str(src_path), str(dst_path)],
                   check=True)


def _get_html_mappings():
    for src_path in src_html_dir.rglob('*.html'):
        if src_path.name.startswith('_'):
            continue
        dst_path = build_dir / src_path.relative_to(src_html_dir)
        yield src_path, dst_path


def _get_scss_mappings():
    for src_path in src_scss_dir.rglob('*.scss'):
        if src_path.name.startswith('_'):
            continue
        dst_path = (build_dir /
                    src_path.relative_to(src_scss_dir).with_suffix('.css'))
        yield src_path, dst_path


def _get_static_mappings():
    for src_path in src_static_dir.rglob('*'):
        if src_path.is_dir():
            continue
        dst_path = build_dir / src_path.relative_to(src_static_dir)
        yield src_path, dst_path
