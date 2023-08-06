import os

def setup_www():
    def _get_www_cmd(port):
        # Serve www folder of the jupyter notebook directory
        os.makedirs('www', exist_ok = True) 
        cmd = [
            'python3', '-m', 'http.server', '-d', 'www', str(port)
        ]
        return cmd

    return {
        "command": _get_www_cmd,
        "timeout": 20,
        "new_browser_tab": True,
        "launcher_entry": {
            "title": "www",
            "icon_path": os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "icons",
                "www.svg"
            ),
        },
    }
