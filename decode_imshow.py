import PyNvCodec as nvc
import numpy as np
import cv2
import argparse

FPS_DEFAULT=30

parser = argparse.ArgumentParser()
parser.add_argument("--gpuId", default = 0, help = "Id of the GPU to use")
parser.add_argument("--filename", required = True, help = "Path to video file to decode")
parser.add_argument("--fps", default = FPS_DEFAULT, type = int, help = f"FPS to process the video at (default = {FPS_DEFAULT})")
parser.add_argument("--verbose", help = "Add verbose output", action = "store_true")

args = parser.parse_args()

gpuID = args.gpuId

vid = cv2.VideoCapture(args.filename)
h = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
w = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

# ffmpeg -r 30 -f image2 -s 640x480 -i %06d_left.png -vcodec libx264 -crf 20 -pix_fmt yuv420p left_yuv420p_h264.mp4

nvDec = nvc.PyNvDecoder(args.filename, gpuID)
frame_nv12 = np.ndarray(shape=(h * 3//2, w), dtype=np.uint8)

decoded_frames = 0
while True:
    if not nvDec.DecodeSingleFrame(frame_nv12):
        break
    else:
        decoded_frames += 1
    
    if args.verbose:
        print(f"Decoded frame: {decoded_frames}")
    
    yuv = frame_nv12.reshape(h * 3//2, w)
    rgb = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB_NV12)
    cv2.imshow("decoded", rgb)
    if cv2.waitKey(1000 // args.fps) & 0xFF == ord('q'):
        break