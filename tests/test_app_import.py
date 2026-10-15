import sys
import types
import unittest


class ExplodingYOLO:
    def __call__(self, *args, **kwargs):
        raise AssertionError("camera loop should not start during import")


class DummyClient:
    def __init__(self, *args, **kwargs):
        self._state = {}

    def register(self, *args, **kwargs):
        return None

    def start(self):
        return None

    def __setitem__(self, key, value):
        self._state[key] = value

    def __getitem__(self, key):
        return self._state.get(key)


class DummyCap:
    def __init__(self, *args, **kwargs):
        pass

    def read(self):
        return True, None

    def set(self, *args, **kwargs):
        return None

    def release(self):
        return None


class AppImportTests(unittest.TestCase):
    def test_import_app_does_not_start_hardware(self):
        for name in [
            "gpiozero",
            "arduino_iot_cloud",
            "ultralytics",
            "cv2",
            "secrets",
            "app",
        ]:
            sys.modules.pop(name, None)

        gpiozero = types.ModuleType("gpiozero")
        gpiozero.LED = lambda *args, **kwargs: None
        gpiozero.Button = lambda *args, **kwargs: None

        arduino = types.ModuleType("arduino_iot_cloud")
        arduino.ArduinoCloudClient = DummyClient

        ultralytics = types.ModuleType("ultralytics")
        ultralytics.YOLO = ExplodingYOLO

        cv2 = types.ModuleType("cv2")
        cv2.VideoCapture = lambda *args, **kwargs: DummyCap()
        cv2.rectangle = lambda *args, **kwargs: None
        cv2.putText = lambda *args, **kwargs: None
        cv2.destroyAllWindows = lambda: None
        cv2.FONT_HERSHEY_SIMPLEX = 0

        secrets = types.ModuleType("secrets")
        secrets.DEVICE_ID = "device"
        secrets.SECRET_KEY = "secret"

        sys.modules["gpiozero"] = gpiozero
        sys.modules["arduino_iot_cloud"] = arduino
        sys.modules["ultralytics"] = ultralytics
        sys.modules["cv2"] = cv2
        sys.modules["secrets"] = secrets

        import app  # noqa: F401

        self.assertTrue(hasattr(app, "main"))


if __name__ == "__main__":
    unittest.main()
