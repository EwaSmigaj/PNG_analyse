import sys
import fourier as ft
from functools import reduce
from chunk import Chunk, IHDR, IDAT



def str_to_class(str):
    return reduce(getattr, str.split("."), sys.modules[__name__])

# print(str_to_class("EWE"))

class PNGfile:
    def __init__(self, path):
        self.path = path
        self.signature = b'\x89PNG\r\n\x1a\n'
        self.chunk_names = [b"IHDR", b"PLTE", b"IDAT", b"IEND",
                            b"cHRM", b"gAMA", b"iCCP", b"sBIT", b"sRGB", b"bKGD", b"hIST", b"tRNS", "pHYs",
                            b"sPLT", b"tIME", b"iTXt", b"tEXt", b"zTXt"]
        self.name = path[:-4]
        self.file = open(path, 'rb')
        self.file_data = self.file.read()
        self.found_chunks_location = {"Critical ": {}, "Ancillary ": {}}
        self.chunks = {}

        # print(self.signature)
        # print(self.file_data[:len(self.signature)])
        if self.file_data[:len(self.signature)] != self.signature:
            raise Exception("Invalid PNG signature!")
        self.file.close()
        self.find_chunks()
        # print(self.found_chunks_location)
        self.get_chunks_bytes()
        # print(self.chunks)
        self.init_chunks()
        # print("PO INIT")
        # print(self.chunks)

        #display img etc

        self.anonimyzation()

    def find_chunks(self):  # fills self.found_chunks_location with chunks name and start position
        i = len(self.signature)

        while self.file_data[i:i+1]:
            if 65 < self.file_data[i] < 90 and self.file_data[i:i+4] in self.chunk_names: # chars 65 - 90 are A-Z
                type = self.file_data[i:i+4].decode("utf-8")
                if type in self.found_chunks_location["Critical "].keys():
                    self.found_chunks_location["Critical "][type].append(i - 4)
                else:
                    self.found_chunks_location["Critical "][type] = [i - 4]
                i += 4
            elif 97 < self.file_data[i] < 122 and self.file_data[i:i+4] in self.chunk_names:
                type = self.file_data[i:i+4].decode("utf-8")
                if type in self.found_chunks_location["Ancillary "].keys():
                    self.found_chunks_location["Ancillary "][type].append(i - 4)
                else:
                    self.found_chunks_location["Ancillary "][type] = [i - 4]
                i += 4
            else:
                i += 1


    '''
    Gets chunks data as a slice of self.byte_data.
    '''
    def get_data(self, index):
        start = index
        length = int.from_bytes(self.file_data[start:start+4], "big")
        end = index + length + 12
        return self.file_data[start:end]

    # using self.found_chunks_location fills self.chunks with byte data of each chunk
    # as list of touples e.g. {'Type': b'byte data', 'Type': b'byte data'}
    def get_chunks_bytes(self):
        for chunks in self.found_chunks_location.values():
            for chunk_type in chunks.keys():
                for index in chunks[chunk_type]:
                    if chunk_type in self.chunks.keys():
                        if type(self.chunks[chunk_type]) != list:
                            self.chunks[chunk_type].append(self.get_data(index))
                    else:
                        self.chunks[chunk_type] = self.get_data(index)

    '''
    finds if class of the chunk exist
    if yes, makes an instnace of that chunk
    if no, makes an universal instance of chunk
    '''
    def init_chunks(self):
        for chunk_type in self.chunks.keys():
            try:
                cls = str_to_class(chunk_type)
            except AttributeError:
                cls = None

            if cls:
                if chunk_type == "IDAT":
                    self.chunks[chunk_type] = cls(self.chunks[chunk_type],
                                                  self.chunks["IHDR"].width,
                                                  self.chunks["IHDR"].height,
                                                  self.chunks["IHDR"].color_type)
                    self.chunks["IHDR"].print_info()
                    #self.chunks["IDAT"].display()
                else:
                    self.chunks[chunk_type] = cls(self.chunks[chunk_type])
                    # self.chunks[chunk_type].print_info()
            else:
                self.chunks[chunk_type] = Chunk(self.chunks[chunk_type])
                # self.chunks[chunk_type].print_info()

    def anonimyzation(self):
            new_name = self.name + "_critical.png"
            tmp_png = open(new_name, "wb")
            tmp_png.write(self.file_data[:8])
            for chunk_type in self.found_chunks_location["Critical "].values():
                for index in chunk_type:
                    chunk_data = self.get_data(index)
                    tmp_png.write(chunk_data)
            print(f"Saved file after anonimyzation as: {new_name}")
            print()

    def fourier_analise(self):
        ft_plots = ft.Fourier(self.path)
        ft_plots.display()

    def display_chunks(self):
        for i in self.chunks:
            print(self.chunks[i].type)

    def display_chunks_info(self):
        for i in self.chunks:
            self.chunks[i].print_info()
            print()




