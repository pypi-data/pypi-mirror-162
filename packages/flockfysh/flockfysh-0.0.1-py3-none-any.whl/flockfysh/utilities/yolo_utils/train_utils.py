import os
import shutil
from tokenize import Name
from scraper.augmentations.run_augs import run_and_save_augments_on_image_sets
from utilities.dataset_setup.setup import setup_raw_dataset
import glob
from config import YOLO_URL, YOLO_DIR, PHOTO_DIRNAME, PHOTO_DIRECTORY, BASE_DIR
import git 
from argparse import Namespace
from importlib import import_module

def train_yolo(DIM = 416, BATCH = 32, EPOCHS = 500, MODEL = 'yolov5s', WORKERS = 8):


	#Programmatically access the main() (training method located in yolov5's train.py file)
	run_train = getattr(import_module(os.path.join('yolov5', 'train').replace('/', '.')), 'run')
	run_train(imgsz = DIM, batch = BATCH, workers = WORKERS, epochs = EPOCHS, data = os.path.abspath(os.path.join(YOLO_DIR, 'raw_dataset', 'data.yaml')), weights = f'{MODEL}.pt', cache = True)

def setup_and_train_yolo(**args):

	for pth in [YOLO_DIR, os.path.join(BASE_DIR, 'false'), os.path.join(BASE_DIR, PHOTO_DIRNAME) , PHOTO_DIRECTORY, os.path.join(args['output-working-dir'], 'finalized-dataset'), os.path.join(args['output-working-dir'], 'best-model-info')]:
		if os.path.exists(pth):
			shutil.rmtree(pth)
			if os.path.exists(pth):
				os.rmdir(pth)

	#TODO: add code to delete any cached json files
	[os.remove(file) for file in glob.glob("*.json" , recursive=True)]

	print('Cloning yolo repo ...')
	git.Repo.clone_from(YOLO_URL, YOLO_DIR)

	data_yaml_fp = setup_raw_dataset(**args)


	global_cnt = 0
	for path in ['train', 'valid']:
		for pth in os.listdir(os.path.join(YOLO_DIR, 'raw_dataset', path, 'images')):
			os.rename(os.path.join(YOLO_DIR, 'raw_dataset' , path, 'images', pth), os.path.join(YOLO_DIR, 'raw_dataset' , path, 'images', f'image-{global_cnt + 1}.{pth.split(".")[-1]}'))
			os.rename(os.path.join(YOLO_DIR, 'raw_dataset', path, 'labels', f'{pth[:pth.rfind(".")]}.txt'), os.path.join(YOLO_DIR, 'raw_dataset' , path, 'labels', f'image-{global_cnt + 1}.txt'))
			global_cnt += 1


	#Generate image augmentations on the training images
	run_and_save_augments_on_image_sets(os.listdir(os.path.abspath(os.path.join(YOLO_DIR, 'raw_dataset', 'train', 'images'))), os.listdir(os.path.abspath(os.path.join(YOLO_DIR, 'raw_dataset', 'train', 'labels'))), args['max-train-images'], os.path.abspath(os.path.join(YOLO_DIR, 'raw_dataset')), 'train')

	train_yolo(args['image-dimension'], args['train-batch'], args['train-epochs'], args['yolo-model'], args['train-workers'])