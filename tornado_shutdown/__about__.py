__all__ = [
    'description',
    'maintainer',
    'maintainer_email',
    'url',
    'version_info',
    'version',
]

version_info = (1, 1, 0)
version = '.'.join(map(bytes, version_info))

maintainer = 'Nick Joyce'
maintainer_email = 'nick.joyce@realkinetic.com'

description = """
Utility library to help graceful shutdown of Tornado processes.
""".strip()

url = 'https://github.com/RealKinetic/tornado-shutdown'
