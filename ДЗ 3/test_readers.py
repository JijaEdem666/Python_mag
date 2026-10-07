import os
import argparse
import numpy as np
from skimage.filters.rank import equalize

from utils.reader import image_reader as imread
from utils.reader import csv_reader, bin_reader, txt_reader, json_reader, wav_histogram_reader
from utils.processor import histogram
from utils.writer import csv_writer, bin_writer, txt_writer, image_writer, json_writer

from utils.image_toner import stat_correction, equalization, gamma_correction
from wav_processor import process_wav


def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-img', '--img_path', default='', help='Path to image')
    parser.add_argument('-p', '--path', default='', help='Input file path')
    parser.add_argument('-o', '--output', help='Save file path')
    parser.add_argument('-m', '--mode', default='hist',
                        choices=['hist', 'equalize', 'gamma', 'wav'],
                        help='Processing mode: hist - statistical correction using reference histogram, '
                             'equalize - OpenCV histogram equalization, gamma - gamma correction, "wav" — WAV histogram + quantization')
    parser.add_argument('-g', '--gamma', type=float, default=1.0,
                        help='Gamma value (used in gamma mode)')
    return parser


def read_template_by_extension(path):
    ext = os.path.splitext(path)[1].lower()

    if ext in ('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.img'):
        img = imread.read_data(path)
        return histogram.image_processing(img)
    elif ext == '.csv':
        return csv_reader.read_data(path)
    elif ext == '.bin':
        return bin_reader.read_data(path)
    elif ext == '.txt':
        return txt_reader.read_data(path)
    elif ext == '.json':
        return json_reader.read_data(path)
    elif ext == '.wav':
        return wav_histogram_reader.read_wav_histogram(path)
    else:
        raise ValueError(f'Unsupported file extension: {ext}')


if __name__ == '__main__':
    parser = init_parser()
    args = parser.parse_args()

    image = imread.read_data(args.img_path)

    if args.mode == 'hist':
        hist = histogram.image_processing(image)
        hist_template = read_template_by_extension(args.path)
        res_image = stat_correction.processing(hist_template, image)
        image_writer.write_data(args.output, res_image)
    elif args.mode == 'equalize':
        res_image = equalization.equalize_histogram(image)
        image_writer.write_data(args.output, res_image)
    elif args.mode == 'gamma':
        res_image = gamma_correction.gamma_correction(image, args.gamma)
        image_writer.write_data(args.output, res_image)
    elif args.mode == 'wav':
        process_wav(args.path, args.output)
    else:
        raise ValueError(f'Unknown mode: {args.mode}')

