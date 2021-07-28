from numpy.lib.function_base import median
import PyNvCodec as nvc
import numpy as np
import cv2
import argparse
import matplotlib.pyplot as plt
import os
from skimage.metrics import structural_similarity as calc_ssim
import statistics

FPS_DEFAULT=10

parser = argparse.ArgumentParser()
parser.add_argument("--gpuId", default = 0, help = "Id of the GPU to use")
parser.add_argument("--filename", required = True, help = "Path to video file to decode")
parser.add_argument("--ground-truth-images", nargs='+', default=[], help = "Glob expression or set of all ground truth images")
parser.add_argument("--plot-filename", default= "metrics.png", help = "Filename to write the PSNR plot to")
parser.add_argument("--fps", default = FPS_DEFAULT, type = int, help = f"FPS to process the video at (default = {FPS_DEFAULT})")
parser.add_argument("--show", help = "Show frame comparison", action = "store_true")

args = parser.parse_args()

gpuID = args.gpuId

vid = cv2.VideoCapture(args.filename)
h = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
w = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
video_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

image_count = min(video_frames, len(args.ground_truth_images))

nvDec = nvc.PyNvDecoder(args.filename, gpuID)
frame_nv12 = np.ndarray(shape=(0), dtype=np.uint8)

args.ground_truth_images.sort()

processed = 0
psnr = []
mse = []
gray_mse = []
ssim = []
for frame in range(image_count):
    print(f"Processing frame: {frame}")

    if not nvDec.DecodeSingleFrame(frame_nv12):
        break
    yuv = frame_nv12.reshape(h * 3//2, w)
    rgb_decoded = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
    rgb_ground_truth = cv2.imread(args.ground_truth_images[frame])

    ground_truth_gray = cv2.cvtColor(rgb_ground_truth, cv2.COLOR_BGR2GRAY)
    decoded_gray = cv2.cvtColor(rgb_decoded, cv2.COLOR_BGR2GRAY)

    psnr.append(cv2.PSNR(rgb_ground_truth, rgb_decoded))    
    mse.append(np.square(np.subtract(rgb_ground_truth, rgb_decoded)).mean())
    gray_mse.append(np.square(np.subtract(ground_truth_gray, decoded_gray)).mean())
    ssim.append(calc_ssim(rgb_ground_truth, rgb_decoded, multichannel = True))

    if args.show:
        compare = cv2.hconcat([rgb_ground_truth, rgb_decoded])
        cv2.putText(compare, os.path.basename(args.ground_truth_images[frame]), (10, 30), 0, 1, 255)
        cv2.putText(compare, f"frame {processed}", (10 + w, 30), 0, 1, 255)
        cv2.imshow("Image comparison", compare)
        cv2.waitKey(1000 // args.fps)

    processed += 1

print(f"PSNR - min: {min(psnr)}, max: {max(psnr)}, mean: {sum(psnr)/len(psnr)}, median: {median(psnr)}")
print(f"MSE - min: {min(mse)}, max: {max(mse)}, mean: {sum(mse)/len(mse)}, median: {median(mse)}")
print(f"Gray MSE - min: {min(gray_mse)}, max: {max(gray_mse)}, mean: {sum(gray_mse)/len(gray_mse)}, median: {median(gray_mse)}")
print(f"SSIM - min: {min(ssim)}, max: {max(ssim)}, mean: {sum(ssim)/len(ssim)}, median: {median(ssim)}")

plt.plot(range(image_count), psnr)
plt.plot(range(image_count), mse)
plt.plot(range(image_count), gray_mse)
plt.plot(range(image_count), ssim)
plt.legend(["PSNR", "MSE", "Gray MSE", "SSIM"])
  
plt.xlabel("frames")
  
plt.title("Metrics - ground truth vs. decoded")

plt.savefig(args.plot_filename)