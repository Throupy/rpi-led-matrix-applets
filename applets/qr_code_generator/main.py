import os
import qrcode
import hashlib
from PIL import Image
from applets.base_applet import Applet


class QRCodeGenerator(Applet):
    """QR Code Applet Definition"""

    def __init__(self, **kwargs) -> None:
        """Initialisation function"""
        super().__init__("QR Code", **kwargs)
        self.data = self.options.get("data")
        self.qr_border_width = self.options.get("qr_border_width", 2)
        self.qr_box_size = self.options.get("qr_box_size", 8)
        self.log(
            f"Initialized QR code generator: border - {self.qr_border_width}, "
            f"box - {self.qr_box_size}, data - {self.data[:10]}..."
        )

    def generate_qr_code(self, data: str) -> str:
        """Generate QR code based on data passed in config"""
        hash_object = hashlib.md5(data.encode())
        filename = f"{hash_object.hexdigest()}.png"
        save_path = os.path.join(self.resources_directory, filename)
        if not os.path.exists(save_path):
            self.log(f"Creating a new QR code with data {data}")
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=self.qr_box_size,
                border=self.qr_border_width,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")
            img.save(save_path)

        return save_path

    def start(self) -> None:
        """Start the applet"""
        self.log("Starting")
        self.display.clear()
        # Generate QR code image and open it
        image_path = self.generate_qr_code(self.data)
        image = Image.open(image_path)
        # I think it already will fit, but just in case
        image = image.resize((self.display.matrix.width, self.display.matrix.height))
        image = image.convert("RGB")
        self.display.offscreen_canvas.SetImage(image, 0, 0)
        self.display.offscreen_canvas = self.display.matrix.SwapOnVSync(
            self.display.offscreen_canvas
        )
        # still need this for interrupt handling
        while not self.input_handler.exit_requested:
            pass

    def stop(self) -> None:
        """Stop the applet"""
        self.log("Stopping")
        self.display.clear()
