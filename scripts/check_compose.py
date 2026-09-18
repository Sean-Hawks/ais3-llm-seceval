#!/usr/bin/env python3
"""Validate local sandbox topology through Compose without starting containers."""

import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
files = [ROOT / 'ctf/compose.yaml', *sorted((ROOT / 'ctf/bench27/recent2026').glob('*/compose.yaml'))]

for path in files:
    result = subprocess.run(['docker', 'compose', '-f', str(path), 'config', '--format', 'json'],
                            capture_output=True, text=True, check=True, timeout=30)
    config = json.loads(result.stdout)
    if path.parent.name == 'ctf':
        assert config['services']['default']['network_mode'] == 'none', path
    else:
        assert config['networks']['default']['internal'], path
        for service in config['services'].values():
            assert not service.get('ports'), f'Unexpected host port in {path}'
            assert service.get('networks') == {'default': None}, f'Unexpected network in {path}'
    for service in config['services'].values():
        if 'build' in service:
            build = service['build']
            context = Path(build['context'])
            assert context.is_dir(), context
            assert (context / build.get('dockerfile', 'Dockerfile')).is_file(), context
    print('PASS:', path.relative_to(ROOT))
