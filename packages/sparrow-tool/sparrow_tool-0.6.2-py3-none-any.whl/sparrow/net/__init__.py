import socket


def get_inner_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]


def get_outer_ip():
    import requests
    return requests.get('http://ifconfig.me/ip', timeout=1).text.strip()


if __name__ == "__main__":
    print(get_inner_ip())
    print(get_outer_ip())
