import re, os
def safe_filename(name):
    name = re.sub(r"[^\w\-. ]", "_", name)
    return name.replace(" ", "_")

# requires 'faster-whisper' installed
def try_transcribe_audio(path):
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("small")                # choose tiny/base/small/...
        segments, info = model.transcribe(path, beam_size=5)
        return " ".join([seg.text for seg in segments]).strip()
    except Exception as e:
        print("transcribe failed", e)
        return None

def try_image_caption(path):
    try:
        from PIL import Image
        from transformers import BlipProcessor, BlipForConditionalGeneration
        proc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        img = Image.open(path).convert("RGB")
        inputs = proc(img, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=30)
        return proc.decode(out[0], skip_special_tokens=True)
    except Exception as e:
        print("caption failed", e)
        return None


import cv2, os
def extract_keyframes(video_path, out_dir, every_n_secs=2):
    os.makedirs(out_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_interval = int(fps * every_n_secs)
    idx = 0; saved=[]
    while True:
        ret, frame = cap.read()
        if not ret: break
        if idx % frame_interval == 0:
            fname = os.path.join(out_dir, f"frame_{idx}.jpg")
            cv2.imwrite(fname, frame)
            saved.append(fname)
        idx += 1
    cap.release()
    return saved

# utils.py
import re, os

def safe_filename(name):
    name = re.sub(r"[^\w\-. ]", "_", name)
    return name.replace(" ", "_")

def try_transcribe_audio(path):
    # TODO: add Whisper/faster-whisper later
    return None

def try_image_caption(path):
    # TODO: add BLIP later
    return None
