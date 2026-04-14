from dataclasses import dataclass

import cv2
import Quartz
import Vision


class HandTrackerError(RuntimeError):
    pass


@dataclass
class Landmark:
    x: float
    y: float
    confidence: float = 1.0


class HandTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

        if not self.cap.isOpened():
            self.cap.release()
            raise HandTrackerError(
                "Camera could not be opened. Check macOS Camera permissions."
            )

        for _ in range(10):
            self.cap.read()

        self.request = Vision.VNDetectHumanHandPoseRequest.alloc().init()
        self.request.setMaximumHandCount_(1)
        self.minimum_confidence = 0.25

        self.smooth_x = 0.0
        self.smooth_y = 0.0
        self.alpha = 0.35

    def _value(self, attribute):
        return attribute() if callable(attribute) else attribute

    def _frame_to_cgimage(self, frame):
        rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        height, width = rgba.shape[:2]

        provider = Quartz.CGDataProviderCreateWithCFData(rgba.tobytes())
        colorspace = Quartz.CGColorSpaceCreateDeviceRGB()
        bitmap_info = (
            Quartz.kCGImageAlphaPremultipliedLast
            | Quartz.kCGBitmapByteOrderDefault
        )

        return Quartz.CGImageCreate(
            width,
            height,
            8,
            32,
            rgba.strides[0],
            colorspace,
            bitmap_info,
            provider,
            None,
            False,
            Quartz.kCGRenderingIntentDefault,
        )

    def _recognized_landmark(self, observation, joint_name):
        point, error = observation.recognizedPointForJointName_error_(
            joint_name, None
        )
        if error is not None or point is None:
            return None

        confidence = float(self._value(point.confidence))
        if confidence < self.minimum_confidence:
            return None

        return Landmark(
            x=float(self._value(point.x)),
            y=1.0 - float(self._value(point.y)),
            confidence=confidence,
        )

    def get_hand(self):
        try:
            success, frame = self.cap.read()
            if not success:
                return None

            frame = cv2.flip(frame, 1)
            cgimage = self._frame_to_cgimage(frame)
            handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(
                cgimage, None
            )

            ok, error = handler.performRequests_error_([self.request], None)
            if not ok or error is not None:
                raise RuntimeError(error or "Vision request failed.")

            results = self.request.results() or []
            if not results:
                return None

            observation = results[0]
            thumb = self._recognized_landmark(
                observation,
                Vision.VNHumanHandPoseObservationJointNameThumbTip,
            )
            index = self._recognized_landmark(
                observation,
                Vision.VNHumanHandPoseObservationJointNameIndexTip,
            )

            if not thumb or not index:
                return None

            self.smooth_x = self.alpha * index.x + (1 - self.alpha) * self.smooth_x
            self.smooth_y = self.alpha * index.y + (1 - self.alpha) * self.smooth_y

            landmarks = [Landmark(0.0, 0.0, 0.0) for _ in range(21)]
            landmarks[4] = thumb
            landmarks[8] = index

            return {
                "x": self.smooth_x,
                "y": self.smooth_y,
                "fingers": [],
                "landmarks": landmarks,
            }

        except Exception as exc:
            print("Tracker error:", exc)
            return None

    def release(self):
        try:
            self.cap.release()
        except Exception:
            pass
        cv2.destroyAllWindows()
