dataset_maps = dict()
"""
each item in the dataset maps are a list of the following info
(
dataset_folder, 
annotation file name (video dataset) / path of annotation file (image dataset), 
split file name (video dataset) / path of image folder (image dataset) , 
modality
)
"""

dataset_maps['TAO'] = ['TAO',
                       'train_482.json',
                       'splits.json',
                       'video']

dataset_maps['BDD100k'] = ['data/bdd100k',
                       'bdd100k_train.json',
                       'splits.json',
                       'video']
#
dataset_maps['coco_vehicle'] = ['data/coco',
                                'annotations/coco_vehicle.json',
                                'train2017',
                                'image']
#
dataset_maps['MOT_vehicle'] = ['data/MOT17_all',
                               'mot17_vehicle_tracking.json',
                               'splits.json',
                               'video']