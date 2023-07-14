import ntplib

timeServer = '10.252.101.174' # NTP SERVER Domain Or IP
c = ntplib.NTPClient()
for i in range(5):
    response = c.request(timeServer, version=3)
    print('NTP Server Time과 Local Time과 차이는 %.2f ms입니다.' % (response.offset*1000.0))