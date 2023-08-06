# Octoxlabs
from octoxlabs import OctoxLabs

octo = OctoxLabs(ip="localhost", token="4e16b40746762515cfbd0072faad65df4fc34b02")

count, adapters = octo.get_adapters(page=3, size=1)
print(count)
print(adapters)
# discovery = octo.get_last_discovery()
#
# print(octo.get_asset_detail(hostname="centos7mariadb", discovery=discovery))
#
# print(discovery.parsed_start_time)
# print(discovery.parsed_end_time)
# print(type(discovery.parsed_end_time))


