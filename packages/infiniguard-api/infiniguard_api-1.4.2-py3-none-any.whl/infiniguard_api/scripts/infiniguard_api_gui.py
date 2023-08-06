from infiniguard_api.api_server.infiniguard_api_app import create_app
import os
from infiniguard_api.lib.logging import iguard_logging as logging


def main():
    console_level = logging.CRITICAL if os.environ.get('INFINIGUARD_NO_CONSOLE_LOG') else logging.DEBUG
    log_handle = logging.setup_application_logger(console_level=console_level)
    with log_handle.applicationbound():
        infiniguard_api_app = create_app()
        infiniguard_api_app.run(host='0.0.0.0', port=5556, threaded=True, debug=False)


if __name__ == '__main__':
    main()
