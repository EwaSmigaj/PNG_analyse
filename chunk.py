import zlib
import matplotlib.pyplot as matplot
import numpy

CHUNKS = {b"IHDR", b"IDAT", b"IEND"}


class Chunk:
    def __init__(self, bytes):
        self.bytes = bytes
        # print(f"CHUNK BYTES = {self.bytes.hex()}")
        self.length = int.from_bytes(self.bytes[0:4], "big")  # length always contains 4bytes
        # print(self.length)
        self.type = self.bytes[4:8].decode("utf-8")                 # type always contains 4 bytes
        self.data = self.bytes[8:8+self.length]   # data always contains {self.length} bytes
        # print(f"CHUNK DATA {self.data.hex()}")
        self.crc = self.bytes[8+self.length:self.length+12]            # crc always contains 4 bytes

    def print_info(self):
        print(f"type: {self.type}")
        print(f"length: {self.length}")
        print(f"crc (hex): {self.crc.hex()}")



def filter_method(t):
    types = {
        0: "None",
        1: "Sub",
        2:  "Up",
        3: "Average",
        4: "Path"
    }
    return types.get(t)

def interlace_method(i):
    if i == 0:
        return "No interlace"
    else:
        return "Adam7 inerlace"

class IHDR(Chunk):
    def __init__(self, bytes):
        super().__init__(bytes)
        self.width = int.from_bytes(self.data[0:4], byteorder='big')
        # print("KONSTRUKTOR IHRT WIDTH")
        # print(int.from_bytes(self.data[0:4], byteorder='big'))
        # print(self.data[0:4])
        self.height = int.from_bytes(self.data[4:8], byteorder='big')
        # print("KONSTRUKTOR IHRT HEIGHT")
        # print(int.from_bytes(self.data[4:8], byteorder='big'))
        # print(self.data[4:8])
        self.bit_depth = int.from_bytes(self.data[8:9], byteorder='big')
        self.color_type = int.from_bytes(self.data[9:10], byteorder='big')
        self.compression_method = int.from_bytes(self.data[10:11], byteorder='big')
        self.filter_method = filter_method(int.from_bytes(self.data[11:12], byteorder='big'))
        self.interlace_method = interlace_method(int.from_bytes(self.data[12:13], byteorder='big'))

    def print_info(self):                       # im not sure if it's good
        super().print_info()
        print(f"width: {self.width}")
        print(f"height: {self.height}")
        print(f"bit depth: {self.bit_depth}")
        print(f"color type: {self.color_type}")
        print(f"compresshion method: {self.compression_method}")
        print(f"filter method: {self.filter_method}")
        print(f"interlace method: {self.interlace_method}")
        print()


def bpp(color_type):
    byte_per_pixel = {
        0: 1,
        2: 3,
        3: 1,
        4: 2,
        6: 4
    }
    return byte_per_pixel.get(color_type)



class IDAT(Chunk):
    def __init__(self, bytes, width, height, color_type):
        super().__init__(bytes)
        self.width = width
        self.height = height
        self.color_type = color_type
        self.bpp = bpp(self.color_type)
        self.reconstructed = []
        self.data = zlib.decompress(self.data)

        a = 0
        line = self.width * self.bpp

        for r in range(self.height):
            filter_type = self.data[a]
            a += 1
            for c in range(line):
                filt_x = self.data[a]
                a += 1
                if filter_type == 0:
                    recon_x = filt_x
                elif filter_type == 1:
                    recon_x = filt_x + self.recon_a(r, c, line)
                elif filter_type == 2:  # Up
                    recon_x = filt_x + self.recon_b(r, c, line)
                elif filter_type == 3:  # Average
                    recon_x = filt_x + (self.recon_a(r, c, line) + self.recon_b(r, c, line)) // 2
                elif filter_type == 4:  # Paeth
                    recon_x = filt_x + self.path_predictor(self.recon_a(r, c, line), self.recon_b(r, c, line), self.recon_c(r, c, line))
                else:
                    raise Exception('unknown filter type: ' + str(filter_type))
                self.reconstructed.append(recon_x & 0xff)  # truncation to byte

    def recon_a(self, r, c, line):
        return self.reconstructed[r * line + c - self.bpp] if c >= self.bpp else 0

    def recon_b(self, r, c, line):
        return self.reconstructed[(r - 1) * line + c] if r > 0 else 0

    def recon_c(self, r, c, line):
        return self.reconstructed[(r - 1) * line + c - self.bpp] if r > 0 and c >= self.bpp else 0

    def path_predictor(self, a, b, c):
        p = a + b - c
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)
        if pa <= pb and pa <= pc:
            Pr = a
        elif pb <= pc:
            Pr = b
        else:
            Pr = c
        return Pr

    def print_info(self):
        super().print_info()
        print(f"length: {len(self.data)}")
        print(f"bytes per pixel: {self.bpp}")
        print(f"expected length: {self.height * (1 + self.width * self.bpp)}") # to check if everything is correct

    def display(self):
        matplot.imshow(numpy.array(self.reconstructed).reshape((self.height, self.width, self.bpp)))
        matplot.show()







