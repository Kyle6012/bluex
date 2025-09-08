#!/usr/bin/env python3
"""Generate simple pcap files containing Ethernet/IPv4/UDP packets with descriptive payloads.
These files are harmless and openable in Wireshark for demonstration purposes."""
import struct, time, random, sys, os
def mac_bytes(mac):
    return bytes(int(x,16) for x in mac.split(':'))

def ipv4_bytes(addr):
    return bytes(int(x) for x in addr.split('.'))

def build_udp_packet(src_mac, dst_mac, src_ip, dst_ip, src_port, dst_port, payload_bytes):
    # Ethernet header (14 bytes)
    eth = mac_bytes(dst_mac) + mac_bytes(src_mac) + struct.pack('!H', 0x0800)
    # IPv4 header (minimal, no options)
    ver_ihl = (4 << 4) | 5
    tos = 0
    total_length = 20 + 8 + len(payload_bytes)
    ident = random.randint(0, 0xFFFF)
    flags_frag = 0
    ttl = 64
    proto = 17  # UDP
    checksum = 0
    ip_hdr = struct.pack('!BBHHHBBH4s4s', ver_ihl, tos, total_length, ident, flags_frag, ttl, proto, checksum, ipv4_bytes(src_ip), ipv4_bytes(dst_ip))
    # skip IP checksum for simplicity (Wireshark will still parse)
    # UDP header
    udp_len = 8 + len(payload_bytes)
    udp_hdr = struct.pack('!HHHH', src_port, dst_port, udp_len, 0)
    pkt = eth + ip_hdr + udp_hdr + payload_bytes
    return pkt

def write_pcap(filename, packets):
    # Global header
    gh = struct.pack('<IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)  # linktype 1 = Ethernet
    with open(filename, 'wb') as f:
        f.write(gh)
        for ts, pkt in packets:
            sec = int(ts)
            usec = int((ts - sec) * 1_000_000)
            f.write(struct.pack('<IIII', sec, usec, len(pkt), len(pkt)))
            f.write(pkt)

def generate(filename, count=50):
    packets = []
    for i in range(count):
        src_mac = '02:00:00:00:00:%02x' % (i%256)
        dst_mac = '02:00:00:11:22:%02x' % (i%256)
        src_ip = '10.0.0.%d' % (1 + (i%250))
        dst_ip = '10.0.1.%d' % (1 + ((i*2)%250))
        src_port = 40000 + (i%1000)
        dst_port = 20000 + (i%1000)
        payload = ('SIM_PKT %d from %s to %s | type: %s' % (i, src_ip, dst_ip, random.choice(['ADV','ATT','GATT_READ','GATT_WRITE']))).encode('utf-8')
        pkt = build_udp_packet(src_mac, dst_mac, src_ip, dst_ip, src_port, dst_port, payload)
        packets.append((time.time() + i*0.001, pkt))
    write_pcap(filename, packets)
    print('WROTE', filename)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv)>1 else 'logs/fake_btle_like.pcap'
    cnt = int(sys.argv[2]) if len(sys.argv)>2 else 100
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    generate(out, cnt)
