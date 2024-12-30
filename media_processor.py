import os
import cv2
import numpy as np
from PIL import Image
import io
import logging
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

class MediaProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Get Azure credentials from environment variables
        self.endpoint = os.environ.get('AZURE_VISION_ENDPOINT')
        self.key = os.environ.get('AZURE_VISION_KEY')

        if not self.endpoint or not self.key:
            self.logger.error("Azure Vision API credentials not found in environment variables")
            raise ValueError("Azure Vision API credentials are required")

        try:
            self.vision_client = ComputerVisionClient(
                endpoint=self.endpoint,
                credentials=CognitiveServicesCredentials(self.key)
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure Vision client: {str(e)}")
            raise

    def compress_image(self, image_data, max_size=(800, 800)):
        """Compress and resize image while maintaining aspect ratio"""
        try:
            img = Image.open(io.BytesIO(image_data))
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85)
            return output.getvalue()
        except Exception as e:
            self.logger.error(f"Error compressing image: {str(e)}")
            raise

    def process_video(self, video_path):
        """Extract key frames from video and compress them"""
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            frame_count = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % 30 == 0:  # Extract frame every second (assuming 30fps)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb)
                    # Convert PIL Image to bytes
                    img_byte_arr = io.BytesIO()
                    pil_img.save(img_byte_arr, format='JPEG')
                    compressed = self.compress_image(img_byte_arr.getvalue())
                    frames.append(compressed)

                frame_count += 1

            cap.release()
            return frames
        except Exception as e:
            self.logger.error(f"Error processing video: {str(e)}")
            raise

    def analyze_media(self, image_data):
        """Analyze image using Azure Computer Vision API"""
        try:
            image = io.BytesIO(image_data)
            analysis = self.vision_client.analyze_image_in_stream(
                image,
                visual_features=['Tags', 'Description', 'Objects', 'Faces']
            )

            return {
                'description': analysis.description.captions[0].text if analysis.description.captions else "",
                'tags': [tag.name for tag in analysis.tags],
                'objects': [obj.object_property for obj in analysis.objects],
                'faces': len(analysis.faces)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing media: {str(e)}")
            raise