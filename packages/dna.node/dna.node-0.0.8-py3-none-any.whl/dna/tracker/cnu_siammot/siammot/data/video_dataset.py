import torch
import itertools
import torch.utils.data as data
import copy

from tqdm import tqdm
from PIL.Image import Image

from detectron2.structures import Instances, Boxes, BoxMode

from gluoncv.torch.data.gluoncv_motion_dataset.dataset import GluonCVMotionDataset, AnnoEntity


class VideoDataset(data.Dataset):

    def __init__(self, dataset: GluonCVMotionDataset, sampling_interval=250, clip_len=1000,
                 is_train=True, frames_in_clip=2, transforms=None, filter_fn=None,
                 amodal=False):
        """
        :param dataset: the ingested dataset with GluonCVMotionDataset
        :param sampling_interval: the temporal stride (in ms) of sliding window
        :param clip_len: the temporal length (in ms) of video clips
        :param is_train: a boolean flag indicating whether it is training
        :param frames_in_clip: the number of frames sampled in a video clip (for a training example)
        :param transforms: frame-level transformation before they are fed into neural networks
        :param filter_fn: a callable function to filter entities
        :param amodal: whether to clip the bounding box beyond image boundary
        """

        if dataset is None:
            raise Exception('dataset should not be None. Call GluonCVMotionDataset to construct dataset first.')

        assert is_train is True, "The dataset class only supports training"
        assert (2 >= frames_in_clip > 0), "frames_in_clip has to be 1 or 2"

        self.data = dict(dataset.train_samples)

        self.clip_len = clip_len
        self.transforms = transforms
        self.filter_fn = None #filter_fn
        self.frames_in_clip = min(clip_len, frames_in_clip)

        # Process dataset to get all valid video clips
        #self.clips = self.get_video_clips(sampling_interval_ms=sampling_interval) #original code
        self.clips = self.get_tao_clips(sampling_interval_ms=sampling_interval)
        self.amodal = amodal

    def __getitem__(self, item_id):

        video = []
        target = []

        (sample_id, clip_frame_ids) = self.clips[item_id]
        video_info = self.data[sample_id]
        video_reader = video_info.get_data_reader()

        # Randomly sampling self.frames_in_clip frames
        # And keep their relative temporal order
        image_ids = []
        info = []
        for frame_idx in clip_frame_ids: #TAO
            info.append(video_info.frame_reader._frame_paths[frame_idx])
            im = video_reader[frame_idx][0]
            w, h = im.size
            entities = video_info.get_entities_for_frame_num(frame_idx)
            for e in entities:
                image_ids.append(e.id)
            if self.filter_fn is not None:
                entities, _ = self.filter_fn(entities, meta_data=video_info.metadata)
            instance = self.entity2target(im, entities)

            video.append(im)
            target.append(instance)

        # Video clip-level augmentation
        if self.transforms is not None:
            video, target = self.transforms(video, target)

        video_target_ = []
        TO_REMOVE = 1
        vt = copy.deepcopy(target)
        for i, vt_ in enumerate(vt):
            h_, w_ = vt_.image_size
            vt[i].gt_boxes.tensor[:, 0].clamp_(min=0, max=w_ - TO_REMOVE)
            vt[i].gt_boxes.tensor[:, 1].clamp_(min=0, max=h_ - TO_REMOVE)
            vt[i].gt_boxes.tensor[:, 2].clamp_(min=0, max=w_ - TO_REMOVE)
            vt[i].gt_boxes.tensor[:, 3].clamp_(min=0, max=h_ - TO_REMOVE)
            box = vt[i].gt_boxes.tensor
            keep = (box[:, 3] > box[:, 1]) & (box[:, 2] > box[:, 0])
            video_target_.append(vt[i][keep])

        outputs = []
        for idx in range(len(clip_frame_ids)):
            image_id = image_ids[idx]
            outputs.append({
                "info": info[idx],
                "image_id": image_id,
                "height": h,
                "width": w,
                "image": video[idx],
                "instances": video_target_[idx]
            })

        return outputs

    def __len__(self):
        return len(self.clips)

    def get_tao_clips(self, sampling_interval_ms=250):
        """
        Process the long videos to a small video chunk (with self.clip_len seconds)
        Video clips are generated in a temporal sliding window fashion
        """
        video_clips = []
        for (sample_id, sample) in tqdm(self.data.items()):
            frame_idxs_with_anno = sample.get_non_empty_frames(self.filter_fn)
            if len(frame_idxs_with_anno) == 0:
                continue
            # The video clip may not be temporally continuous
            start_frame = min(frame_idxs_with_anno)
            end_frame = max(frame_idxs_with_anno)
            # make sure that the video clip has at least two frames
            clip_len_in_frames = max(self.frames_in_clip, int(self.clip_len / 1000. * sample.fps))
            sampling_interval = int(sampling_interval_ms / 1000. * sample.fps)
            if sampling_interval == 0: #not original code
                sampling_interval = 1 #not original code
            for idx in range(start_frame, end_frame, sampling_interval):
                clip_frame_ids = []
                # only include frames with annotation within the video clip
                for frame_idx in range(idx, idx + clip_len_in_frames):
                    if frame_idx in frame_idxs_with_anno:
                        clip_frame_ids.append(frame_idx)
                # Only include video clips that have at least self.frames_in_clip annotating frames
                if len(clip_frame_ids) >= self.frames_in_clip:
                    video_clips.append((sample_id, clip_frame_ids))

        return video_clips

    def get_video_clips(self, sampling_interval_ms=250):
        """
        Process the long videos to a small video chunk (with self.clip_len seconds)
        Video clips are generated in a temporal sliding window fashion
        """
        video_clips = []
        for (sample_id, sample) in tqdm(self.data.items()):
            frame_idxs_with_anno = sample.get_non_empty_frames(self.filter_fn)
            if len(frame_idxs_with_anno) == 0:
                continue
            # The video clip may not be temporally continuous
            start_frame = min(frame_idxs_with_anno)
            end_frame = max(frame_idxs_with_anno)
            # make sure that the video clip has at least two frames
            clip_len_in_frames = max(self.frames_in_clip, int(self.clip_len / 1000. * sample.fps))
            sampling_interval = int(sampling_interval_ms / 1000. * sample.fps)
            if sampling_interval == 0: #not original code
                sampling_interval = 1 #not original code
            for idx in range(start_frame, end_frame, sampling_interval):
                clip_frame_ids = []
                # only include frames with annotation within the video clip
                for frame_idx in range(idx, idx + clip_len_in_frames):
                    if frame_idx in frame_idxs_with_anno:
                        clip_frame_ids.append(frame_idx)
                # Only include video clips that have at least self.frames_in_clip annotating frames
                if len(clip_frame_ids) >= self.frames_in_clip:
                    video_clips.append((sample_id, clip_frame_ids))

        return video_clips

    def entity2target(self, im: Image, entities: [AnnoEntity]):
        """
        Wrap up the entity to maskrcnn-benchmark compatible format - BoxList
        """
        boxes = [entity.bbox for entity in entities]
        ids = [int(entity.id) for entity in entities]
        # we only consider person tracking for now,
        # thus all the labels are 1,
        # reserve category 0 for background during training
        int_labels = [int(entity.labels['label']) - 1 for entity in entities]
        # int_labels = [entity.labels[list(entity.labels.keys())[0]] for entity in entities]
        boxes = torch.as_tensor(boxes).reshape(-1, 4)
        boxes = BoxMode.convert(boxes, BoxMode.XYWH_ABS, BoxMode.XYXY_ABS)

        w, h = im.size
        bbox = Boxes(boxes)
        instance = Instances((h, w))
        instance.set("gt_boxes", bbox)
        instance.set("gt_classes", torch.as_tensor(int_labels, dtype=torch.int64))
        instance.set("ids", torch.as_tensor(ids, dtype=torch.int64))

        return instance


class VideoDatasetBatchCollator(object):
    """
    From a list of samples from the dataset,
    returns the batched images and targets.
    This should be passed to the DataLoader
    """
    def __init__(self, size_divisible=0):
        self.size_divisible = size_divisible

    def __call__(self, batch):
        return list(itertools.chain(*batch))