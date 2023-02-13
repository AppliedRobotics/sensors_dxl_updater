DAC_DXL_RETURN = 240
DAC_PACKET_HEADER = 255
DAC_PACKET_END = 254
class DACPacketHandler(object):
    def txPacket(self, port, packet) :
        packet.insert(0, DAC_PACKET_HEADER)
        packet.append(DAC_PACKET_END)
        port.isUsing = True
        port.clearPort()
        written_packet_length = port.writePort(packet)
    def return_to_DXL(port):
        packet = DAC_DXL_RETURN
        written_packet_length = port.writePort(packet)