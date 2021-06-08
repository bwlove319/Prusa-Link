"""/api/connection endpoint handlers"""
from poorwsgi import state
from poorwsgi.response import JSONResponse

from .. import errors

from .main import PRINTER_STATES
from .lib.core import app
from .lib.auth import check_api_digest


@app.route('/api/connection')
@check_api_digest
def api_connection(req):
    """Returns printer connection info"""
    # pylint: disable=unused-argument
    service_connect = app.daemon.settings.service_connect
    cfg = app.daemon.cfg
    tel = app.daemon.prusa_link.model.last_telemetry

    # Token is available only after successful registration to Connect
    is_registrated = len(service_connect.token) > 0

    return JSONResponse(
        **{
            "current": {
                "baudrate": cfg.printer.baudrate,
                "port": cfg.printer.port,
                "printerProfile": "_default",
                "state": PRINTER_STATES[tel.state],
            },
            "options": {
                "ports": [cfg.printer.port],
                "baudrates": [cfg.printer.baudrate],
                "printerProfiles": [{
                    "id": "_default",
                    "name": "Prusa MK3S"
                }],
                "autoconnect": True
            },
            "connect": {
                "hostname": service_connect.hostname,
                "port": service_connect.port,
                "tls": bool(service_connect.tls),
                "registrated": is_registrated
            },
            "states": {
                "printer": errors.printer_status(),
                "connect": errors.connect_status()
            }
        })


@app.route('/api/connection', method=state.METHOD_POST)
@check_api_digest
def api_connection_set(req):
    """Returns URL for Connect registration completion"""
    service_connect = app.daemon.settings.service_connect
    printer_settings = app.daemon.settings.printer
    printer = app.daemon.prusa_link.printer

    hostname = req.json.get('hostname')
    port = req.json.get('port')
    tls = req.json.get('tls')

    type_ = printer.type
    code = printer.register()
    name = printer_settings.name
    location = printer_settings.location

    service_connect.hostname = hostname
    service_connect.port = port
    service_connect.tls = tls
    url = printer.connect_url(hostname, tls, port)

    url_ = f'{url}/add-printer/connect/{type_}/{code}/{name}/{location}'
    return JSONResponse(status_code=state.HTTP_OK, url=url_)
