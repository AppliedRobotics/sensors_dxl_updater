DAC_DXL_RETURN = 240
DAC_PACKET_HEADER = 255
DAC_PACKET_END = 254

class DACPacketHandler(object):
    def txPacket(self, port, addr, packet) :                #transmit packet
        l = len(packet)
        b = []
        b.append(DAC_PACKET_HEADER)
        b.append(addr)
        b.append(l)
        b.extend(packet)
        b.append(DAC_PACKET_END)
        port.isUsing = True
        port.clearPort()
        written_packet_length = port.writePort(b)

    def return_to_DXL(self, port):                          #return to dxl
        packet = [DAC_DXL_RETURN, DAC_PACKET_END]
        port.isUsing = True
        port.clearPort()
        written_packet_length = port.writePort(packet)
        port.isUsing = False

    def rxPacket(self, port):                               #receive packet
        packet = []
        packet.extend(port.readPort(5))
        return packet