"""Build the pinned Unicode CascLib reader using local VS and SDK files only."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess

REVISION = '4971d363e665551ac4142f541e5f2d71f1cda653'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--visual-studio', type=Path, required=True)
    parser.add_argument('--sdk-common', type=Path, required=True)
    parser.add_argument('--sdk-x64', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    if subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() != REVISION:
        raise SystemExit('CascLib source revision mismatch')
    if subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain'], text=True).strip():
        raise SystemExit('CascLib source must be unmodified')
    vs = args.visual_studio.resolve()
    compiler = sorted((vs / 'VC/Tools/MSVC').iterdir())[-1]
    sdk = args.sdk_common.resolve() / 'c'
    version = sorted((sdk / 'Include').iterdir())[-1].name
    libraries = args.sdk_x64.resolve() / 'c'
    tool_root = vs / 'Common7/IDE/CommonExtensions/Microsoft/CMake'
    cmake = tool_root / 'CMake/bin/cmake.exe'
    env = {key.upper(): value for key, value in os.environ.items()}
    env['PATH'] = os.pathsep.join(map(str, [compiler / 'bin/Hostx64/x64', sdk / 'bin' / version / 'x64', tool_root / 'Ninja'])) + os.pathsep + env.get('PATH', '')
    env['INCLUDE'] = os.pathsep.join(map(str, [compiler / 'include', *(sdk / 'Include' / version / part for part in ('ucrt', 'shared', 'um', 'winrt'))]))
    env['LIB'] = os.pathsep.join(map(str, [compiler / 'lib/x64', libraries / 'um/x64', libraries / 'ucrt/x64']))
    root = Path(__file__).resolve().parents[1]
    output = root / 'build/casc-offline-reader'
    subprocess.run([str(cmake), '-S', str(source), '-B', str(output), '-G', 'Ninja',
                    '-DCMAKE_BUILD_TYPE=Release', '-DCASC_UNICODE=ON', '-DCASC_BUILD_SHARED_LIB=ON',
                    '-DCASC_BUILD_TESTS=OFF', '-DCMAKE_POLICY_VERSION_MINIMUM=3.5'], env=env, check=True)
    subprocess.run([str(cmake), '--build', str(output), '--parallel', '2'], env=env, check=True)
    target = root / 'desktop-app/src/dpslab/native'
    target.mkdir(exist_ok=True)
    shutil.copy2(output / 'CascLib.dll', target / 'CascLib.dll')
    shutil.copy2(source / 'LICENSE', target / 'CascLib-LICENSE.txt')


if __name__ == '__main__':
    main()
