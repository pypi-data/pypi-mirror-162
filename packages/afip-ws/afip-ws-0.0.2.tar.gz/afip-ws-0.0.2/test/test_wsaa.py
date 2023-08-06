from afip import WSAA


wsdl_testing = 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms?WSDL'
wsdl_production = 'https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL'

wsaa = WSAA(
    wsdl_testing,
    open('../wsaa_test.crt').read(),
    open('../wsaa.key').read(),
)

wsaa.authorize('ws_sr_padron_a5')

wsaa = WSAA(
    wsdl_production,
    open('../wsaa.crt').read(),
    open('../wsaa.key').read(),
)

print(wsaa.authorize('ws_sr_padron_a5'))
