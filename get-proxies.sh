#!/bin/sh
#
# Download fresh proxies

curl https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt > proxies.txt
curl https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt >> proxies.txt
