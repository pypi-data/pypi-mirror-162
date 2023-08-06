import logging
import platform
import os
import pmg


log = logging.getLogger(__name__)

def get_os_name():
    os_name = f"{platform.system()} {platform.version()}"
    try:
        if os.path.isfile('/etc/os-release'):
            with open('/etc/os-release', 'rt', encoding='utf-8') as f:
                for line in f:
                    k, v = line.split('=')
                    if k == "PRETTY_NAME":
                        os_name = pmg.unquote(v.strip(), '"')
                        break
    except Exception:
        pass
    return f'{os_name} ({platform.platform()})'

def get_package_versions(*packages_start_with):
    versions = []
    import pkg_resources
    for pkg in iter(pkg_resources.working_set):
        dist = pkg_resources.get_distribution(pkg)
        if any([dist.project_name.startswith(package_name) for package_name in packages_start_with]):
            versions.append(f'{dist.project_name} {dist.version}')
    return sorted(versions)
