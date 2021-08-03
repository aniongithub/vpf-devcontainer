import os
import PyNvCodec as nvc
import numpy as np
import cv2
import argparse

FPS_DEFAULT=30

class Decoder:
    _nvDec: nvc.PyNvDecoder
    _h: int
    _w: int

    def __init__(self, nvDec: nvc.PyNvDecoder):
        self._nvDec = nvDec
        self._h = int(self._nvDec.Height())
        self._w = int(self._nvDec.Width())

    def __iter__(self):
        pass

    def __next__(self):
        pass

    @staticmethod
    def Create(filename: str, gpuID: int):
        nvDec = nvc.PyNvDecoder(filename, gpuID)
        if nvDec.Format() == nvc.PixelFormat.NV12:
            return NV12Decoder(nvDec)
        elif nvDec.Format() == nvc.PixelFormat.YUV444:
            return YUV444Decoder(nvDec)
        
class NV12Decoder(Decoder):
    _frame: np.ndarray
    
    def __iter__(self):
        self._frame = np.ndarray(shape=(self._h * 3//2, self._w), dtype=np.uint8)
        return self
    
    def __next__(self):
        if not self._nvDec.DecodeSingleFrame(self._frame):
            raise StopIteration
        yuv = self._frame.reshape(self._h * 3//2, self._w)
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)

class YUV444Decoder(Decoder):
    _frame: np.ndarray

    def __iter__(self):
        self._frame = np.ndarray(shape = (self._h * 3, self._w), dtype = np.uint8)
        return self

    def __next__(self):
        if not self._nvDec.DecodeSingleFrame(self._frame):
            raise StopIteration

        y = self._frame[:self._h, :self._w]
        u = self._frame[self._h: 2 * self._h, :self._w]
        v = self._frame[2 * self._h: 3 * self._h, : self._w]
        yuv = cv2.merge((y, u, v))
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpuID", default = 0, help = "Id of the GPU to use")
    parser.add_argument("--filename", required = True, help = "Path to video file to decode")
    parser.add_argument("--fps", default = FPS_DEFAULT, type = int, help = f"FPS to process the video at (default = {FPS_DEFAULT})")
    parser.add_argument("--verbose", help = "Add verbose output", action = "store_true")

    args = parser.parse_args()

    decoder = Decoder.Create(args.filename, args.gpuID)

    for frame in decoder:
        cv2.imshow(f"{os.path.basename(args.filename)}", frame)
        if cv2.waitKey(1000 // args.fps) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()