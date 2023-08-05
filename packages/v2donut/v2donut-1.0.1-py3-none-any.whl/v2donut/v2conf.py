from __future__ import annotations

import json
import os

from v2donut.appsettings import AppSettings
from v2donut.subscription import VmessShare
from v2donut.utils import isipaddress


def gen_policy_settings():
    policy = {
        "levels": {"0": {"uplinkOnly": 0, "downlinkOnly": 0}},
        "system": {
            "statsInboundUplink": False,
            "statsInboundDownlink": False,
            "statsOutboundUplink": False,
            "statsOutboundDownlink": False,
        },
    }

    return policy


def gen_dns_settings(settings: AppSettings):
    hosts = {}
    servers = []

    for (k, v) in settings.dns.items():
        if isipaddress(k):
            servers.append({"address": k, "port": 53, "domains": v.split(",")})
        else:
            hosts[k] = v

    return {"hosts": hosts, "servers": servers}


def gen_routing_settings(settings: AppSettings):
    rules = []

    proxy = settings.rules.get("proxy")
    if proxy is not None:
        ip = []
        domain = []
        for p in proxy:
            if p.startswith("geoip:") or isipaddress(p):
                ip.append(p)
            else:
                domain.append(p)
        rules.append({"type": "field", "ip": ip, "domain": domain, "outboundTag": "proxy"})

    direct = settings.rules.get("direct")
    if direct is not None:
        ip = []
        domain = []
        for d in direct:
            if d.startswith("geoip:") or isipaddress(d):
                ip.append(d)
            else:
                domain.append(d)
        rules.append({"type": "field", "ip": ip, "domain": domain, "outboundTag": "direct"})

    blocked = settings.rules.get("blocked")
    if blocked is not None:
        ip = []
        domain = []
        for b in blocked:
            if b.startswith("geoip:") or isipaddress(b):
                ip.append(b)
            else:
                domain.append(b)
        rules.append({"type": "field", "ip": ip, "domain": domain, "outboundTag": "blocked"})

    return {"domainStrategy": "IPOnDemand", "rules": rules}


def gen_inbounds_settings(settings: AppSettings):
    socks_inbound = {
        "port": settings.socks_port,
        "listen": "0.0.0.0",
        "tag": "socks-inbound",
        "protocol": "socks",
        "settings": {"auth": "noauth", "udp": True},
        "sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
    }

    http_inbound = {
        "port": settings.http_port,
        "listen": "0.0.0.0",
        "tag": "http-inbound",
        "protocol": "http",
        "settings": {"auth": "noauth", "udp": True},
        "sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
    }

    return [socks_inbound, http_inbound]


def gen_outbounds_settings(v: VmessShare):
    proxy_outbound = {
        "tag": "proxy",
        "protocol": "vmess",
        "settings": {
            "vnext": [
                {
                    "address": v.host,
                    "port": v.port,
                    "users": [
                        {
                            "id": v.id,
                            "alterId": v.aid,
                            "security": "auto",
                        }
                    ],
                }
            ],
        },
        "streamSettings": {
            "network": "ws",
            "security": "tls",
            "tlsSettings": {"allowInsecure": False, "serverName": v.host},
            "wsSettings": {"connectionReuse": True, "path": "/v2ray", "headers": {"Host": v.host}},
        },
        "mux": {"enabled": True, "concurrency": 8},
    }

    return [
        proxy_outbound,
        {"protocol": "freedom", "settings": {}, "tag": "direct"},
        {"protocol": "blackhole", "settings": {}, "tag": "blocked"},
    ]


def gen_v2conf(v: VmessShare, settings: AppSettings):
    if not os.path.exists(settings.v2conf):
        raise ValueError(f"指定的 V2Ray 配置文件不存在")

    v2conf = {
        "log": {"loglevel": "warning"},
        "policy": gen_policy_settings(),
        "dns": gen_dns_settings(settings),
        "routing": gen_routing_settings(settings),
        "inbounds": gen_inbounds_settings(settings),
        "outbounds": gen_outbounds_settings(v),
        "other": {},
    }

    with open(settings.v2conf, "w") as v2conf_file:
        json.dump(v2conf, v2conf_file, indent=4)
